import os
import warnings
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from beanie import PydanticObjectId

warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")

from agents.persona_generator import PersonaGenerationAgent
from agents.persona_memory import PersonaMemoryModule
from agents.survey_agent import SurveyAgent
from agents.insight_agent import InsightExtractionAgent
from config.settings import (
    get_config_status,
    CORS_ORIGINS,
)
from db.connection import init_db, close_db
from db.models import (
    User,
    Experiment,
    Persona,
    SurveySession,
    InterviewSession,
    ResearchReport,
)
from auth.router import router as auth_router
from auth.dependencies import get_current_user, security
from auth.utils import decode_token
from utils.normalizer import normalize_experiment
from utils.pdf_exporter import export_pdf


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes MongoDB and Beanie on startup, closes connection on shutdown."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Universal Synthetic User Research Platform API",
    description="Backend services for OpenRouter LLM-powered synthetic user research simulations across any product domain.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration with explicit allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Router
app.include_router(auth_router)

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


# ==========================================
# Public System & Config Endpoints
# ==========================================

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


# ==========================================
# Experiment Management Endpoints
# ==========================================

@app.post("/api/setup-experiment")
async def setup_experiment(exp: ExperimentModel, current_user: User = Depends(get_current_user)):
    """Sets up and normalizes a new experiment for the authenticated user, making it active."""
    user_id_str = str(current_user.id)
    data = exp.model_dump()
    data["created_at"] = datetime.utcnow().isoformat()
    norm_data = normalize_experiment(data)

    # Deactivate existing active experiments for this user
    await Experiment.find(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    ).update({"$set": {"is_active": False}})

    # Create new experiment document
    doc = Experiment(
        user_id=user_id_str,
        product_name=norm_data["product_name"],
        product_description=norm_data["product_description"],
        target_audience=norm_data["target_audience"],
        research_objectives=norm_data.get("research_objectives", []),
        industry_domain=norm_data.get("industry_domain", "Technology"),
        is_active=True,
        domain_profile=norm_data.get("_domain_profile")
    )
    await doc.insert()

    result_dict = {
        "id": str(doc.id),
        "product_name": doc.product_name,
        "product_description": doc.product_description,
        "target_audience": doc.target_audience,
        "research_objectives": doc.research_objectives,
        "industry_domain": doc.industry_domain,
        "is_active": doc.is_active,
        "created_at": doc.created_at.isoformat()
    }
    return {
        "message": "Experiment workspace configured and normalized successfully",
        "experiment": result_dict
    }


@app.get("/api/experiment")
async def get_active_experiment(current_user: User = Depends(get_current_user)):
    """Retrieves the currently active experiment for the authenticated user."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active experiment found. Please call /api/setup-experiment."
        )

    return {
        "id": str(exp.id),
        "product_name": exp.product_name,
        "product_description": exp.product_description,
        "target_audience": exp.target_audience,
        "research_objectives": exp.research_objectives,
        "industry_domain": exp.industry_domain,
        "is_active": exp.is_active,
        "created_at": exp.created_at.isoformat()
    }


@app.get("/api/experiments")
async def list_user_experiments(current_user: User = Depends(get_current_user)):
    """Lists all experiments created by the authenticated user."""
    user_id_str = str(current_user.id)
    experiments = await Experiment.find(
        Experiment.user_id == user_id_str
    ).sort(-Experiment.created_at).to_list()

    return {
        "count": len(experiments),
        "experiments": [
            {
                "id": str(e.id),
                "product_name": e.product_name,
                "product_description": e.product_description,
                "target_audience": e.target_audience,
                "research_objectives": e.research_objectives,
                "industry_domain": e.industry_domain,
                "is_active": e.is_active,
                "created_at": e.created_at.isoformat()
            }
            for e in experiments
        ]
    }


@app.post("/api/experiment/{experiment_id}/activate")
async def activate_experiment(experiment_id: str, current_user: User = Depends(get_current_user)):
    """Switches the user's active experiment."""
    user_id_str = str(current_user.id)
    try:
        exp = await Experiment.get(PydanticObjectId(experiment_id))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid experiment ID format.")

    if not exp or exp.user_id != user_id_str:
        raise HTTPException(status_code=404, detail="Experiment not found.")

    await Experiment.find(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    ).update({"$set": {"is_active": False}})

    exp.is_active = True
    await exp.save()

    return {"message": f"Experiment '{exp.product_name}' is now active."}


