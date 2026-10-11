from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status

from db.models import User, Experiment, Persona, InterviewSession
from auth.dependencies import get_current_user
from schemas import InterviewMessageModel
from agents.persona_memory import PersonaMemoryModule

router = APIRouter(prefix="/api", tags=["Interviews"])


@router.post("/interview")
async def interview_turn(payload: InterviewMessageModel, current_user: User = Depends(get_current_user)):
    """Executes a single conversational turn with a specific persona, isolated per product experiment in MongoDB."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    exp_id_str = str(exp.id) if exp else None

    # First attempt to find persona scoped to active experiment
    persona_doc = None
    if exp_id_str:
        persona_doc = await Persona.find_one(
            Persona.user_id == user_id_str,
            Persona.experiment_id == exp_id_str,
            Persona.persona_id == payload.persona_id
        )
    if not persona_doc:
        persona_doc = await Persona.find_one(
            Persona.user_id == user_id_str,
            Persona.persona_id == payload.persona_id
        )
    if not persona_doc:
        raise HTTPException(status_code=404, detail=f"Persona {payload.persona_id} not found.")

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
            experiment_id=exp_id_str or persona_doc.experiment_id,
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


@router.get("/interviews")
async def list_interview_sessions(
    experiment_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Lists summary of all recorded interview sessions for the authenticated user's active (or specified) experiment."""
    user_id_str = str(current_user.id)
    exp_id = experiment_id
    if not exp_id:
        exp = await Experiment.find_one(
            Experiment.user_id == user_id_str,
            Experiment.is_active == True
        )
        if exp:
            exp_id = str(exp.id)

    if exp_id:
        logs = await InterviewSession.find(
            InterviewSession.user_id == user_id_str,
            InterviewSession.experiment_id == exp_id
        ).sort(-InterviewSession.created_at).to_list()
    else:
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


# Place /reset BEFORE /{session_id} so it is never masked as a parameter
@router.post("/interview/reset")
async def reset_interviews(current_user: User = Depends(get_current_user)):
    """Clears interview logs for the authenticated user's active experiment."""
    user_id_str = str(current_user.id)
    exp = await Experiment.find_one(
        Experiment.user_id == user_id_str,
        Experiment.is_active == True
    )
    if exp:
        await InterviewSession.find(
            InterviewSession.user_id == user_id_str,
            InterviewSession.experiment_id == str(exp.id)
        ).delete()
    else:
        await InterviewSession.find(InterviewSession.user_id == user_id_str).delete()
    return {"message": "Interview logs cleared successfully for active product."}


@router.get("/interview/{session_id}")
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
