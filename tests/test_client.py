"""Tests for the main ScrapeBadger client."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scrapebadger import ScrapeBadger
from scrapebadger.twitter.client import TwitterClient

if TYPE_CHECKING:
    from scrapebadger._internal.config import ClientConfig


class TestScrapeBadgerClient:
    """Tests for the ScrapeBadger client."""

    def test_init_with_api_key(self, api_key: str) -> None:
        """Test client initialization with API key."""
        client = ScrapeBadger(api_key=api_key)
        assert client.config.api_key == api_key
        assert client.config.base_url == "https://scrapebadger.com"

    def test_init_with_custom_base_url(self, api_key: str) -> None:
        """Test client initialization with custom base URL."""
        client = ScrapeBadger(
            api_key=api_key,
            base_url="https://custom.api.com",
        )
        assert client.config.base_url == "https://custom.api.com"

    def test_init_with_custom_timeout(self, api_key: str) -> None:
        """Test client initialization with custom timeout."""
        client = ScrapeBadger(api_key=api_key, timeout=60.0)
        assert client.config.timeout == 60.0

    def test_init_with_custom_retries(self, api_key: str) -> None:
        """Test client initialization with custom retries."""
        client = ScrapeBadger(api_key=api_key, max_retries=5)
        assert client.config.max_retries == 5

    def test_init_with_config(self, config: ClientConfig) -> None:
        """Test client initialization with config object."""
        client = ScrapeBadger(config=config)
        assert client.config == config

    def test_init_without_api_key_raises_error(self) -> None:
        """Test that initialization without API key raises error."""
        with pytest.raises(ValueError, match="API key is required"):
            ScrapeBadger(api_key=None)

    def test_twitter_property(self, api_key: str) -> None:
        """Test twitter property returns TwitterClient."""
        client = ScrapeBadger(api_key=api_key)
        assert isinstance(client.twitter, TwitterClient)

    def test_twitter_property_is_cached(self, api_key: str) -> None:
        """Test twitter property returns same instance."""
        client = ScrapeBadger(api_key=api_key)
        twitter1 = client.twitter
        twitter2 = client.twitter
        assert twitter1 is twitter2

    def test_repr(self, api_key: str) -> None:
        """Test string representation."""
        client = ScrapeBadger(api_key=api_key)
        assert "ScrapeBadger" in repr(client)
        assert "scrapebadger.com" in repr(client)

    async def test_context_manager(self, api_key: str) -> None:
        """Test async context manager."""
        async with ScrapeBadger(api_key=api_key) as client:
            assert isinstance(client, ScrapeBadger)

    async def test_close(self, api_key: str) -> None:
        """Test close method."""
        client = ScrapeBadger(api_key=api_key)
        await client.close()
        # Should not raise when called multiple times
        await client.close()
