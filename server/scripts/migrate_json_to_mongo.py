"""Migration utility to import legacy flat JSON data into MongoDB collections."""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Ensure server package path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pymongo import AsyncMongoClient
from beanie import init_beanie
from config.settings import MONGODB_URL, MONGODB_DB_NAME
from db.models import (
    ALL_DOCUMENT_MODELS,
    User,
    Experiment,
    Persona,
    SurveySession,
    InterviewSession,
)
from auth.utils import hash_password
from utils.storage import load_json


async def migrate(email: str = "admin@syntharesearch.com", password: str = "admin123"):
    client = AsyncMongoClient(MONGODB_URL)
    database = client[MONGODB_DB_NAME]
    await init_beanie(database=database, document_models=ALL_DOCUMENT_MODELS)
    print(f"Connected to MongoDB '{MONGODB_DB_NAME}'.")

    # 1. Ensure default/admin user exists
    user = await User.find_one(User.email == email)
    if not user:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name="Default Researcher"
        )
        await user.insert()
        print(f"Created default user: {email} (password: {password})")
    else:
        print(f"Using existing user: {email}")

    user_id_str = str(user.id)
    base_data = Path(__file__).resolve().parent.parent / "data"

    # 2. Migrate experiment.json
    exp_file = base_data / "experiment.json"
    exp_doc = None
    if exp_file.exists():
        exp_data = load_json(str(exp_file), {})
        if exp_data and "product_name" in exp_data:
            # Check if already imported
            existing_exp = await Experiment.find_one(
                Experiment.user_id == user_id_str,
                Experiment.product_name == exp_data["product_name"]
            )
            if not existing_exp:
                exp_doc = Experiment(
                    user_id=user_id_str,
                    product_name=exp_data.get("product_name", "Migrated Product"),
                    product_description=exp_data.get("product_description", ""),
                    target_audience=exp_data.get("target_audience", ""),
                    research_objectives=exp_data.get("research_objectives", []),
                    industry_domain=exp_data.get("industry_domain", "Technology"),
                    is_active=True,
                    domain_profile=exp_data.get("_domain_profile")
                )
                await exp_doc.insert()
                print(f"Migrated experiment: '{exp_doc.product_name}'")
            else:
                exp_doc = existing_exp
                print(f"Experiment already in MongoDB: '{exp_doc.product_name}'")

    exp_id_str = str(exp_doc.id) if exp_doc else None

    # 3. Migrate persona_pool.json
    persona_file = base_data / "persona_pool.json"
    if persona_file.exists():
        personas = load_json(str(persona_file), [])
        migrated_personas = 0
        for p in personas:
            pid = p.get("id")
            existing = await Persona.find_one(
                Persona.user_id == user_id_str,
                Persona.persona_id == pid
            )
            if not existing:
                doc = Persona(
                    user_id=user_id_str,
                    experiment_id=exp_id_str,
                    persona_id=pid,
                    name=p.get("name", "Unnamed"),
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
                migrated_personas += 1
        print(f"Migrated {migrated_personas} personas into MongoDB.")

    # 4. Migrate survey_responses.json
    survey_file = base_data / "survey_responses.json"
    if survey_file.exists():
        s_data = load_json(str(survey_file), {})
        if s_data and "questions" in s_data and s_data.get("questions"):
            existing_survey = await SurveySession.find_one(SurveySession.user_id == user_id_str)
            if not existing_survey:
                s_doc = SurveySession(
                    user_id=user_id_str,
                    experiment_id=exp_id_str,
                    questions=s_data.get("questions", []),
                    responses=s_data.get("responses", []),
                    summary_stats={"matrix": s_data.get("matrix")}
                )
                await s_doc.insert()
                print("Migrated survey responses into MongoDB.")

    # 5. Migrate interview_logs.json
    logs_file = base_data / "interview_logs.json"
    if logs_file.exists():
        logs = load_json(str(logs_file), [])
        migrated_logs = 0
        for item in logs:
            sid = item.get("session_id")
            existing_sess = await InterviewSession.find_one(
                InterviewSession.user_id == user_id_str,
                InterviewSession.session_id == sid
            )
            if not existing_sess:
                i_doc = InterviewSession(
                    user_id=user_id_str,
                    experiment_id=exp_id_str,
                    session_id=sid,
                    persona_id=item.get("persona_id", ""),
                    persona_name=item.get("persona_name", ""),
                    archetype=item.get("archetype", ""),
                    turns=item.get("turns", []),
                    session_started=item.get("session_started")
                )
                await i_doc.insert()
                migrated_logs += 1
        print(f"Migrated {migrated_logs} interview sessions into MongoDB.")

    await client.close()
    print("Migration finished successfully!")


if __name__ == "__main__":
    asyncio.run(migrate())
