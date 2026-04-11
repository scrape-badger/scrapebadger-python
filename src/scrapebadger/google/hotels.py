"""Google Hotels client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class HotelsClient:
    """Client for Google Hotels endpoints.

    Example:
        ```python
        hotels = await client.google.hotels.search(
            "Paris",
            check_in="2026-05-01",
            check_out="2026-05-05",
            adults=2,
        )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        check_in: str,
        check_out: str,
        adults: int = 2,
        currency: str = "USD",
        gl: str = "us",
    ) -> dict[str, Any]:
        """Search hotels by location + dates.

        Args:
            q: Location or hotel name.
            check_in: YYYY-MM-DD check-in date.
            check_out: YYYY-MM-DD check-out date.
            adults: Number of adults (default 2).
            currency: ISO currency code (default "USD").
            gl: Country code.
        """
        params: dict[str, Any] = {
            "q": q,
            "check_in": check_in,
            "check_out": check_out,
            "adults": adults,
            "currency": currency,
            "gl": gl,
        }
        return await self._client.get("/v1/google/hotels/search", params=params)

    async def details(
        self,
        property_token: str,
        *,
        check_in: str,
        check_out: str,
    ) -> dict[str, Any]:
        """Get detailed property information.

        Args:
            property_token: Property token from a search response.
            check_in: YYYY-MM-DD.
            check_out: YYYY-MM-DD.
        """
        params: dict[str, Any] = {
            "property_token": property_token,
            "check_in": check_in,
            "check_out": check_out,
        }
        return await self._client.get("/v1/google/hotels/details", params=params)
