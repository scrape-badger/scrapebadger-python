"""DuckDuckGo Reference / Instant Answer API client.

Search-box autocomplete, the zero-click Instant Answer, and the supported
region list.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.duckduckgo.models import (
    AutocompleteResponse,
    InstantAnswerResponse,
    RegionsResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for DuckDuckGo autocomplete, instant answer, and region endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            suggestions = await client.duckduckgo.reference.autocomplete("pyth")
            answer = await client.duckduckgo.reference.instant("pi")
            regions = await client.duckduckgo.reference.regions()
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def autocomplete(
        self,
        query: str,
        *,
        region: str = "wt-wt",
    ) -> AutocompleteResponse:
        """DuckDuckGo search-box suggestions.

        Args:
            query: Partial search term, e.g. ``"pyth"``.
            region: Region code. Default ``"wt-wt"``.

        Returns:
            AutocompleteResponse with the suggestion strings.

        Example:
            ```python
            result = await client.duckduckgo.reference.autocomplete("pyth")
            for s in result.suggestions:
                print(s)
            ```
        """
        params: dict[str, Any] = {"query": query, "region": region}
        response = await self._client.get("/v1/duckduckgo/autocomplete", params=params)
        return AutocompleteResponse.model_validate(response)

    async def instant(self, query: str) -> InstantAnswerResponse:
        """DuckDuckGo Instant Answer (zero-click) for a query.

        Args:
            query: Search term, e.g. ``"pi"`` or ``"define serendipity"``.

        Returns:
            InstantAnswerResponse with the abstract, answer, definition, and
            related topics.

        Example:
            ```python
            result = await client.duckduckgo.reference.instant("pi")
            print(result.answer, result.abstract_source)
            ```
        """
        params: dict[str, Any] = {"query": query}
        response = await self._client.get("/v1/duckduckgo/instant", params=params)
        return InstantAnswerResponse.model_validate(response)

    async def regions(self) -> RegionsResponse:
        """Get all supported DuckDuckGo regions.

        Returns:
            RegionsResponse with the region codes and names.

        Example:
            ```python
            result = await client.duckduckgo.reference.regions()
            for r in result.regions:
                print(f"{r.code}: {r.name}")
            ```
        """
        response = await self._client.get("/v1/duckduckgo/regions")
        return RegionsResponse.model_validate(response)