# ==========================================
# Persona Generation & Retrieval
# ==========================================

@app.get("/api/suggest-questions")
async def suggest_survey_questions(
    count: Optional[int] = 3,
    current_user: User = Depends(get_current_user)
):
    """Dynamically suggests survey questions tailored to the active product using OpenRouter LLM."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active experiment found. Configure an experiment first."
        )

    exp_dict = {
        "product_name": exp.product_name,
        "product_description": exp.product_description,
        "target_audience": exp.target_audience,
        "research_objectives": exp.research_objectives,
        "industry_domain": exp.industry_domain
    }
    questions = survey_agent.suggest_questions(experiment=exp_dict, count=count)
    return {"product_name": exp.product_name, "suggested_questions": questions}


@app.post("/api/generate-personas")
async def generate_personas(
    count: Optional[int] = 5,
    current_user: User = Depends(get_current_user)
):
    """Generates synthetic personas tailored to the active product experiment and persists them in MongoDB."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active experiment found. Please call /api/setup-experiment first."
        )

    exp_dict = {
        "product_name": exp.product_name,
        "product_description": exp.product_description,
        "target_audience": exp.target_audience,
        "research_objectives": exp.research_objectives,
        "industry_domain": exp.industry_domain
    }

    # Generate personas via agent (save_json disabled so we store in MongoDB)
    generated = persona_agent.generate_personas(exp_dict, count=count)

    # Clean existing personas for this user & active experiment
    exp_id_str = str(exp.id)
    await Persona.find(
        Persona.user_id == user_id_str,
        Persona.experiment_id == exp_id_str
    ).delete()

    # Insert into MongoDB
    saved_personas = []
    for p in generated:
        doc = Persona(
            user_id=user_id_str,
            experiment_id=exp_id_str,
            persona_id=p.get("id"),
            name=p.get("name"),
            age=p.get("age", 30),
            gender=p.get("gender", "Diverse"),
            occupation=p.get("occupation", "Professional"),
            location=p.get("location", "Urban"),
            income_bracket=p.get("income_bracket"),
            education=p.get("education"),
            archetype=p.get("archetype", "Target User"),
            personality_traits=p.get("personality_traits", []),
            behavioral_patterns=p.get("behavioral_patterns", {}),
            domain_specific_profile=p.get("domain_specific_profile", {}),
            memory_profile=p.get("memory_profile", {}),
            opinion_seeds=p.get("opinion_seeds", {}),
            background_story=p.get("background_story")
        )
        await doc.insert()
        saved_personas.append(p)

    return {
        "count": len(saved_personas),
        "product": exp.product_name,
        "personas": saved_personas
    }


