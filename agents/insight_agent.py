import json
import sys
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Ensure venv site-packages is discoverable if present
_venv_site = Path(__file__).resolve().parent.parent / "venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

from config.settings import is_openrouter_configured
from utils.llm_client import llm_client
from utils.nlp_utils import tokenize_and_clean, count_bigrams
from utils.pdf_exporter import export_pdf
from utils.storage import load_json, save_json

def _print_msg(msg: str):
    if HAS_RICH and console:
        console.print(msg)
    else:
        import re
        clean_msg = re.sub(r"\[/?(?:bold|dim|italic|yellow|cyan|green|red|blue|magenta)[^\]]*\]", "", msg)
        print(clean_msg)

class InsightExtractionAgent:
    def __init__(
        self,
        survey_path: str = "data/survey_responses.json",
        interview_path: str = "data/interview_logs.json",
        persona_path: str = "data/persona_pool.json",
        experiment_path: str = "data/experiment.json",
        report_dir: str = "reports"
    ):
        self.survey_path = survey_path
        self.interview_path = interview_path
        self.persona_path = persona_path
        self.experiment_path = experiment_path
        self.report_dir = report_dir

    def generate_report(self) -> Dict[str, Any]:
        survey_data = load_json(self.survey_path, {})
        interview_logs = load_json(self.interview_path, [])
        personas = load_json(self.persona_path, [])
        experiment = load_json(self.experiment_path, {})

        product_name = experiment.get("product_name", "Product Under Research")
        date_str = datetime.now().strftime("%Y-%m-%d")

        all_texts: List[str] = []
        sentiments: List[str] = []

        if "responses" in survey_data:
            for resp in survey_data["responses"]:
                for ans in resp.get("answers", []):
                    all_texts.append(ans.get("answer", ""))
                    sentiments.append(ans.get("sentiment", "neutral"))

        for sess in interview_logs:
            for t in sess.get("turns", []):
                all_texts.append(t.get("persona_response", ""))

        total_s = len(sentiments) if sentiments else 1
        calc_sentiment_dist = {
            "positive": round(sentiments.count("positive") / total_s, 2),
            "neutral": round(sentiments.count("neutral") / total_s, 2),
            "negative": round(sentiments.count("negative") / total_s, 2)
        }

        tokens = tokenize_and_clean(all_texts)
        bigram_counts = count_bigrams(tokens)
        nlp_themes = [f"{phrase} ({count} mentions)" for phrase, count in bigram_counts.most_common(5)]

        if is_openrouter_configured():
            try:
                report_data = self._generate_with_llm(
                    experiment=experiment,
                    personas=personas,
                    survey_data=survey_data,
                    interview_logs=interview_logs,
                    calc_sentiment_dist=calc_sentiment_dist,
                    nlp_themes=nlp_themes
                )
            except Exception as e:
                _print_msg(f"[bold yellow]OpenRouter Report Generation Notice:[/bold yellow] {e}")
                report_data = self._generate_fallback(
                    experiment=experiment,
                    personas=personas,
                    survey_data=survey_data,
                    calc_sentiment_dist=calc_sentiment_dist,
                    nlp_themes=nlp_themes
                )
        else:
            report_data = self._generate_fallback(
                experiment=experiment,
                personas=personas,
                survey_data=survey_data,
                calc_sentiment_dist=calc_sentiment_dist,
                nlp_themes=nlp_themes
            )

        if isinstance(report_data, list):
            if report_data and isinstance(report_data[0], dict):
                report_data = report_data[0]
            else:
                report_data = self._generate_fallback(
                    experiment=experiment,
                    personas=personas,
                    survey_data=survey_data,
                    calc_sentiment_dist=calc_sentiment_dist,
                    nlp_themes=nlp_themes
                )

        report_data["report_date"] = date_str
        report_data["product"] = product_name
        report_data["persona_count"] = len(personas)
        report_data["survey_questions_asked"] = len(survey_data.get("questions", []))
        report_data["interview_sessions_count"] = len(interview_logs)

        json_path = f"{self.report_dir}/report_{date_str}.json"
        pdf_path = f"{self.report_dir}/report_{date_str}.pdf"

        save_json(json_path, report_data)
        export_pdf(report_data, pdf_path)
        return report_data

    def _generate_with_llm(
        self,
        experiment: Dict[str, Any],
        personas: List[Dict[str, Any]],
        survey_data: Dict[str, Any],
        interview_logs: List[Dict[str, Any]],
        calc_sentiment_dist: Dict[str, float],
        nlp_themes: List[str]
    ) -> Dict[str, Any]:
        """Synthesizes comprehensive research findings using OpenRouter LLM."""
        p_name = experiment.get("product_name", "Product")
        p_desc = experiment.get("product_description", "")
        audience = experiment.get("target_audience", "")
        objs = experiment.get("research_objectives", [])

        persona_summaries = []
        for p in personas:
            persona_summaries.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "archetype": p.get("archetype"),
                "occupation": p.get("occupation"),
                "traits": p.get("personality_traits", []),
                "pain_points": p.get("behavioral_patterns", {}).get("primary_pain_points", ""),
                "willingness_to_pay": p.get("behavioral_patterns", {}).get("willingness_to_pay", ""),
                "churn_triggers": p.get("behavioral_patterns", {}).get("churn_triggers", "")
            })

        prompt = f"""You are a Principal Product Discovery & Strategy Director.
Analyze the following empirical synthetic user research data:

PRODUCT CONTEXT:
- Name: {p_name}
- Description: {p_desc}
- Target Audience: {audience}
- Research Objectives: {json.dumps(objs)}

PERSONAS IN STUDY:
{json.dumps(persona_summaries, indent=2)}

SURVEY RESULTS:
{json.dumps(survey_data.get("responses", []), indent=2)}

INTERVIEW LOGS:
{json.dumps(interview_logs, indent=2)}

EMPIRICAL METRICS:
- Measured Sentiment: {calc_sentiment_dist}
- Top Frequent Text Themes: {nlp_themes}

Produce an insightful, highly actionable user research synthesis in valid JSON with this exact schema:
{{
  "executive_summary": "2-3 sentences synthesizing product-market validation signals and core user reception.",
  "themes": ["Key Theme 1", "Key Theme 2", "Key Theme 3", "Key Theme 4"],
  "sentiment_distribution": {{"positive": 0.50, "neutral": 0.30, "negative": 0.20}},
  "sentiment_analysis": "Explanation of what factors created enthusiasm vs skepticism.",
  "behavioral_trends": [
    {{"group": "Cohort/Archetype Name", "finding": "Specific empirical behavioral trend, preference, or objection"}},
    {{"group": "Cohort/Archetype Name", "finding": "Specific empirical behavioral trend, preference, or objection"}}
  ],
  "critical_objections": [
    "Primary friction or risk factor 1",
    "Primary friction or risk factor 2"
  ],
  "top_insights": [
    "Actionable product or UX recommendation 1",
    "Actionable product or UX recommendation 2",
    "Actionable pricing or go-to-market recommendation 3",
    "Actionable retention or differentiation recommendation 4"
  ],
  "per_persona_breakdown": [
    {{"id": "persona_001", "name": "Name", "archetype": "Archetype", "key_takeaway": "Precise stance and conclusion for this persona"}}
  ]
}}
"""

        messages = [
            {"role": "system", "content": "You are an expert UX and product strategy researcher. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ]

        data = llm_client.chat_completion_json(messages, temperature=0.4, max_tokens=3000)
        return data

    def _generate_fallback(
        self,
        experiment: Dict[str, Any],
        personas: List[Dict[str, Any]],
        survey_data: Dict[str, Any],
        calc_sentiment_dist: Dict[str, float],
        nlp_themes: List[str]
    ) -> Dict[str, Any]:
        """Universal fallback synthesizer when LLM is unavailable."""
        p_name = experiment.get("product_name", "Product")
        p_desc = experiment.get("product_description", "")
        audience = experiment.get("target_audience", "")

        themes = nlp_themes if nlp_themes else [
            "Workflow integration and setup friction",
            "Pricing transparency and ROI justification",
            "Reliability versus existing traditional tools",
            "Ease of use and immediate value realization"
        ]

        behavioral_trends = []
        for p in personas:
            arch = p.get("archetype", "Participant")
            bp = p.get("behavioral_patterns", {})
            behavioral_trends.append({
                "group": arch,
                "finding": f"Prioritizes: {bp.get('feature_priorities', 'usability')}. Churn risk triggered by: {bp.get('churn_triggers', 'friction')}."
            })

        top_insights = [
            f"VALUE PROPOSITION: Clear ROI messaging is vital for {p_name} when targeting {audience}.",
            f"ONBOARDING FRICTION: Minimizing time-to-first-value is the primary determinant of long-term adoption across cohorts.",
            f"PRICING MODEL: Cohorts express reluctance toward aggressive upfront commitments without hands-on trial periods.",
            f"DIFFERENTIATION: Focus core messaging on resolving specific bottlenecks rather than broad feature lists."
        ]

        breakdown = []
        for p in personas:
            breakdown.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "archetype": p.get("archetype"),
                "key_takeaway": f"Stance shaped by: {p.get('behavioral_patterns', {}).get('willingness_to_pay', 'ROI')}."
            })

        return {
            "executive_summary": f"Evaluation of {p_name} reveals actionable feedback across {len(personas)} synthetic user profiles in the {audience} space.",
            "themes": themes,
            "sentiment_distribution": calc_sentiment_dist,
            "sentiment_analysis": f"User reception shows {calc_sentiment_dist.get('positive', 0)*100:.0f}% positive interest balanced with practical adoption concerns.",
            "behavioral_trends": behavioral_trends,
            "critical_objections": [
                "Switching cost and friction from established habits",
                "Uncertainty around sustained daily utility"
            ],
            "top_insights": top_insights,
            "per_persona_breakdown": breakdown
        }

    def print_report_summary(self, report: Dict[str, Any]) -> None:
        if HAS_RICH and console:
            console.print(Panel(
                f"[bold blue]SYNTHETIC USER RESEARCH INSIGHT REPORT[/bold blue]\n"
                f"[bold]Product:[/bold] {report.get('product')} | [bold]Date:[/bold] {report.get('report_date')}\n"
                f"[bold]Sample Size:[/bold] {report.get('persona_count')} synthetic personas | "
                f"[bold]Surveys:[/bold] {report.get('survey_questions_asked')} questions | "
                f"[bold]Interviews:[/bold] {report.get('interview_sessions_count')} sessions",
                border_style="blue"
            ))

            if "executive_summary" in report:
                console.print(f"\n[bold]Executive Summary:[/bold]\n{report['executive_summary']}")

            s_table = Table(title="Sentiment Distribution", show_header=True)
            s_table.add_column("Positive", style="green")
            s_table.add_column("Neutral", style="yellow")
            s_table.add_column("Negative", style="red")
            dist = report.get("sentiment_distribution", {})
            s_table.add_row(
                f"{dist.get('positive', 0)*100:.1f}%",
                f"{dist.get('neutral', 0)*100:.1f}%",
                f"{dist.get('negative', 0)*100:.1f}%"
            )
            console.print(s_table)

            console.print("\n[bold cyan]Top Emergent Themes:[/bold cyan]")
            for th in report.get("themes", []):
                console.print(f"  • {th}")

            if "behavioral_trends" in report:
                console.print("\n[bold magenta]Behavioral Cohort Trends:[/bold magenta]")
                for bt in report.get("behavioral_trends", []):
                    console.print(f"  • [bold]{bt.get('group')}:[/bold] {bt.get('finding')}")

            if "critical_objections" in report:
                console.print("\n[bold red]Critical Objections & Blockers:[/bold red]")
                for obj in report.get("critical_objections", []):
                    console.print(f"  ⚠ {obj}")

            console.print("\n[bold green]Actionable Product Insights & Recommendations:[/bold green]")
            for ins in report.get("top_insights", []):
                console.print(f"  [bold]✔[/bold] {ins}")
        else:
            print(f"\n=== SYNTHETIC USER RESEARCH INSIGHT REPORT ===")
            print(f"Product: {report.get('product')} | Date: {report.get('report_date')}")
            print(f"Sample Size: {report.get('persona_count')} personas | Surveys: {report.get('survey_questions_asked')} questions")
            if "executive_summary" in report:
                print(f"Executive Summary: {report['executive_summary']}")
            dist = report.get("sentiment_distribution", {})
            print(f"Sentiment: Positive {dist.get('positive', 0)*100:.1f}% | Neutral {dist.get('neutral', 0)*100:.1f}% | Negative {dist.get('negative', 0)*100:.1f}%")
            print("Top Themes:")
            for th in report.get("themes", []):
                print(f"  • {th}")
            print("Top Actionable Insights:")
            for ins in report.get("top_insights", []):
                print(f"  ✔ {ins}")
