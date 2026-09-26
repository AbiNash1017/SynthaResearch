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

    # 4. Interactive Interview Turn
    target_persona = personas[0]
    p_id = target_persona["id"]
    test_question = f"What is your biggest concern with adopting {product_name}?"
    reply = PersonaMemoryModule.generate_response(
        persona=target_persona,
        question=test_question,
        experiment=loaded_exp,
        mode="interview"
    )
    assert isinstance(reply, str) and len(reply) > 5, "Invalid persona response"
    print(f"  User Question: {test_question}")
    print(f"  {target_persona['name']}: {reply}")

    # Verify memory update
    history = target_persona["memory"]["conversation_history"]
    assert len(history) >= 2, "Conversation turn not stored in persona memory"
    print(f"✔ Step 4: Interview & Memory Consistency Verified")

    # 5. Insight & Report Generation
    insight_agent = InsightExtractionAgent(
        survey_path="data/survey_responses.json",
        interview_path="data/interview_logs.json",
        persona_path="data/persona_pool.json",
        experiment_path=exp_path,
        report_dir="reports"
    )
    report = insight_agent.generate_report()
    assert "sentiment_distribution" in report
    assert "top_insights" in report
    assert len(report["top_insights"]) > 0
    print(f"✔ Step 5: Research Report Generated (Sentiment: {report['sentiment_distribution']})")
    print(f"  Top Actionable Insight: {report['top_insights'][0]}")

    # Check generated files
    date_str = report["report_date"]
    json_report = Path(f"reports/report_{date_str}.json")
    pdf_report = Path(f"reports/report_{date_str}.pdf")
    assert json_report.exists(), f"JSON report file not found at {json_report}"
    assert pdf_report.exists(), f"PDF report file not found at {pdf_report}"
    print(f"  Report files verified: {json_report} & {pdf_report}")

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