@app.get("/api/personas")
async def list_personas(current_user: User = Depends(get_current_user)):
    """Retrieves all personas associated with the authenticated user's active experiment."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )

    query = Persona.user_id == user_id_str
    if exp:
        personas = await Persona.find(
            Persona.user_id == user_id_str,
            Persona.experiment_id == str(exp.id)
        ).to_list()
        # Fallback to any user personas if none tied to current experiment yet
        if not personas:
            personas = await Persona.find(Persona.user_id == user_id_str).to_list()
    else:
        personas = await Persona.find(query).to_list()

    p_list = [
        {
            "id": p.persona_id,
            "name": p.name,
            "age": p.age,
            "gender": p.gender,
            "occupation": p.occupation,
            "location": p.location,
            "income_bracket": p.income_bracket,
            "education": p.education,
            "archetype": p.archetype,
            "personality_traits": p.personality_traits,
            "behavioral_patterns": p.behavioral_patterns,
            "domain_specific_profile": p.domain_specific_profile,
            "memory_profile": p.memory_profile,
            "opinion_seeds": p.opinion_seeds,
            "background_story": p.background_story
        }
        for p in personas
    ]
    return {"count": len(p_list), "personas": p_list}


# ==========================================
# Survey Endpoints
# ==========================================

@app.post("/api/run-survey")
async def run_survey(payload: SurveyRequestModel, current_user: User = Depends(get_current_user)):
    """Executes a survey across the user's active personas and persists results in MongoDB."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(status_code=400, detail="No active experiment found.")

    exp_id_str = str(exp.id)
    persona_docs = await Persona.find(
        Persona.user_id == user_id_str,
        Persona.experiment_id == exp_id_str
    ).to_list()

    if not persona_docs:
        # Fallback to any user personas
        persona_docs = await Persona.find(Persona.user_id == user_id_str).to_list()

    if not persona_docs:
        raise HTTPException(status_code=400, detail="No personas found. Please generate personas first.")

    personas_dicts = [
        {
            "id": p.persona_id,
            "name": p.name,
            "age": p.age,
            "gender": p.gender,
            "occupation": p.occupation,
            "location": p.location,
            "archetype": p.archetype,
            "personality_traits": p.personality_traits,
            "behavioral_patterns": p.behavioral_patterns,
            "domain_specific_profile": p.domain_specific_profile,
            "memory_profile": p.memory_profile,
            "opinion_seeds": p.opinion_seeds,
            "background_story": p.background_story
        }
        for p in persona_docs
    ]

    exp_dict = {
        "product_name": exp.product_name,
        "product_description": exp.product_description,
        "target_audience": exp.target_audience,
        "research_objectives": exp.research_objectives,
        "industry_domain": exp.industry_domain
    }

    try:
        results = survey_agent.run_survey(
            questions=payload.questions,
            experiment=exp_dict,
            personas=personas_dicts,
            save_to_file=False
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Persist SurveySession in MongoDB
    session = SurveySession(
        user_id=user_id_str,
        experiment_id=exp_id_str,
        questions=payload.questions,
        responses=results.get("responses", []),
        summary_stats={"matrix": results.get("matrix")}
    )
    await session.insert()

    return results


@app.get("/api/survey-matrix")
async def get_survey_matrix(current_user: User = Depends(get_current_user)):
    """Returns side-by-side comparison matrix for the active survey from MongoDB."""
    user_id_str = str(current_user.id)
    latest_survey = await SurveySession.find(
        SurveySession.user_id == user_id_str
    ).sort(-SurveySession.created_at).first_or_none()

    if not latest_survey or not latest_survey.questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active survey results found. Run /api/run-survey first."
        )

    survey_data = {
        "questions": latest_survey.questions,
        "responses": latest_survey.responses
    }
    matrix = survey_agent.format_survey_matrix(survey_data)
    return matrix


# ==========================================
# 1-on-1 Interactive Interview Endpoints
# ==========================================

@app.post("/api/interview")
async def interview_turn(payload: InterviewMessageModel, current_user: User = Depends(get_current_user)):
    """Executes a single conversational turn with a specific persona, isolated per user in MongoDB."""
    user_id_str = str(current_user.id)
    persona_doc = await Persona.find_one(
        Persona.user_id == user_id_str,
        Persona.persona_id == payload.persona_id
    )
    if not persona_doc:
        raise HTTPException(status_code=404, detail=f"Persona {payload.persona_id} not found.")

    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    exp_dict = {
        "product_name": exp.product_name if exp else "Product",
        "product_description": exp.product_description if exp else "",
        "target_audience": exp.target_audience if exp else "",
        "research_objectives": exp.research_objectives if exp else []
    }

    persona_dict = {
        "id": persona_doc.persona_id,
        "name": persona_doc.name,
        "age": persona_doc.age,
        "gender": persona_doc.gender,
        "occupation": persona_doc.occupation,
        "location": persona_doc.location,
        "archetype": persona_doc.archetype,
        "personality_traits": persona_doc.personality_traits,
        "behavioral_patterns": persona_doc.behavioral_patterns,
        "domain_specific_profile": persona_doc.domain_specific_profile,
        "memory_profile": persona_doc.memory_profile,
        "opinion_seeds": persona_doc.opinion_seeds,
        "background_story": persona_doc.background_story
    }

    # Session management in MongoDB: load or initialize session first
    session = None
    if payload.session_id:
        session = await InterviewSession.find_one(
            InterviewSession.user_id == user_id_str,
            InterviewSession.session_id == payload.session_id
        )

    if not session:
        session_id = payload.session_id or f"session_{persona_doc.persona_id}_{int(datetime.utcnow().timestamp())}"
        session = InterviewSession(
            user_id=user_id_str,
            experiment_id=str(exp.id) if exp else None,
            session_id=session_id,
            persona_id=persona_doc.persona_id,
            persona_name=persona_doc.name,
            archetype=persona_doc.archetype,
            turns=[],
            session_started=datetime.utcnow().isoformat()
        )

    # Reconstruct previous conversation turns for authentic multi-turn memory
    history = []
    for t in session.turns[-8:]:
        history.append({"role": "user", "content": t.get("user_message", "")})
        history.append({"role": "persona", "content": t.get("persona_response", "")})

    memory = dict(persona_doc.memory_profile or {})
    memory["conversation_history"] = history
    persona_dict["memory"] = memory

    response = PersonaMemoryModule.generate_response(
        persona=persona_dict,
        question=payload.user_message,
        experiment=exp_dict,
        mode="interview"
    )

    # Concurrency-safe atomic update of persona memory profile in MongoDB
    persona_doc.memory_profile = persona_dict.get("memory", {})
    await persona_doc.save()

    session.turns.append({
        "turn": len(session.turns) + 1,
        "user_message": payload.user_message,
        "persona_response": response,
        "timestamp": datetime.utcnow().isoformat()
    })
    await session.save()

    return {
        "session_id": session.session_id,
        "persona_id": persona_doc.persona_id,
        "persona_name": persona_doc.name,
        "archetype": persona_doc.archetype,
        "user_message": payload.user_message,
        "persona_response": response
    }


