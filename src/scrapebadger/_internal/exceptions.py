"""Custom exceptions for the ScrapeBadger SDK.

All exceptions inherit from ScrapeBadgerError, allowing for easy
catching of all SDK-related errors.

Example:
    ```python
    try:
        tweets = await client.twitter.tweets.get_by_id("123456")
    except RateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after}s")
    except AuthenticationError:
        print("Invalid API key")
    except ScrapeBadgerError as e:
        print(f"API error: {e}")
    ```
"""

from __future__ import annotations

from typing import Any


class ScrapeBadgerError(Exception):
    """Base exception for all ScrapeBadger SDK errors.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code if applicable.
        response_data: Raw response data from the API.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, status_code={self.status_code})"


class AuthenticationError(ScrapeBadgerError):
    """Raised when API key authentication fails.

    This typically occurs when:
    - The API key is missing
    - The API key is invalid or revoked
    - The API key has been disabled

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        # This will raise AuthenticationError
        client = ScrapeBadger(api_key="invalid-key")
        await client.twitter.users.get_by_username("elonmusk")
        ```
    """

    def __init__(
        self,
        message: str = "Invalid or missing API key",
        status_code: int = 401,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, response_data)


class RateLimitError(ScrapeBadgerError):
    """Raised when rate limit is exceeded.

    Attributes:
        limit: Maximum requests allowed per minute.
        remaining: Requests remaining in current window.
        reset_at: Unix timestamp when the rate limit resets.
        retry_after: Seconds until the rate limit resets.
        tier: The user's current rate limit tier.

    Example:
        ```python
        try:
            tweets = await client.twitter.tweets.search("python")
        except RateLimitError as e:
            print(f"Rate limited. Wait {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
        ```
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int = 429,
        response_data: dict[str, Any] | None = None,
        *,
        limit: int | None = None,
        remaining: int | None = None,
        reset_at: int | None = None,
        retry_after: int | None = None,
        tier: str | None = None,
    ) -> None:
        super().__init__(message, status_code, response_data)
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at
        self.retry_after = retry_after
        self.tier = tier


class InsufficientCreditsError(ScrapeBadgerError):
    """Raised when the account has insufficient credits.

    This occurs when your credit balance reaches zero. You'll need
    to purchase more credits to continue making API calls.

    Example:
        ```python
        try:
            tweets = await client.twitter.tweets.search("python")
        except InsufficientCreditsError:
            print("Out of credits! Visit dashboard to purchase more.")
        ```
    """

    def __init__(
        self,
        message: str = "Insufficient credits. Please purchase more credits.",
        status_code: int = 402,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, response_data)


class NotFoundError(ScrapeBadgerError):
    """Raised when the requested resource is not found.

    This typically occurs when:
    - The tweet/user/list ID doesn't exist
    - The user has been suspended or deleted
    - The content has been removed

    Example:
        ```python
        try:
            user = await client.twitter.users.get_by_username("nonexistent")
        except NotFoundError:
            print("User not found")
        ```
    """

    def __init__(
        self,
        message: str = "Resource not found",
        status_code: int = 404,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, response_data)


class ValidationError(ScrapeBadgerError):
    """Raised when request parameters are invalid.

    This occurs when:
    - Required parameters are missing
    - Parameter values are out of valid range
    - Parameter types are incorrect

    Example:
        ```python
        try:
            # Empty query will raise ValidationError
            tweets = await client.twitter.tweets.search("")
        except ValidationError as e:
            print(f"Invalid parameters: {e}")
        ```
    """

    def __init__(
        self,
        message: str = "Invalid request parameters",
        status_code: int = 422,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, response_data)


class ServerError(ScrapeBadgerError):
    """Raised when the server encounters an error.

    This indicates an issue on the ScrapeBadger server side.
    These are typically temporary and can be retried.

    Example:
        ```python
        import asyncio
        from scrapebadger import ServerError

        async def fetch_with_retry(client, retries=3):
            for attempt in range(retries):
                try:
                    return await client.twitter.users.get_by_username("elonmusk")
                except ServerError:
                    if attempt < retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise
        ```
    """

    def __init__(
        self,
        message: str = "Server error occurred",
        status_code: int = 500,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, response_data)


class WebSocketStreamError(ScrapeBadgerError):
    """Raised when the WebSocket stream connection fails or is terminated.

    Attributes:
        code: WebSocket close code or server error code (4001, 4003, etc.).
              None if the error is a network-level failure.

    Common codes:
        4001 -- Invalid or missing API key (auth failure)
        4003 -- Connection limit exceeded (max 5 per API key)
        1001 -- Server closed due to pong timeout

    Example:
        ```python
        from scrapebadger import WebSocketStreamError

        try:
            async with client.twitter.stream.connect() as events:
                async for event in events:
                    ...
        except WebSocketStreamError as e:
            if e.code == 4001:
                print("API key rejected -- check your key")
            else:
                print(f"Stream error: {e}")
        ```
    """

    def __init__(
        self,
        message: str = "WebSocket stream error",
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        *,
        code: int | None = None,
    ) -> None:
        super().__init__(message, status_code, response_data)
        self.code = code
