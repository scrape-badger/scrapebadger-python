"""Naver API client combining all sub-clients.

This module provides the main NaverClient class that serves as the entry
point for all Naver API operations (search, places, shopping, stores,
products, and reviews).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.naver.places import PlacesClient
from scrapebadger.naver.products import ProductsClient
from scrapebadger.naver.reviews import ReviewsClient
from scrapebadger.naver.search import SearchClient
from scrapebadger.naver.shopping import ShoppingClient
from scrapebadger.naver.stores import StoresClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class NaverClient:
    """Client for all Naver API operations.

    This class provides access to all Naver scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        search: Client for integrated SERP, autocomplete, and verticals.
        places: Client for place detail, reviews, and photos.
        shopping: Client for shopping rankings, finder search, catalog, and
            Shopping Live (via ``shopping.live``).
        stores: Client for SmartStore / Brand store profile and listings.
        products: Client for commerce product detail, reviews, Q&A, and groups.
        reviews: Client for commerce review detail and helpers.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Integrated search
            results = await client.naver.search.search("커피머신")

            # Place detail
            place = await client.naver.places.get("1234567890")

            # Shopping bestsellers
            top = await client.naver.shopping.bestsellers()

            # Store profile
            store = await client.naver.stores.get("somestore")
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `naver` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Naver client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        self._search = SearchClient(client)
        self._places = PlacesClient(client)
        self._shopping = ShoppingClient(client)
        self._stores = StoresClient(client)
        self._products = ProductsClient(client)
        self._reviews = ReviewsClient(client)

    @property
    def search(self) -> SearchClient:
        """Access integrated SERP, autocomplete, and vertical endpoints.

        Returns:
            SearchClient for search, news, blog, autocomplete, local, web,
            cafe, kin, image, video, and clip.
        """
        return self._search

    @property
    def places(self) -> PlacesClient:
        """Access place detail, reviews, and photos endpoints.

        Returns:
            PlacesClient for place detail, reviews, and photos.
        """
        return self._places

    @property
    def shopping(self) -> ShoppingClient:
        """Access shopping and Shopping Live endpoints.

        Returns:
            ShoppingClient for rankings, insight, finder search, catalog,
            price comparison, and Shopping Live (via ``shopping.live``).
        """
        return self._shopping

    @property
    def stores(self) -> StoresClient:
        """Access SmartStore / Brand store endpoints.

        Returns:
            StoresClient for store profile, categories, products, and bestsellers.
        """
        return self._stores

    @property
    def products(self) -> ProductsClient:
        """Access commerce product endpoints.

        Returns:
            ProductsClient for product detail, review summary, reviews, Q&A,
            variant group graph, and group review summary.
        """
        return self._products

    @property
    def reviews(self) -> ReviewsClient:
        """Access commerce review endpoints.

        Returns:
            ReviewsClient for review detail, video in-key, and SSR queries.
        """
        return self._reviews
