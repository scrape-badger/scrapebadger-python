"""Base HTTP client for the ScrapeBadger SDK."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, TypeVar

import httpx

from scrapebadger._internal.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    NotFoundError,
    RateLimitError,
    ScrapeBadgerError,
    ServerError,
    ValidationError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType

    from scrapebadger._internal.config import ClientConfig

T = TypeVar("T")

# User agent for SDK requests
SDK_VERSION = "0.1.1"
USER_AGENT = f"scrapebadger-python/{SDK_VERSION}"


class BaseClient:
    """Base HTTP client with retry logic and error handling.

    This client handles all HTTP communication with the ScrapeBadger API,
    including authentication, retries, and error mapping.

    The client should be used as an async context manager to ensure
    proper resource cleanup:

    Example:
        ```python
        async with BaseClient(config) as client:
            response = await client.get("/v1/twitter/users/elonmusk/by_username")
        ```
    """

    def __init__(self, config: ClientConfig) -> None:
        """Initialize the base client.

        Args:
            config: Client configuration including API key and options.
        """
        self._config = config
        self._client: httpx.AsyncClient | None = None

    @property
    def config(self) -> ClientConfig:
        """Get the client configuration."""
        return self._config

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            timeout = httpx.Timeout(
                timeout=self._config.timeout,
                connect=self._config.connect_timeout,
            )
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "x-api-key": self._config.api_key,
                **self._config.headers,
            }
            self._client = httpx.AsyncClient(
                base_url=self._config.base_url,
                timeout=timeout,
                headers=headers,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> BaseClient:
        """Enter async context manager."""
        await self._get_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager."""
        await self.close()

    def _handle_error_response(
        self,
        response: httpx.Response,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Handle error responses and raise appropriate exceptions.

        Args:
            response: The HTTP response object.
            data: Parsed response data if available.

        Raises:
            AuthenticationError: For 401 responses.
            InsufficientCreditsError: For 402 responses.
            NotFoundError: For 404 responses.
            ValidationError: For 422 responses.
            RateLimitError: For 429 responses.
            ServerError: For 5xx responses.
            ScrapeBadgerError: For other error responses.
        """
        status_code = response.status_code
        data = data or {}

        # Extract error message from response
        message = data.get("detail", data.get("error", response.reason_phrase))
        if isinstance(message, list):
            # Handle FastAPI validation errors
            errors = [f"{e.get('loc', [])}: {e.get('msg', '')}" for e in message]
            message = "; ".join(errors)

        if status_code == 401:
            raise AuthenticationError(message, status_code, data)

        if status_code == 402:
            raise InsufficientCreditsError(message, status_code, data)

        if status_code == 404:
            raise NotFoundError(message, status_code, data)

        if status_code == 422:
            raise ValidationError(message, status_code, data)

        if status_code == 429:
            raise RateLimitError(
                message,
                status_code,
                data,
                limit=data.get("limit"),
                remaining=data.get("remaining"),
                reset_at=data.get("reset_at"),
                retry_after=int(response.headers.get("Retry-After", 60)),
                tier=data.get("tier"),
            )

        if status_code >= 500:
            raise ServerError(message, status_code, data)

        raise ScrapeBadgerError(message, status_code, data)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            params: Query parameters.
            json: JSON body for POST/PUT requests.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            ScrapeBadgerError: For API errors.
            httpx.RequestError: For network errors after retries exhausted.
        """
        client = await self._get_client()

        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        last_exception: Exception | None = None
        for attempt in range(self._config.max_retries + 1):
            try:
                response = await client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json,
                )

                # Parse response
                try:
                    data: dict[str, Any] = response.json()
                except Exception:
                    data = {}

                # Check for errors
                if response.status_code >= 400:
                    # Don't retry client errors (except specific status codes)
                    if response.status_code not in self._config.retry_on_status:
                        self._handle_error_response(response, data)

                    # Retry on configured status codes
                    if attempt < self._config.max_retries:
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue

                    self._handle_error_response(response, data)

                # Check for application-level errors in response
                if data.get("error"):
                    raise ScrapeBadgerError(
                        data["error"],
                        response.status_code,
                        data,
                    )

                return data

            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout) as e:
                last_exception = e
                if attempt < self._config.max_retries:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    continue
                raise

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        msg = "Request failed after retries"
        raise ScrapeBadgerError(msg)

    async def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a GET request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            Parsed JSON response.
        """
        return await self._request("GET", path, params=params)

    async def post(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request.

        Args:
            path: API endpoint path.
            params: Query parameters.
            json: JSON body.

        Returns:
            Parsed JSON response.
        """
        return await self._request("POST", path, params=params, json=json)
