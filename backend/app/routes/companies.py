from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from uuid import UUID
from datetime import datetime

from app.models.company import Company, CompanyCreate, CompanyUpdate
from app.database import get_supabase
from app.agents.company_researcher import CompanyResearcherAgent

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=Company)
async def create_company(company: CompanyCreate):
    """Create a new company."""
    supabase = get_supabase()

    company_data = company.model_dump()

    # Convert nested models to dicts
    if company_data.get("recent_news"):
        company_data["recent_news"] = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in company_data["recent_news"]
        ]
    if company_data.get("key_people"):
        company_data["key_people"] = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in company_data["key_people"]
        ]

    result = supabase.table("companies").insert(company_data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create company")

    return result.data[0]


@router.get("/", response_model=List[Company])
async def list_companies():
    """List all companies."""
    supabase = get_supabase()
    result = (
        supabase.table("companies")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/{company_id}", response_model=Company)
async def get_company(company_id: UUID):
    """Get a specific company."""
    supabase = get_supabase()

    result = (
        supabase.table("companies")
        .select("*")
        .eq("id", str(company_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Company not found")

    return result.data[0]


@router.get("/by-name/{company_name}")
async def get_company_by_name(company_name: str):
    """Get a company by name."""
    supabase = get_supabase()

    result = (
        supabase.table("companies")
        .select("*")
        .ilike("name", company_name)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Company not found")

    return result.data[0]


@router.patch("/{company_id}", response_model=Company)
async def update_company(company_id: UUID, company_update: CompanyUpdate):
    """Update a company."""
    supabase = get_supabase()

    update_data = company_update.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Convert nested models to dicts
    if "recent_news" in update_data:
        update_data["recent_news"] = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in update_data["recent_news"]
        ]
    if "key_people" in update_data:
        update_data["key_people"] = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in update_data["key_people"]
        ]

    result = (
        supabase.table("companies")
        .update(update_data)
        .eq("id", str(company_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Company not found")

    return result.data[0]


@router.delete("/{company_id}")
async def delete_company(company_id: UUID):
    """Delete a company."""
    supabase = get_supabase()

    result = (
        supabase.table("companies")
        .delete()
        .eq("id", str(company_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Company not found")

    return {"message": "Company deleted successfully"}


@router.post("/research")
async def research_company(
    company_name: str,
    website: str = None,
    job_title: str = None,
):
    """Research a company using the AI agent."""
    supabase = get_supabase()

    # Check if company already exists
    existing = (
        supabase.table("companies")
        .select("*")
        .ilike("name", company_name)
        .execute()
    )

    # Run research agent
    agent = CompanyResearcherAgent()
    research_result = await agent.execute({
        "company_name": company_name,
        "website": website or "",
        "job_title": job_title or "",
    })

    # Prepare data for database
    company_data = {
        "name": research_result.get("company_name", company_name),
        "website": research_result.get("website", website),
        "industry": research_result.get("industry"),
        "size": research_result.get("size"),
        "description": research_result.get("description"),
        "culture_notes": research_result.get("culture_notes"),
        "recent_news": research_result.get("recent_news", []),
        "key_people": research_result.get("key_people", []),
        "research_summary": research_result.get("research_summary"),
        "last_researched_at": datetime.utcnow().isoformat(),
    }

    # Convert Pydantic models to dicts
    if company_data.get("recent_news"):
        company_data["recent_news"] = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in company_data["recent_news"]
        ]
    if company_data.get("key_people"):
        company_data["key_people"] = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in company_data["key_people"]
        ]

    # Update or create company
    if existing.data:
        result = (
            supabase.table("companies")
            .update(company_data)
            .eq("id", existing.data[0]["id"])
            .execute()
        )
        company_id = existing.data[0]["id"]
    else:
        result = supabase.table("companies").insert(company_data).execute()
        company_id = result.data[0]["id"]

    return {
        "company_id": company_id,
        "research": research_result,
    }
