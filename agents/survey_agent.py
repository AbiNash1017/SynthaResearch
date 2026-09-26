import json
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
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

Return only a valid JSON array of {count} strings (the survey questions).
Focus on:
1. Core problem/pain point resonance.
2. Willingness to adopt/switch and key hesitations.
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

        # Dynamic fallback questions based on experiment details
        return [
            f"What is your single biggest frustration with current tools or methods you use in this space?",
            f"If {p_name} could solve that problem reliably, what would make you hesitate to switch?",
            f"What pricing structure or monthly amount would you consider fair for this solution?"
        ]

    def run_survey(self, questions: List[str], experiment: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        personas = load_json(self.persona_path, [])
        if not personas:
            raise ValueError("No personas found in persona_pool.json! Please generate personas first.")

        if experiment is None:
            experiment = load_json(self.experiment_path, {})

        responses = []
        for p in personas:
            answers = []
            for q in questions:
                ans = PersonaMemoryModule.generate_response(p, q, experiment=experiment, mode="survey")
                stance = PersonaMemoryModule.extract_stance(ans)
                key_phrase = extract_key_phrase(ans)
                answers.append({
                    "question": q,
                    "answer": ans,
                    "sentiment": stance,
                    "key_phrase": key_phrase
                })
            responses.append({
                "persona_id": p.get("id"),
                "persona_name": p.get("name"),
                "archetype": p.get("archetype"),
                "answers": answers
            })
            PersonaMemoryModule.update_persona_pool(p, self.persona_path)

        survey_payload = {
            "survey_id": f"survey_{int(datetime.now().timestamp())}",
            "product_name": experiment.get("product_name", "Product"),
            "questions": questions,
            "responses": responses,
            "created_at": datetime.now().isoformat()
        }

        save_json(self.output_path, survey_payload)
        return survey_payload

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
