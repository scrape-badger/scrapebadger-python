"""Google Autocomplete client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AutocompleteClient:
    """Client for Google Autocomplete (search suggestions).

    Example:
        ```python
        suggestions = await client.google.autocomplete.get("pyth")
        print(suggestions["suggestions"])  # ['python', 'python download', ...]
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
        """Get Google autocomplete suggestions for a query."""
        params: dict[str, Any] = {"q": q, "hl": hl, "gl": gl}
        return await self._client.get("/v1/google/autocomplete", params=params)
