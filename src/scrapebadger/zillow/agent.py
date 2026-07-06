"""Zillow Agent API client.

Provides the method for fetching a real-estate professional's profile and
their active listings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.zillow.models import Agent, AgentResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AgentClient:
    """Client for the Zillow agent-profile endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            agent = await client.zillow.agents.get_agent(username="jane-doe")
            print(agent.name, agent.rating, agent.review_count)
            for sale in agent.past_sales:
                print(sale.street_address, sale.price)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize agent client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_agent(
        self,
        username: str | None = None,
        *,
        url: str | None = None,
    ) -> Agent:
        """Get a Zillow professional's profile and their active listings.

        Provide either a ``username`` (the profile screen name) or a full
        profile ``url``.

        Args:
            username: Zillow profile username (screen name).
            url: Full Zillow /profile/... URL.

        Returns:
            The agent profile including reviews, past sales, licenses, service
            areas, contact info, and their active listings.

        Raises:
            NotFoundError: If the agent doesn't exist.
            AuthenticationError: If the API key is invalid.
            ValidationError: If neither ``username`` nor ``url`` is provided.

        Example:
            ```python
            agent = await client.zillow.agents.get_agent(username="jane-doe")
            for review in agent.reviews:
                print(review.rating, review.comment)
            ```
        """
        params: dict[str, Any] = {"username": username, "url": url}
        response = await self._client.get("/v1/zillow/agent", params=params)
        return AgentResponse.model_validate(response).agent
