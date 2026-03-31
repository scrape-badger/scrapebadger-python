"""Vinted Users API client.

Provides methods for fetching Vinted user profiles and their listed items.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.vinted.models import UserItemsResponse, UserProfileResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class UsersClient:
    """Client for Vinted user endpoints.

    Provides async methods for fetching user profiles and browsing
    items listed by a specific user.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            # Get user profile
            result = await client.vinted.users.get_profile(12345)
            print(f"{result.user.login}: {result.user.item_count} items")

            # Get user's items
            items_result = await client.vinted.users.get_items(12345)
            for item in items_result.items:
                print(f"  {item.title}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize users client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_profile(
        self,
        user_id: int,
        *,
        market: str = "fr",
    ) -> UserProfileResponse:
        """Get a Vinted user's profile.

        Args:
            user_id: The numeric user ID.
            market: Vinted market code (e.g. "fr", "de"). Defaults to "fr".

        Returns:
            User profile response with full profile data.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.vinted.users.get_profile(12345, market="fr")
            user = result.user
            print(f"{user.login} from {user.city}, {user.country_code}")
            print(f"Reputation: {user.feedback_reputation}")
            print(f"Items: {user.item_count}")
            ```
        """
        response = await self._client.get(
            f"/v1/vinted/users/{user_id}",
            params={"market": market},
        )
        return UserProfileResponse.model_validate(response)

    async def get_items(
        self,
        user_id: int,
        *,
        market: str = "fr",
        page: int = 1,
        per_page: int = 20,
    ) -> UserItemsResponse:
        """Get items listed by a Vinted user.

        Args:
            user_id: The numeric user ID.
            market: Vinted market code (e.g. "fr", "de"). Defaults to "fr".
            page: Page number (1-indexed). Defaults to 1.
            per_page: Number of items per page. Defaults to 20.

        Returns:
            User items response with the user's listed items and pagination.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            result = await client.vinted.users.get_items(12345, per_page=40)
            print(f"Page {result.pagination.current_page}/{result.pagination.total_pages}")
            for item in result.items:
                print(f"  {item.title} - {item.price.amount} {item.price.currency_code}")
            ```
        """
        response = await self._client.get(
            f"/v1/vinted/users/{user_id}/items",
            params={
                "market": market,
                "page": page,
                "per_page": per_page,
            },
        )
        return UserItemsResponse.model_validate(response)
