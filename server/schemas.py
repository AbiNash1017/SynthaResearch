from typing import List, Optional
from pydantic import BaseModel


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
