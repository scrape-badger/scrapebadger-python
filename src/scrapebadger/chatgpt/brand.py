"""ChatGPT Brand Visibility API client.

Answer-engine-optimisation (AEO/GEO) analysis: ask ChatGPT a prompt and get
back how a brand fares in the answer, next to its competitors.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.chatgpt.models import BrandVisibilityResponse

if TYPE_CHECKING:
    from collections.abc import Sequence

    from scrapebadger._internal.client import BaseClient
    from scrapebadger.chatgpt.ask import WebSearchMode


class BrandClient:
    """Client for the ChatGPT brand-visibility endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            result = await client.chatgpt.brand.visibility(
                "best web scraping API",
                brand="ScrapeBadger",
                domain="scrapebadger.com",
                competitors=["Bright Data", "Apify"],
            )
            print(result.mentioned, result.share_of_voice_pct)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize brand-visibility client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def visibility(
        self,
        prompt: str,
        *,
        brand: str,
        domain: str | None = None,
        aliases: Sequence[str] | None = None,
        competitors: Sequence[str] | None = None,
        country: str = "US",
        web_search: WebSearchMode = "force",
    ) -> BrandVisibilityResponse:
        """Analyse how a brand shows up in ChatGPT's answer to a prompt.

        Costs 25 credits.

        Args:
            prompt: The prompt to send. Maximum 4096 characters.
            brand: The brand name to look for in the answer.
            domain: The brand's domain, used to detect brand citations.
            aliases: Other spellings of the brand that should count as mentions.
            competitors: Competitor names to measure share of voice against.
            country: ISO-3166 alpha-2 egress country. Defaults to "US".
            web_search: Whether ChatGPT should browse — "auto", "force", or
                "off". Defaults to "force".

        Returns:
            The brand analysis plus the answer and its citations.

        Example:
            ```python
            result = await client.chatgpt.brand.visibility(
                "which proxy provider should I use?",
                brand="ScrapeBadger",
                domain="scrapebadger.com",
                aliases=["Scrape Badger"],
                competitors=["Bright Data", "Oxylabs"],
                country="DE",
            )
            print(f"position score: {result.position_score}")
            for competitor in result.competitors:
                print(f"{competitor.name}: {competitor.mention_count}")
            ```
        """
        response = await self._client.get(
            "/v1/chatgpt/brand-visibility",
            params={
                "prompt": prompt,
                "brand": brand,
                "domain": domain,
                "aliases": ",".join(aliases) if aliases else None,
                "competitors": ",".join(competitors) if competitors else None,
                "country": country,
                "web_search": web_search,
            },
        )
        return BrandVisibilityResponse.model_validate(response)
