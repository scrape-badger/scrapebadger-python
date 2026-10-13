"""Gumtree API client.

Gumtree endpoints: search (listings with category, location/postcode radius,
price, seller-type and category-specific filters), search_filters (the filters,
sort orders and radius options a category offers, with live counts),
get_listing (full detail incl. vehicle spec and seller), get_seller_listings,
keyword autocomplete, location autocomplete, the location and category trees,
and list_markets. All methods are async and return strongly-typed Pydantic
models.

Three markets, chosen per call with ``market``: ``"uk"`` (gumtree.com, GBP —
the server default), ``"au"`` (gumtree.com.au, AUD) and ``"za"``
(gumtree.co.za, ZAR). They are separate sites: uk takes slugs for category
and location, au takes numeric ids and za takes refs (``"p6dnh"``) from
:meth:`GumtreeClient.list_categories` and :meth:`GumtreeClient.list_locations`
of the same market.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.gumtree.models import (
    AutocompleteResponse,
    FiltersResponse,
    ListingDetail,
    LocationAutocompleteResponse,
    MarketsResponse,
    SearchResponse,
    SellerListingsResponse,
    TreeResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

GumtreeMarket = Literal["uk", "au", "za"]
GumtreeSort = Literal["relevance", "date", "price_asc", "price_desc", "distance"]
GumtreeSellerType = Literal["private", "trade"]


class GumtreeClient:
    """Client for all Gumtree API operations.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search used BMWs within 25 miles of a UK postcode
            results = await client.gumtree.search(
                category="cars",
                location="SW1A 1AA",
                distance=25,
                filters="vehicle_make:bmw,vehicle_fuel_type:petrol",
            )
            for listing in results.listings:
                print(listing.title, listing.price_text, listing.distance_text)

            # Australia: numeric ids — cars (18320) within 10 km of Sydney
            au = await client.gumtree.search(
                market="au", category="18320", location="3003435", distance=10
            )

            # South Africa: refs — Cars & Bakkies (p6dnh) in Gauteng (dkp8y)
            za = await client.gumtree.search(
                market="za", category="p6dnh", location="dkp8y", filters="make:toyota"
            )
            detail = await client.gumtree.get_listing(za.listings[0].id, market="za")
            print(detail.seller.name if detail.seller else None)

            # Browse a market's category tree
            tree = await client.gumtree.list_categories(market="au")
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
        location: str | None = None,
        distance: float | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        sort: GumtreeSort | None = None,
        seller_type: GumtreeSellerType | None = None,
        urgent_only: bool = False,
        with_photos: bool = False,
        filters: str | None = None,
        page: int = 1,
        market: GumtreeMarket | None = None,
    ) -> SearchResponse:
        """Search Gumtree listings in the UK, Australia or South Africa.

        Args:
            query: Search keywords, e.g. ``"mountain bike"``. Optional — a
                category alone browses it.
            category: uk: category slug, e.g. ``"cars"``, ``"for-sale"``,
                ``"property-to-rent"``. au: numeric category id as a string,
                e.g. ``"18320"`` (cars). za: category ref, e.g. ``"p6dnh"``
                (Cars & Bakkies). Browse the tree with :meth:`list_categories`.
                Default ``"all"``.
            location: uk: location slug (``"london"``), town name or UK postcode
                (``"SW1A 1AA"``). au: numeric location id as a string, e.g.
                ``"3003435"`` (Sydney). za: location ref, e.g. ``"dkp8y"``
                (Gauteng). Resolve one with :meth:`location_autocomplete`.
                Default: the whole country.
            distance: Radius around ``location`` (>0, max 1000): miles (uk) or
                km (au). Not offered by za.
            min_price: Minimum price in the market's currency (uk: needs a
                category other than ``"all"``).
            max_price: Maximum price in the market's currency (uk: needs a
                category other than ``"all"``).
            sort: ``"relevance"`` (default), ``"date"``, ``"price_asc"``,
                ``"price_desc"`` or ``"distance"`` (not za).
            seller_type: ``"private"`` or ``"trade"`` (dealers, agencies,
                recruiters). uk and za.
            urgent_only: uk only: only ads marked urgent.
            with_photos: uk only: only ads with photos.
            filters: Category-specific filters as comma-separated ``key:value``
                pairs, e.g. ``"vehicle_make:bmw,min_vehicle_mileage:10000"`` (uk)
                or ``"make:toyota,fuelType:petrol,max_mileageKm:100000"`` (za).
                Range filters
                take ``min_<key>``/``max_<key>``. Discover keys with
                :meth:`search_filters` for the same market.
            page: Page number, 1-50 (za: only the first 375 matches are
                reachable; a page past them comes back empty).
            market: ``"uk"`` (gumtree.com), ``"au"`` (gumtree.com.au) or ``"za"``
                (gumtree.co.za). Unset = the server default, ``"uk"``.

        Returns:
            SearchResponse — uk ~25-30 listings per page (Gumtree pins up to 5
            paid featured ads, ``is_featured``, above the chosen sort order),
            au 24, za 20. Prices are in ``currency``.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid, or not supported
                by the market.
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
            "market": market,
        }
        response = await self._client.get("/v1/gumtree/search", params=params)
        return SearchResponse.model_validate(response)

    async def search_filters(
        self,
        category: str = "all",
        *,
        location: str | None = None,
        query: str | None = None,
        filters: str | None = None,
        market: GumtreeMarket | None = None,
    ) -> FiltersResponse:
        """The filters, sort orders and radius options Gumtree offers for a category.

        Each filter lists its values with live result counts. Feed a ``key`` and
        a ``value`` back into :meth:`search` as ``filters="key:value"``.

        Args:
            category: uk: category slug, e.g. ``"cars"``; au: numeric category
                id; za: category ref, e.g. ``"p6dnh"``. Default ``"all"``.
            location: uk: location slug, town or UK postcode; au: numeric
                location id; za: location ref, e.g. ``"dkp8y"``. Default: the
                whole country.
            query: Optional keywords to scope the counts.
            filters: za only: filters already applied, e.g. ``"make:toyota"``
                to narrow the model counts to Toyota's models.
            market: ``"uk"``, ``"au"`` or ``"za"``. Unset = ``"uk"``.

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
        params: dict[str, Any] = {
            "category": category,
            "location": location,
            "query": query,
            "filters": filters,
            "market": market,
        }
        response = await self._client.get("/v1/gumtree/search/filters", params=params)
        return FiltersResponse.model_validate(response)

    async def get_listing(
        self, listing_id: str, *, market: GumtreeMarket | None = None
    ) -> ListingDetail:
        """Full listing: description, every attribute, images, location, seller and similar ads.

        Motors listings carry the full vehicle spec (uk: make, model, mileage,
        MPG, emissions, insurance group, history-check flags; au: make, model,
        variant, odometer, VIN, rego).

        Args:
            listing_id: Gumtree listing id from the end of the listing URL
                (uk/au: ~10 digits; za: the listing ref, e.g.
                ``"ls26bvmcpnsqmz7l9jz"``).
            market: ``"uk"``, ``"au"`` or ``"za"``. Unset = ``"uk"``.

        Returns:
            ListingDetail.

        Raises:
            NotFoundError: If the listing does not exist or has expired.
        """
        response = await self._client.get(
            f"/v1/gumtree/listings/{listing_id}", params={"market": market}
        )
        return ListingDetail.model_validate(response)

    async def get_seller_listings(
        self, listing_id: str, *, page: int = 1, market: GumtreeMarket | None = None
    ) -> SellerListingsResponse:
        """Every live listing by the seller of ``listing_id``.

        Gumtree keys a seller's ad list by one of their ads, so any listing id
        of theirs works.

        Args:
            listing_id: Any Gumtree listing id belonging to the seller (za: a
                listing ref, e.g. ``"ls26bvmcpnsqmz7l9jz"``).
            page: Page number, 1-50.
            market: ``"uk"``, ``"au"`` or ``"za"``. Unset = ``"uk"``.

        Returns:
            SellerListingsResponse with the seller's name and listings.
        """
        response = await self._client.get(
            f"/v1/gumtree/listings/{listing_id}/seller-listings",
            params={"page": page, "market": market},
        )
        return SellerListingsResponse.model_validate(response)

    async def autocomplete(
        self, query: str, *, market: GumtreeMarket | None = None
    ) -> AutocompleteResponse:
        """Gumtree search-box keyword suggestions, each with the category it maps to.

        Args:
            query: Partial search term, e.g. ``"iph"``.
            market: ``"uk"``, ``"au"`` or ``"za"``. Unset = ``"uk"``.

        Returns:
            AutocompleteResponse.
        """
        response = await self._client.get(
            "/v1/gumtree/autocomplete", params={"query": query, "market": market}
        )
        return AutocompleteResponse.model_validate(response)

    async def location_autocomplete(
        self, query: str, *, market: GumtreeMarket | None = None
    ) -> LocationAutocompleteResponse:
        """Resolve a place name or postcode prefix to Gumtree locations.

        The ``id`` (au: a number; za: a ref such as ``"pfw8k"``) or ``name``
        (uk) is what :meth:`search` takes as ``location``.

        Args:
            query: Town, area or postcode prefix (min 2 chars), e.g. ``"manch"``
                or ``"SW1A"``.
            market: ``"uk"``, ``"au"`` or ``"za"``. Unset = ``"uk"``.

        Returns:
            LocationAutocompleteResponse.
        """
        response = await self._client.get(
            "/v1/gumtree/locations/autocomplete", params={"query": query, "market": market}
        )
        return LocationAutocompleteResponse.model_validate(response)

    async def list_locations(
        self, parent_id: int | str | None = None, *, market: GumtreeMarket | None = None
    ) -> TreeResponse:
        """Browse Gumtree's location tree.

        uk: UK -> nations -> counties -> towns. au: states -> regions -> areas.
        za: provinces -> towns and suburbs.

        Args:
            parent_id: Location id to list the children of — a number on uk/au,
                a ref on za (e.g. ``"dkp8y"`` for Gauteng). Unset = the
                market's root (the whole country) server-side.
            market: ``"uk"``, ``"au"`` or ``"za"``. Unset = ``"uk"``.

        Returns:
            TreeResponse whose ``children`` carry ``id``, ``name`` and ``slug``.
        """
        response = await self._client.get(
            "/v1/gumtree/locations", params={"parent_id": parent_id, "market": market}
        )
        return TreeResponse.model_validate(response)

    async def list_categories(
        self, parent_id: int | str | None = None, *, market: GumtreeMarket | None = None
    ) -> TreeResponse:
        """Browse Gumtree's category tree.

        A node's ``slug`` (uk) or ``id`` (au: a number; za: a ref such as
        ``"p6dnh"``) is the :meth:`search` category.

        Args:
            parent_id: Category id to list the children of — a number on uk/au,
                a ref on za (e.g. ``"l4dq6"`` for Vehicles). Unset = the
                market's root (all categories) server-side.
            market: ``"uk"``, ``"au"`` or ``"za"``. Unset = ``"uk"``.

        Returns:
            TreeResponse whose ``children`` carry ``id``, ``name`` and ``slug``.
        """
        response = await self._client.get(
            "/v1/gumtree/categories", params={"parent_id": parent_id, "market": market}
        )
        return TreeResponse.model_validate(response)

    async def list_markets(self) -> MarketsResponse:
        """The Gumtree sites this API covers, with their currency and id formats.

        Returns:
            MarketsResponse — one entry per market (``uk``, ``au``, ``za``).

        Example:
            ```python
            result = await client.gumtree.list_markets()
            for m in result.markets:
                print(m.market, m.domain, m.currency, m.distance_unit)
            ```
        """
        response = await self._client.get("/v1/gumtree/markets")
        return MarketsResponse.model_validate(response)
