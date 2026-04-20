"""Google Autocomplete client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AutocompleteClient:
    """Client for Google Autocomplete (search suggestions).

    Returns up to 10 suggestions. Suggestions that resolve to
    Knowledge-Graph entities (companies, people, movies, stocks, local
    businesses, …) additionally carry ``entity_name`` and ``thumbnail``
    URL — the same enrichment Google's own search-box surfaces.

    Example:
        ```python
        suggestions = await client.google.autocomplete.get("apple")
        for s in suggestions["suggestions"]:
            print(s["value"], s.get("entity_name"), s.get("thumbnail"))
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def get(
        self,
        q: str,
        *,
        hl: str = "en",
        gl: str = "us",
    ) -> dict[str, Any]:
        """Get Google autocomplete suggestions for a query.

        Args:
            q: Query prefix to autocomplete.
            hl: Language code (e.g. ``"en"``).
            gl: Country code (e.g. ``"us"``).
        """
        params: dict[str, Any] = {"q": q, "hl": hl, "gl": gl}
        return await self._client.get("/v1/google/autocomplete", params=params)
