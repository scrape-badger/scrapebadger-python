"""Tests for client configuration."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from scrapebadger._internal.config import (
    DEFAULT_BASE_URL,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_TIMEOUT,
    ClientConfig,
)


class TestClientConfig:
    """Tests for ClientConfig."""

    def test_default_values(self, api_key: str) -> None:
        """Test default configuration values."""
        config = ClientConfig(api_key=api_key)

        assert config.api_key == api_key
        assert config.base_url == DEFAULT_BASE_URL
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.connect_timeout == DEFAULT_CONNECT_TIMEOUT
        assert config.max_retries == 3
        assert config.retry_on_status == (502, 503, 504)
        assert config.headers == {}

    def test_custom_values(self, api_key: str) -> None:
        """Test custom configuration values."""
        config = ClientConfig(
            api_key=api_key,
            base_url="https://custom.api.com",
            timeout=60.0,
            connect_timeout=5.0,
            max_retries=5,
            retry_on_status=(500, 502),
            headers={"X-Custom": "value"},
        )

        assert config.base_url == "https://custom.api.com"
        assert config.timeout == 60.0
        assert config.connect_timeout == 5.0
        assert config.max_retries == 5
        assert config.retry_on_status == (500, 502)
        assert config.headers == {"X-Custom": "value"}

    def test_empty_api_key_raises_error(self) -> None:
        """Test that empty API key raises error."""
        with pytest.raises(ValueError, match="API key is required"):
            ClientConfig(api_key="")

    def test_negative_timeout_raises_error(self, api_key: str) -> None:
        """Test that negative timeout raises error."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            ClientConfig(api_key=api_key, timeout=-1.0)

    def test_zero_timeout_raises_error(self, api_key: str) -> None:
        """Test that zero timeout raises error."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            ClientConfig(api_key=api_key, timeout=0.0)

    def test_negative_connect_timeout_raises_error(self, api_key: str) -> None:
        """Test that negative connect timeout raises error."""
        with pytest.raises(ValueError, match="Connect timeout must be positive"):
            ClientConfig(api_key=api_key, connect_timeout=-1.0)

    def test_negative_retries_raises_error(self, api_key: str) -> None:
        """Test that negative retries raises error."""
        with pytest.raises(ValueError, match="Max retries cannot be negative"):
            ClientConfig(api_key=api_key, max_retries=-1)

    def test_config_is_frozen(self, api_key: str) -> None:
        """Test that config is immutable."""
        config = ClientConfig(api_key=api_key)
        with pytest.raises(FrozenInstanceError):
            config.api_key = "new_key"  # type: ignore[misc]

    def test_with_overrides(self, api_key: str) -> None:
        """Test creating config with overrides."""
        config = ClientConfig(api_key=api_key)
        new_config = config.with_overrides(timeout=60.0, max_retries=5)

        # Original unchanged
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.max_retries == 3

        # New config has overrides
        assert new_config.timeout == 60.0
        assert new_config.max_retries == 5
        assert new_config.api_key == api_key
