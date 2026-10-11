from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status

from db.models import User, Experiment, Persona, SurveySession
from auth.dependencies import get_current_user
from schemas import SurveyRequestModel
from services import survey_agent

router = APIRouter(prefix="/api", tags=["Surveys"])


@router.get("/suggest-questions")
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


@router.post("/run-survey")
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
        raise HTTPException(status_code=400, detail="No personas found for active product. Please generate personas first.")

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


@router.get("/survey-matrix")
async def get_survey_matrix(current_user: User = Depends(get_current_user)):
    """Returns side-by-side comparison matrix for the active product survey from MongoDB."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active experiment found."
        )

    latest_survey = await SurveySession.find(
        SurveySession.user_id == user_id_str,
        SurveySession.experiment_id == str(exp.id)
    ).sort(-SurveySession.created_at).first_or_none()

    if not latest_survey or not latest_survey.questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No survey results found for this product. Run /api/run-survey first."
        )

    survey_data = {
        "questions": latest_survey.questions,
        "responses": latest_survey.responses
    }
    matrix = survey_agent.format_survey_matrix(survey_data)
    return matrix
