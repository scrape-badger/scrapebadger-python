"""Instagram hashtag, location, and audio API clients.

These endpoints return standalone entities plus their associated media feeds,
so they live together in one reference module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.instagram.models import (
    Audio,
    Hashtag,
    Location,
    Media,
    Paginated,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class HashtagsClient:
    """Client for Instagram hashtag endpoints."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def get(self, tag: str) -> Hashtag:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get a hashtag's info (media count, cover).
        """
        response = await self._client.get(f"/v1/instagram/hashtags/{tag}")
        return Hashtag.model_validate(response)

    async def top(
        self, tag: str, *, amount: int = 20, cursor: str | None = None
    ) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get the top/popular media for a hashtag.
        """
        return await _media(self._client, f"/v1/instagram/hashtags/{tag}/top", amount, cursor)

    async def recent(
        self, tag: str, *, amount: int = 20, cursor: str | None = None
    ) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get the most recent media for a hashtag.
        """
        return await _media(self._client, f"/v1/instagram/hashtags/{tag}/recent", amount, cursor)

    async def reels(
        self, tag: str, *, amount: int = 20, cursor: str | None = None
    ) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get reels for a hashtag.
        """
        return await _media(self._client, f"/v1/instagram/hashtags/{tag}/reels", amount, cursor)


class LocationsClient:
    """Client for Instagram location endpoints."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def get(self, pk: str) -> Location:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get a location's info.
        """
        response = await self._client.get(f"/v1/instagram/locations/{pk}")
        return Location.model_validate(response)

    async def top(
        self, pk: str, *, amount: int = 20, cursor: str | None = None
    ) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get the top/popular media for a location.
        """
        return await _media(self._client, f"/v1/instagram/locations/{pk}/top", amount, cursor)

    async def recent(
        self, pk: str, *, amount: int = 20, cursor: str | None = None
    ) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get the most recent media for a location.
        """
        return await _media(self._client, f"/v1/instagram/locations/{pk}/recent", amount, cursor)

    async def search(self, query: str) -> Paginated[Location]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Search locations by name.
        """
        params: dict[str, Any] = {"query": query}
        response = await self._client.get("/v1/instagram/locations/search", params=params)
        return Paginated[Location].model_validate(response)


class AudioClient:
    """Client for Instagram audio/music endpoints."""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def get(self, audio_id: str) -> Audio:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get an audio track's info.
        """
        response = await self._client.get(f"/v1/instagram/audio/{audio_id}")
        return Audio.model_validate(response)

    async def media(
        self, audio_id: str, *, amount: int = 20, cursor: str | None = None
    ) -> Paginated[Media]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get media that use an audio track.
        """
        return await _media(self._client, f"/v1/instagram/audio/{audio_id}/media", amount, cursor)

    async def trending(self) -> Paginated[Audio]:
        """Temporarily unavailable: authenticated Instagram data is temporarily offline.

        Get currently-trending audio tracks.
        """
        response = await self._client.get("/v1/instagram/audio/trending")
        return Paginated[Audio].model_validate(response)


async def _media(
    client: BaseClient, path: str, amount: int, cursor: str | None
) -> Paginated[Media]:
    params: dict[str, Any] = {"amount": amount, "cursor": cursor}
    response = await client.get(path, params=params)
    return Paginated[Media].model_validate(response)