@app.get("/api/interviews")
async def list_interview_sessions(current_user: User = Depends(get_current_user)):
    """Lists summary of all recorded interview sessions for the authenticated user."""
    user_id_str = str(current_user.id)
    logs = await InterviewSession.find(
        InterviewSession.user_id == user_id_str
    ).sort(-InterviewSession.created_at).to_list()

    summaries = [
        {
            "session_id": s.session_id,
            "persona_id": s.persona_id,
            "persona_name": s.persona_name,
            "archetype": s.archetype,
            "turns_count": len(s.turns),
            "session_started": s.session_started
        }
        for s in logs
    ]
    return {"count": len(logs), "sessions": summaries}


# FIX B3: Place /api/interview/reset BEFORE /api/interview/{session_id} so it is never masked!
@app.post("/api/interview/reset")
async def reset_interviews(current_user: User = Depends(get_current_user)):
    """Clears interview logs for the authenticated user for fresh testing."""
    user_id_str = str(current_user.id)
    await InterviewSession.find(InterviewSession.user_id == user_id_str).delete()
    return {"message": "Interview logs cleared successfully."}


@app.get("/api/interview/{session_id}")
async def get_interview_session(session_id: str, current_user: User = Depends(get_current_user)):
    """Retrieves full transcript and details of a specific interview session."""
    user_id_str = str(current_user.id)
    session = await InterviewSession.find_one(
        InterviewSession.user_id == user_id_str,
        InterviewSession.session_id == session_id
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session '{session_id}' not found."
        )
    return {
        "session_id": session.session_id,
        "persona_id": session.persona_id,
        "persona_name": session.persona_name,
        "archetype": session.archetype,
        "turns": session.turns,
        "session_started": session.session_started
    }


# ==========================================
# Adoption Score & Insight Report Endpoints
# ==========================================

