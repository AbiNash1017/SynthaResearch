from datetime import datetime
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table

from agents.persona_memory import PersonaMemoryModule
from templates.response_templates import extract_stance
from utils.nlp_utils import extract_key_phrase
from utils.storage import load_json, save_json

console = Console()

class SurveyAgent:
    def __init__(self, persona_path: str = "data/persona_pool.json", output_path: str = "data/survey_responses.json"):
        self.persona_path = persona_path
        self.output_path = output_path

    def run_survey(self, questions: List[str]) -> Dict[str, Any]:
        personas = load_json(self.persona_path, [])
        if not personas:
            raise ValueError("No personas found in persona_pool.json! Please generate personas first.")

        responses = []
        for p in personas:
            answers = []
            for q in questions:
                ans = PersonaMemoryModule.generate_response(p, q, mode="survey")
                stance = extract_stance(ans)
                key_phrase = extract_key_phrase(ans)
                answers.append({
                    "question": q,
                    "answer": ans,
                    "sentiment": stance,
                    "key_phrase": key_phrase
                })
            responses.append({
                "persona_id": p["id"],
                "persona_name": p["name"],
                "archetype": p["archetype"],
                "answers": answers
            })
            PersonaMemoryModule.update_persona_pool(p, self.persona_path)

        survey_payload = {
            "survey_id": f"survey_{int(datetime.now().timestamp())}",
            "questions": questions,
            "responses": responses,
            "created_at": datetime.now().isoformat()
        }

        save_json(self.output_path, survey_payload)
        return survey_payload

    def print_survey_table(self, survey_data: Dict[str, Any]) -> None:
        table = Table(title="Survey Results — Cross-Persona Side-by-Side Comparison", show_header=True, header_style="bold magenta")
        table.add_column("Question", style="dim", width=25)

        for resp in survey_data["responses"]:
            table.add_column(f"{resp['persona_name']}\n({resp['archetype']})", width=24)

        questions = survey_data["questions"]
        for q_idx, q in enumerate(questions):
            row = [q]
            for resp in survey_data["responses"]:
                ans_item = resp["answers"][q_idx]
                sentiment = ans_item["sentiment"]
                color = "green" if sentiment == "positive" else ("red" if sentiment == "negative" else "yellow")
                row.append(f"[{color}][{sentiment.upper()}][/{color}]\n{ans_item['answer']}")
            table.add_row(*row)
            table.add_section()

        console.print(table)
