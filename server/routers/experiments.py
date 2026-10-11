from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from beanie import PydanticObjectId

from db.models import User, Experiment
from auth.dependencies import get_current_user
from schemas import ExperimentModel
from utils.normalizer import normalize_experiment

router = APIRouter(prefix="/api", tags=["Experiments"])


@router.post("/setup-experiment")
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


@router.get("/experiment")
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


@router.get("/experiments")
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


@router.post("/experiment/{experiment_id}/activate")
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
