"""Gumtree API client.

Gumtree endpoints: search (listings with category, location/postcode radius,
price, seller-type and category-specific filters), search_filters (the filters,
sort orders and radius options a category offers, with live counts),
get_listing (full detail incl. vehicle spec and seller), get_seller_listings,
keyword autocomplete, location autocomplete, and the location and category
trees. All methods are async and return strongly-typed Pydantic models.
UK-only: gumtree.com is the single supported market, prices are in GBP.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.gumtree.models import (
    AutocompleteResponse,
    FiltersResponse,
    ListingDetail,
    LocationAutocompleteResponse,
    SearchResponse,
    SellerListingsResponse,
    TreeResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

GumtreeSort = Literal["relevance", "date", "price_asc", "price_desc", "distance"]
GumtreeSellerType = Literal["private", "trade"]


class GumtreeClient:
    """Client for all Gumtree API operations.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search used BMWs within 25 miles of a postcode
            results = await client.gumtree.search(
                category="cars",
                location="SW1A 1AA",
                distance=25,
                filters="vehicle_make:bmw,vehicle_fuel_type:petrol",
            )
            for listing in results.listings:
                print(listing.title, listing.price_text, listing.distance_text)

            # Full listing detail with vehicle spec and seller
            detail = await client.gumtree.get_listing("1803293391")
            print(detail.seller.name if detail.seller else None)

            # Browse the category tree
            tree = await client.gumtree.list_categories()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `gumtree` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Gumtree client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def search(
        self,
        query: str | None = None,
        *,
        category: str = "all",
        location: str = "uk",
        distance: float | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        sort: GumtreeSort | None = None,
        seller_type: GumtreeSellerType | None = None,
        urgent_only: bool = False,
        with_photos: bool = False,
        filters: str | None = None,
        page: int = 1,
    ) -> SearchResponse:
        """Search gumtree.com listings.

        Args:
            query: Search keywords, e.g. ``"mountain bike"``. Optional — a
                category alone browses it.
            category: Category slug, e.g. ``"cars"``, ``"for-sale"``,
                ``"property-to-rent"``, ``"jobs"``, ``"bicycles"``. Browse the
                tree with :meth:`list_categories`. Default ``"all"``.
            location: Location slug (``"london"``), town name or UK postcode
                (``"SW1A 1AA"``). Resolve one with :meth:`location_autocomplete`.
                Default ``"uk"`` (nationwide).
            distance: Radius in miles around ``location`` (>0, max 1000).
            min_price: Minimum price in GBP. Needs a category other than ``"all"``.
            max_price: Maximum price in GBP. Needs a category other than ``"all"``.
            sort: ``"relevance"`` (default), ``"date"``, ``"price_asc"``,
                ``"price_desc"`` or ``"distance"``.
            seller_type: ``"private"`` or ``"trade"`` (dealers, agencies, recruiters).
            urgent_only: Only ads marked urgent.
            with_photos: Only ads with photos.
            filters: Category-specific filters as comma-separated ``key:value``
                pairs, e.g. ``"vehicle_make:bmw,min_vehicle_mileage:10000"``.
                Repeat a key to select several values. Discover keys with
                :meth:`search_filters`.
            page: Page number, 1-50.

        Returns:
            SearchResponse with ~25-30 listings per page. Gumtree pins up to 5
            paid featured ads (``is_featured``) above the chosen sort order.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.
        """
        params: dict[str, Any] = {
            "query": query,
            "category": category,
            "location": location,
            "distance": distance,
            "min_price": min_price,
            "max_price": max_price,
            "sort": sort,
            "seller_type": seller_type,
            "urgent_only": urgent_only or None,
            "with_photos": with_photos or None,
            "filters": filters,
            "page": page,
        }
        response = await self._client.get("/v1/gumtree/search", params=params)
        return SearchResponse.model_validate(response)

    async def search_filters(
        self,
        category: str = "all",
        *,
        location: str = "uk",
        query: str | None = None,
    ) -> FiltersResponse:
        """The filters, sort orders and radius options Gumtree offers for a category.

        Each filter lists its values with live result counts. Feed a ``key`` and
        a ``value`` back into :meth:`search` as ``filters="key:value"``.

        Args:
            category: Category slug, e.g. ``"cars"``. Default ``"all"``.
            location: Location slug, town or UK postcode. Default ``"uk"``.
            query: Optional keywords to scope the counts.

        Returns:
            FiltersResponse with filters, sort options, distance options and
            category facets.

        Example:
            ```python
            result = await client.gumtree.search_filters("cars")
            for f in result.filters:
                print(f.key, [o.value for o in f.options][:5])
            ```
        """
        params: dict[str, Any] = {"category": category, "location": location, "query": query}
        response = await self._client.get("/v1/gumtree/search/filters", params=params)
        return FiltersResponse.model_validate(response)

    async def get_listing(self, listing_id: str) -> ListingDetail:
        """Full listing: description, every attribute, images, location, seller and similar ads.

        Motors listings carry the full vehicle spec (make, model, mileage, MPG,
        emissions, insurance group, history-check flags).

        Args:
            listing_id: Gumtree listing id — the number at the end of a
                ``gumtree.com/p/...`` URL.

        Returns:
            ListingDetail.

        Raises:
            NotFoundError: If the listing does not exist or has expired.
        """
        response = await self._client.get(f"/v1/gumtree/listings/{listing_id}")
        return ListingDetail.model_validate(response)

    async def get_seller_listings(
        self, listing_id: str, *, page: int = 1
    ) -> SellerListingsResponse:
        """Every live listing by the seller of ``listing_id``.

        Gumtree keys a seller's ad list by one of their ads, so any listing id
        of theirs works.

        Args:
            listing_id: Any Gumtree listing id belonging to the seller.
            page: Page number, 1-50.

        Returns:
            SellerListingsResponse with the seller's name and listings.
        """
        response = await self._client.get(
            f"/v1/gumtree/listings/{listing_id}/seller-listings", params={"page": page}
        )
        return SellerListingsResponse.model_validate(response)

    async def autocomplete(self, query: str) -> AutocompleteResponse:
        """Gumtree search-box keyword suggestions, each with the category it maps to.

        Args:
            query: Partial search term, e.g. ``"iph"``.

        Returns:
            AutocompleteResponse.
        """
        response = await self._client.get("/v1/gumtree/autocomplete", params={"query": query})
        return AutocompleteResponse.model_validate(response)

    async def location_autocomplete(self, query: str) -> LocationAutocompleteResponse:
        """Resolve a place name or postcode prefix to Gumtree locations with coordinates.

        Args:
            query: Town, area or postcode prefix (min 2 chars), e.g. ``"manch"``
                or ``"SW1A"``.

        Returns:
            LocationAutocompleteResponse.
        """
        response = await self._client.get(
            "/v1/gumtree/locations/autocomplete", params={"query": query}
        )
        return LocationAutocompleteResponse.model_validate(response)

    async def list_locations(self, parent_id: int | None = None) -> TreeResponse:
        """Browse Gumtree's location tree: UK -> nations -> counties -> towns.

        Args:
            parent_id: Location id to list the children of. Defaults to the
                United Kingdom (``10000392``) server-side.

        Returns:
            TreeResponse whose ``children`` carry ``id``, ``name`` and ``slug``.
        """
        response = await self._client.get("/v1/gumtree/locations", params={"parent_id": parent_id})
        return TreeResponse.model_validate(response)

    async def list_categories(self, parent_id: int | None = None) -> TreeResponse:
        """Browse Gumtree's category tree. A node's ``slug`` is the :meth:`search` category.

        Args:
            parent_id: Category id to list the children of. Defaults to all
                categories (``1``) server-side.

        Returns:
            TreeResponse whose ``children`` carry ``id``, ``name`` and ``slug``.
        """
        response = await self._client.get("/v1/gumtree/categories", params={"parent_id": parent_id})
        return TreeResponse.model_validate(response)
