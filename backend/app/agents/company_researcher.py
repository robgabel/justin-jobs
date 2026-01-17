from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.tools.web_search import WebSearch
from app.tools.web_scraper import WebScraper
from app.models.company import NewsItem, KeyPerson


class CompanyResearcherAgent(BaseAgent):
    """Agent for researching companies through web search and scraping."""

    def __init__(self):
        super().__init__()
        self.web_search = WebSearch()
        self.web_scraper = WebScraper()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research a company and compile comprehensive information.

        Args:
            input_data: {
                "company_name": str,
                "website": str (optional),
                "job_title": str (optional) - for context
            }

        Returns:
            {
                "company_name": str,
                "website": str,
                "description": str,
                "industry": str,
                "size": str,
                "culture_notes": str,
                "recent_news": List[NewsItem],
                "key_people": List[KeyPerson],
                "research_summary": str
            }
        """
        company_name = input_data["company_name"]
        website = input_data.get("website", "")
        job_title = input_data.get("job_title", "")

        results = {}

        # 1. Search for company information
        company_info = await self._search_company_info(company_name)
        results.update(company_info)

        # 2. Scrape company website if available
        if website:
            website_info = await self._scrape_company_website(website)
            results.update(website_info)

        # 3. Search for recent news
        news = await self._search_recent_news(company_name)
        results["recent_news"] = news

        # 4. Search for key people
        key_people = await self._search_key_people(company_name)
        results["key_people"] = key_people

        # 5. Generate comprehensive research summary
        summary = await self._generate_research_summary(
            company_name, results, job_title
        )
        results["research_summary"] = summary

        return results

    async def _search_company_info(self, company_name: str) -> Dict[str, Any]:
        """Search for general company information."""
        search_results = await self.web_search.search_company(company_name)

        # Compile search results
        search_text = "\n\n".join(
            [
                f"Source: {r['title']}\n{r['content']}"
                for r in search_results[:3]
            ]
        )

        prompt = f"""Based on these search results about {company_name}, extract:
1. Company description (2-3 sentences)
2. Industry
3. Company size (approximate employee count if available)
4. Website URL if mentioned

Search results:
{search_text}

Provide the information in a structured format."""

        system_prompt = "You are a research assistant extracting company information from web search results."

        response = await self.generate_response(prompt, system=system_prompt)

        # Parse response (simplified - could use structured output)
        return {
            "company_name": company_name,
            "description": self._extract_section(response, "description"),
            "industry": self._extract_section(response, "industry"),
            "size": self._extract_section(response, "size"),
            "website": self._extract_section(response, "website"),
        }

    async def _scrape_company_website(self, website: str) -> Dict[str, Any]:
        """Scrape company website for additional information."""
        scrape_result = await self.web_scraper.scrape_company_website(website)

        if not scrape_result.get("success"):
            return {"culture_notes": "Unable to scrape website"}

        # Analyze scraped content
        content = scrape_result.get("content", "")
        about_content = scrape_result.get("additional_pages", {}).get("about_page", {}).get("content", "")

        combined_content = f"{content}\n\n{about_content}"[:5000]

        prompt = f"""Analyze this content from the company website and extract:
1. Company culture and values
2. Mission statement
3. What makes them unique
4. Work environment insights

Website content:
{combined_content}

Summarize in 2-3 paragraphs."""

        system_prompt = "You are analyzing company website content to understand their culture and values."

        response = await self.generate_response(prompt, system=system_prompt, max_tokens=1024)

        return {"culture_notes": response}

    async def _search_recent_news(self, company_name: str) -> List[NewsItem]:
        """Search for recent news about the company."""
        news_results = await self.web_search.search_company_news(company_name)

        news_items = []
        for result in news_results[:5]:
            news_items.append(
                NewsItem(
                    title=result["title"],
                    url=result["url"],
                    summary=result["content"][:200],
                )
            )

        return news_items

    async def _search_key_people(self, company_name: str) -> List[KeyPerson]:
        """Search for key people at the company."""
        people_results = await self.web_search.search_company_people(company_name)

        # Use Claude to extract structured information
        results_text = "\n\n".join(
            [f"{r['title']}\n{r['content']}" for r in people_results[:3]]
        )

        prompt = f"""From these search results, identify key people at {company_name}.
For each person, extract:
- Name
- Title/Role
- LinkedIn URL if available

Search results:
{results_text}

List up to 5 key people."""

        response = await self.generate_response(prompt, max_tokens=1024)

        # Parse response (simplified)
        key_people = []
        lines = response.split("\n")
        current_person = {}

        for line in lines:
            line = line.strip()
            if "name:" in line.lower():
                if current_person:
                    key_people.append(KeyPerson(**current_person))
                current_person = {"name": line.split(":", 1)[1].strip()}
            elif "title:" in line.lower() or "role:" in line.lower():
                current_person["title"] = line.split(":", 1)[1].strip()
            elif "linkedin:" in line.lower():
                current_person["linkedin_url"] = line.split(":", 1)[1].strip()

        if current_person and "name" in current_person and "title" in current_person:
            key_people.append(KeyPerson(**current_person))

        return key_people[:5]

    async def _generate_research_summary(
        self, company_name: str, research_data: Dict[str, Any], job_title: str
    ) -> str:
        """Generate a comprehensive research summary."""
        context = f"""Company: {company_name}
Description: {research_data.get('description', 'N/A')}
Industry: {research_data.get('industry', 'N/A')}
Size: {research_data.get('size', 'N/A')}

Culture Notes:
{research_data.get('culture_notes', 'N/A')}

Recent News ({len(research_data.get('recent_news', []))} items):
{self._format_news_items(research_data.get('recent_news', []))}

Key People ({len(research_data.get('key_people', []))} identified):
{self._format_key_people(research_data.get('key_people', []))}
"""

        if job_title:
            context += f"\nJob Title Context: {job_title}"

        prompt = f"""Based on this research about {company_name}, create a comprehensive summary
that would be useful for someone applying for a job there.

Include:
1. Company overview and what they do
2. Culture and values
3. Recent developments and news
4. Key people to be aware of
5. Why this might be a good opportunity
{f"6. How this relates to the {job_title} role" if job_title else ""}

Research Data:
{context}

Create a well-organized summary (3-4 paragraphs)."""

        system_prompt = """You are a career advisor summarizing company research to help a job seeker
        understand if this is a good opportunity and how to tailor their application."""

        summary = await self.generate_response(prompt, system=system_prompt, max_tokens=2048)

        return summary

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from formatted text."""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if section_name.lower() in line.lower() and ":" in line:
                return line.split(":", 1)[1].strip()
        return ""

    def _format_news_items(self, news_items: List[NewsItem]) -> str:
        """Format news items for display."""
        if not news_items:
            return "No recent news found"

        return "\n".join([f"- {item.title}" for item in news_items[:3]])

    def _format_key_people(self, key_people: List[KeyPerson]) -> str:
        """Format key people for display."""
        if not key_people:
            return "No key people identified"

        return "\n".join([f"- {p.name}, {p.title}" for p in key_people])
