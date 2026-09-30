import warnings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")

from agents.persona_generator import PersonaGenerationAgent
from agents.persona_memory import PersonaMemoryModule
from agents.survey_agent import SurveyAgent
from agents.insight_agent import InsightExtractionAgent
from config.settings import get_config_status, is_openrouter_configured, OPENROUTER_MODEL
from utils.storage import load_json, save_json

app = FastAPI(
    title="Universal Synthetic User Research Platform API",
    description="Backend services for OpenRouter LLM-powered synthetic user research simulations across any product domain.",
    version="2.0.0"
)

persona_agent = PersonaGenerationAgent()
survey_agent = SurveyAgent()
insight_agent = InsightExtractionAgent()

class ExperimentModel(BaseModel):
    product_name: str
    product_description: str
    target_audience: str
    research_objectives: List[str]
    industry_domain: Optional[str] = "Technology"

class SurveyRequestModel(BaseModel):
    questions: List[str]

class InterviewMessageModel(BaseModel):
    persona_id: str
    user_message: str
    session_id: Optional[str] = None

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Universal Synthetic Users Research Platform",
        "llm_config": get_config_status()
    }

@app.get("/api/llm-config")
def get_llm_config():
    """Returns the current LLM configuration and whether OpenRouter is ready."""
    return get_config_status()

@app.post("/api/setup-experiment")
def setup_experiment(exp: ExperimentModel):
    data = exp.model_dump()
    data["created_at"] = datetime.now().isoformat()
    from utils.normalizer import normalize_experiment
    norm_data = normalize_experiment(data)
    norm_data.pop("_domain_profile", None)
    save_json("data/experiment.json", norm_data)
    return {"message": "Experiment workspace configured and normalized successfully", "experiment": norm_data}

@app.get("/api/experiment")
def get_experiment():
    exp = load_json("data/experiment.json", None)
    if not exp:
        raise HTTPException(status_code=404, detail="No active experiment found. Please call /api/setup-experiment.")
    return exp

@app.get("/api/suggest-questions")
def suggest_survey_questions(count: Optional[int] = 3):
    """Dynamically suggests survey questions tailored to the active product using OpenRouter LLM."""
    exp = load_json("data/experiment.json", None)
    if not exp:
        raise HTTPException(status_code=400, detail="No active experiment found. Configure an experiment first.")
    questions = survey_agent.suggest_questions(experiment=exp, count=count)
    return {"product_name": exp.get("product_name"), "suggested_questions": questions}

@app.post("/api/generate-personas")
def generate_personas(count: Optional[int] = 5):
    exp = load_json("data/experiment.json", None)
    if not exp:
        raise HTTPException(status_code=400, detail="No active experiment found. Please call /api/setup-experiment first.")
    personas = persona_agent.generate_personas(exp, count=count)
    return {"count": len(personas), "product": exp.get("product_name"), "personas": personas}

@app.get("/api/personas")
def list_personas():
    personas = load_json("data/persona_pool.json", [])
    return {"count": len(personas), "personas": personas}

@app.post("/api/run-survey")
def run_survey(payload: SurveyRequestModel):
    exp = load_json("data/experiment.json", None)
    try:
        results = survey_agent.run_survey(payload.questions, experiment=exp)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/survey-matrix")
def get_survey_matrix():
    """Returns side-by-side comparison matrix for the active survey."""
    matrix = survey_agent.format_survey_matrix()
    if not matrix.get("questions"):
        raise HTTPException(status_code=404, detail="No active survey results found. Run /api/run-survey first.")
    return matrix

@app.post("/api/interview")
def interview_turn(payload: InterviewMessageModel):
    personas = load_json("data/persona_pool.json", [])
    persona = next((p for p in personas if p["id"] == payload.persona_id), None)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona {payload.persona_id} not found")

    exp = load_json("data/experiment.json", {})
    response = PersonaMemoryModule.generate_response(
        persona=persona,
        question=payload.user_message,
        experiment=exp,
        mode="interview"
    )
    PersonaMemoryModule.update_persona_pool(persona, "data/persona_pool.json")

    # Record turn in interview logs with explicit session management
    logs = load_json("data/interview_logs.json", [])
    session = None
    if payload.session_id:
        session = next((s for s in logs if s.get("session_id") == payload.session_id), None)

    if not session:
        session_id = payload.session_id or f"session_{persona['id']}_{int(datetime.now().timestamp())}"
        session = {
            "session_id": session_id,
            "product_name": exp.get("product_name", "Product"),
            "persona_id": persona["id"],
            "persona_name": persona["name"],
            "archetype": persona.get("archetype", "User"),
            "turns": [],
            "session_started": datetime.now().isoformat()
        }
        logs.append(session)

    session["turns"].append({
        "turn": len(session["turns"]) + 1,
        "user_message": payload.user_message,
        "persona_response": response,
        "timestamp": datetime.now().isoformat()
    })
    save_json("data/interview_logs.json", logs)

    return {
        "session_id": session["session_id"],
        "persona_id": persona["id"],
        "persona_name": persona["name"],
        "archetype": persona.get("archetype"),
        "user_message": payload.user_message,
        "persona_response": response
    }

@app.get("/api/interviews")
def list_interview_sessions():
    """Lists summary of all recorded interview sessions."""
    logs = load_json("data/interview_logs.json", [])
    summaries = [
        {
            "session_id": s.get("session_id"),
            "persona_id": s.get("persona_id"),
            "persona_name": s.get("persona_name"),
            "archetype": s.get("archetype"),
            "turns_count": len(s.get("turns", [])),
            "session_started": s.get("session_started")
        }
        for s in logs
    ]
    return {"count": len(logs), "sessions": summaries}

@app.get("/api/interview/{session_id}")
def get_interview_session(session_id: str):
    """Retrieves full transcript and details of a specific interview session."""
    logs = load_json("data/interview_logs.json", [])
    session = next((s for s in logs if s.get("session_id") == session_id), None)
    if not session:
        raise HTTPException(status_code=404, detail=f"Interview session {session_id} not found.")
    return session

@app.post("/api/interview/reset")
def reset_interviews():
    """Clears interview logs for fresh testing."""
    save_json("data/interview_logs.json", [])
    return {"message": "Interview logs cleared successfully."}

@app.get("/api/adoption-score")
def get_adoption_score():
    """Calculates and returns the 'Would use this product?' adoption propensity score and segment breakdown."""
    exp = load_json("data/experiment.json", {})
    personas = load_json("data/persona_pool.json", [])
    survey_data = load_json("data/survey_responses.json", {})
    if not personas:
        raise HTTPException(status_code=400, detail="No personas found. Generate personas first.")
    score_data = insight_agent.calculate_would_use_score(exp, personas, survey_data)
    return score_data

@app.get("/api/generate-report")
def generate_report():
    try:
        report = insight_agent.generate_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
