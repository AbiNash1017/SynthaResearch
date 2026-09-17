from datetime import datetime
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns

from config.archetype_map import ARCHETYPE_PROFILES
from templates.name_bank import ARCHETYPE_DETAILS
from utils.storage import save_json, load_json

console = Console()

class PersonaGenerationAgent:
    def __init__(self, data_path: str = "data/persona_pool.json"):
        self.data_path = data_path

    def generate_personas(self, experiment: Dict[str, Any], count: int = 5) -> List[Dict[str, Any]]:
        archetypes = list(ARCHETYPE_PROFILES.keys())
        personas = []

        for i in range(count):
            arch = archetypes[i % len(archetypes)]
            profile = ARCHETYPE_PROFILES[arch]
            details = ARCHETYPE_DETAILS[arch]

            persona_id = f"persona_{i+1:03d}"
            name = details["names"][i % len(details["names"])]
            gender = details["genders"][i % len(details["genders"])]
            age = details["ages"][i % len(details["ages"])]
            occ = details["occupations"][i % len(details["occupations"])]
            loc = details["locations"][i % len(details["locations"])]
            income = details["incomes"][i % len(details["incomes"])]
            edu = details["educations"][i % len(details["educations"])]
            story = details["story"]

            persona = {
                "id": persona_id,
                "name": name,
                "archetype": arch,
                "age": age,
                "gender": gender,
                "occupation": occ,
                "location": loc,
                "income_bracket": income,
                "education": edu,
                "personality_traits": list(profile["personality_traits"]),
                "learning_behavioral_patterns": dict(profile["learning_behavioral_patterns"]),
                "psychological_profile": dict(profile["psychological_profile"]),
                "background_story": story,
                "opinion_seeds": dict(profile["opinion_seeds"]),
                "memory": {
                    "conversation_history": [],
                    "established_opinions": {},
                    "last_updated": datetime.now().isoformat()
                }
            }
            personas.append(persona)

        save_json(self.data_path, personas)
        return personas

    def print_persona_cards(self, personas: List[Dict[str, Any]]) -> None:
        cards = []
        for p in personas:
            content = (
                f"[bold cyan]{p['name']}[/bold cyan] ({p['age']}y, {p['gender']})\n"
                f"[yellow]{p['archetype']}[/yellow]\n"
                f"[dim]{p['occupation']} | {p['location']}[/dim]\n\n"
                f"[bold]Traits:[/bold] {', '.join(p['personality_traits'])}\n"
                f"[bold]Learning Goal:[/bold] {p['learning_behavioral_patterns']['motivation_trigger']}\n"
                f"[bold]Dropout Trigger:[/bold] {p['learning_behavioral_patterns']['dropout_trigger']}\n"
                f"[bold]Pref. Lesson:[/bold] {p['learning_behavioral_patterns']['preferred_lesson_length']}\n"
                f"[bold]Gamification:[/bold] {p['learning_behavioral_patterns']['gamification_response']}"
            )
            cards.append(Panel(content, title=f"ID: {p['id']}", expand=False, border_style="blue"))
        console.print(Columns(cards, equal=True))
