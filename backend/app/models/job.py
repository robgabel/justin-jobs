from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class JobSource(str, Enum):
    """Job source types."""
    MANUAL = "manual"
    SEARCH = "search"


class JobStatus(str, Enum):
    """Job application status."""
    INTERESTED = "interested"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    REJECTED = "rejected"
    OFFERED = "offered"


class JobBase(BaseModel):
    """Base job model."""
    title: str
    company_name: str
    company_id: Optional[UUID] = None
    description: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    source: JobSource = JobSource.MANUAL
    status: JobStatus = JobStatus.INTERESTED


class JobCreate(JobBase):
    """Job creation model."""
    profile_id: UUID


class JobUpdate(BaseModel):
    """Job update model - all fields optional."""
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_id: Optional[UUID] = None
    description: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    source: Optional[JobSource] = None
    status: Optional[JobStatus] = None


class Job(JobBase):
    """Complete job model with database fields."""
    id: UUID
    profile_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
