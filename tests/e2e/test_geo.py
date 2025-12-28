"""E2E tests for GeoClient.

Tests all geo/places-related API endpoints with real API calls.
"""

from __future__ import annotations

from scrapebadger import ScrapeBadger
from scrapebadger.twitter.models import Place

from .conftest import E2ETestData


class TestGetDetail:
    """Tests for get_detail method."""

    async def test_get_detail_returns_place(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching place details returns valid place data."""
        place = await client.twitter.geo.get_detail(test_data.place_id)

        assert isinstance(place, Place)
        assert place.id == test_data.place_id
        assert place.name is not None

    async def test_get_detail_includes_location_info(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test that place data includes location information."""
        place = await client.twitter.geo.get_detail(test_data.place_id)

        # Should have full name and country
        assert place.full_name is not None or place.name is not None


class TestSearch:
    """Tests for search method."""

    async def test_search_by_query_returns_places(self, client: ScrapeBadger) -> None:
        """Test searching for places by name returns paginated response."""
        result = await client.twitter.geo.search(query="San Francisco")

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(p, Place) for p in result.data)

    async def test_search_by_coordinates_returns_places(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test searching for places by coordinates returns paginated response."""
        result = await client.twitter.geo.search(lat=test_data.lat, long=test_data.long)

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(p, Place) for p in result.data)

    async def test_search_with_granularity_city(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test search with city granularity."""
        result = await client.twitter.geo.search(
            lat=test_data.lat, long=test_data.long, granularity="city"
        )

        assert hasattr(result, "data")

    async def test_search_with_granularity_neighborhood(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test search with neighborhood granularity."""
        result = await client.twitter.geo.search(
            lat=test_data.lat, long=test_data.long, granularity="neighborhood"
        )

        assert hasattr(result, "data")

    async def test_search_with_max_results(self, client: ScrapeBadger) -> None:
        """Test search with max_results limit."""
        result = await client.twitter.geo.search(query="New York", max_results=5)

        assert hasattr(result, "data")
        if result.data:
            assert len(result.data) <= 5

    async def test_search_by_ip_returns_places(self, client: ScrapeBadger) -> None:
        """Test searching for places by IP address returns paginated response."""
        # Using Google's public DNS IP for testing
        result = await client.twitter.geo.search(ip="8.8.8.8")

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(p, Place) for p in result.data)

    async def test_search_combined_query_and_coordinates(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test search combining query with coordinates."""
        result = await client.twitter.geo.search(
            query="cafe",
            lat=test_data.lat,
            long=test_data.long,
        )

        assert hasattr(result, "data")
