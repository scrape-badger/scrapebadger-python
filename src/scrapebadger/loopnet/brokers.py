"""LoopNet Brokers API client.

Provides a broker/professional's profile and their active listings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.loopnet.models import BrokerResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class BrokersClient:
    """Client for the LoopNet broker profile endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            profile = await client.loopnet.brokers.get("jane-doe", "w7x123")
            print(profile.broker.name, profile.broker.company)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize brokers client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get(
        self,
        slug: str,
        broker_id: str,
        *,
        market: str = "us",
    ) -> BrokerResponse:
        """Get a LoopNet broker's profile and their listings. Costs 8 credits.

        Args:
            slug: The broker's URL slug (e.g. "jane-doe").
            broker_id: The LoopNet broker id.
            market: Coverage market ("us", "ca", "uk", "fr", "es"). Defaults to "us".

        Returns:
            Broker profile response with the broker and their listings.

        Raises:
            NotFoundError: If the broker doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            profile = await client.loopnet.brokers.get("jane-doe", "w7x123")
            for card in profile.broker.listings:
                print(card.address)
            ```
        """
        params: dict[str, Any] = {"market": market}
        response = await self._client.get(f"/v1/loopnet/brokers/{slug}/{broker_id}", params=params)
        return BrokerResponse.model_validate(response)
