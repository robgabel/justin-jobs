from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from uuid import UUID
import json

from app.models.profile import (
    Profile,
    ProfileCreate,
    ProfileUpdate,
    STARAnswer,
    STARAnswerCreate,
)
from app.database import get_supabase
from app.tools.resume_parser import ResumeParser
from app.agents.profile_builder import ProfileBuilderAgent

router = APIRouter(prefix="/profiles", tags=["profiles"])
resume_parser = ResumeParser()


@router.post("/", response_model=Profile)
async def create_profile(profile: ProfileCreate):
    """Create a new profile."""
    supabase = get_supabase()

    # Convert Pydantic model to dict
    profile_data = profile.model_dump()

    # Convert career_goals to JSON if present
    if profile_data.get("career_goals"):
        profile_data["career_goals"] = profile_data["career_goals"]

    result = supabase.table("profiles").insert(profile_data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create profile")

    return result.data[0]


@router.get("/", response_model=List[Profile])
async def list_profiles():
    """List all profiles."""
    supabase = get_supabase()
    result = supabase.table("profiles").select("*").execute()
    return result.data


@router.get("/{profile_id}", response_model=Profile)
async def get_profile(profile_id: UUID):
    """Get a specific profile."""
    supabase = get_supabase()
    result = (
        supabase.table("profiles")
        .select("*")
        .eq("id", str(profile_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return result.data[0]


@router.patch("/{profile_id}", response_model=Profile)
async def update_profile(profile_id: UUID, profile_update: ProfileUpdate):
    """Update a profile."""
    supabase = get_supabase()

    # Only include non-None fields
    update_data = profile_update.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = (
        supabase.table("profiles")
        .update(update_data)
        .eq("id", str(profile_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return result.data[0]


@router.delete("/{profile_id}")
async def delete_profile(profile_id: UUID):
    """Delete a profile."""
    supabase = get_supabase()

    result = (
        supabase.table("profiles")
        .delete()
        .eq("id", str(profile_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"message": "Profile deleted successfully"}


@router.post("/{profile_id}/upload-resume")
async def upload_resume(
    profile_id: UUID,
    file: UploadFile = File(...),
):
    """Upload and parse a resume for a profile."""
    supabase = get_supabase()

    # Read file content
    content = await file.read()

    # Parse based on file type
    try:
        if file.filename.endswith(".pdf"):
            resume_text = resume_parser.parse_pdf(content)
        elif file.filename.endswith(".txt"):
            resume_text = resume_parser.parse_text(content)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Use PDF or TXT.",
            )

        # Extract structured info
        resume_info = resume_parser.extract_resume_info(resume_text)

        # Update profile with resume text
        result = (
            supabase.table("profiles")
            .update({"resume_text": resume_text})
            .eq("id", str(profile_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {
            "message": "Resume uploaded successfully",
            "resume_info": resume_info,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{profile_id}/build")
async def build_profile(
    profile_id: UUID,
    resume_text: Optional[str] = None,
    user_response: Optional[str] = None,
):
    """Use AI agent to build/enhance profile through Q&A."""
    supabase = get_supabase()

    # Get existing profile
    profile_result = (
        supabase.table("profiles")
        .select("*")
        .eq("id", str(profile_id))
        .execute()
    )

    if not profile_result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    existing_profile = profile_result.data[0]

    # Run profile builder agent
    agent = ProfileBuilderAgent()

    input_data = {
        "resume_text": resume_text,
        "existing_profile": existing_profile,
        "user_response": user_response,
    }

    result = await agent.execute(input_data)

    # If there are profile updates, apply them
    if result.get("profile_updates"):
        supabase.table("profiles").update(
            result["profile_updates"]
        ).eq("id", str(profile_id)).execute()

    return result


# STAR Answers endpoints
@router.post("/{profile_id}/star-answers", response_model=STARAnswer)
async def create_star_answer(profile_id: UUID, star_answer: STARAnswerCreate):
    """Add a STAR answer to a profile."""
    supabase = get_supabase()

    star_data = star_answer.model_dump()
    star_data["profile_id"] = str(profile_id)

    result = supabase.table("star_answers").insert(star_data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create STAR answer")

    return result.data[0]


@router.get("/{profile_id}/star-answers", response_model=List[STARAnswer])
async def list_star_answers(profile_id: UUID):
    """List all STAR answers for a profile."""
    supabase = get_supabase()

    result = (
        supabase.table("star_answers")
        .select("*")
        .eq("profile_id", str(profile_id))
        .execute()
    )

    return result.data


@router.delete("/star-answers/{star_id}")
async def delete_star_answer(star_id: UUID):
    """Delete a STAR answer."""
    supabase = get_supabase()

    result = (
        supabase.table("star_answers")
        .delete()
        .eq("id", str(star_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="STAR answer not found")

    return {"message": "STAR answer deleted successfully"}
