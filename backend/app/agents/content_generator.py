from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.models.application import OutreachEmail


class ContentGeneratorAgent(BaseAgent):
    """Agent for generating cover letters and outreach emails."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate application content (cover letter and outreach emails).

        Args:
            input_data: {
                "job": {
                    "title": str,
                    "company_name": str,
                    "description": str,
                    "url": str
                },
                "profile": {
                    "name": str,
                    "resume_text": str,
                    "career_goals": dict,
                    "interests": list,
                    "strengths": list
                },
                "company_research": {
                    "research_summary": str,
                    "key_people": list
                } (optional),
                "star_answers": list (optional)
            }

        Returns:
            {
                "cover_letter": str,
                "outreach_emails": List[OutreachEmail],
                "application_strategy": str
            }
        """
        job = input_data["job"]
        profile = input_data["profile"]
        company_research = input_data.get("company_research", {})
        star_answers = input_data.get("star_answers", [])

        # Generate cover letter
        cover_letter = await self._generate_cover_letter(
            job, profile, company_research, star_answers
        )

        # Generate outreach emails
        outreach_emails = await self._generate_outreach_emails(
            job, profile, company_research
        )

        # Generate application strategy
        strategy = await self._generate_application_strategy(
            job, profile, company_research
        )

        return {
            "cover_letter": cover_letter,
            "outreach_emails": outreach_emails,
            "application_strategy": strategy,
        }

    async def _generate_cover_letter(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any],
        company_research: Dict[str, Any],
        star_answers: List[Dict[str, Any]],
    ) -> str:
        """Generate a personalized cover letter."""
        # Select relevant STAR answers
        relevant_stars = self._select_relevant_star_answers(
            job.get("description", ""), star_answers
        )

        star_context = self._format_star_answers(relevant_stars)

        prompt = f"""Write a compelling cover letter for this job application.

Job Information:
- Title: {job['title']}
- Company: {job['company_name']}
- Description: {job.get('description', 'N/A')[:1000]}

Candidate Profile:
- Name: {profile.get('name', 'Candidate')}
- Resume Summary: {profile.get('resume_text', 'N/A')[:1000]}
- Career Goals: {profile.get('career_goals', {})}
- Key Strengths: {', '.join(profile.get('strengths', []))}
- Interests: {', '.join(profile.get('interests', []))}

Company Research:
{company_research.get('research_summary', 'N/A')[:500]}

Relevant Experience (STAR format):
{star_context}

Instructions:
1. Keep it to 3-4 paragraphs
2. Show genuine interest in the company and role
3. Highlight relevant experience and skills from the resume
4. Reference specific aspects of the company or their work
5. Be authentic and enthusiastic but professional
6. Use specific examples from the STAR answers when relevant
7. Explain why this role aligns with career goals

Write the cover letter now."""

        system_prompt = """You are an expert career advisor who writes compelling, personalized
        cover letters that help candidates stand out. You write in a professional but authentic voice,
        avoiding clichés and generic statements."""

        cover_letter = await self.generate_response(
            prompt, system=system_prompt, max_tokens=2048
        )

        return cover_letter

    async def _generate_outreach_emails(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any],
        company_research: Dict[str, Any],
    ) -> List[OutreachEmail]:
        """Generate outreach email templates."""
        key_people = company_research.get("key_people", [])

        outreach_emails = []

        # Generate recruiter outreach email
        recruiter_email = await self._generate_recruiter_email(job, profile)
        outreach_emails.append(recruiter_email)

        # Generate hiring manager outreach email
        hiring_manager_email = await self._generate_hiring_manager_email(
            job, profile, company_research
        )
        outreach_emails.append(hiring_manager_email)

        # If we have key people, generate connection emails
        if key_people:
            for person in key_people[:2]:  # Limit to 2
                connection_email = await self._generate_connection_email(
                    job, profile, person
                )
                outreach_emails.append(connection_email)

        return outreach_emails

    async def _generate_recruiter_email(
        self, job: Dict[str, Any], profile: Dict[str, Any]
    ) -> OutreachEmail:
        """Generate email for reaching out to recruiter."""
        prompt = f"""Write a short, professional email to a recruiter about this position:

Job: {job['title']} at {job['company_name']}

Candidate: {profile.get('name', 'Candidate')}
Background: {profile.get('resume_text', 'N/A')[:500]}

Instructions:
1. Keep it brief (3-4 sentences)
2. Express interest in the role
3. Highlight one key qualification
4. Request a conversation
5. Include a clear subject line

Format as:
Subject: [subject line]
Body: [email body]"""

        response = await self.generate_response(prompt, max_tokens=512)

        # Parse subject and body
        subject, body = self._parse_email_response(response)

        return OutreachEmail(
            recipient="Recruiter",
            subject=subject,
            body=body,
            purpose="Initial outreach to recruiter about the position",
        )

    async def _generate_hiring_manager_email(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any],
        company_research: Dict[str, Any],
    ) -> OutreachEmail:
        """Generate email for reaching out to hiring manager."""
        prompt = f"""Write a compelling email to the hiring manager for this position:

Job: {job['title']} at {job['company_name']}

Candidate: {profile.get('name', 'Candidate')}
Background: {profile.get('resume_text', 'N/A')[:500]}

Company Context: {company_research.get('research_summary', 'N/A')[:300]}

Instructions:
1. Keep it concise (4-5 sentences)
2. Show you've researched the company
3. Explain why you're interested and qualified
4. Mention specific relevant experience
5. Request a conversation
6. Include a clear subject line

Format as:
Subject: [subject line]
Body: [email body]"""

        response = await self.generate_response(prompt, max_tokens=768)

        subject, body = self._parse_email_response(response)

        return OutreachEmail(
            recipient="Hiring Manager",
            subject=subject,
            body=body,
            purpose="Direct outreach to hiring manager",
        )

    async def _generate_connection_email(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any],
        person: Dict[str, Any],
    ) -> OutreachEmail:
        """Generate email for networking/connection."""
        prompt = f"""Write a friendly networking email to connect with someone at the target company:

Target Person: {person.get('name', 'Employee')}, {person.get('title', 'Employee')}
Company: {job['company_name']}
Your Background: {profile.get('resume_text', 'N/A')[:300]}

Instructions:
1. Keep it very brief (3 sentences)
2. Mention shared interests or background
3. Ask for a brief informational chat
4. Don't directly ask for a referral
5. Be genuine and respectful of their time

Format as:
Subject: [subject line]
Body: [email body]"""

        response = await self.generate_response(prompt, max_tokens=512)

        subject, body = self._parse_email_response(response)

        return OutreachEmail(
            recipient=f"{person.get('name', 'Employee')} ({person.get('title', '')})",
            subject=subject,
            body=body,
            purpose="Networking and informational interview",
        )

    async def _generate_application_strategy(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any],
        company_research: Dict[str, Any],
    ) -> str:
        """Generate a strategic plan for the application."""
        prompt = f"""Create a strategic action plan for applying to this position:

Job: {job['title']} at {job['company_name']}
Candidate Background: {profile.get('resume_text', 'N/A')[:500]}
Company Info: {company_research.get('research_summary', 'N/A')[:300]}

Provide:
1. Timeline (when to apply, when to follow up)
2. Who to reach out to and in what order
3. Key points to emphasize in application
4. Potential connections or referrals to seek
5. Interview prep recommendations

Keep it concise and actionable."""

        strategy = await self.generate_response(prompt, max_tokens=1024)

        return strategy

    def _select_relevant_star_answers(
        self, job_description: str, star_answers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Select STAR answers most relevant to the job."""
        # Simple implementation - in production, use embeddings/semantic search
        if not star_answers:
            return []

        # For now, return up to 3 STAR answers
        return star_answers[:3]

    def _format_star_answers(self, star_answers: List[Dict[str, Any]]) -> str:
        """Format STAR answers for inclusion in prompt."""
        if not star_answers:
            return "No specific examples provided."

        formatted = []
        for i, star in enumerate(star_answers, 1):
            formatted.append(
                f"{i}. Situation: {star.get('situation', 'N/A')}\n"
                f"   Task: {star.get('task', 'N/A')}\n"
                f"   Action: {star.get('action', 'N/A')}\n"
                f"   Result: {star.get('result', 'N/A')}"
            )

        return "\n\n".join(formatted)

    def _parse_email_response(self, response: str) -> tuple[str, str]:
        """Parse email response into subject and body."""
        lines = response.strip().split("\n")

        subject = ""
        body_lines = []
        in_body = False

        for line in lines:
            if line.strip().lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
            elif line.strip().lower().startswith("body:"):
                in_body = True
                body_text = line.split(":", 1)[1].strip()
                if body_text:
                    body_lines.append(body_text)
            elif in_body:
                body_lines.append(line)
            elif not subject and not in_body:
                # If we haven't found subject/body markers, first line might be subject
                if not subject and ":" not in line:
                    subject = line.strip()
                else:
                    body_lines.append(line)

        body = "\n".join(body_lines).strip()

        if not subject:
            subject = "Regarding the position at the company"

        return subject, body
