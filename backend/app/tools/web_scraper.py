import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import asyncio


class WebScraper:
    """Scrape and extract information from websites."""

    def __init__(self):
        self.timeout = 30.0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a URL."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Extract text
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = "\n".join(chunk for chunk in chunks if chunk)

                # Extract metadata
                title = soup.title.string if soup.title else ""
                meta_description = ""
                meta_tag = soup.find("meta", attrs={"name": "description"})
                if meta_tag:
                    meta_description = meta_tag.get("content", "")

                return {
                    "url": url,
                    "title": title,
                    "description": meta_description,
                    "content": text[:10000],  # Limit content size
                    "success": True,
                }

        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False,
            }

    async def scrape_company_website(self, website_url: str) -> Dict[str, Any]:
        """Scrape company website and extract relevant information."""
        result = await self.scrape_url(website_url)

        if not result["success"]:
            return result

        # Try to find about page, careers page, etc.
        additional_pages = {}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    website_url, headers=self.headers, follow_redirects=True
                )
                soup = BeautifulSoup(response.text, "html.parser")

                # Look for about and careers links
                for link in soup.find_all("a", href=True):
                    link_text = link.get_text().lower()
                    href = link["href"]

                    if "about" in link_text and "about_page" not in additional_pages:
                        about_url = self._normalize_url(website_url, href)
                        about_result = await self.scrape_url(about_url)
                        if about_result["success"]:
                            additional_pages["about_page"] = about_result

                    if "career" in link_text and "careers_page" not in additional_pages:
                        careers_url = self._normalize_url(website_url, href)
                        careers_result = await self.scrape_url(careers_url)
                        if careers_result["success"]:
                            additional_pages["careers_page"] = careers_result

        except Exception:
            pass  # Continue even if additional pages fail

        result["additional_pages"] = additional_pages
        return result

    def _normalize_url(self, base_url: str, href: str) -> str:
        """Normalize relative URLs."""
        if href.startswith("http"):
            return href
        elif href.startswith("/"):
            from urllib.parse import urlparse

            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{href}"
        else:
            return f"{base_url.rstrip('/')}/{href}"
