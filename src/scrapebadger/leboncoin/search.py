"""Leboncoin Search API client.

Provides keyword/filter search across Leboncoin classified ads.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.leboncoin.models import SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for the Leboncoin search endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            results = await client.leboncoin.search.search("velo")
            for ad in results.ads:
                print(f"{ad.subject}: {ad.price_eur}")
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
        text: str,
        *,
        category: str | None = None,
        region_id: str | None = None,
        department_id: str | None = None,
        city: str | None = None,
        zipcode: str | None = None,
        price_min: int | None = None,
        price_max: int | None = None,
        owner_type: str | None = None,
        ad_type: str | None = None,
        sort: str | None = None,
        page: int = 1,
        limit: int | None = None,
    ) -> SearchResponse:
        """Search Leboncoin for classified ads.

        Args:
            text: Search keywords.
            category: Restrict the search to a category id.
            region_id: Restrict the search to a region id.
            department_id: Restrict the search to a department id.
            city: Restrict the search to a city.
            zipcode: Restrict the search to a postal code.
            price_min: Minimum price filter (euros).
            price_max: Maximum price filter (euros).
            owner_type: Seller type ("all", "pro", "private").
            ad_type: Ad type ("offer", "demand").
            sort: Sort order ("relevance", "newest", "oldest", "price_low", "price_high").
            page: Page number (1-indexed). Defaults to 1.
            limit: Results per page.

        Returns:
            Search response with matching ads and pagination metadata.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.leboncoin.search.search(
                "velo",
                region_id="12",
                price_min=100,
                price_max=500,
                sort="price_low",
            )
            print(f"Page {results.page} of {results.max_pages}")
            ```
        """
        params: dict[str, Any] = {
            "text": text,
            "category": category,
            "region_id": region_id,
            "department_id": department_id,
            "city": city,
            "zipcode": zipcode,
            "price_min": price_min,
            "price_max": price_max,
            "owner_type": owner_type,
            "ad_type": ad_type,
            "sort": sort,
            "page": page,
            "limit": limit,
        }
        response = await self._client.get("/v1/leboncoin/search", params=params)
        return SearchResponse.model_validate(response)
