from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID

from app.models.job import Job, JobCreate, JobUpdate
from app.database import get_supabase

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=Job)
async def create_job(job: JobCreate):
    """Create a new job listing."""
    supabase = get_supabase()

    job_data = job.model_dump()

    # Convert UUIDs to strings
    job_data["profile_id"] = str(job_data["profile_id"])
    if job_data.get("company_id"):
        job_data["company_id"] = str(job_data["company_id"])

    result = supabase.table("jobs").insert(job_data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create job")

    return result.data[0]


@router.get("/", response_model=List[Job])
async def list_jobs(
    profile_id: Optional[UUID] = None,
    status: Optional[str] = None,
    company_name: Optional[str] = None,
):
    """List jobs with optional filters."""
    supabase = get_supabase()

    query = supabase.table("jobs").select("*")

    if profile_id:
        query = query.eq("profile_id", str(profile_id))
    if status:
        query = query.eq("status", status)
    if company_name:
        query = query.ilike("company_name", f"%{company_name}%")

    result = query.order("created_at", desc=True).execute()

    return result.data


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: UUID):
    """Get a specific job."""
    supabase = get_supabase()

    result = (
        supabase.table("jobs")
        .select("*")
        .eq("id", str(job_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    return result.data[0]


@router.patch("/{job_id}", response_model=Job)
async def update_job(job_id: UUID, job_update: JobUpdate):
    """Update a job."""
    supabase = get_supabase()

    update_data = job_update.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Convert UUIDs to strings
    if "company_id" in update_data and update_data["company_id"]:
        update_data["company_id"] = str(update_data["company_id"])

    result = (
        supabase.table("jobs")
        .update(update_data)
        .eq("id", str(job_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    return result.data[0]


@router.delete("/{job_id}")
async def delete_job(job_id: UUID):
    """Delete a job."""
    supabase = get_supabase()

    result = (
        supabase.table("jobs")
        .delete()
        .eq("id", str(job_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"message": "Job deleted successfully"}


@router.get("/{job_id}/full")
async def get_job_full_context(job_id: UUID):
    """Get job with company info and applications."""
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

    # Get company info if available
    company = None
    if job.get("company_id"):
        company_result = (
            supabase.table("companies")
            .select("*")
            .eq("id", job["company_id"])
            .execute()
        )
        if company_result.data:
            company = company_result.data[0]

    # Get applications
    applications_result = (
        supabase.table("applications")
        .select("*")
        .eq("job_id", str(job_id))
        .execute()
    )

    return {
        "job": job,
        "company": company,
        "applications": applications_result.data,
    }
