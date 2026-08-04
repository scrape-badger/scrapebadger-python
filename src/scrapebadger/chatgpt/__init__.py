"""ChatGPT API module for ScrapeBadger SDK.

Sends prompts to the real chatgpt.com — not the OpenAI API — anonymously, and
returns the answer as structured JSON including the web sources ChatGPT cited.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        # Ask a question
        result = await client.chatgpt.ask.ask("best running shoes 2026")
        print(result.answer)
        for citation in result.citations:
            print(f"{citation.domain}: {citation.url}")

        # Brand visibility (AEO/GEO)
        brand = await client.chatgpt.brand.visibility(
            "best web scraping API",
            brand="ScrapeBadger",
            domain="scrapebadger.com",
            competitors=["Bright Data", "Apify"],
        )
        print(f"share of voice: {brand.share_of_voice_pct}%")

        # Available models
        models = await client.chatgpt.reference.models()
        for model in models.models:
            print(model.slug)
    ```
"""

from scrapebadger.chatgpt.ask import AskClient, WebSearchMode
from scrapebadger.chatgpt.brand import BrandClient
from scrapebadger.chatgpt.client import ChatGPTClient
from scrapebadger.chatgpt.models import (
    AskResponse,
    BrandVisibilityResponse,
    ChatGPTModel,
    Citation,
    CompetitorMention,
    ModelsResponse,
    SearchResult,
)
from scrapebadger.chatgpt.reference import ReferenceClient

__all__ = [
    # Sub-clients
    "AskClient",
    # Response envelopes
    "AskResponse",
    "BrandClient",
    "BrandVisibilityResponse",
    # Client
    "ChatGPTClient",
    # Reference models
    "ChatGPTModel",
    # Nested models
    "Citation",
    "CompetitorMention",
    "ModelsResponse",
    "ReferenceClient",
    "SearchResult",
    "WebSearchMode",
]
