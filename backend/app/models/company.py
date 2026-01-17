from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class KeyPerson(BaseModel):
    """Key person at a company."""
    name: str
    title: str
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None


class NewsItem(BaseModel):
    """News item about a company."""
    title: str
    url: str
    date: Optional[str] = None
    summary: Optional[str] = None


class CompanyBase(BaseModel):
    """Base company model."""
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    culture_notes: Optional[str] = None
    recent_news: List[NewsItem] = []
    key_people: List[KeyPerson] = []
    research_summary: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Company creation model."""
    pass


class CompanyUpdate(BaseModel):
    """Company update model - all fields optional."""
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    culture_notes: Optional[str] = None
    recent_news: Optional[List[NewsItem]] = None
    key_people: Optional[List[KeyPerson]] = None
    research_summary: Optional[str] = None


class Company(CompanyBase):
    """Complete company model with database fields."""
    id: UUID
    last_researched_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
