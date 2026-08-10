"""Gemini API module for ScrapeBadger SDK.

Sends prompts to the real gemini.google.com — not the Gemini API —
anonymously, and returns the answer as structured JSON including the web
sources Gemini cited.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Ask a question
        result = await client.gemini.ask.ask("best running shoes 2026")
        print(result.answer)
        for citation in result.citations:
            print(f"{citation.domain}: {citation.url}")

        # Brand visibility (AEO/GEO)
        brand = await client.gemini.brand.visibility(
            "best web scraping API",
            brand="ScrapeBadger",
            domain="scrapebadger.com",
            competitors=["Bright Data", "Apify"],
        )
        print(f"share of voice: {brand.share_of_voice_pct}%")
    ```
"""

from scrapebadger.gemini.ask import AskClient, WebSearchMode
from scrapebadger.gemini.brand import BrandClient
from scrapebadger.gemini.client import GeminiClient
from scrapebadger.gemini.models import (
    AskResponse,
    BrandVisibilityResponse,
    Citation,
    CompetitorMention,
    SearchResult,
)

__all__ = [
    # Sub-clients
    "AskClient",
    # Response envelopes
    "AskResponse",
    "BrandClient",
    "BrandVisibilityResponse",
    # Nested models
    "Citation",
    "CompetitorMention",
    # Client
    "GeminiClient",
    "SearchResult",
    "WebSearchMode",
]