@app.get("/api/adoption-score")
async def get_adoption_score(current_user: User = Depends(get_current_user)):
    """Calculates and returns the 'Would use this product?' adoption propensity score."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(status_code=400, detail="No active experiment found.")

    exp_dict = {
        "product_name": exp.product_name,
        "product_description": exp.product_description,
        "target_audience": exp.target_audience,
        "research_objectives": exp.research_objectives,
        "industry_domain": exp.industry_domain
    }

    persona_docs = await Persona.find(
        Persona.user_id == user_id_str,
        Persona.experiment_id == str(exp.id)
    ).to_list()
    if not persona_docs:
        persona_docs = await Persona.find(Persona.user_id == user_id_str).to_list()

    if not persona_docs:
        raise HTTPException(status_code=400, detail="No personas found. Generate personas first.")

    personas_dicts = [
        {
            "id": p.persona_id,
            "name": p.name,
            "archetype": p.archetype,
            "personality_traits": p.personality_traits,
            "behavioral_patterns": p.behavioral_patterns,
            "domain_specific_profile": p.domain_specific_profile,
            "opinion_seeds": p.opinion_seeds
        }
        for p in persona_docs
    ]

    latest_survey = await SurveySession.find(
        SurveySession.user_id == user_id_str
    ).sort(-SurveySession.created_at).first_or_none()

    survey_data = {
        "questions": latest_survey.questions if latest_survey else [],
        "responses": latest_survey.responses if latest_survey else []
    }

    score_data = insight_agent.calculate_would_use_score(exp_dict, personas_dicts, survey_data)
    
    # Calculate response sentiment counts
    pos_count = 0
    neu_count = 0
    neg_count = 0
    total_answers = 0
    for resp in survey_data.get("responses", []):
        for ans in resp.get("answers", []):
            total_answers += 1
            s = str(ans.get("sentiment", "neutral")).lower()
            if s == "positive":
                pos_count += 1
            elif s == "negative":
                neg_count += 1
            else:
                neu_count += 1

    score_data["total_personas"] = len(persona_docs)
    score_data["breakdown"] = {
        "positive_sentiment_count": pos_count,
        "neutral_sentiment_count": neu_count,
        "negative_sentiment_count": neg_count,
        "total_responses": total_answers,
        "would_use_count": sum(1 for s in score_data.get("segment_breakdown", []) if s.get("score", 0) >= 50)
    }
    score_data["adoption_score"] = round(score_data.get("overall_score", 0) / 100.0, 3)
    score_data["sentiment_label"] = score_data.get("score_label", "Evaluated")
    score_data["product_name"] = exp.product_name
    return score_data


@app.get("/api/generate-report")
async def generate_report(current_user: User = Depends(get_current_user)):
    """Generates an executive research synthesis report and stores it in MongoDB."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(status_code=400, detail="No active experiment found.")

    exp_dict = {
        "product_name": exp.product_name,
        "product_description": exp.product_description,
        "target_audience": exp.target_audience,
        "research_objectives": exp.research_objectives,
        "industry_domain": exp.industry_domain
    }

    persona_docs = await Persona.find(
        Persona.user_id == user_id_str,
        Persona.experiment_id == str(exp.id)
    ).to_list()
    if not persona_docs:
        persona_docs = await Persona.find(Persona.user_id == user_id_str).to_list()

    personas_dicts = [
        {
            "id": p.persona_id,
            "name": p.name,
            "archetype": p.archetype,
            "personality_traits": p.personality_traits,
            "behavioral_patterns": p.behavioral_patterns,
            "domain_specific_profile": p.domain_specific_profile,
            "opinion_seeds": p.opinion_seeds
        }
        for p in persona_docs
    ]

    latest_survey = await SurveySession.find(
        SurveySession.user_id == user_id_str
    ).sort(-SurveySession.created_at).first_or_none()

    survey_data = {
        "questions": latest_survey.questions if latest_survey else [],
        "responses": latest_survey.responses if latest_survey else []
    }

    interview_sessions = await InterviewSession.find(
        InterviewSession.user_id == user_id_str
    ).to_list()

    interview_logs = [
        {
            "session_id": s.session_id,
            "persona_id": s.persona_id,
            "persona_name": s.persona_name,
            "archetype": s.archetype,
            "turns": s.turns
        }
        for s in interview_sessions
    ]

    try:
        report = insight_agent.generate_report(
            experiment=exp_dict,
            personas=personas_dicts,
            survey_data=survey_data,
            interview_logs=interview_logs,
            save_to_file=True
        )

        # Store in MongoDB
        doc = ResearchReport(
            user_id=user_id_str,
            experiment_id=str(exp.id),
            timestamp=datetime.utcnow().isoformat(),
            date_str=report.get("report_date", datetime.utcnow().strftime("%Y-%m-%d")),
            product_name=exp.product_name,
            executive_summary=report.get("executive_summary", ""),
            findings=report.get("findings", []),
            sentiment_analysis=report.get("sentiment_distribution", {}),
            behavioral_themes=report.get("behavioral_trends", []),
            adoption_score=report.get("would_use_score", {}),
            strategic_recommendations=report.get("top_insights", []),
            domain_context=report.get("domain_context", {}),
            raw_data=report
        )
        await doc.insert()
        report["id"] = str(doc.id)

        # Export report with doc.id for stable ID retrieval
        try:
            os.makedirs("reports", exist_ok=True)
            export_pdf(report, f"reports/report_{doc.id}.pdf")
        except Exception as pdf_err:
            print(f"Notice: Non-critical PDF export error: {pdf_err}")

        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_user_from_auth_or_query(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token: Optional[str] = Query(None)
) -> User:
    """Dependency supporting either Authorization Bearer header or ?token= query parameter."""
    raw_token = None
    if credentials and credentials.credentials:
        raw_token = credentials.credentials
    elif token:
        raw_token = token

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a Bearer token or token parameter.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(raw_token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type.")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing subject.")
        user = await User.get(PydanticObjectId(user_id))
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive.")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials.")


