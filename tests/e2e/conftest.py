"""E2E test configuration and fixtures.

These tests make real API calls against the ScrapeBadger API.
Requires SCRAPEBADGER_API_KEY and SCRAPEBADGER_BASE_URL environment variables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from scrapebadger import ScrapeBadger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "e2e: mark test as end-to-end test requiring real API access",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Add e2e marker to all tests in e2e directory."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


@dataclass(frozen=True)
class E2ETestData:
    """Test data for e2e tests.

    Uses stable public accounts and resources that are unlikely to change.
    Override via environment variables if needed.
    """

    # User test data
    username: str = "X"  # Twitter/X official account (stable)
    username_alt: str = "elonmusk"  # Elon Musk (active, stable)
    user_id: str = "783214"  # @X user ID

    # Tweet test data - use recent tweets from stable accounts
    # These may need periodic updates if tweets are deleted
    tweet_id: str = "1802331592918618529"

    # List test data - use public lists
    list_id: str = "1736495155853967360"

    # Community test data
    community_id: str = "1493016274714259462"

    # Geo test data
    place_id: str = "5a110d312052166f"  # San Francisco
    lat: float = 37.7749
    long: float = -122.4194

    # Trend test data
    woeid_us: int = 23424977  # United States
    woeid_worldwide: int = 1  # Worldwide

    @classmethod
    def from_env(cls) -> E2ETestData:
        """Create test data from environment variables with fallbacks."""
        return cls(
            username=os.environ.get("TEST_USERNAME", cls.username),
            username_alt=os.environ.get("TEST_USERNAME_ALT", cls.username_alt),
            user_id=os.environ.get("TEST_USER_ID", cls.user_id),
            tweet_id=os.environ.get("TEST_TWEET_ID", cls.tweet_id),
            list_id=os.environ.get("TEST_LIST_ID", cls.list_id),
            community_id=os.environ.get("TEST_COMMUNITY_ID", cls.community_id),
            place_id=os.environ.get("TEST_PLACE_ID", cls.place_id),
        )


@pytest.fixture(scope="session")
def api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("SCRAPEBADGER_API_KEY")
    if not key:
        pytest.skip("SCRAPEBADGER_API_KEY environment variable not set")
    return key


@pytest.fixture(scope="session")
def base_url() -> str:
    """Get base URL from environment."""
    return os.environ.get("SCRAPEBADGER_BASE_URL", "https://scrapebadger.com")


@pytest.fixture(scope="session")
def test_data() -> E2ETestData:
    """Get test data with environment variable overrides."""
    return E2ETestData.from_env()


@pytest.fixture
async def client(api_key: str, base_url: str) -> AsyncGenerator[ScrapeBadger, None]:
    """Create a ScrapeBadger client for e2e tests.

    This fixture creates a new client for each test to ensure isolation.
    """
    async with ScrapeBadger(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,  # Longer timeout for e2e tests
        max_retries=2,
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def session_client(api_key: str, base_url: str) -> AsyncGenerator[ScrapeBadger, None]:
    """Create a session-scoped ScrapeBadger client.

    Use this for tests that can share a client to reduce connection overhead.
    """
    async with ScrapeBadger(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,
        max_retries=2,
    ) as client:
        yield client
