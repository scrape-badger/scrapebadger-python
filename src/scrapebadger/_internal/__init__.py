"""Internal utilities for the ScrapeBadger SDK."""

from scrapebadger._internal.client import BaseClient
from scrapebadger._internal.config import ClientConfig
from scrapebadger._internal.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    NotFoundError,
    RateLimitError,
    ScrapeBadgerError,
    ServerError,
    ValidationError,
)
from scrapebadger._internal.pagination import PaginatedResponse, paginate

__all__ = [
    "AuthenticationError",
    "BaseClient",
    "ClientConfig",
    "InsufficientCreditsError",
    "NotFoundError",
    "PaginatedResponse",
    "RateLimitError",
    "ScrapeBadgerError",
    "ServerError",
    "ValidationError",
    "paginate",
]
