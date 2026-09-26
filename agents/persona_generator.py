import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Ensure venv site-packages is discoverable if present
_venv_site = Path(__file__).resolve().parent.parent / "venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.columns import Columns
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

from config.archetype_map import UNIVERSAL_ARCHETYPES
from config.settings import is_openrouter_configured, OPENROUTER_MODEL
from utils.llm_client import llm_client, OpenRouterConfigurationError
from utils.storage import save_json, load_json

def _print_msg(msg: str):
    if HAS_RICH and console:
        console.print(msg)
    else:
        # Strip rich formatting tags for plain output
        import re
        clean_msg = re.sub(r"\[/?(?:bold|dim|italic|yellow|cyan|green|red|blue|magenta)[^\]]*\]", "", msg)
        print(clean_msg)

class PersonaGenerationAgent:
    def __init__(self, data_path: str = "data/persona_pool.json"):
        self.data_path = data_path

    def generate_personas(
        self,
        experiment: Dict[str, Any],
        count: int = 5,
        allow_fallback: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generates diverse synthetic personas tailored to the given product experiment using OpenRouter LLM.
        """
        if is_openrouter_configured():
            try:
                personas = self._generate_with_llm(experiment, count)
                save_json(self.data_path, personas)
                return personas
            except Exception as e:
                _print_msg(f"[bold yellow]OpenRouter Generation Notice:[/bold yellow] {e}")
                if not allow_fallback:
                    raise

        if not allow_fallback and not is_openrouter_configured():
            raise OpenRouterConfigurationError(
                "OpenRouter is not configured. Please set OPENROUTER_API_KEY and OPENROUTER_MODEL in .env."
            )

        _print_msg("[yellow]Notice: Using universal archetype fallback (Configure OPENROUTER_API_KEY and OPENROUTER_MODEL in .env for full LLM generation).[/yellow]")
        personas = self._generate_fallback(experiment, count)
        save_json(self.data_path, personas)
        return personas

    def _generate_with_llm(self, experiment: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Invokes OpenRouter to produce dynamic, domain-tailored synthetic personas."""
        product_name = experiment.get("product_name", "Innovative Product")
        product_desc = experiment.get("product_description", "")
        target_audience = experiment.get("target_audience", "General Users")
        research_objs = experiment.get("research_objectives", [])
        industry = experiment.get("industry_domain", "Technology")

        prompt = f"""You are an elite product research scientist.
Generate {count} diverse, realistic synthetic user personas specifically tailored for research on the following product:

Product Name: {product_name}
Product Category / Domain: {industry}
Product Description: {product_desc}
Target Audience: {target_audience}
Research Objectives: {json.dumps(research_objs)}

The personas must represent diverse archetypes across the target market. Ensure demographic, occupational, and psychological diversity.

Return a valid JSON array containing exactly {count} persona objects. Each persona object must have the following structure:
[
  {{
    "id": "persona_001",
    "name": "Full Name",
    "age": 28,
    "gender": "Female",
    "occupation": "Job Title",
    "location": "City, Country",
    "income_bracket": "middle",
    "education": "Degree or background",
    "archetype": "Descriptive Archetype Title",
    "personality_traits": ["trait1", "trait2", "trait3"],
    "behavioral_patterns": {{
      "current_tools": "Tools or habits currently used for this problem",
      "usage_frequency": "How often they deal with this problem",
      "primary_pain_points": "Main frustrations in this domain",
      "willingness_to_pay": "Stance on pricing and budget tolerance for this solution",
      "churn_triggers": "Specific dealbreakers that would make them abandon this product",
      "feature_priorities": "Top capabilities they look for"
    }},
    "psychological_profile": {{
      "mbti": "INTJ",
      "risk_tolerance": "medium",
      "motivation_type": "intrinsic",
      "decision_style": "analytical"
    }},
    "background_story": "A 2-3 sentence realistic narrative explaining their context and perspective on this product category.",
    "opinion_seeds": {{
      "price_sensitivity": 0.65,
      "tech_comfort": 0.80,
      "openness_to_change": 0.70,
      "overall_sentiment_bias": 0.50
    }}
  }}
]
"""

        messages = [
            {"role": "system", "content": "You are a specialized JSON data generator for synthetic user research simulations. Return only a valid JSON array of persona objects."},
            {"role": "user", "content": prompt}
        ]

        data = llm_client.chat_completion_json(messages, temperature=0.7)
        if not isinstance(data, list):
            if isinstance(data, dict) and "personas" in data:
                data = data["personas"]
            else:
                raise ValueError(f"Expected a list of personas from LLM, received {type(data)}")

        now_iso = datetime.now().isoformat()
        cleaned_personas = []
        for i, item in enumerate(data[:count]):
            p_id = f"persona_{i+1:03d}"
            item["id"] = p_id
            item["memory"] = {
                "conversation_history": [],
                "established_opinions": {},
                "last_updated": now_iso
            }
            cleaned_personas.append(item)

        return cleaned_personas

    def _generate_fallback(self, experiment: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Universal fallback personas when OpenRouter LLM is not configured."""
        import random
        archetypes = list(UNIVERSAL_ARCHETYPES.keys())
        p_name = experiment.get("product_name", "Product")
        p_desc = experiment.get("product_description", "Modern software solution")
        audience = experiment.get("target_audience", "General users")

        names = ["Alex Rivera", "Priya Nair", "Jordan Smith", "Elena Vance", "Marcus Chen", "Sarah Miller"]
        occupations = ["Product Specialist", "Independent Consultant", "Operations Manager", "Software Developer", "Small Business Owner", "Team Lead"]
        locations = ["Chicago, USA", "Bengaluru, India", "London, UK", "Toronto, Canada", "Berlin, Germany", "Sydney, Australia"]
        genders = ["Male", "Female", "Non-binary", "Female", "Male", "Female"]
        income_brackets = ["lower-middle", "middle", "upper-middle", "middle", "lower-middle", "upper-middle"]
        educations = [
            "Bachelor's in Business Administration",
            "Master's in Computer Science",
            "Associate Degree in Design",
            "Bachelor's in Engineering",
            "Self-taught / Bootcamp Graduate",
            "MBA"
        ]
        # Fixed age pool — no cycling repeats within typical counts
        ages = [27, 34, 41, 29, 47, 31]

        # Domain-aware patterns for fallback simulation
        p_desc_lower = p_desc.lower()
        industry_lower = experiment.get("industry_domain", "").lower()

        if any(k in p_desc_lower or k in industry_lower for k in ["chat", "social", "anonym", "messaging", "community"]):
            domain_tools = ["Discord, Reddit, and WhatsApp", "Instagram DMs and Telegram", "Slack and Twitter/X", "Signal and private forums", "Snapchat and group chats", "iMessage and Discord"]
            domain_pains = [
                "Toxic anonymous spam and lack of genuine moderation",
                "App fatigue and doomscrolling without meaningful connection",
                "Privacy concerns and unwanted creepy direct messages",
                "Superficial conversations that die out after five minutes",
                "Overcomplicated features when all I want is clean, safe chat"
            ]
            domain_wtp = "Prefers free with optional cosmetic perks under $5/mo"
        elif any(k in p_desc_lower or k in industry_lower for k in ["dev", "code", "software", "api", "git"]):
            domain_tools = ["GitHub PRs, Slack, and Jira", "GitLab CI/CD and VS Code", "Bitbucket and email threads", "Linear and manual code review", "Docker and terminal tools", "Jenkins and Slack alerts"]
            domain_pains = [
                "Review bottlenecks and waiting days for PR approvals",
                "Noisy false-positive automated alerts",
                "Lack of context on complex legacy codebases",
                "Context switching between Jira, GitHub, and Slack",
                "Security compliance and hallucinated recommendations"
            ]
            domain_wtp = "Willing to spend $20-$40/seat/mo if it saves 3+ engineering hours weekly"
        elif any(k in p_desc_lower or k in industry_lower for k in ["health", "fitness", "wellness", "hydrate", "nutrition"]):
            domain_tools = ["Apple Health and standard water bottle", "MyFitnessPal and Strava", "Whoop and phone reminders", "Fitbit and paper habit log", "Garmin Connect and basic timers", "Peloton app and smart scale"]
            domain_pains = [
                "Nagging notifications that make me feel guilty instead of motivated",
                "Inaccurate sensor tracking and bluetooth disconnects",
                "Too much manual data entry every day",
                "Battery running out every single day",
                "Cluttered apps with bloated premium paywalls"
            ]
            domain_wtp = "Willing to pay $50-$80 one-time hardware or $8-$12/mo for actionable health insights"
        else:
            domain_tools = [f"Traditional manual tools and spreadsheets for {audience}"] * 6
            domain_pains = [f"Friction and time wasted with existing solutions in {audience}"] * 6
            domain_wtp = "Strictly value-driven; requires clear proof of time/cost savings"

        personas = []
        now_iso = datetime.now().isoformat()

        # Use a seeded RNG for reproducibility per experiment but variation across personas
        rng = random.Random(hash(p_name + str(count)))

        for i in range(count):
            arch_key = archetypes[i % len(archetypes)]
            arch_data = UNIVERSAL_ARCHETYPES[arch_key]
            name = names[i % len(names)]
            occ = occupations[i % len(occupations)]
            loc = locations[i % len(locations)]
            gender = genders[i % len(genders)]
            income = income_brackets[i % len(income_brackets)]
            edu = educations[i % len(educations)]
            age = ages[i % len(ages)]
            tool = domain_tools[i % len(domain_tools)]
            pain = domain_pains[i % len(domain_pains)]

            # Per-persona opinion seed jitter (±0.10) to ensure differentiation
            base_seeds = dict(arch_data["opinion_seeds"])
            opinion_seeds = {
                k: round(min(1.0, max(0.0, v + rng.uniform(-0.10, 0.10))), 2)
                for k, v in base_seeds.items()
            }

            persona = {
                "id": f"persona_{i+1:03d}",
                "name": name,
                "age": age,
                "gender": gender,
                "occupation": occ,
                "location": loc,
                "income_bracket": income,
                "education": edu,
                "archetype": arch_key,
                "personality_traits": list(arch_data["personality_traits"]),
                "behavioral_patterns": {
                    "current_tools": tool,
                    "usage_frequency": "Daily or several times a week",
                    "primary_pain_points": pain,
                    "willingness_to_pay": domain_wtp,
                    "churn_triggers": arch_data["behavioral_patterns"]["churn_trigger"],
                    "feature_priorities": "Simplicity, reliability, and immediate practical value"
                },
                "psychological_profile": dict(arch_data["psychological_profile"]),
                "background_story": (
                    f"{name} is a {age}-year-old {occ} living in {loc}. "
                    f"As a {arch_key}, their daily routine heavily involves {tool}, but they are frustrated by {pain.lower()}."
                ),
                "opinion_seeds": opinion_seeds,
                "memory": {
                    "conversation_history": [],
                    "established_opinions": {},
                    "last_updated": now_iso
                }
            }
            personas.append(persona)

        return personas


    def print_persona_cards(self, personas: List[Dict[str, Any]]) -> None:
        if HAS_RICH and console:
            cards = []
            for p in personas:
                bp = p.get("behavioral_patterns", {})
                current_tools = bp.get("current_tools", "N/A")
                pain_points = bp.get("primary_pain_points", "N/A")
                wtp = bp.get("willingness_to_pay", "N/A")
                churn = bp.get("churn_triggers", "N/A")

                content = (
                    f"[bold cyan]{p['name']}[/bold cyan] ({p.get('age')}y, {p.get('gender')})\n"
                    f"[yellow]{p.get('archetype')}[/yellow]\n"
                    f"[dim]{p.get('occupation')} | {p.get('location')}[/dim]\n\n"
                    f"[bold]Traits:[/bold] {', '.join(p.get('personality_traits', []))}\n"
                    f"[bold]Current Tools:[/bold] {current_tools}\n"
                    f"[bold]Pain Point:[/bold] {pain_points}\n"
                    f"[bold]Pricing View:[/bold] {wtp}\n"
                    f"[bold]Churn Risk:[/bold] {churn}"
                )
                cards.append(Panel(content, title=f"ID: {p['id']}", expand=False, border_style="blue"))
            console.print(Columns(cards, equal=True))
        else:
            for p in personas:
                bp = p.get("behavioral_patterns", {})
                print(f"\n--- Persona [{p['id']}]: {p['name']} ({p.get('archetype')}) ---")
                print(f"Demographics: {p.get('age')}y, {p.get('gender')}, {p.get('occupation')} in {p.get('location')}")
                print(f"Traits: {', '.join(p.get('personality_traits', []))}")
                print(f"Pain Points: {bp.get('primary_pain_points', 'N/A')}")
                print(f"Current Tools: {bp.get('current_tools', 'N/A')}")
                print(f"Willingness to Pay: {bp.get('willingness_to_pay', 'N/A')}")
                print(f"Churn Risk: {bp.get('churn_triggers', 'N/A')}")
