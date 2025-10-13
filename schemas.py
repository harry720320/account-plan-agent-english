"""
Pydantic data models
Used for API request and response data validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AccountCreate(BaseModel):
    """Create account request model"""
    company_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    country: str  # Country information, required field
    description: Optional[str] = None

class AccountResponse(BaseModel):
    """Account response model"""
    id: int
    company_name: str
    industry: Optional[str]
    company_size: Optional[str]
    website: Optional[str]
    country: str  # Country information
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

class InteractionCreate(BaseModel):
    """Create interaction record request model"""
    question: str
    answer: str
    plan_id: Optional[int] = None

class InteractionResponse(BaseModel):
    """Interaction record response model"""
    id: int
    account_id: int
    interaction_type: str
    question: Optional[str]
    answer: Optional[str]
    structured_data: Optional[dict]
    created_at: datetime

class PlanCreate(BaseModel):
    """Create plan request model"""
    title: Optional[str] = None
    description: Optional[str] = None

class PlanResponse(BaseModel):
    """Plan response model"""
    id: int
    account_id: int
    title: str
    content: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

class ExternalInfoRequest(BaseModel):
    """External information collection request model"""
    info_type: str = "all"  # all, company_profile, news, market_info

class QuestionResponse(BaseModel):
    """Question response model"""
    id: int
    category: str
    question_text: str
    follow_up_questions: list
    order: int