@app.get("/api/reports/latest")
async def get_latest_report(current_user: User = Depends(get_current_user)):
    """Returns the most recent research report generated for the user."""
    user_id_str = str(current_user.id)
    doc = await ResearchReport.find(
        ResearchReport.user_id == user_id_str
    ).sort(-ResearchReport.created_at).first_or_none()

    if not doc:
        return {"report": None}

    report_data = doc.raw_data or {}
    if not report_data:
        report_data = {
            "id": str(doc.id),
            "product": doc.product_name,
            "report_date": doc.date_str,
            "executive_summary": doc.executive_summary,
            "would_use_score": doc.adoption_score,
            "sentiment_distribution": doc.sentiment_analysis,
            "behavioral_trends": doc.behavioral_themes,
            "top_insights": doc.strategic_recommendations,
        }
    report_data["id"] = str(doc.id)
    return {"report": report_data}


@app.get("/api/reports/latest/pdf")
async def get_latest_report_pdf(
    user: User = Depends(get_user_from_auth_or_query)
):
    """Streams the PDF file for the most recent research report."""
    user_id_str = str(user.id)
    doc = await ResearchReport.find(
        ResearchReport.user_id == user_id_str
    ).sort(-ResearchReport.created_at).first_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="No generated reports found.")

    doc_id_str = str(doc.id)
    pdf_path = f"reports/report_{doc_id_str}.pdf"
    date_pdf_path = f"reports/report_{doc.date_str}.pdf"

    if not os.path.exists(pdf_path):
        if os.path.exists(date_pdf_path):
            pdf_path = date_pdf_path
        elif doc.raw_data:
            os.makedirs("reports", exist_ok=True)
            export_pdf(doc.raw_data, pdf_path)
        else:
            raise HTTPException(status_code=404, detail="PDF report file not found on disk.")

    safe_name = "".join(c for c in doc.product_name if c.isalnum() or c in (" ", "_", "-")).strip() or "Research"
    safe_name = safe_name.replace(" ", "_")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{safe_name}_Research_Report.pdf",
        headers={
            "Content-Disposition": f'inline; filename="{safe_name}_Research_Report.pdf"'
        }
    )


@app.get("/api/reports/{report_id}/pdf")
async def get_report_pdf_by_id(
    report_id: str,
    user: User = Depends(get_user_from_auth_or_query)
):
    """Streams the PDF file for a specific research report by ID."""
    user_id_str = str(user.id)

    try:
        obj_id = PydanticObjectId(report_id)
        doc = await ResearchReport.get(obj_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid report ID format.")

    if not doc or doc.user_id != user_id_str:
        raise HTTPException(status_code=404, detail="Report not found.")

    pdf_path = f"reports/report_{report_id}.pdf"
    date_pdf_path = f"reports/report_{doc.date_str}.pdf"

    if not os.path.exists(pdf_path):
        if os.path.exists(date_pdf_path):
            pdf_path = date_pdf_path
        elif doc.raw_data:
            os.makedirs("reports", exist_ok=True)
            export_pdf(doc.raw_data, pdf_path)
        else:
            raise HTTPException(status_code=404, detail="PDF report file not found.")

    safe_name = "".join(c for c in doc.product_name if c.isalnum() or c in (" ", "_", "-")).strip() or "Research"
    safe_name = safe_name.replace(" ", "_")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{safe_name}_Research_Report.pdf",
        headers={
            "Content-Disposition": f'inline; filename="{safe_name}_Research_Report.pdf"'
        }
    )


@app.get("/api/reports")
async def list_reports(current_user: User = Depends(get_current_user)):
    """Lists past research reports generated for the user."""
    user_id_str = str(current_user.id)
    reports = await ResearchReport.find(
        ResearchReport.user_id == user_id_str
    ).sort(-ResearchReport.created_at).to_list()

    return {
        "count": len(reports),
        "reports": [
            {
                "id": str(r.id),
                "product_name": r.product_name,
                "date_str": r.date_str,
                "executive_summary": r.executive_summary[:200] if r.executive_summary else "",
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]
    }
