"""ChatGPT Reference Data API client.

Provides the list of models chatgpt.com currently offers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.chatgpt.models import ModelsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ReferenceClient:
    """Client for ChatGPT reference data endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            result = await client.chatgpt.reference.models()
            for model in result.models:
                print(f"{model.slug}: {model.title}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize reference client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def models(self, *, country: str = "US") -> ModelsResponse:
        """Get the models chatgpt.com currently offers.

        Costs 1 credit.

        Args:
            country: ISO-3166 alpha-2 egress country. Defaults to "US".

        Returns:
            The available models.

        Example:
            ```python
            result = await client.chatgpt.reference.models()
            print(f"{result.count} models")
            for model in result.models:
                print(f"{model.slug}: {model.max_tokens} tokens")
            ```
        """
        response = await self._client.get(
            "/v1/chatgpt/models",
            params={"country": country},
        )
        return ModelsResponse.model_validate(response)
