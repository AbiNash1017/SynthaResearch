"""
Automated end-to-end test suite for Universal Synthetic Users Research Platform.
Tests persona generation, survey, interview, and report generation for diverse product domains.
"""

import os
import sys
import json
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")

# Ensure workspace root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from agents.persona_generator import PersonaGenerationAgent
from agents.persona_memory import PersonaMemoryModule
from agents.survey_agent import SurveyAgent
from agents.interview_agent import InterviewAgent
from agents.insight_agent import InsightExtractionAgent
from config.settings import get_config_status, is_openrouter_configured, OPENROUTER_MODEL
from utils.storage import save_json, load_json

def test_pipeline_for_product(product_data: dict):
    product_name = product_data["product_name"]
    print(f"\n==================================================")
    print(f"RUNNING PIPELINE TEST FOR: {product_name} ({product_data['industry_domain']})")
    print(f"==================================================")

    # 1. Setup Experiment
    exp_path = "data/experiment.json"
    save_json(exp_path, product_data)
    loaded_exp = load_json(exp_path, None)
    assert loaded_exp is not None, "Failed to load saved experiment"
    assert loaded_exp["product_name"] == product_name, "Experiment product name mismatch"
    print(f"✔ Step 1: Experiment Workspace Configured: {product_name}")

    # 2. Generate Personas
    persona_agent = PersonaGenerationAgent(data_path="data/persona_pool.json")
    personas = persona_agent.generate_personas(loaded_exp, count=3, allow_fallback=True)
    assert len(personas) == 3, f"Expected 3 personas, got {len(personas)}"
    for p in personas:
        assert "id" in p and "name" in p and "archetype" in p
        assert "behavioral_patterns" in p
        assert "memory" in p
        print(f"  - Persona: {p['name']} | Archetype: {p['archetype']} | Occupation: {p['occupation']}")
    print(f"✔ Step 2: Personas Generated successfully")

    # 3. Suggest & Run Survey
    survey_agent = SurveyAgent(
        persona_path="data/persona_pool.json",
        output_path="data/survey_responses.json",
        experiment_path=exp_path
    )
    questions = survey_agent.suggest_questions(loaded_exp, count=2)
    assert len(questions) >= 1, "Expected at least 1 survey question"
    print(f"  Survey Questions: {questions}")

    survey_res = survey_agent.run_survey(questions, experiment=loaded_exp)
    assert "responses" in survey_res
    assert len(survey_res["responses"]) == len(personas)
    print(f"✔ Step 3: Multi-Persona Survey Executed ({len(survey_res['responses'])} personas answered)")

    # 4. Interactive Interview Simulation Mode (Multi-turn session logged)
    target_persona = personas[0]
    p_id = target_persona["id"]
    interview_turns = []
    
    q1 = f"What is your biggest concern or potential dealbreaker with adopting {product_name}?"
    reply1 = PersonaMemoryModule.generate_response(
        persona=target_persona,
        question=q1,
        experiment=loaded_exp,
        mode="interview"
    )
    assert isinstance(reply1, str) and len(reply1) > 5, "Invalid persona response on turn 1"
    interview_turns.append({
        "turn": 1,
        "user_message": q1,
        "persona_response": reply1,
        "timestamp": "2026-10-13T12:00:00"
    })

    q2 = f"How would your team justify the pricing and switching cost for {product_name}?"
    reply2 = PersonaMemoryModule.generate_response(
        persona=target_persona,
        question=q2,
        experiment=loaded_exp,
        mode="interview"
    )
    assert isinstance(reply2, str) and len(reply2) > 5, "Invalid persona response on turn 2"
    interview_turns.append({
        "turn": 2,
        "user_message": q2,
        "persona_response": reply2,
        "timestamp": "2026-10-13T12:01:00"
    })

    # Save session into interview logs for insight extraction
    session_data = [{
        "session_id": f"sess_{p_id}",
        "product_name": product_name,
        "persona_id": p_id,
        "persona_name": target_persona["name"],
        "archetype": target_persona.get("archetype", "User"),
        "turns": interview_turns
    }]
    interview_logs_path = "data/interview_logs.json"
    save_json(interview_logs_path, session_data)

    # Verify memory update
    history = target_persona["memory"]["conversation_history"]
    assert len(history) >= 4, f"Expected at least 4 turns in persona memory, found {len(history)}"
    print(f"✔ Step 4: Multi-Turn Interview Simulation Executed & Session Logged ({len(interview_turns)} turns)")
    print(f"  {target_persona['name']} on Q1: \"{reply1[:120]}...\"")

    # 5. Insight & Comprehensive Report Generation
    insight_agent = InsightExtractionAgent(
        survey_path="data/survey_responses.json",
        interview_path="data/interview_logs.json",
        persona_path="data/persona_pool.json",
        experiment_path=exp_path,
        report_dir="reports"
    )
    report = insight_agent.generate_report()

    # Assertions on core validation metrics
    assert "would_use_score" in report, "Report missing 'would_use_score'"
    w_score = report["would_use_score"]
    assert 0.0 <= w_score["overall_score"] <= 100.0, f"Invalid overall score: {w_score['overall_score']}"
    assert len(w_score.get("segment_breakdown", [])) > 0, "Missing segment breakdown in would_use_score"

    assert "sentiment_distribution" in report, "Report missing 'sentiment_distribution'"
    assert "top_insights" in report and len(report["top_insights"]) > 0, "Missing top actionable insights"

    # Assertions on Theme Clusters
    assert "theme_clusters" in report, "Report missing 'theme_clusters'"
    assert len(report["theme_clusters"]) >= 2, f"Expected >= 2 theme clusters, got {len(report['theme_clusters'])}"
    for cl in report["theme_clusters"]:
        assert "name" in cl and "category" in cl and "sentiment" in cl and "mention_count" in cl
    print(f"✔ Step 5a: Theme Clusters Extracted ({len(report['theme_clusters'])} clusters across categories: {list(set(c['category'] for c in report['theme_clusters']))})")

    # Assertions on Key Persona Quotes
    assert "key_persona_quotes" in report, "Report missing 'key_persona_quotes'"
    assert len(report["key_persona_quotes"]) >= 2, f"Expected >= 2 key persona quotes, got {len(report['key_persona_quotes'])}"
    for q in report["key_persona_quotes"]:
        assert "quote" in q and "persona_name" in q and "archetype" in q and "sentiment" in q
    print(f"✔ Step 5b: Key Persona Quotes Extracted ({len(report['key_persona_quotes'])} verbatim voices captured)")

    # Assertions on Response Highlights
    assert "response_highlights" in report, "Report missing 'response_highlights'"
    assert len(report["response_highlights"]) >= 2, f"Expected >= 2 response highlights, got {len(report['response_highlights'])}"
    for h in report["response_highlights"]:
        assert "topic" in h and "highlight" in h and "respondent_name" in h
    print(f"✔ Step 5c: Response Highlights Extracted ({len(report['response_highlights'])} empirical signals)")

    # Assertions on Persona Profiles Dossier
    assert "persona_profiles" in report, "Report missing 'persona_profiles'"
    assert len(report["persona_profiles"]) == len(personas), f"Expected {len(personas)} profiles, got {len(report['persona_profiles'])}"
    for prof in report["persona_profiles"]:
        assert "name" in prof and "archetype" in prof and "pain_points" in prof
    print(f"✔ Step 5d: Persona Profiles Dossier Compiled ({len(report['persona_profiles'])} profiles)")

    # Check generated report files (JSON & PDF)
    date_str = report["report_date"]
    json_report = Path(f"reports/report_{date_str}.json")
    pdf_report = Path(f"reports/report_{date_str}.pdf")
    assert json_report.exists(), f"JSON report file not found at {json_report}"
    assert pdf_report.exists(), f"PDF report file not found at {pdf_report}"
    assert pdf_report.stat().st_size > 3000, f"PDF report size too small ({pdf_report.stat().st_size} bytes)"
    print(f"✔ Step 5e: Exported PDF Report Validated: {pdf_report} ({pdf_report.stat().st_size} bytes)")

