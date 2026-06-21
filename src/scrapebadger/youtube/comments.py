"""YouTube Comments API client.

Provides methods for video comments, comment replies, and community post comments.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.youtube.models import CommentsResponse, RepliesResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class CommentsClient:
    """Client for YouTube comment endpoints (video comments, replies, post comments).

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            comments = await client.youtube.comments.get_comments("dQw4w9WgXcQ")
            for c in comments.comments:
                print(f"{c.author}: {c.text}")

            if comments.comments and comments.comments[0].replies_continuation:
                replies = await client.youtube.comments.get_replies(
                    "dQw4w9WgXcQ",
                    comments.comments[0].comment_id,
                    continuation=comments.comments[0].replies_continuation,
                )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize comments client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_comments(
        self,
        video_id: str,
        *,
        sort_by: str = "top",
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> CommentsResponse:
        """Get a page of top-level comments for a video.

        Args:
            video_id: The YouTube video id.
            sort_by: Comment sort order ("top", "newest"). Defaults to "top".
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Comments response with comments, sorting tokens, and a continuation token.

        Example:
            ```python
            comments = await client.youtube.comments.get_comments(
                "dQw4w9WgXcQ", sort_by="newest"
            )
            ```
        """
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "continuation": continuation,
            "gl": gl,
            "hl": hl,
        }
        response = await self._client.get(f"/v1/youtube/videos/{video_id}/comments", params=params)
        return CommentsResponse.model_validate(response)

    async def get_replies(
        self,
        video_id: str,
        comment_id: str,
        *,
        continuation: str,
        gl: str | None = None,
        hl: str | None = None,
    ) -> RepliesResponse:
        """Get a page of replies to a comment.

        Args:
            video_id: The YouTube video id.
            comment_id: The parent comment id.
            continuation: Replies continuation token (from a comment's
                ``replies_continuation``).
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Replies response with reply comments and a continuation token.

        Example:
            ```python
            replies = await client.youtube.comments.get_replies(
                "dQw4w9WgXcQ", "commentId", continuation="token"
            )
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(
            f"/v1/youtube/videos/{video_id}/comments/{comment_id}/replies", params=params
        )
        return RepliesResponse.model_validate(response)

    async def get_post_comments(
        self,
        post_id: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> CommentsResponse:
        """Get a page of comments on a community post.

        Args:
            post_id: The community post id.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Comments response with comments and a continuation token.

        Example:
            ```python
            comments = await client.youtube.comments.get_post_comments("postId")
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/posts/{post_id}/comments", params=params)
        return CommentsResponse.model_validate(response)
