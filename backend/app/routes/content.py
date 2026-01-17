from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID

from app.models.application import (
    Application,
    ApplicationCreate,
    ApplicationUpdate,
)
from app.database import get_supabase
from app.agents.content_generator import ContentGeneratorAgent

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/applications", response_model=Application)
async def create_application(application: ApplicationCreate):
    """Create a new application."""
    supabase = get_supabase()

    app_data = application.model_dump()

    # Convert UUIDs to strings
    app_data["job_id"] = str(app_data["job_id"])
    app_data["profile_id"] = str(app_data["profile_id"])

    # Convert outreach_emails to dicts
    if app_data.get("outreach_emails"):
        app_data["outreach_emails"] = [
            email.model_dump() if hasattr(email, "model_dump") else email
            for email in app_data["outreach_emails"]
        ]

    result = supabase.table("applications").insert(app_data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create application")

    return result.data[0]


@router.get("/applications", response_model=List[Application])
async def list_applications(
    profile_id: Optional[UUID] = None,
    job_id: Optional[UUID] = None,
):
    """List applications with optional filters."""
    supabase = get_supabase()

    query = supabase.table("applications").select("*")

    if profile_id:
        query = query.eq("profile_id", str(profile_id))
    if job_id:
        query = query.eq("job_id", str(job_id))

    result = query.order("created_at", desc=True).execute()

    return result.data


@router.get("/applications/{application_id}", response_model=Application)
async def get_application(application_id: UUID):
    """Get a specific application."""
    supabase = get_supabase()

    result = (
        supabase.table("applications")
        .select("*")
        .eq("id", str(application_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Application not found")

    return result.data[0]


@router.patch("/applications/{application_id}", response_model=Application)
async def update_application(
    application_id: UUID,
    application_update: ApplicationUpdate,
):
    """Update an application."""
    supabase = get_supabase()

    update_data = application_update.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Convert outreach_emails to dicts
    if "outreach_emails" in update_data:
        update_data["outreach_emails"] = [
            email.model_dump() if hasattr(email, "model_dump") else email
            for email in update_data["outreach_emails"]
        ]

    result = (
        supabase.table("applications")
        .update(update_data)
        .eq("id", str(application_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Application not found")

    return result.data[0]


@router.delete("/applications/{application_id}")
async def delete_application(application_id: UUID):
    """Delete an application."""
    supabase = get_supabase()

    result = (
        supabase.table("applications")
        .delete()
        .eq("id", str(application_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Application not found")

    return {"message": "Application deleted successfully"}


@router.post("/generate")
async def generate_content(
    job_id: UUID,
    profile_id: UUID,
):
    """Generate cover letter and outreach emails for a job application."""
    supabase = get_supabase()

    # Get job
    job_result = (
        supabase.table("jobs")
        .select("*")
        .eq("id", str(job_id))
        .execute()
    )

    if not job_result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_result.data[0]

    # Get profile
    profile_result = (
        supabase.table("profiles")
        .select("*")
        .eq("id", str(profile_id))
        .execute()
    )

    if not profile_result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = profile_result.data[0]

    # Get STAR answers
    star_result = (
        supabase.table("star_answers")
        .select("*")
        .eq("profile_id", str(profile_id))
        .execute()
    )

    star_answers = star_result.data

    # Get company research if available
    company_research = {}
    if job.get("company_id"):
        company_result = (
            supabase.table("companies")
            .select("*")
            .eq("id", job["company_id"])
            .execute()
        )
        if company_result.data:
            company_research = company_result.data[0]

    # Run content generator agent
    agent = ContentGeneratorAgent()
    content_result = await agent.execute({
        "job": job,
        "profile": profile,
        "company_research": company_research,
        "star_answers": star_answers,
    })

    return content_result
