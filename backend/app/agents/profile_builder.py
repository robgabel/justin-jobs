from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.tools.resume_parser import ResumeParser


class ProfileBuilderAgent(BaseAgent):
    """Agent for building and enriching user profiles through interactive Q&A."""

    def __init__(self):
        super().__init__()
        self.resume_parser = ResumeParser()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build or enrich a user profile.

        Args:
            input_data: {
                "resume_text": str (optional),
                "existing_profile": dict (optional),
                "user_response": str (optional) - for follow-up questions
            }

        Returns:
            {
                "questions": List[str] - questions to ask the user,
                "profile_updates": dict - suggested profile updates,
                "completed": bool - whether profile building is complete
            }
        """
        resume_text = input_data.get("resume_text", "")
        existing_profile = input_data.get("existing_profile", {})
        user_response = input_data.get("user_response", "")

        # If this is the first interaction with a resume
        if resume_text and not self.conversation_history:
            return await self._initial_profile_extraction(resume_text)

        # If user is responding to questions
        if user_response:
            return await self._process_user_response(user_response, existing_profile)

        # Default: start profile building
        return await self._start_profile_building(existing_profile)

    async def _initial_profile_extraction(
        self, resume_text: str
    ) -> Dict[str, Any]:
        """Extract initial information from resume."""
        system_prompt = """You are a career advisor assistant helping to build a comprehensive profile
        for job seekers. Extract key information from their resume and identify gaps that need to be filled
        through conversation."""

        prompt = f"""Analyze this resume and extract the following information:
1. Name
2. Email
3. Key skills and technologies
4. Notable projects or experiences
5. Education
6. Career interests (if mentioned)

Resume:
{resume_text}

Return your analysis in a structured format, and suggest 3-5 questions to ask the user to build
a more complete profile (focus on career goals, interests, strengths, weaknesses, and specific
experiences that would make good STAR stories)."""

        response = await self.generate_response(prompt, system=system_prompt)

        return {
            "analysis": response,
            "questions": self._extract_questions_from_response(response),
            "profile_updates": {},
            "completed": False,
        }

    async def _start_profile_building(
        self, existing_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start profile building process."""
        profile_summary = self._summarize_profile(existing_profile)

        prompt = f"""Current profile information:
{profile_summary}

Generate 3-5 thoughtful questions to help build a comprehensive profile for this job seeker.
Focus on:
- Career goals (short-term and long-term)
- Preferred industries, roles, and locations
- Key strengths and areas for improvement
- Specific experiences that demonstrate their skills (for STAR stories)
- What they're looking for in their next opportunity

Make the questions conversational and specific."""

        system_prompt = """You are a friendly career advisor building a profile to help someone
        find their ideal job opportunity."""

        response = await self.generate_response(prompt, system=system_prompt)

        return {
            "questions": self._extract_questions_from_response(response),
            "profile_updates": {},
            "completed": False,
        }

    async def _process_user_response(
        self, user_response: str, existing_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user's response to questions."""
        profile_summary = self._summarize_profile(existing_profile)

        prompt = f"""Current profile:
{profile_summary}

User's response to previous questions:
{user_response}

Based on this response:
1. Extract any new information to add to their profile (career goals, interests, strengths, weaknesses, experiences)
2. Determine if we have enough information for a complete profile
3. If not complete, generate 2-3 more questions to fill gaps

Respond in a structured format."""

        system_prompt = """You are a career advisor analyzing responses to build a complete profile."""

        response = await self.generate_response(prompt, system=system_prompt)

        # Parse response to extract profile updates
        profile_updates = self._extract_profile_updates(response, user_response)

        # Check if profile is complete
        completed = self._is_profile_complete(existing_profile, profile_updates)

        return {
            "analysis": response,
            "questions": [] if completed else self._extract_questions_from_response(response),
            "profile_updates": profile_updates,
            "completed": completed,
        }

    def _summarize_profile(self, profile: Dict[str, Any]) -> str:
        """Create a text summary of the profile."""
        if not profile:
            return "No profile information yet."

        parts = []
        if profile.get("name"):
            parts.append(f"Name: {profile['name']}")
        if profile.get("email"):
            parts.append(f"Email: {profile['email']}")
        if profile.get("career_goals"):
            parts.append(f"Career Goals: {profile['career_goals']}")
        if profile.get("interests"):
            parts.append(f"Interests: {', '.join(profile['interests'])}")
        if profile.get("strengths"):
            parts.append(f"Strengths: {', '.join(profile['strengths'])}")
        if profile.get("weaknesses"):
            parts.append(f"Weaknesses: {', '.join(profile['weaknesses'])}")

        return "\n".join(parts) if parts else "Minimal profile information."

    def _extract_questions_from_response(self, response: str) -> List[str]:
        """Extract questions from Claude's response."""
        questions = []
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            # Look for lines that end with ? or start with numbers
            if "?" in line:
                # Remove common prefixes
                question = line
                for prefix in ["Question:", "Q:", "-", "*", "1.", "2.", "3.", "4.", "5."]:
                    if question.startswith(prefix):
                        question = question[len(prefix):].strip()
                if question and len(question) > 10:
                    questions.append(question)

        return questions[:5]  # Limit to 5 questions

    def _extract_profile_updates(
        self, analysis: str, user_response: str
    ) -> Dict[str, Any]:
        """Extract structured profile updates from the analysis."""
        # Simple keyword-based extraction
        # In production, this would use Claude with structured output
        updates = {}

        response_lower = user_response.lower()

        # Extract interests
        if "interest" in response_lower or "passionate" in response_lower:
            updates["interests"] = [user_response[:200]]

        # Extract career goals
        if "goal" in response_lower or "want to" in response_lower:
            updates["career_goals"] = {"notes": user_response[:300]}

        return updates

    def _is_profile_complete(
        self, existing_profile: Dict[str, Any], new_updates: Dict[str, Any]
    ) -> bool:
        """Check if profile has enough information."""
        # Merge existing with new
        combined = {**existing_profile, **new_updates}

        # Check for essential fields
        has_name = bool(combined.get("name"))
        has_goals = bool(combined.get("career_goals"))
        has_interests = bool(combined.get("interests"))
        has_strengths = bool(combined.get("strengths"))

        # Profile is complete if it has at least 3 of 4 essential fields
        score = sum([has_name, has_goals, has_interests, has_strengths])
        return score >= 3
