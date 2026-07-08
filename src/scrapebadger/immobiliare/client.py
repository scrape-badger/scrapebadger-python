"""Immobiliare API client.

Immobiliare endpoints: autocomplete (resolve a free-text place to geography
ids), search (list listings by location or explicit ids), get_listing (full
single-listing detail), get_agency / get_agency_listings (agency profile +
active listings), price_stats (€/m² time series per area), list_markets, and
reference (filter enums). All methods are async and return strongly-typed
Pydantic models. Markets: it, es, gr, lu (the Immobiliare Group).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.immobiliare.models import (
    AgencyListingsResponse,
    AgencyProfile,
    Listing,
    Market,
    PriceStatsResponse,
    ReferenceResponse,
    SearchResponse,
    SuggestResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ImmobiliareClient:
    """Client for all Immobiliare API operations.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Resolve a place name to geography ids
            hits = await client.immobiliare.autocomplete("Milano")
            city = hits.suggestions[0]

            # Search listings
            results = await client.immobiliare.search(
                city_id=city.city_id, price_max=500000
            )
            for listing in results.listings:
                print(f"{listing.id}: {listing.title}")

            # Full single-listing detail
            detail = await client.immobiliare.get_listing(123456789)
            print(detail.price.formatted if detail.price else None)

            # Supported markets
            markets = await client.immobiliare.list_markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `immobiliare` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Immobiliare client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def autocomplete(self, query: str, *, market: str = "it") -> SuggestResponse:
        """Resolve a free-text place name into geography ids for search.

        Args:
            query: Free-text place name, e.g. "Milano".
            market: "it", "es", "gr", or "lu". Defaults to "it".

        Returns:
            Suggest response with region/province/city/zone id candidates.

        Example:
            ```python
            hits = await client.immobiliare.autocomplete("Milano")
            for s in hits.suggestions:
                print(s.label, s.type, s.city_id)
            ```
        """
        params: dict[str, Any] = {"query": query, "market": market}
        response = await self._client.get("/v1/immobiliare/autocomplete", params=params)
        return SuggestResponse.model_validate(response)

    async def search(
        self,
        *,
        market: str = "it",
        location: str | None = None,
        region_id: str | None = None,
        province_id: str | None = None,
        city_id: str | None = None,
        contract: str = "sale",
        category: str = "residential",
        price_min: int | None = None,
        price_max: int | None = None,
        surface_min: int | None = None,
        surface_max: int | None = None,
        rooms_min: int | None = None,
        rooms_max: int | None = None,
        bathrooms_min: int | None = None,
        sort: str = "relevance",
        page: int = 1,
    ) -> SearchResponse:
        """Search Immobiliare-group listings.

        Scope the search by ``location`` (free text, auto-resolved) OR explicit
        ``region_id`` / ``province_id`` / ``city_id`` from :meth:`autocomplete`.

        Args:
            market: "it", "es", "gr", or "lu". Defaults to "it".
            location: Free-text place, auto-resolved to geography ids.
            region_id: Region id (fkRegione) from :meth:`autocomplete`.
            province_id: Province id (idProvincia) from :meth:`autocomplete`.
            city_id: City id (idComune) from :meth:`autocomplete`.
            contract: "sale" or "rent". Defaults to "sale".
            category: One of residential, commercial, garages, offices, land,
                buildings, warehouses (see :meth:`reference`). Defaults to
                "residential".
            price_min: Minimum price filter (EUR).
            price_max: Maximum price filter (EUR).
            surface_min: Minimum surface filter (m²).
            surface_max: Maximum surface filter (m²).
            rooms_min: Minimum number of rooms.
            rooms_max: Maximum number of rooms.
            bathrooms_min: Minimum number of bathrooms.
            sort: One of relevance, price_asc, price_desc, newest, oldest,
                surface_desc, surface_asc. Defaults to "relevance".
            page: Page number (>= 1). Defaults to 1.

        Returns:
            Search response with ``listings`` and pagination metadata.

        Example:
            ```python
            results = await client.immobiliare.search(
                location="Milano",
                contract="rent",
                price_max=2000,
                sort="price_asc",
            )
            print(f"Page {results.current_page}/{results.max_pages}")
            ```
        """
        params: dict[str, Any] = {
            "market": market,
            "location": location,
            "region_id": region_id,
            "province_id": province_id,
            "city_id": city_id,
            "contract": contract,
            "category": category,
            "price_min": price_min,
            "price_max": price_max,
            "surface_min": surface_min,
            "surface_max": surface_max,
            "rooms_min": rooms_min,
            "rooms_max": rooms_max,
            "bathrooms_min": bathrooms_min,
            "sort": sort,
            "page": page,
        }
        response = await self._client.get("/v1/immobiliare/search", params=params)
        return SearchResponse.model_validate(response)

    async def get_listing(self, listing_id: int, *, market: str = "it") -> Listing:
        """Get the full detail for a single Immobiliare listing.

        Args:
            listing_id: The Immobiliare listing id.
            market: "it", "es", "gr", or "lu". Defaults to "it".

        Returns:
            The full :class:`Listing` detail.

        Example:
            ```python
            detail = await client.immobiliare.get_listing(123456789)
            print(detail.title, detail.energy_class)
            ```
        """
        params: dict[str, Any] = {"market": market}
        response = await self._client.get(f"/v1/immobiliare/listings/{listing_id}", params=params)
        return Listing.model_validate(response)

    async def get_agency(self, agency_id: int, *, market: str = "it") -> AgencyProfile:
        """Get an agency/advertiser profile.

        Args:
            agency_id: The Immobiliare agency id.
            market: "it", "es", "gr", or "lu". Defaults to "it".

        Returns:
            The full :class:`AgencyProfile`.

        Example:
            ```python
            agency = await client.immobiliare.get_agency(12345)
            print(agency.name, agency.real_estate_ads)
            ```
        """
        params: dict[str, Any] = {"market": market}
        response = await self._client.get(f"/v1/immobiliare/agencies/{agency_id}", params=params)
        return AgencyProfile.model_validate(response)

    async def get_agency_listings(
        self,
        agency_id: int,
        *,
        market: str = "it",
        page: int = 1,
    ) -> AgencyListingsResponse:
        """Get an agency's active listings (25 per page).

        Args:
            agency_id: The Immobiliare agency id.
            market: "it", "es", "gr", or "lu". Defaults to "it".
            page: Page number (>= 1). Defaults to 1.

        Returns:
            Agency-listings response with ``listings`` and pagination.

        Example:
            ```python
            result = await client.immobiliare.get_agency_listings(12345, page=2)
            print(result.count, len(result.listings))
            ```
        """
        params: dict[str, Any] = {"market": market, "page": page}
        response = await self._client.get(
            f"/v1/immobiliare/agencies/{agency_id}/listings", params=params
        )
        return AgencyListingsResponse.model_validate(response)

    async def price_stats(
        self,
        region_id: str,
        *,
        province_id: str | None = None,
        city_id: str | None = None,
        market: str = "it",
        contract: str = "sale",
    ) -> PriceStatsResponse:
        """Get the historical average €/m² time series for an area.

        Args:
            region_id: Region id, e.g. "lom" (required).
            province_id: Province id, e.g. "MI". Optional.
            city_id: City id (idComune). Optional.
            market: "it", "es", "gr", or "lu". Defaults to "it".
            contract: "sale" or "rent". Defaults to "sale".

        Returns:
            Price-stats response with monthly ``points`` (label + EUR/m² value).

        Example:
            ```python
            stats = await client.immobiliare.price_stats("lom", province_id="MI")
            for point in stats.points:
                print(point.label, point.value)
            ```
        """
        params: dict[str, Any] = {
            "market": market,
            "region_id": region_id,
            "province_id": province_id,
            "city_id": city_id,
            "contract": contract,
        }
        response = await self._client.get("/v1/immobiliare/market-insights/prices", params=params)
        return PriceStatsResponse.model_validate(response)

    async def list_markets(self) -> list[Market]:
        """Get all supported Immobiliare-group markets (it, es, gr, lu).

        Returns:
            List of supported markets (code, domain, country, locale, currency).

        Example:
            ```python
            markets = await client.immobiliare.list_markets()
            for m in markets:
                print(f"{m.code}: {m.domain} ({m.currency})")
            ```
        """
        response = await self._client.get("/v1/immobiliare/markets")
        # The endpoint returns a bare JSON array of markets.
        return [Market.model_validate(m) for m in response]

    async def reference(self) -> ReferenceResponse:
        """Get the filter enums accepted by :meth:`search`.

        Returns:
            Reference response with ``contracts``, ``categories``, and ``sorts``.

        Example:
            ```python
            ref = await client.immobiliare.reference()
            print(ref.categories)
            ```
        """
        response = await self._client.get("/v1/immobiliare/reference")
        return ReferenceResponse.model_validate(response)
