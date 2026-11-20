from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status

from db.models import User, Experiment, Persona, InterviewSession, SurveySession
from auth.dependencies import get_current_user
from services import persona_agent

router = APIRouter(prefix="/api", tags=["Personas"])


@router.post("/generate-personas")
async def generate_personas(
    count: Optional[int] = 5,
    current_user: User = Depends(get_current_user)
):
    """Generates synthetic personas tailored to the active product experiment and persists them in MongoDB. Clears previous persona chats and survey sessions for this experiment."""
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

    # Clean existing personas, interview chat sessions, and surveys for this user & active experiment
    exp_id_str = str(exp.id)
    await Persona.find(
        Persona.user_id == user_id_str,
        Persona.experiment_id == exp_id_str
    ).delete()

    await InterviewSession.find(
        InterviewSession.user_id == user_id_str,
        InterviewSession.experiment_id == exp_id_str
    ).delete()

    await SurveySession.find(
        SurveySession.user_id == user_id_str,
        SurveySession.experiment_id == exp_id_str
    ).delete()

    # Generate unique timestamp tag to prevent any slot or ID collision across generations
    gen_tag = hex(int(datetime.utcnow().timestamp()))[2:]

    # Insert into MongoDB with experiment-scoped, generation-unique persona IDs
    saved_personas = []
    for i, p in enumerate(generated):
        p_id = f"persona_{exp_id_str[:6]}_{gen_tag}_{i+1:03d}"
        p["id"] = p_id
        doc = Persona(
            user_id=user_id_str,
            experiment_id=exp_id_str,
            persona_id=p_id,
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


@router.get("/personas")
async def list_personas(
    experiment_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Retrieves all personas associated with the authenticated user's active (or specified) experiment."""
    user_id_str = str(current_user.id)
    exp_id = experiment_id
    if not exp_id:
        exp = await Experiment.find_one(
            Experiment.user_id == user_id_str,
            Experiment.is_active == True
        )
        if exp:
            exp_id = str(exp.id)

    if not exp_id:
        return {"count": 0, "personas": []}

    # Strictly retrieve personas belonging to this experiment - never leak old personas
    personas = await Persona.find(
        Persona.user_id == user_id_str,
        Persona.experiment_id == exp_id
    ).to_list()

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
