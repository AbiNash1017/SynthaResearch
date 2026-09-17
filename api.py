from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from agents.persona_generator import PersonaGenerationAgent
from agents.persona_memory import PersonaMemoryModule
from agents.survey_agent import SurveyAgent
from agents.insight_agent import InsightExtractionAgent
from utils.storage import load_json, save_json

app = FastAPI(
    title="Synthetic Users Research Platform API",
    description="Backend services for AI-powered synthetic user research simulations",
    version="1.0.0"
)

persona_agent = PersonaGenerationAgent()
survey_agent = SurveyAgent()
insight_agent = InsightExtractionAgent()

class ExperimentModel(BaseModel):
    product_name: str
    product_description: str
    target_audience: str
    research_objectives: List[str]

class SurveyRequestModel(BaseModel):
    questions: List[str]

class InterviewMessageModel(BaseModel):
    persona_id: str
    user_message: str

@app.get("/")
def read_root():
    return {"status": "online", "system": "Synthetic Users Research Platform"}

@app.post("/api/setup-experiment")
def setup_experiment(exp: ExperimentModel):
    data = exp.model_dump()
    data["created_at"] = datetime.now().isoformat()
    save_json("data/experiment.json", data)
    return {"message": "Experiment workspace configured successfully", "experiment": data}

@app.get("/api/experiment")
def get_experiment():
    exp = load_json("data/experiment.json", None)
    if not exp:
        raise HTTPException(status_code=404, detail="No experiment setup found.")
    return exp

@app.post("/api/generate-personas")
def generate_personas(count: Optional[int] = 5):
    exp = load_json("data/experiment.json", {})
    if not exp:
        exp = {
            "product_name": "LearnFlow",
            "target_audience": "Online course self-learners",
            "product_description": "Udemy + Duolingo hybrid study platform"
        }
    personas = persona_agent.generate_personas(exp, count=count)
    return {"count": len(personas), "personas": personas}

@app.get("/api/personas")
def list_personas():
    personas = load_json("data/persona_pool.json", [])
    return {"count": len(personas), "personas": personas}

@app.post("/api/run-survey")
def run_survey(payload: SurveyRequestModel):
    try:
        results = survey_agent.run_survey(payload.questions)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/interview")
def interview_turn(payload: InterviewMessageModel):
    personas = load_json("data/persona_pool.json", [])
    persona = next((p for p in personas if p["id"] == payload.persona_id), None)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona {payload.persona_id} not found")

    response = PersonaMemoryModule.generate_response(persona, payload.user_message, mode="interview")
    PersonaMemoryModule.update_persona_pool(persona, "data/persona_pool.json")

    # Record turn in interview logs
    logs = load_json("data/interview_logs.json", [])
    # Find active session or create new
    session = next((s for s in logs if s.get("persona_id") == persona["id"]), None)
    if not session:
        session = {
            "session_id": f"session_{int(datetime.now().timestamp())}",
            "persona_id": persona["id"],
            "persona_name": persona["name"],
            "archetype": persona["archetype"],
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
        "persona_id": persona["id"],
        "persona_name": persona["name"],
        "user_message": payload.user_message,
        "persona_response": response
    }

@app.get("/api/generate-report")
def generate_report():
    report = insight_agent.generate_report()
    return report
