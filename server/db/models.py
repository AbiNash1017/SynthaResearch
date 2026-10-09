from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Document, Indexed
from pydantic import Field


class User(Document):
    email: Indexed(str, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"


class Experiment(Document):
    user_id: Indexed(str)
    product_name: str
    product_description: str
    target_audience: str
    research_objectives: List[str] = []
    industry_domain: Optional[str] = "Technology"
    is_active: bool = True
    domain_profile: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "experiments"


class Persona(Document):
    user_id: Indexed(str)
    experiment_id: Optional[str] = None
    persona_id: Indexed(str)
    name: str
    age: int
    gender: str
    occupation: str
    location: str
    income_bracket: Optional[str] = None
    education: Optional[str] = None
    archetype: str
    personality_traits: List[str] = []
    behavioral_patterns: Dict[str, Any] = {}
    domain_specific_profile: Dict[str, Any] = {}
    memory_profile: Dict[str, Any] = {}
    opinion_seeds: Dict[str, Any] = {}
    background_story: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "personas"


class SurveySession(Document):
    user_id: Indexed(str)
    experiment_id: Optional[str] = None
    questions: List[str] = []
    responses: List[Dict[str, Any]] = []
    summary_stats: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "survey_sessions"


class InterviewSession(Document):
    user_id: Indexed(str)
    experiment_id: Optional[str] = None
    session_id: Indexed(str)
    persona_id: str
    persona_name: str
    archetype: str
    turns: List[Dict[str, Any]] = []
    session_started: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "interview_sessions"


class ResearchReport(Document):
    user_id: Indexed(str)
    experiment_id: Optional[str] = None
    timestamp: str
    date_str: str
    product_name: str
    executive_summary: str
    findings: List[Dict[str, Any]] = []
    sentiment_analysis: Dict[str, Any] = {}
    behavioral_themes: List[Dict[str, Any]] = []
    adoption_score: Dict[str, Any] = {}
    strategic_recommendations: List[str] = []
    domain_context: Dict[str, Any] = {}
    raw_data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reports"


ALL_DOCUMENT_MODELS = [
    User,
    Experiment,
    Persona,
    SurveySession,
    InterviewSession,
    ResearchReport,
]
