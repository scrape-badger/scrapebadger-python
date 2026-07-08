"""LoopNet Search API client.

Provides commercial-real-estate listing search for for-lease / for-sale /
auction listings across 5 markets (us/ca/uk/fr/es).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.loopnet.models import SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for the LoopNet listing search endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.loopnet.search.search("Houston, TX")
            for card in results.results:
                print(f"{card.position}. {card.address} — {card.price_text}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize search client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def search(
        self,
        location: str,
        *,
        market: str = "us",
        listing_type: str = "for-lease",
        property_type: str | None = None,
        page: int = 1,
        min_price: float | None = None,
        max_price: float | None = None,
        price_type: str | None = None,
        min_size: int | None = None,
        max_size: int | None = None,
    ) -> SearchResponse:
        """Search LoopNet for commercial listings. Costs 10 credits.

        Args:
            location: City/state ("Houston, TX"), ZIP, state code, or "usa" (required).
            market: Coverage market ("us", "ca", "uk", "fr", "es"). Defaults to "us".
            listing_type: Listing type ("for-lease", "for-sale", "auctions").
                Defaults to "for-lease".
            property_type: Property-type slug (from ``reference.property_types()``).
                Defaults to all types.
            page: Page number (1-20; LoopNet caps ~500 results). Defaults to 1.
            min_price: Minimum price filter.
            max_price: Maximum price filter.
            price_type: Price basis for the price filters ("unit", "sf", "acre").
            min_size: Minimum size (square feet).
            max_size: Maximum size (square feet).

        Returns:
            Search response with matching listing cards and pagination.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.loopnet.search.search(
                "Houston, TX",
                listing_type="for-sale",
                property_type="office",
                max_price=5000000,
            )
            print(f"Page {results.pagination.current_page}")
            ```
        """
        params: dict[str, Any] = {
            "location": location,
            "market": market,
            "listing_type": listing_type,
            "property_type": property_type,
            "page": page,
            "min_price": min_price,
            "max_price": max_price,
            "price_type": price_type,
            "min_size": min_size,
            "max_size": max_size,
        }
        response = await self._client.get("/v1/loopnet/search", params=params)
        return SearchResponse.model_validate(response)
