import httpx
from typing import List, Dict, Any, Optional
from app.config import get_settings

settings = get_settings()


class WebSearch:
    """Web search tool for finding information."""

    def __init__(self):
        self.tavily_api_key = settings.tavily_api_key
        self.has_tavily = bool(self.tavily_api_key)

    async def search(
        self, query: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the web for information.
        Falls back to mock results if no API key is configured.
        """
        if self.has_tavily:
            return await self._search_tavily(query, max_results)
        else:
            return self._mock_search_results(query, max_results)

    async def _search_tavily(
        self, query: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using Tavily API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_api_key,
                        "query": query,
                        "max_results": max_results,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                return [
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0),
                    }
                    for result in data.get("results", [])
                ]

        except Exception as e:
            print(f"Tavily search failed: {str(e)}")
            return self._mock_search_results(query, max_results)

    def _mock_search_results(
        self, query: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Return mock search results when no API is available."""
        return [
            {
                "title": f"Result for: {query}",
                "url": f"https://example.com/search?q={query}",
                "content": f"This is a mock search result for '{query}'. Configure TAVILY_API_KEY for real results.",
                "score": 0.0,
            }
        ]

    async def search_company(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for information about a specific company."""
        query = f"{company_name} company information"
        return await self.search(query, max_results=5)

    async def search_company_news(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for recent news about a company."""
        query = f"{company_name} company news recent"
        return await self.search(query, max_results=5)

    async def search_company_people(self, company_name: str, role: str = "") -> List[Dict[str, Any]]:
        """Search for key people at a company."""
        if role:
            query = f"{company_name} {role} LinkedIn"
        else:
            query = f"{company_name} leadership team executives"
        return await self.search(query, max_results=5)
