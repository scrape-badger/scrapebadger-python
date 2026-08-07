"""Walmart Sellers API client.

Marketplace seller profiles and their catalogues.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.walmart.models import SearchResponse, SellerResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SellersClient:
    """Client for Walmart marketplace seller endpoints.

    Note:
        The ``seller_id`` here is the NUMERIC catalog seller id (e.g.
        ``"101040442"``) — a product's ``seller.catalog_seller_id``, NOT the
        32-char hex ``seller_id``, which 404s as a storefront URL.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            seller = await client.walmart.sellers.get_seller("101040442")
            print(seller.seller.name, seller.seller.rating)

            catalogue = await client.walmart.sellers.get_seller_products(
                "101040442", query="laptop"
            )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize sellers client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_seller(self, seller_id: str) -> SellerResponse:
        """Get a marketplace seller's profile.

        Args:
            seller_id: Numeric catalog seller id, e.g. ``"101040442"``.

        Returns:
            SellerResponse with contact details, address, rating, and policies.

        Raises:
            NotFoundError: If the seller doesn't exist.

        Note:
            There is no ``page`` parameter: adding ``?page=`` to a Walmart seller
            URL makes Walmart's own SSR throw. Use :meth:`get_seller_products`
            for the catalogue.

        Example:
            ```python
            result = await client.walmart.sellers.get_seller("101040442")
            print(result.seller.display_name, result.seller.review_count)
            ```
        """
        response = await self._client.get(f"/v1/walmart/sellers/{seller_id}")
        return SellerResponse.model_validate(response)

    async def get_seller_products(
        self,
        seller_id: str,
        query: str,
        *,
        page: int = 1,
        sort: str | None = None,
    ) -> SearchResponse:
        """List a marketplace seller's catalogue.

        Args:
            seller_id: Numeric catalog seller id, e.g. ``"101040442"``.
            query: Search term scoping the seller's catalogue. REQUIRED —
                Walmart returns nothing for a seller facet with no query term.
            page: Page number, 1-10.
            sort: Result ordering — ``"best_match"``, ``"best_seller"``,
                ``"price_low"``, ``"price_high"``, ``"rating_high"``, ``"new"``.

        Returns:
            SearchResponse with the seller's matching products.

        Example:
            ```python
            result = await client.walmart.sellers.get_seller_products(
                "101040442", "laptop", sort="price_low"
            )
            for item in result.items:
                print(item.name, item.price)
            ```
        """
        params: dict[str, Any] = {"query": query, "page": page, "sort": sort}
        response = await self._client.get(
            f"/v1/walmart/sellers/{seller_id}/products", params=params
        )
        return SearchResponse.model_validate(response)
