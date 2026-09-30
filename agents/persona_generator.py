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
from utils.normalizer import normalize_experiment, generate_aligned_personas_fallback
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
        Automatically normalizes input context, corrects any typos, and aligns personas with the target market.
        """
        normalized_exp = normalize_experiment(experiment)

        if is_openrouter_configured():
            try:
                personas = self._generate_with_llm(normalized_exp, count)
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

        _print_msg("[yellow]Notice: Using aligned archetype fallback generator (100% domain-tailored, typo-free).[/yellow]")
        personas = self._generate_fallback(normalized_exp, count)
        save_json(self.data_path, personas)
        return personas

    def _generate_with_llm(self, experiment: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Invokes OpenRouter to produce dynamic, domain-tailored synthetic personas with strict target market alignment."""
        product_name = experiment.get("product_name", "Innovative Product")
        product_desc = experiment.get("product_description", "")
        target_audience = experiment.get("target_audience", "General Users")
        research_objs = experiment.get("research_objectives", [])
        industry = experiment.get("industry_domain", "Technology")

        prompt = f"""You are an elite UX research scientist and synthetic persona generator.
Generate {count} diverse, authentic, realistic synthetic user personas specifically tailored for research on the following product:

Product Name: {product_name}
Product Domain / Category: {industry}
Product Description & Value Proposition: {product_desc}
Target Audience & User Demographics: {target_audience}
Research Objectives: {json.dumps(research_objs)}

CRITICAL GENERATION RULES:
1. STRICT TARGET CUSTOMER ALIGNMENT: Every single persona MUST be an authentic, direct target customer, operator, buyer, or user for this specific product.
   - For example, if the product is for restaurants, cloud kitchens, POS, and food billing, personas MUST have real hospitality job titles (such as Multi-Unit Restaurant Owner, Cloud Kitchen Operations Manager, Restaurant General Manager, Food & Beverage Accounts Lead, Cafe Franchisee). NEVER generate unrelated generic professions like software developers or general consultants unless they are the direct target market.
2. ZERO TYPO REPRODUCTION: The user's original concept notes may have contained informal typos or misspellings. Infer the true commercial intent and business use case. Under no circumstances should you copy, repeat, or carry over any typos or raw text mistakes into persona cards, tools, or pain points.
3. AUTHENTIC TOOLS & PAIN POINTS: 'current_tools' and 'primary_pain_points' MUST describe real tools and operational bottlenecks specific to this industry.
4. PSYCHOLOGICAL & OPINION DIVERSITY: Ensure diverse age ranges, genders, geographic locations, and distinct archetypes (pragmatists, optimizers, busy professionals, skeptics, etc.).

Return a valid JSON array containing exactly {count} persona objects. Each persona object must have the following structure:
[
  {{
    "id": "persona_001",
    "name": "Full Name",
    "age": 36,
    "gender": "Female",
    "occupation": "Industry-Specific Role",
    "location": "City, Country",
    "income_bracket": "middle",
    "education": "Degree or background",
    "archetype": "Descriptive Archetype Title",
    "personality_traits": ["trait1", "trait2", "trait3"],
    "behavioral_patterns": {{
      "current_tools": "Real-world tools currently used in this domain",
      "usage_frequency": "Daily during operations",
      "primary_pain_points": "Specific operational frustration in this workflow",
      "willingness_to_pay": "Pricing attitude and budget stance",
      "churn_triggers": "Specific dealbreakers for abandoning this product",
      "feature_priorities": "Top capabilities sought"
    }},
    "psychological_profile": {{
      "mbti": "ISTJ",
      "risk_tolerance": "medium",
      "motivation_type": "extrinsic-economic",
      "decision_style": "analytical"
    }},
    "background_story": "A 2-3 sentence realistic narrative explaining their daily workflow, industry role, and perspective on this product.",
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
        """Domain-aligned fallback personas guaranteeing zero typos and authentic industry roles."""
        return generate_aligned_personas_fallback(experiment, count)



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
