"""Instagram Media API client.

Fetches media details, oEmbed metadata, comments, comment replies, and the
users who liked a media or a comment.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.instagram.models import (
    Comment,
    Media,
    Oembed,
    Paginated,
    UserShort,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class MediaClient:
    """Client for Instagram media endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            media = await client.instagram.media.get("C1abcdEfGhI")
            print(media.caption_text, media.like_count)

            comments = await client.instagram.media.comments(media.code, amount=20)
            for comment in comments.items:
                print(f"@{comment.user.username}: {comment.text}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def get(self, code: str) -> Media:
        """Get a media's full details.

        Args:
            code: The media shortcode (from the ``/p/<code>/`` URL).
        """
        response = await self._client.get(f"/v1/instagram/media/{code}")
        return Media.model_validate(response)

    async def oembed(self, code: str) -> Oembed:
        """Get oEmbed metadata for a media permalink."""
        response = await self._client.get(f"/v1/instagram/media/{code}/oembed")
        return Oembed.model_validate(response)

    async def comments(
        self,
        code: str,
        *,
        amount: int = 20,
        cursor: str | None = None,
    ) -> Paginated[Comment]:
        """Get top-level comments on a media."""
        params: dict[str, Any] = {"amount": amount, "cursor": cursor}
        response = await self._client.get(f"/v1/instagram/media/{code}/comments", params=params)
        return Paginated[Comment].model_validate(response)

    async def likers(self, code: str) -> Paginated[UserShort]:
        """Get the users who liked a media."""
        response = await self._client.get(f"/v1/instagram/media/{code}/likers")
        return Paginated[UserShort].model_validate(response)

    async def replies(
        self,
        code: str,
        comment_id: str,
        *,
        amount: int = 20,
        cursor: str | None = None,
    ) -> Paginated[Comment]:
        """Get replies to a comment."""
        params: dict[str, Any] = {"amount": amount, "cursor": cursor}
        response = await self._client.get(
            f"/v1/instagram/media/{code}/comments/{comment_id}/replies", params=params
        )
        return Paginated[Comment].model_validate(response)

    async def comment_likers(self, code: str, comment_id: str) -> Paginated[UserShort]:
        """Get the users who liked a comment."""
        response = await self._client.get(
            f"/v1/instagram/media/{code}/comments/{comment_id}/likers"
        )
        return Paginated[UserShort].model_validate(response)
