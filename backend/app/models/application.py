from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class OutreachEmail(BaseModel):
    """Outreach email template."""
    recipient: str
    subject: str
    body: str
    purpose: Optional[str] = None


class ApplicationBase(BaseModel):
    """Base application model."""
    cover_letter: Optional[str] = None
    outreach_emails: List[OutreachEmail] = []
    notes: Optional[str] = None
    status: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    """Application creation model."""
    job_id: UUID
    profile_id: UUID


class ApplicationUpdate(BaseModel):
    """Application update model - all fields optional."""
    cover_letter: Optional[str] = None
    outreach_emails: Optional[List[OutreachEmail]] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    applied_at: Optional[datetime] = None


class Application(ApplicationBase):
    """Complete application model with database fields."""
    id: UUID
    job_id: UUID
    profile_id: UUID
    applied_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AgentTaskBase(BaseModel):
    """Base agent task model."""
    task_type: str
    input_data: Dict[str, Any] = {}
    output_data: Dict[str, Any] = {}
    status: str = "pending"


class AgentTaskCreate(AgentTaskBase):
    """Agent task creation model."""
    profile_id: UUID


class AgentTask(AgentTaskBase):
    """Complete agent task model."""
    id: UUID
    profile_id: UUID
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
