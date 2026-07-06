"""Leboncoin Reference Data API client.

Provides methods for fetching categories, regions, departments, location
suggestions, and supported markets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.leboncoin.models import (
    CategoriesResponse,
    DepartmentsResponse,
    LocationSearchResponse,
    MarketsResponse,
    RegionsResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for Leboncoin reference data endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            categories = await client.leboncoin.reference.list_categories()
            for c in categories.categories:
                print(f"{c.label} -> {c.category_id}")

            regions = await client.leboncoin.reference.list_regions()
            for r in regions.regions:
                print(f"{r.name}: {r.region_id}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def list_categories(self) -> CategoriesResponse:
        """Get Leboncoin's reference category list.

        Returns:
            Categories response with all categories.

        Example:
            ```python
            result = await client.leboncoin.reference.list_categories()
            for c in result.categories:
                print(f"{c.label}: {c.category_id}")
            ```
        """
        response = await self._client.get("/v1/leboncoin/categories")
        return CategoriesResponse.model_validate(response)

    async def list_regions(self) -> RegionsResponse:
        """Get Leboncoin's reference region list.

        Returns:
            Regions response with all regions.

        Example:
            ```python
            result = await client.leboncoin.reference.list_regions()
            for r in result.regions:
                print(f"{r.name}: {r.region_id}")
            ```
        """
        response = await self._client.get("/v1/leboncoin/regions")
        return RegionsResponse.model_validate(response)

    async def list_departments(self, *, region_id: str | None = None) -> DepartmentsResponse:
        """Get Leboncoin's reference department list.

        Args:
            region_id: Optional region id to scope the departments.

        Returns:
            Departments response with all matching departments.

        Example:
            ```python
            result = await client.leboncoin.reference.list_departments(region_id="12")
            for d in result.departments:
                print(f"{d.name}: {d.department_id}")
            ```
        """
        params: dict[str, Any] = {"region_id": region_id}
        response = await self._client.get("/v1/leboncoin/departments", params=params)
        return DepartmentsResponse.model_validate(response)

    async def search_locations(self, q: str) -> LocationSearchResponse:
        """Get location autocomplete suggestions.

        Args:
            q: Partial location query.

        Returns:
            Location search response with the query and suggestions.

        Example:
            ```python
            result = await client.leboncoin.reference.search_locations("bordeaux")
            for s in result.suggestions:
                print(s.label)
            ```
        """
        params: dict[str, Any] = {"q": q}
        response = await self._client.get("/v1/leboncoin/locations/search", params=params)
        return LocationSearchResponse.model_validate(response)

    async def list_markets(self) -> MarketsResponse:
        """Get all supported Leboncoin markets.

        Returns:
            Markets response with all supported markets.

        Example:
            ```python
            result = await client.leboncoin.reference.list_markets()
            for m in result.markets:
                print(m)
            ```
        """
        response = await self._client.get("/v1/leboncoin/markets")
        return MarketsResponse.model_validate(response)
