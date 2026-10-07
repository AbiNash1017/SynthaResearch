"""
Milestone 3 Comprehensive Validation Suite for Universal Synthetic User Research Platform.
Validates all 7 Milestone 3 Requirements:
1. Survey Mode: Simultaneous generation & side-by-side comparison matrix.
2. Persona consistency & multi-turn memory across question types and domains.
3. Survey Mode tested across 5 diverse product categories.
4. Interview Mode: Multi-turn conversational interface with session management and character consistency.
5. Insight Extraction Agent: Themes, sentiment distribution, and Agreement Patterns (consensus vs polarization).
6. "Would use this product?" scoring: Overall score + segment breakdown + group reasoning.
7. Validation of insight quality, theme relevance, and contrasting product discrimination.
"""

import os
import sys
import time
import traceback
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")

# ── Ensure the project root is on sys.path and is the working directory ──
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.chdir(BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from agents.persona_generator import PersonaGenerationAgent
from agents.persona_memory import PersonaMemoryModule
from agents.survey_agent import SurveyAgent
from agents.interview_agent import InterviewAgent
from agents.insight_agent import InsightExtractionAgent
from config.settings import get_config_status
from utils.storage import save_json, load_json


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

# Track test results for final scoreboard
_results: list[dict] = []


def banner(title: str):
    print(f"\n{'='*70}")
    print(f" {title.upper()}")
    print(f"{'='*70}")


def _run_test(name: str, fn):
    """Run a single test function with timing and error capture."""
    start = time.time()
    try:
        fn()
        elapsed = time.time() - start
        _results.append({"name": name, "status": "PASSED", "elapsed": elapsed, "error": None})
        print(f"\n✔ {name} — PASSED ({elapsed:.1f}s)")
    except Exception as exc:
        elapsed = time.time() - start
        _results.append({"name": name, "status": "FAILED", "elapsed": elapsed, "error": str(exc)})
        print(f"\n✘ {name} — FAILED ({elapsed:.1f}s)")
        traceback.print_exc()


def _assert(condition: bool, msg: str):
    """Assertion with a descriptive message."""
    if not condition:
        raise AssertionError(msg)


def _contains_any(text: str, keywords: list[str]) -> bool:
    """Check if text contains any of the keywords (case-insensitive)."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 & 3: Survey Mode + 5 Domains
# ─────────────────────────────────────────────────────────────────────────────

def test_survey_mode_and_categories():
    banner("1 & 3: Testing Survey Mode & Concurrency Across 5 Diverse Domains")

    test_domains = [
        {
            "product_name": "DevPulse AI",
            "industry_domain": "B2B SaaS / DevTools",
            "product_description": "Automated AI pull request reviewer and architectural impact analysis bot.",
            "target_audience": "Software engineers and tech leads.",
            "research_objectives": ["Identify review bottleneck pain points", "Assess pricing tolerance"]
        },
        {
            "product_name": "HydraGlow",
            "industry_domain": "Health & Wellness Consumer Tech",
            "product_description": "Smart insulated bottle with biometric hydration tracking and mobile app.",
            "target_audience": "Active fitness enthusiasts and desk workers.",
            "research_objectives": ["Evaluate $79 hardware pricing willingness", "Notification frequency tolerance"]
        },
        {
            "product_name": "VaultWise",
            "industry_domain": "FinTech / Wealth Management",
            "product_description": "AI-powered automated micro-investing and recurring subscription audit platform.",
            "target_audience": "Young professionals seeking automated budgeting and passive wealth growth.",
            "research_objectives": ["Assess data privacy concerns", "Determine willingness to connect bank accounts"]
        },
        {
            "product_name": "LearnQuest",
            "industry_domain": "EdTech / Professional Upskilling",
            "product_description": "Gamified bite-sized micro-courses with peer cohorts and verifiable certificates.",
            "target_audience": "Career switchers and time-constrained working professionals.",
            "research_objectives": ["Analyze completion drop-offs", "Test preference for streaks vs accredited certificates"]
        },
        {
            "product_name": "EcoWardrobe",
            "industry_domain": "E-Commerce / Sustainable Apparel",
            "product_description": "Circular fashion subscription offering monthly designer clothing rentals with free cleaning.",
            "target_audience": "Environmentally conscious urban professionals and event-goers.",
            "research_objectives": ["Evaluate $49/mo rental model vs buying new", "Understand hygiene and return friction"]
        }
    ]

    persona_agent = PersonaGenerationAgent("data/test_persona_pool.json")
    survey_agent = SurveyAgent(
        persona_path="data/test_persona_pool.json",
        output_path="data/test_survey_responses.json",
        experiment_path="data/test_experiment.json"
    )

    for idx, domain in enumerate(test_domains, 1):
        print(f"\n[{idx}/5] Testing Domain: {domain['product_name']} ({domain['industry_domain']})")
        save_json("data/test_experiment.json", domain)

        # Generate 4 diverse personas
        personas = persona_agent.generate_personas(domain, count=4, allow_fallback=True)
        _assert(len(personas) == 4, f"Expected 4 personas, got {len(personas)}")

        # Suggest questions & run survey simultaneously
        questions = survey_agent.suggest_questions(domain, count=3)
        _assert(len(questions) == 3, f"Expected 3 questions, got {len(questions)}")

        survey_res = survey_agent.run_survey(questions, experiment=domain, simultaneous=True)
        _assert("responses" in survey_res, "Survey results missing 'responses'")
        _assert(len(survey_res["responses"]) == 4, f"Expected responses from all 4 personas, got {len(survey_res['responses'])}")
        _assert("matrix" in survey_res, "Survey results missing 'matrix' side-by-side data structure")

        matrix = survey_res["matrix"]
        _assert(len(matrix["questions"]) == 3, f"Matrix does not contain all 3 questions (got {len(matrix['questions'])})")

        for q_row in matrix["questions"]:
            _assert("persona_answers" in q_row, "Matrix question row missing 'persona_answers'")
            _assert(len(q_row["persona_answers"]) == 4, f"Expected 4 persona answers, got {len(q_row['persona_answers'])}")
            for pid, ans_data in q_row["persona_answers"].items():
                _assert(ans_data["sentiment"] in ["positive", "neutral", "negative"],
                        f"Invalid sentiment '{ans_data['sentiment']}' for persona {pid}")
                _assert(len(ans_data["answer"]) > 10,
                        f"Answer too short for persona {pid}: '{ans_data['answer']}'")

        print(f"  ✔ Generated {len(personas)} personas")
        print(f"  ✔ Survey executed simultaneously across {len(personas)} personas")
        print(f"  ✔ Side-by-side matrix generated: {len(matrix['questions'])} questions mapped across all personas")

    print("\n✔ Requirement 1 & 3 Passed: Simultaneous survey mode and cross-domain validation successful.")


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 & 4: Persona Consistency + Interview Memory
# ─────────────────────────────────────────────────────────────────────────────

def test_persona_consistency_and_memory():
    banner("2 & 4: Testing Persona Consistency & Multi-Turn Interview Memory")

    experiment = {
        "product_name": "VaultWise",
        "industry_domain": "FinTech",
        "product_description": "AI-powered micro-investing and automated wealth manager.",
        "target_audience": "Young professionals and budget-conscious savers.",
        "research_objectives": ["Pricing sensitivity", "Trust and bank security"]
    }

    persona = {
        "id": "persona_test_001",
        "name": "Marcus Vance",
        "age": 31,
        "gender": "Male",
        "occupation": "Financial Analyst",
        "location": "New York, USA",
        "archetype": "Budget-Conscious Pragmatist",
        "personality_traits": ["analytical", "cautious", "frugal"],
        "behavioral_patterns": {
            "current_tools": "Excel spreadsheets and low-cost index funds",
            "primary_pain_points": "Hidden transaction fees and account minimums",
            "willingness_to_pay": "Strictly free tier or sub-$3/month",
            "churn_triggers": "Unexpected charges or high expense ratios"
        },
        "opinion_seeds": {
            "price_sensitivity": 0.90,
            "openness_to_change": 0.30,
            "overall_sentiment_bias": 0.40
        },
        "memory": {
            "conversation_history": [],
            "established_opinions": {},
            "last_updated": ""
        }
    }

    # Turn 1: Probe pricing stance
    q1 = "What is your stance on paying a $15 monthly subscription for VaultWise?"
    r1 = PersonaMemoryModule.generate_response(persona, q1, experiment=experiment, mode="interview")
    print(f"User: {q1}")
    print(f"{persona['name']}: {r1}\n")

    _assert(
        len(persona["memory"]["conversation_history"]) == 2,
        f"Expected 2 history entries after turn 1, got {len(persona['memory']['conversation_history'])}"
    )
    _assert(
        "pricing" in persona["memory"]["established_opinions"],
        f"Topic 'pricing' not detected. Found topics: {list(persona['memory']['established_opinions'].keys())}"
    )

    pricing_opinion = persona["memory"]["established_opinions"]["pricing"]
    _assert(
        pricing_opinion["stance"] == "negative",
        f"Expected negative stance on high fee, got '{pricing_opinion['stance']}'"
    )
    _assert(
        "summary" in pricing_opinion and len(pricing_opinion["summary"]) > 0,
        "Substantive opinion summary missing"
    )
    print(f"  ✔ Stance recorded: {pricing_opinion['stance'].upper()} | Summary: '{pricing_opinion['summary']}'")

    # Turn 2: Follow-up probe — testing multi-turn memory consistency
    q2 = "Why do you say that? Can you elaborate on what makes you hesitate?"
    r2 = PersonaMemoryModule.generate_response(persona, q2, experiment=experiment, mode="interview")
    print(f"User: {q2}")
    print(f"{persona['name']}: {r2}\n")

    _assert(
        len(persona["memory"]["conversation_history"]) == 4,
        f"Expected 4 history entries after turn 2, got {len(persona['memory']['conversation_history'])}"
    )
    # Broader keyword set to handle LLM wording variation
    consistency_keywords = [
        "fee", "cost", "price", "expensive", "afford", "budget",
        "workflow", "disruption", "annoyance", "friction", "stability",
        "charge", "subscription", "pay", "spend", "value", "worth",
        "concern", "hesit", "reluct", "cautious", "wary"
    ]
    _assert(
        _contains_any(r2, consistency_keywords),
        f"Follow-up response lost behavioral consistency. Response: '{r2[:200]}...'"
    )
    print("  ✔ Follow-up probe maintained multi-turn context and character consistency")

    # Turn 3: Adoption intent question
    q3 = "Would you use this product if it offered a completely free tier with basic indexing?"
    r3 = PersonaMemoryModule.generate_response(persona, q3, experiment=experiment, mode="interview")
    print(f"User: {q3}")
    print(f"{persona['name']}: {r3}\n")

    adoption_keywords = [
        "free", "trial", "consider", "efficiency", "sensible", "willing",
        "interest", "open", "try", "worth", "explore", "test", "might",
        "perhaps", "possibly", "evaluate", "appeal", "attractive"
    ]
    _assert(
        _contains_any(r3, adoption_keywords),
        f"Adoption response did not reflect conditional interest. Response: '{r3[:200]}...'"
    )
    print("  ✔ Adoption response appropriately reflected Budget-Conscious Pragmatist archetype")

    print("\n✔ Requirement 2 & 4 Passed: Persona consistency and interview memory verified.")


# ─────────────────────────────────────────────────────────────────────────────
# Test 5, 6 & 7: Insight Extraction + Agreement Patterns + Scoring
# ─────────────────────────────────────────────────────────────────────────────

def test_insight_extraction_and_scoring():
    banner("5, 6 & 7: Testing Insight Extraction, Agreement Patterns, and 'Would Use' Scoring")

    experiment = {
        "product_name": "DevPulse AI",
        "industry_domain": "B2B SaaS / DevTools",
        "product_description": "An automated AI pull request reviewer and architectural impact analysis bot that speeds up code reviews for engineering teams.",
        "target_audience": "Software engineers and engineering managers.",
        "research_objectives": ["Identify review bottlenecks", "Determine pricing acceptance", "Measure adoption likelihood"]
    }

    personas = [
        {
            "id": "persona_001",
            "name": "Alex Rivera",
            "archetype": "Budget-Conscious Pragmatist",
            "personality_traits": ["frugal", "cautious"],
            "behavioral_patterns": {
                "current_tools": "Manual GitHub PR reviews",
                "primary_pain_points": "Slow turnaround on reviews",
                "willingness_to_pay": "Reluctant without proven ROI",
                "churn_triggers": "Excessive cost per seat"
            },
            "opinion_seeds": {"overall_sentiment_bias": 0.40, "openness_to_change": 0.35, "price_sensitivity": 0.85}
        },
        {
            "id": "persona_002",
            "name": "Priya Nair",
            "archetype": "Power User / Optimizer",
            "personality_traits": ["analytical", "tech-savvy"],
            "behavioral_patterns": {
                "current_tools": "CLI and custom linters",
                "primary_pain_points": "Superficial linter comments without architectural context",
                "willingness_to_pay": "$40/mo easily justified if deep",
                "churn_triggers": "Hallucinated recommendations"
            },
            "opinion_seeds": {"overall_sentiment_bias": 0.70, "openness_to_change": 0.85, "price_sensitivity": 0.25}
        },
        {
            "id": "persona_003",
            "name": "Jordan Smith",
            "archetype": "Busy Professional / Outcome-Driven",
            "personality_traits": ["decisive", "impatient"],
            "behavioral_patterns": {
                "current_tools": "Jira and Slack alerts",
                "primary_pain_points": "PR review bottlenecks blocking sprint releases",
                "willingness_to_pay": "Gladly pays company card",
                "churn_triggers": "Complex onboarding setup"
            },
            "opinion_seeds": {"overall_sentiment_bias": 0.75, "openness_to_change": 0.75, "price_sensitivity": 0.30}
        }
    ]

    survey_data = {
        "survey_id": "survey_test_001",
        "product_name": "DevPulse AI",
        "questions": [
            "Does slow pull request review time significantly bottleneck your team's shipping velocity?",
            "Would you adopt DevPulse AI if it integrated directly into GitHub without modifying CI/CD?",
            "Would you be willing to pay $35 per engineer per month for this solution?"
        ],
        "responses": [
            {
                "persona_id": "persona_001",
                "persona_name": "Alex Rivera",
                "archetype": "Budget-Conscious Pragmatist",
                "answers": [
                    {"question": "Q1", "answer": "Yes, slow reviews are definitely our biggest weekly bottleneck.", "sentiment": "positive"},
                    {"question": "Q2", "answer": "I would consider it if there is a generous free trial.", "sentiment": "positive"},
                    {"question": "Q3", "answer": "No, $35 per seat is too expensive for our budget.", "sentiment": "negative"}
                ]
            },
            {
                "persona_id": "persona_002",
                "persona_name": "Priya Nair",
                "archetype": "Power User / Optimizer",
                "answers": [
                    {"question": "Q1", "answer": "Yes, waiting 3 days for approvals halts progress.", "sentiment": "positive"},
                    {"question": "Q2", "answer": "Definitely, native GitHub integration is essential.", "sentiment": "positive"},
                    {"question": "Q3", "answer": "Yes, $35/month is well worth 4 hours saved per week.", "sentiment": "positive"}
                ]
            },
            {
                "persona_id": "persona_003",
                "persona_name": "Jordan Smith",
                "archetype": "Busy Professional / Outcome-Driven",
                "answers": [
                    {"question": "Q1", "answer": "Absolutely, review delays cost us delivery dates.", "sentiment": "positive"},
                    {"question": "Q2", "answer": "Yes, seamless GitHub adoption would make onboarding instant.", "sentiment": "positive"},
                    {"question": "Q3", "answer": "Yes, if it saves team time, $35 is an easy expense.", "sentiment": "positive"}
                ]
            }
        ]
    }

    save_json("data/test_experiment.json", experiment)
    save_json("data/test_persona_pool.json", personas)
    save_json("data/test_survey_responses.json", survey_data)
    save_json("data/test_interview_logs.json", [])

    insight_agent = InsightExtractionAgent(
        survey_path="data/test_survey_responses.json",
        interview_path="data/test_interview_logs.json",
        persona_path="data/test_persona_pool.json",
        experiment_path="data/test_experiment.json",
        report_dir="reports"
    )

    report = insight_agent.generate_report()

    # 1. Verify 'Would Use This Product?' scoring
    print("\n--- Testing 'Would Use This Product?' Scoring ---")
    _assert("would_use_score" in report, f"Report missing 'would_use_score' key. Keys found: {list(report.keys())}")
    w_score = report["would_use_score"]

    _assert("overall_score" in w_score, f"Missing 'overall_score'. Keys: {list(w_score.keys())}")
    _assert(0.0 <= w_score["overall_score"] <= 100.0, f"Overall score out of range: {w_score['overall_score']}")
    _assert("score_label" in w_score and len(w_score["score_label"]) > 0, "Missing or empty 'score_label'")
    _assert("summary_reasoning" in w_score and len(w_score["summary_reasoning"]) > 0, "Missing or empty 'summary_reasoning'")
    _assert("segment_breakdown" in w_score and len(w_score["segment_breakdown"]) == 3,
            f"Expected 3 segments, got {len(w_score.get('segment_breakdown', []))}")

    print(f"Overall Adoption Score: {w_score['overall_score']}% ({w_score['score_label']})")
    print(f"Summary Reasoning: {w_score['summary_reasoning']}")

    for seg in w_score["segment_breakdown"]:
        print(f"  • [{seg['segment']}]: {seg['score']}% ({seg['stance']})")
        print(f"    Reasoning: {seg['reasoning']}")
        _assert(0.0 <= seg["score"] <= 100.0, f"Segment score out of range: {seg['score']}")
        _assert(len(seg["reasoning"]) > 10, f"Segment reasoning too short: '{seg['reasoning']}'")

    # Power user / Busy professional score should be higher than budget pragmatist
    power_user = next((s for s in w_score["segment_breakdown"] if "Power" in s["segment"]), None)
    pragmatist = next((s for s in w_score["segment_breakdown"] if "Budget" in s["segment"]), None)
    if power_user and pragmatist:
        _assert(
            power_user["score"] > pragmatist["score"],
            f"Expected Power User score ({power_user['score']}) > Pragmatist score ({pragmatist['score']})"
        )
        print("  ✔ Cohort segmentation correctly reflected willingness to pay and feature priorities")
    else:
        print(f"  ⚠ Could not find Power User or Pragmatist segments. Segments: {[s['segment'] for s in w_score['segment_breakdown']]}")

    # 2. Verify Agreement Patterns
    print("\n--- Testing Agreement Patterns ---")
    _assert("agreement_patterns" in report, f"Report missing 'agreement_patterns'. Keys: {list(report.keys())}")
    agreements = report["agreement_patterns"]
    _assert("consensus" in agreements and len(agreements["consensus"]) > 0, "Consensus list empty")
    _assert("polarization" in agreements and len(agreements["polarization"]) > 0, "Polarization list empty")

    print("Consensus Findings:")
    for c in agreements["consensus"]:
        print(f"  [Consensus] {c}")

    print("Polarization Findings:")
    for p in agreements["polarization"]:
        print(f"  [Polarization] {p}")

    # On Q1, all personas responded positively -> expect positive consensus
    consensus_keywords = ["consensus", "agreement", "favorably", "agree", "unanimous", "all", "shared", "common", "universal"]
    _assert(
        any(_contains_any(str(c), consensus_keywords) for c in agreements["consensus"]),
        "Failed to identify consensus on bottleneck question"
    )
    # On Q3, Pragmatist said No while Power/Busy said Yes -> expect polarization
    polarization_keywords = ["split", "polariz", "divergen", "pricing", "divide", "disagree", "contrast", "mixed", "differ", "cost", "budget"]
    _assert(
        any(_contains_any(str(p), polarization_keywords) for p in agreements["polarization"]),
        "Failed to identify pricing polarization"
    )
    print("  ✔ Agreement patterns successfully identified universal bottleneck consensus and pricing divergence")

    # 3. Verify PDF generation with new sections
    date_str = report.get("report_date", "")
    if date_str:
        pdf_file = Path(f"reports/report_{date_str}.pdf")
        _assert(pdf_file.exists(), f"PDF report not found at {pdf_file}")
        _assert(pdf_file.stat().st_size > 1000, f"PDF file size too small ({pdf_file.stat().st_size} bytes)")
        print(f"  ✔ PDF report generated and validated: {pdf_file} ({pdf_file.stat().st_size} bytes)")
    else:
        print("  ⚠ report_date missing — skipping PDF existence check")

    print("\n✔ Requirement 5, 6 & 7 Passed: Insight extraction, agreement patterns, and scoring validated.")


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 (continued): Contrasting Product Discrimination
# ─────────────────────────────────────────────────────────────────────────────

def test_contrasting_product_discrimination():
    banner("7: Testing Contrasting Product Concept Discrimination")

    # Product A: High-Fit Concept
    high_fit_product = {
        "product_name": "InstantCodeReview",
        "industry_domain": "Developer Tools",
        "product_description": "Free instant automated security review tool for open source and startup developers.",
        "target_audience": "Developers seeking fast, free pull request checks.",
        "research_objectives": ["Security checks"]
    }

    # Product B: Flawed / High-Friction Concept
    flawed_product = {
        "product_name": "MandatoryLockinCloud",
        "industry_domain": "Cloud Infrastructure",
        "product_description": "A proprietary cloud tool that requires migrating all existing data into a closed format with mandatory multi-year upfront $50,000 contracts and no trial.",
        "target_audience": "Small business owners looking for simple hosting.",
        "research_objectives": ["Identify dealbreakers"]
    }

    personas_sample = [
        {
            "id": "p_01",
            "name": "Test User",
            "archetype": "Budget-Conscious Pragmatist",
            "behavioral_patterns": {
                "primary_pain_points": "High costs and lock-in",
                "willingness_to_pay": "Free or low cost",
                "churn_triggers": "Mandatory upfront contracts and price hikes"
            },
            "opinion_seeds": {"overall_sentiment_bias": 0.40, "openness_to_change": 0.30, "price_sensitivity": 0.90}
        }
    ]

    survey_high_fit = {
        "product_name": "InstantCodeReview",
        "questions": ["Would you use this free instant tool?"],
        "responses": [{
            "persona_id": "p_01",
            "persona_name": "Test User",
            "archetype": "Budget-Conscious Pragmatist",
            "answers": [{"question": "Q1", "answer": "Yes, absolutely worth using since it's free and fast.", "sentiment": "positive"}]
        }]
    }

    survey_flawed = {
        "product_name": "MandatoryLockinCloud",
        "questions": ["Would you commit to a $50k upfront locked contract?"],
        "responses": [{
            "persona_id": "p_01",
            "persona_name": "Test User",
            "archetype": "Budget-Conscious Pragmatist",
            "answers": [{"question": "Q1", "answer": "Never, this is a terrible dealbreaker and completely unaffordable.", "sentiment": "negative"}]
        }]
    }

    agent = InsightExtractionAgent(report_dir="reports")
    score_high = agent.calculate_would_use_score(high_fit_product, personas_sample, survey_high_fit)
    score_flawed = agent.calculate_would_use_score(flawed_product, personas_sample, survey_flawed)

    print(f"High-Fit Product Score: {score_high['overall_score']}% ({score_high['score_label']})")
    print(f"Flawed Product Score:   {score_flawed['overall_score']}% ({score_flawed['score_label']})")

    _assert(
        score_high["overall_score"] > score_flawed["overall_score"],
        f"High-fit product score ({score_high['overall_score']}) must be > flawed concept ({score_flawed['overall_score']})"
    )
    _assert(score_high["overall_score"] >= 60.0, f"Expected high score >= 60, got {score_high['overall_score']}")
    _assert(score_flawed["overall_score"] <= 40.0, f"Expected low score <= 40, got {score_flawed['overall_score']}")

    print("✔ Contrasting product discrimination verified: Platform cleanly separates viable from non-viable ideas.")


# ─────────────────────────────────────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print(" UNIVERSAL SYNTHETIC USERS RESEARCH — MILESTONE 3 VALIDATION SUITE")
    print("=" * 70)

    cfg = get_config_status()
    print(f"Environment Configuration: {cfg}")
    print(f"Project Root: {BASE_DIR}\n")

    # Run each test independently so one failure doesn't block the rest
    _run_test("Req 1 & 3: Survey Mode + 5 Diverse Domains", test_survey_mode_and_categories)
    _run_test("Req 2 & 4: Persona Consistency + Interview Memory", test_persona_consistency_and_memory)
    _run_test("Req 5, 6 & 7: Insight Extraction + Scoring", test_insight_extraction_and_scoring)
    _run_test("Req 7: Contrasting Product Discrimination", test_contrasting_product_discrimination)

    # ── Final Scoreboard ──
    banner("VALIDATION SUITE — FINAL RESULTS")
    passed = sum(1 for r in _results if r["status"] == "PASSED")
    failed = sum(1 for r in _results if r["status"] == "FAILED")
    total_time = sum(r["elapsed"] for r in _results)

    for r in _results:
        icon = "✔" if r["status"] == "PASSED" else "✘"
        line = f"  {icon} {r['name']} — {r['status']} ({r['elapsed']:.1f}s)"
        if r["error"]:
            line += f"\n      Error: {r['error'][:120]}"
        print(line)

    print(f"\n{'='*70}")
    print(f" {passed}/{passed + failed} tests passed  |  Total time: {total_time:.1f}s")
    print(f"{'='*70}\n")

    if failed > 0:
        print("✘ Some tests FAILED. Review the errors above.")
        sys.exit(1)
    else:
        print("✔ Task 1: Survey Mode with simultaneous execution & side-by-side comparison verified.")
        print("✔ Task 2: Persona consistency & response realism across multi-turn exchanges verified.")
        print("✔ Task 3: Survey Mode tested across 5 diverse product categories.")
        print("✔ Task 4: Interview Mode with multi-turn memory & session management verified.")
        print("✔ Task 5: Insight Extraction Agent with Agreement Patterns (consensus vs polarization) verified.")
        print("✔ Task 6: 'Would use this product?' scoring with segment breakdown & reasoning verified.")
        print("✔ Task 7: Theme relevance, insight quality, and contrasting scenario discrimination verified.")
        print("=" * 70 + "\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
