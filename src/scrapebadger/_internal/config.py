"""Client configuration for the ScrapeBadger SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Default API base URL
DEFAULT_BASE_URL = "https://api.scrapebadger.com"

# Default timeout in seconds
DEFAULT_TIMEOUT = 300.0  # 5 minutes (matching server MAX_POLL_TIME)

# Default connection timeout
DEFAULT_CONNECT_TIMEOUT = 10.0


@dataclass(frozen=True, slots=True)
class ClientConfig:
    """Configuration for the ScrapeBadger client.

    This class holds all configuration options for the SDK client.
    It is immutable after creation to prevent accidental modifications.

    Attributes:
        api_key: Your ScrapeBadger API key.
        base_url: The API base URL. Defaults to production API.
        timeout: Request timeout in seconds. Defaults to 300s (5 minutes).
        connect_timeout: Connection timeout in seconds. Defaults to 10s.
        max_retries: Maximum number of retries for failed requests. Defaults to 3.
        retry_on_status: HTTP status codes that trigger a retry.
        headers: Additional headers to include in all requests.

    Example:
        ```python
        from scrapebadger import ScrapeBadger
        from scrapebadger._internal import ClientConfig

        config = ClientConfig(
            api_key="your-api-key",
            timeout=120.0,
            max_retries=5,
        )
        client = ScrapeBadger(config=config)
        ```
    """

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT
    max_retries: int = 3
    retry_on_status: tuple[int, ...] = (502, 503, 504)
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.api_key:
            msg = "API key is required"
            raise ValueError(msg)
        if self.timeout <= 0:
            msg = "Timeout must be positive"
            raise ValueError(msg)
        if self.connect_timeout <= 0:
            msg = "Connect timeout must be positive"
            raise ValueError(msg)
        if self.max_retries < 0:
            msg = "Max retries cannot be negative"
            raise ValueError(msg)

    def with_overrides(self, **kwargs: Any) -> ClientConfig:
        """Create a new config with overridden values.

        Args:
            **kwargs: Configuration values to override.

        Returns:
            A new ClientConfig instance with the overridden values.

        Example:
            ```python
            config = ClientConfig(api_key="key")
            new_config = config.with_overrides(timeout=60.0)
            ```
        """
        current: dict[str, Any] = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "connect_timeout": self.connect_timeout,
            "max_retries": self.max_retries,
            "retry_on_status": self.retry_on_status,
            "headers": dict(self.headers),
        }
        current.update(kwargs)
        return ClientConfig(**current)
