"""Vinted Search API client.

Provides methods for searching Vinted items.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.vinted.models import SearchResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SearchClient:
    """Client for Vinted search endpoints.

    Provides async methods for searching items on Vinted marketplaces.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Search for items
            results = await client.vinted.search.search("nike air max")
            for item in results.items:
                print(f"{item.title}: {item.price.amount} {item.price.currency_code}")

            # Search with filters
            results = await client.vinted.search.search(
                "nike",
                market="fr",
                price_from="10",
                price_to="50",
                per_page=40,
            )
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
        query: str,
        *,
        market: str = "fr",
        page: int = 1,
        per_page: int = 20,
        price_from: str | None = None,
        price_to: str | None = None,
        brand_ids: str | None = None,
        catalog_ids: str | None = None,
        color_ids: str | None = None,
        status_ids: str | None = None,
        order: str | None = None,
        seller_country: str | None = None,
    ) -> SearchResponse:
        """Search for items on Vinted.

        Args:
            query: Search query string.
            market: Vinted market code (e.g. "fr", "de", "uk"). Defaults to "fr".
            page: Page number (1-indexed). Defaults to 1.
            per_page: Number of items per page (max varies by market). Defaults to 20.
            price_from: Minimum price filter.
            price_to: Maximum price filter.
            brand_ids: Comma-separated brand IDs to filter by.
            catalog_ids: Comma-separated Vinted catalog (category) IDs to
                restrict the search to (e.g. ``"221"`` or ``"221,1242"``).
                Vinted applies this before the search runs, and sub-categories
                are included. A catalog ID is the ``catalog[]`` value in a
                Vinted category URL (vinted.fr/catalog?catalog[]=221); IDs are
                per market.
            color_ids: Comma-separated color IDs to filter by.
            status_ids: Comma-separated status IDs to filter by.
            order: Sort order (e.g. "newest_first", "price_low_to_high").
            seller_country: Filter results to items whose seller is physically
                located in one of the given countries. A comma-separated list of
                ISO-2 country codes (e.g. ``"fr"`` or ``"fr,be"``). Vinted
                federates cross-border EU listings into each market domain and has
                no native country filter, so ScrapeBadger applies this filter.
                When set, each returned item gains a ``seller_country_code`` and
                the response gains a top-level ``seller_country`` echo.
                Billing: a search is a flat 5 credits whatever filters you
                pass; seller lookups are not billed on top.

        Returns:
            Search response with matching items and pagination metadata.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.vinted.search.search(
                "vintage jacket",
                market="de",
                price_from="20",
                price_to="100",
                order="newest_first",
            )
            print(f"Found {results.pagination.total_entries} items")
            for item in results.items:
                print(f"  {item.title} - {item.price.amount} {item.price.currency_code}")

            # Restrict to a Vinted category (women's T-shirts on vinted.fr).
            tshirts = await client.vinted.search.search("nike", catalog_ids="221")

            # Filter to sellers physically located in France or Belgium.
            local = await client.vinted.search.search(
                "vintage jacket",
                seller_country="fr,be",
            )
            print(f"Applied seller_country filter: {local.seller_country}")
            for item in local.items:
                print(f"  {item.title} - seller in {item.seller_country_code}")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "market": market,
            "page": page,
            "per_page": per_page,
            "price_from": price_from,
            "price_to": price_to,
            "brand_ids": brand_ids,
            "catalog_ids": catalog_ids,
            "color_ids": color_ids,
            "status_ids": status_ids,
            "order": order,
            "seller_country": seller_country,
        }
        response = await self._client.get("/v1/vinted/search", params=params)
        return SearchResponse.model_validate(response)
