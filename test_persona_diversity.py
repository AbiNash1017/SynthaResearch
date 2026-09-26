"""Quick diagnostic: persona generation + LLM + diversity check."""
import json
from agents.persona_generator import PersonaGenerationAgent
from agents.persona_memory import PersonaMemoryModule
from config.settings import get_config_status

experiment = {
    "product_name": "FocusFlow",
    "product_description": "An AI-powered productivity app for remote teams to track goals, reduce meeting overhead, and surface blockers.",
    "target_audience": "Remote knowledge workers and distributed team leads",
    "research_objectives": ["Validate pain points", "Pricing sensitivity", "Feature prioritization"],
    "industry_domain": "productivity software"
}

print("=== Config Status ===")
print(json.dumps(get_config_status(), indent=2))

print("\n=== Generating Personas (LLM or Fallback) ===")
agent = PersonaGenerationAgent("data/test_persona_pool.json")
personas = agent.generate_personas(experiment, count=4, allow_fallback=True)
print(f"Generated {len(personas)} personas\n")

names = set()
archetypes = set()
mbti_set = set()
locations = set()

for p in personas:
    pid = p.get("id")
    name = p.get("name", "?")
    age = p.get("age", "?")
    gender = p.get("gender", "?")
    arch = p.get("archetype", "?")
    occ = p.get("occupation", "?")
    loc = p.get("location", "?")
    traits = p.get("personality_traits", [])
    psych = p.get("psychological_profile", {})
    mbti = psych.get("mbti", "?")
    names.add(name)
    archetypes.add(arch)
    mbti_set.add(mbti)
    locations.add(loc)
    print(f"  [{pid}] {name} | {age}y | {gender}")
    print(f"    Archetype: {arch}")
    print(f"    Role: {occ} @ {loc}")
    print(f"    Traits: {traits}")
    print(f"    MBTI: {mbti} | Risk: {psych.get('risk_tolerance','?')} | Decision: {psych.get('decision_style','?')}")
    seeds = p.get("opinion_seeds", {})
    print(f"    Opinion seeds: price_sensitivity={seeds.get('price_sensitivity','?')} tech_comfort={seeds.get('tech_comfort','?')}")
    print()

print("=== Diversity Checks ===")
print(f"  Unique names:     {len(names)}/{len(personas)} (expect all unique)")
print(f"  Unique archetypes:{len(archetypes)}/{len(personas)} (expect variety)")
print(f"  Unique MBTIs:     {len(mbti_set)}/{len(personas)} (expect variety)")
print(f"  Unique locations: {len(locations)}/{len(personas)} (expect variety)")

if len(names) < len(personas):
    print("  [WARN] Duplicate persona names detected!")
if len(archetypes) == 1:
    print("  [WARN] All personas have the same archetype — no diversity!")

print("\n=== Persona Response Test ===")
for p in personas[:2]:
    q = "What's your biggest concern about switching to a new productivity tool?"
    resp = PersonaMemoryModule.generate_response(p, q, experiment=experiment, mode="survey")
    print(f"  {p.get('name')} ({p.get('archetype')}): {resp[:200]}")
    print()

print("All checks passed.")
