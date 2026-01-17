from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class CareerGoals(BaseModel):
    """Career goals structure."""
    short_term: Optional[str] = None
    long_term: Optional[str] = None
    preferred_industries: List[str] = []
    preferred_roles: List[str] = []
    preferred_locations: List[str] = []


class ProfileBase(BaseModel):
    """Base profile model."""
    name: str
    email: Optional[str] = None
    resume_text: Optional[str] = None
    resume_url: Optional[str] = None
    career_goals: Optional[CareerGoals] = None
    interests: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []


class ProfileCreate(ProfileBase):
    """Profile creation model."""
    pass


class ProfileUpdate(BaseModel):
    """Profile update model - all fields optional."""
    name: Optional[str] = None
    email: Optional[str] = None
    resume_text: Optional[str] = None
    resume_url: Optional[str] = None
    career_goals: Optional[CareerGoals] = None
    interests: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None


class Profile(ProfileBase):
    """Complete profile model with database fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class STARAnswerBase(BaseModel):
    """Base STAR answer model."""
    situation: str
    task: str
    action: str
    result: str
    tags: List[str] = []


class STARAnswerCreate(STARAnswerBase):
    """STAR answer creation model."""
    profile_id: UUID


class STARAnswer(STARAnswerBase):
    """Complete STAR answer model."""
    id: UUID
    profile_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