def main():
    print("==================================================")
    print("UNIVERSAL SYNTHETIC USERS RESEARCH — TEST SUITE")
    print("==================================================")
    status = get_config_status()
    print(f"LLM Config Status: {status}")

    # Test 1: Developer Tools Product (B2B SaaS)
    dev_tool_product = {
        "product_name": "DevPulse AI",
        "industry_domain": "Developer Tools & B2B SaaS",
        "product_description": "An automated AI pull request reviewer and architectural impact analysis bot that speeds up code reviews for engineering teams.",
        "target_audience": "Software engineers, tech leads, and engineering directors at mid-to-large tech companies.",
        "research_objectives": [
            "Assess skepticism around AI-generated review hallucinations and security flaws",
            "Determine willingness to pay per seat ($20-$50/developer/month)",
            "Identify what integrations (GitHub, GitLab, Slack) are strict dealbreakers"
        ]
    }
    test_pipeline_for_product(dev_tool_product)

    # Test 2: Consumer Health & Fitness Product (Hardware / Mobile IoT)
    health_product = {
        "product_name": "HydraGlow",
        "industry_domain": "Health & Wellness Consumer Tech",
        "product_description": "A smart insulated water bottle with biometric hydration tracking, ambient LED reminders, and an accompanying mobile wellness app.",
        "target_audience": "Active fitness enthusiasts, desk workers struggling with daily water intake, and biohackers.",
        "research_objectives": [
            "Evaluate willingness to purchase a $79 smart bottle vs standard bottles",
            "Identify if daily push notification reminders cause app uninstalls",
            "Discover interest in Apple Health and Garmin synchronization"
        ]
    }
    test_pipeline_for_product(health_product)

    print("\n==================================================")
    print("ALL END-TO-END PIPELINE TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    main()
