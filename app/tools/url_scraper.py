from pydantic import HttpUrl
import httpx
from bs4 import BeautifulSoup

from app.tools.base import BaseTool, ToolInput, ToolOutput
from app.core.exceptions import ToolError
from app.config import get_settings


class URLInput(ToolInput):
    url: HttpUrl


class URLScraperTool(BaseTool):
    """
    Fetches an article URL and extracts clean readable text.
    Strips scripts, styles, navigation, and boilerplate.
    """

    name        = "url_scraper"
    description = "Fetch and extract article text from a URL."

    async def execute(self, tool_input: ToolInput) -> ToolOutput:
        assert isinstance(tool_input, URLInput)
        settings = get_settings()

        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout_seconds,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
            },

            ) as client:
                response = await client.get(str(tool_input.url))
                response.raise_for_status()

        except httpx.TimeoutException as e:
            raise ToolError(f"Request timed out fetching: {tool_input.url}") from e
        except httpx.HTTPStatusError as e:
            raise ToolError(
                f"HTTP {e.response.status_code} fetching: {tool_input.url}"
            ) from e
        except httpx.RequestError as e:
            raise ToolError(f"Could not reach: {tool_input.url}") from e

        text = self._extract_text(response.text)
        text = self._truncate(text, settings.max_content_tokens)

        return ToolOutput(
            content=text,
            metadata={"url": str(tool_input.url), "chars": len(text)},
        )

    def _extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)

    def _truncate(self, text: str, max_tokens: int) -> str:
        # Rough approximation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        if len(text) > max_chars:
            return text[:max_chars]
        return text