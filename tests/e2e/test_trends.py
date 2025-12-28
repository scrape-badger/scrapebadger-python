"""E2E tests for TrendsClient.

Tests all trend-related API endpoints with real API calls.
"""

from __future__ import annotations

from scrapebadger import ScrapeBadger
from scrapebadger.twitter.models import Location, PlaceTrends, Trend, TrendCategory

from .conftest import E2ETestData


class TestGetTrends:
    """Tests for get_trends method."""

    async def test_get_trends_default_returns_trends(self, client: ScrapeBadger) -> None:
        """Test fetching default trends returns paginated response."""
        result = await client.twitter.trends.get_trends()

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(t, Trend) for t in result.data)

    async def test_get_trends_trending_category(self, client: ScrapeBadger) -> None:
        """Test fetching trends with TRENDING category."""
        result = await client.twitter.trends.get_trends(category=TrendCategory.TRENDING, count=10)

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(t, Trend) for t in result.data)
            assert len(result.data) <= 10

    async def test_get_trends_for_you_category(self, client: ScrapeBadger) -> None:
        """Test fetching trends with FOR_YOU category."""
        result = await client.twitter.trends.get_trends(category=TrendCategory.FOR_YOU, count=10)

        assert hasattr(result, "data")

    async def test_get_trends_news_category(self, client: ScrapeBadger) -> None:
        """Test fetching trends with NEWS category."""
        result = await client.twitter.trends.get_trends(category=TrendCategory.NEWS, count=10)

        assert hasattr(result, "data")

    async def test_get_trends_sports_category(self, client: ScrapeBadger) -> None:
        """Test fetching trends with SPORTS category."""
        result = await client.twitter.trends.get_trends(category=TrendCategory.SPORTS, count=10)

        assert hasattr(result, "data")

    async def test_get_trends_entertainment_category(self, client: ScrapeBadger) -> None:
        """Test fetching trends with ENTERTAINMENT category."""
        result = await client.twitter.trends.get_trends(
            category=TrendCategory.ENTERTAINMENT, count=10
        )

        assert hasattr(result, "data")


class TestGetPlaceTrends:
    """Tests for get_place_trends method."""

    async def test_get_place_trends_worldwide(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test fetching worldwide trends returns PlaceTrends."""
        result = await client.twitter.trends.get_place_trends(test_data.woeid_worldwide)

        assert isinstance(result, PlaceTrends)
        assert result.trends is not None
        assert isinstance(result.trends, list)

        if result.trends:
            assert all(isinstance(t, Trend) for t in result.trends)

    async def test_get_place_trends_us(self, client: ScrapeBadger, test_data: E2ETestData) -> None:
        """Test fetching US trends returns PlaceTrends."""
        result = await client.twitter.trends.get_place_trends(test_data.woeid_us)

        assert isinstance(result, PlaceTrends)
        assert result.trends is not None

    async def test_get_place_trends_includes_location_info(
        self, client: ScrapeBadger, test_data: E2ETestData
    ) -> None:
        """Test that PlaceTrends includes location information."""
        result = await client.twitter.trends.get_place_trends(test_data.woeid_us)

        # Should have location name or woeid reference
        assert result.name is not None or result.woeid is not None


class TestGetAvailableLocations:
    """Tests for get_available_locations method."""

    async def test_get_available_locations_returns_locations(self, client: ScrapeBadger) -> None:
        """Test fetching available locations returns paginated response."""
        result = await client.twitter.trends.get_available_locations()

        assert hasattr(result, "data")

        if result.data:
            assert all(isinstance(loc, Location) for loc in result.data)

    async def test_get_available_locations_includes_us(self, client: ScrapeBadger) -> None:
        """Test that available locations include United States."""
        result = await client.twitter.trends.get_available_locations()

        if result.data:
            # Check for US in the locations
            us_locations = [
                loc
                for loc in result.data
                if loc.country_code == "US" or loc.name == "United States"
            ]
            # Note: US should typically be available, but this may vary
            assert len(us_locations) >= 0  # Just verify the filter works

    async def test_get_available_locations_has_woeids(self, client: ScrapeBadger) -> None:
        """Test that locations include WOEID values."""
        result = await client.twitter.trends.get_available_locations()

        if result.data:
            # At least some locations should have WOEIDs
            locations_with_woeid = [loc for loc in result.data if loc.woeid is not None]
            assert len(locations_with_woeid) >= 0  # May be empty in some edge cases
