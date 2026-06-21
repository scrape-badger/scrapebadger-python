"""YouTube Playlists API client.

Provides methods for playlist detail, a continuation page of playlist items, and
auto-generated mix / radio queues.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.youtube.models import Playlist, PlaylistItemsResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class PlaylistsClient:
    """Client for YouTube playlist and mix endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            playlist = await client.youtube.playlists.get_playlist("PLxxxx")
            for item in playlist.videos:
                print(item.position, item.title)

            page = await client.youtube.playlists.get_items(
                "PLxxxx", continuation=playlist.continuation
            )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize playlists client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_playlist(
        self,
        playlist_id: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> Playlist:
        """Get a playlist's full detail plus the first page of items.

        Args:
            playlist_id: The YouTube playlist id.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Full playlist detail with the first page of items and a continuation token.

        Raises:
            NotFoundError: If the playlist doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            playlist = await client.youtube.playlists.get_playlist("PLxxxx")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/playlists/{playlist_id}", params=params)
        return Playlist.model_validate(response)

    async def get_items(
        self,
        playlist_id: str,
        *,
        continuation: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> PlaylistItemsResponse:
        """Get a continuation page of playlist items.

        Args:
            playlist_id: The YouTube playlist id.
            continuation: Pagination token from a previous page.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Playlist items response with items and a continuation token.

        Example:
            ```python
            page = await client.youtube.playlists.get_items(
                "PLxxxx", continuation="token"
            )
            ```
        """
        params: dict[str, Any] = {"continuation": continuation, "gl": gl, "hl": hl}
        response = await self._client.get(
            f"/v1/youtube/playlists/{playlist_id}/items", params=params
        )
        return PlaylistItemsResponse.model_validate(response)

    async def get_mix(
        self,
        playlist_id: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> Playlist:
        """Resolve an auto-generated mix / radio (RD…) queue.

        Args:
            playlist_id: The mix / radio playlist id (typically starts with ``RD``).
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Playlist with ``is_mix=True`` and the resolved queue items.

        Example:
            ```python
            mix = await client.youtube.playlists.get_mix("RDxxxx")
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/mixes/{playlist_id}", params=params)
        return Playlist.model_validate(response)
