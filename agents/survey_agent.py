import json
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Ensure venv site-packages is discoverable if present
_venv_site = Path(__file__).resolve().parent.parent / "venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

from agents.persona_memory import PersonaMemoryModule
from config.settings import is_openrouter_configured
from utils.llm_client import llm_client
from utils.nlp_utils import extract_key_phrase
from utils.storage import load_json, save_json

def _print_msg(msg: str):
    if HAS_RICH and console:
        console.print(msg)
    else:
        import re
        clean_msg = re.sub(r"\[/?(?:bold|dim|italic|yellow|cyan|green|red|blue|magenta)[^\]]*\]", "", msg)
        print(clean_msg)

class SurveyAgent:
    def __init__(
        self,
        persona_path: str = "data/persona_pool.json",
        output_path: str = "data/survey_responses.json",
        experiment_path: str = "data/experiment.json"
    ):
        self.persona_path = persona_path
        self.output_path = output_path
        self.experiment_path = experiment_path

    def suggest_questions(self, experiment: Optional[Dict[str, Any]] = None, count: int = 3) -> List[str]:
        """
        Uses OpenRouter LLM to dynamically generate smart, tailored research questions
        based on the active product experiment and objectives.
        """
        if experiment is None:
            experiment = load_json(self.experiment_path, {})
        from utils.normalizer import normalize_experiment
        experiment = normalize_experiment(experiment)

        p_name = experiment.get("product_name", "the product")
        p_desc = experiment.get("product_description", "")
        audience = experiment.get("target_audience", "")
        objs = experiment.get("research_objectives", [])

        if is_openrouter_configured():
            try:
                prompt = f"""You are a senior UX researcher.
Generate {count} targeted, insightful user research survey questions for:
Product Name: {p_name}
Description: {p_desc}
Target Audience: {audience}
Research Objectives: {json.dumps(objs)}

CRITICAL: Understand the intended business domain and user use case even if raw notes had typos. NEVER repeat or propagate typos into the questions.

Return only a valid JSON array of {count} strings (the survey questions).
Focus on:
1. Core problem/pain point resonance in this specific industry.
2. Willingness to adopt/switch and key operational hesitations.
3. Pricing perception or essential feature requirements.
"""
                messages = [
                    {"role": "system", "content": "You are a UX research survey designer. Output only a JSON array of strings."},
                    {"role": "user", "content": prompt}
                ]
                questions = llm_client.chat_completion_json(messages, temperature=0.5)
                if isinstance(questions, list) and len(questions) > 0:
                    return [str(q).strip() for q in questions[:count]]
            except Exception as e:
                _print_msg(f"[dim yellow]Notice: Could not auto-generate questions via LLM ({e}), using generalized questions.[/dim yellow]")

        # Dynamic, domain-tailored fallback questions based on product and industry profile
        combined_text = f"{p_name} {experiment.get('industry_domain', '')} {p_desc} {audience}".lower()

        if any(k in combined_text for k in ["devtools", "developer", "code", "github", "api", "software engineer", "devops", "pull request"]):
            pool = [
                f"How significantly do pull request review bottlenecks and CI/CD turnaround times impact your team's shipping velocity?",
                f"Would your team adopt {p_name} if it integrated directly into GitHub/GitLab without requiring workflow reconfiguration?",
                f"What pricing structure (e.g. per active developer vs team flat fee) would you consider fair for {p_name}?",
                f"What are your biggest technical concerns or security dealbreakers when adopting automated developer tooling like {p_name}?",
                f"How does your current tool stack handle these workflows, and what would make you hesitate to switch?"
            ]
        elif any(k in combined_text for k in ["fintech", "finance", "billing", "invoic", "account", "invest", "banking", "wealth"]):
            pool = [
                f"What is your biggest operational headache when managing financial tracking, automated budgeting, or recurring subscriptions today?",
                f"Would you connect your primary accounts or payment tools to {p_name} if it automated end-to-end reconciliation reliably?",
                f"What monthly subscription or fee structure would make {p_name} an easy ROI justification for you?",
                f"What data privacy, encryption, or regulatory guarantees are absolute prerequisites before you would adopt {p_name}?",
                f"What friction in your current financial routines would make you hesitate to switch to {p_name}?"
            ]
        elif any(k in combined_text for k in ["restaurant", "kitchen", "pos", "hospitality", "food", "dining", "cafe"]):
            pool = [
                f"What causes the most chaos during peak service hours between front-of-house ordering, kitchen tickets, and online delivery portals?",
                f"Would you switch your primary register or billing workflow to {p_name} if it eliminated end-of-day reconciliation discrepancies?",
                f"What monthly fee per outlet would you consider fair and sustainable for a unified system like {p_name}?",
                f"How critical are offline stability and hardware compatibility when evaluating a new platform for your venue?",
                f"What would prevent your staff from quickly adopting {p_name} during a busy service shift?"
            ]
        elif any(k in combined_text for k in ["ecommerce", "e-commerce", "retail", "shop", "apparel", "wardrobe", "rental", "fashion"]):
            pool = [
                f"What is your biggest frustration with current purchasing, rental, or return logistics in this space?",
                f"If {p_name} delivered a seamless experience with zero hidden fees, how likely would you be to adopt it regularly?",
                f"What monthly subscription or pricing model would you consider fair and compelling for {p_name}?",
                f"What hygiene, reliability, or customer support concerns would make you hesitate before committing to {p_name}?",
                f"How does your current shopping or rental routine compare, and what would make {p_name} stand out?"
            ]
        elif any(k in combined_text for k in ["health", "wellness", "fitness", "hydration", "medical", "clinic", "biometric"]):
            pool = [
                f"What is your single biggest frustration with existing wellness tracking, habit apps, or smart gear you currently use?",
                f"Would you consistently use {p_name} in your daily routine if it provided effortless, actionable health insights?",
                f"What upfront hardware price or monthly subscription would you consider fair and justified for {p_name}?",
                f"How sensitive are you to notification frequency, daily charging, and data privacy when evaluating products like {p_name}?",
                f"What typically causes you to abandon health or wellness products after the first month?"
            ]
        elif any(k in combined_text for k in ["education", "edtech", "learning", "course", "student", "upskilling", "career"]):
            pool = [
                f"What causes the greatest drop-off in motivation or course completion in your current learning setup?",
                f"Would you adopt {p_name} if it measurably accelerated your learning progress and fit into short daily breaks?",
                f"What pricing structure (e.g. monthly access vs per-certificate fee) would you consider fair for {p_name}?",
                f"What features (like cohort accountability or verifiable credentials) are essential for you to stay engaged?",
                f"What would make you hesitate to replace your existing educational resources with {p_name}?"
            ]
        else:
            pool = [
                f"What is your single biggest frustration with current tools or workflows you use when dealing with {audience}?",
                f"If {p_name} could reliably solve your primary workflow bottleneck, what would make you hesitate to switch?",
                f"What pricing model or monthly cost would you consider a fair investment for {p_name}?",
                f"How does your current setup handle these challenges, and what would make {p_name} indispensable?",
                f"What onboarding or operational dealbreakers would cause you to abandon {p_name}?"
            ]

        return pool[:count]

    def run_survey(
        self,
        questions: List[str],
        experiment: Optional[Dict[str, Any]] = None,
        simultaneous: bool = True
    ) -> Dict[str, Any]:
        """
        Executes a survey across all synthetic personas.
        When simultaneous=True, all personas generate responses concurrently via ThreadPoolExecutor.
        """
        personas = load_json(self.persona_path, [])
        if not personas:
            raise ValueError("No personas found in persona_pool.json! Please generate personas first.")

        if experiment is None:
            experiment = load_json(self.experiment_path, {})

        def _process_single_persona(persona_obj: Dict[str, Any]) -> tuple:
            p_answers = []
            for q in questions:
                ans = PersonaMemoryModule.generate_response(persona_obj, q, experiment=experiment, mode="survey")
                stance = PersonaMemoryModule.extract_stance(ans)
                key_phrase = extract_key_phrase(ans)
                p_answers.append({
                    "question": q,
                    "answer": ans,
                    "sentiment": stance,
                    "key_phrase": key_phrase
                })
            return persona_obj, {
                "persona_id": persona_obj.get("id"),
                "persona_name": persona_obj.get("name"),
                "archetype": persona_obj.get("archetype"),
                "answers": p_answers
            }

        responses = []
        if simultaneous and len(personas) > 1:
            max_workers = min(len(personas), 8)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_persona = {executor.submit(_process_single_persona, p): p for p in personas}
                results_map = {}
                for future in as_completed(future_to_persona):
                    orig_p = future_to_persona[future]
                    updated_p, resp_dict = future.result()
                    results_map[orig_p["id"]] = (updated_p, resp_dict)

            # Preserve original persona order
            for p in personas:
                updated_p, resp_dict = results_map[p["id"]]
                responses.append(resp_dict)
                PersonaMemoryModule.update_persona_pool(updated_p, self.persona_path)
        else:
            for p in personas:
                updated_p, resp_dict = _process_single_persona(p)
                responses.append(resp_dict)
                PersonaMemoryModule.update_persona_pool(updated_p, self.persona_path)

        survey_payload = {
            "survey_id": f"survey_{int(datetime.now().timestamp())}",
            "product_name": experiment.get("product_name", "Product"),
            "questions": questions,
            "responses": responses,
            "created_at": datetime.now().isoformat()
        }

        # Embed side-by-side matrix view
        survey_payload["matrix"] = self.format_survey_matrix(survey_payload)

        save_json(self.output_path, survey_payload)
        return survey_payload

    def format_survey_matrix(self, survey_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Transforms survey responses into a cross-persona side-by-side comparison matrix.
        Allows API and frontend consumers to view all persona responses side-by-side per question.
        """
        if survey_data is None:
            survey_data = load_json(self.output_path, {})

        questions = survey_data.get("questions", [])
        responses = survey_data.get("responses", [])

        matrix_rows = []
        for q_idx, q in enumerate(questions):
            persona_answers = {}
            for resp in responses:
                if q_idx < len(resp.get("answers", [])):
                    ans_item = resp["answers"][q_idx]
                    persona_answers[resp["persona_id"]] = {
                        "persona_name": resp.get("persona_name"),
                        "archetype": resp.get("archetype"),
                        "answer": ans_item.get("answer"),
                        "sentiment": ans_item.get("sentiment"),
                        "key_phrase": ans_item.get("key_phrase")
                    }
            matrix_rows.append({
                "question_index": q_idx + 1,
                "question": q,
                "persona_answers": persona_answers
            })

        return {
            "survey_id": survey_data.get("survey_id"),
            "product_name": survey_data.get("product_name"),
            "persona_count": len(responses),
            "questions": matrix_rows,
            "created_at": survey_data.get("created_at")
        }

    def print_survey_table(self, survey_data: Dict[str, Any]) -> None:
        if HAS_RICH and console:
            table = Table(
                title=f"Survey Results: {survey_data.get('product_name', 'Product')} — Cross-Persona Comparison",
                show_header=True,
                header_style="bold magenta"
            )
            table.add_column("Question", style="dim", width=25)

            for resp in survey_data.get("responses", []):
                table.add_column(f"{resp['persona_name']}\n({resp['archetype']})", width=24)

            questions = survey_data.get("questions", [])
            for q_idx, q in enumerate(questions):
                row = [q]
                for resp in survey_data.get("responses", []):
                    ans_item = resp["answers"][q_idx]
                    sentiment = ans_item["sentiment"]
                    color = "green" if sentiment == "positive" else ("red" if sentiment == "negative" else "yellow")
                    row.append(f"[{color}][{sentiment.upper()}][/{color}]\n{ans_item['answer']}")
                table.add_row(*row)
                table.add_section()

            console.print(table)
        else:
            print(f"\n=== Survey Results: {survey_data.get('product_name', 'Product')} ===")
            questions = survey_data.get("questions", [])
            for q_idx, q in enumerate(questions):
                print(f"\nQ{q_idx+1}: {q}")
                for resp in survey_data.get("responses", []):
                    ans_item = resp["answers"][q_idx]
                    print(f"  [{ans_item['sentiment'].upper()}] {resp['persona_name']} ({resp['archetype']}): {ans_item['answer']}")
