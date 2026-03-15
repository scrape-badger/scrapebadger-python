"""Twitter Spaces API client.

Provides methods for fetching Twitter Space and broadcast details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.twitter.models import Broadcast, Space

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class SpacesClient:
    """Client for Twitter Spaces endpoints.

    Provides async methods for fetching Space details and live broadcast information.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Get Space details
            space = await client.twitter.spaces.get_detail("1YqJDqDpqzAxV")
            print(f"{space.title} ({space.state})")
            print(f"Participants: {space.participant_count}")

            # Get broadcast details
            broadcast = await client.twitter.spaces.get_broadcast("1zqKVBnwwPoxB")
            print(f"{broadcast.title}: {broadcast.total_viewers} viewers")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize spaces client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_detail(self, space_id: str) -> Space:
        """Get details for a Twitter Space.

        Args:
            space_id: The Space ID.

        Returns:
            The Space details.

        Raises:
            NotFoundError: If the Space doesn't exist.

        Example:
            ```python
            space = await client.twitter.spaces.get_detail("1YqJDqDpqzAxV")
            print(f"{space.title} — {space.state}")
            print(f"Created by @{space.creator_username}")
            ```
        """
        response = await self._client.get(f"/v1/twitter/spaces/{space_id}")
        return Space.model_validate(response)

    async def get_broadcast(self, broadcast_id: str) -> Broadcast:
        """Get details for a live video broadcast.

        Args:
            broadcast_id: The broadcast ID.

        Returns:
            The broadcast details.

        Raises:
            NotFoundError: If the broadcast doesn't exist.

        Example:
            ```python
            broadcast = await client.twitter.spaces.get_broadcast("1zqKVBnwwPoxB")
            print(f"{broadcast.title} ({broadcast.state})")
            print(f"Total viewers: {broadcast.total_viewers}")
            ```
        """
        response = await self._client.get(f"/v1/twitter/spaces/broadcast/{broadcast_id}")
        return Broadcast.model_validate(response)
