"""YouTube Transcript API client.

Provides methods for fetching a video transcript and listing caption tracks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapebadger.youtube.models import CaptionsResponse, Transcript

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class TranscriptClient:
    """Client for YouTube transcript and caption-track endpoints.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            transcript = await client.youtube.transcript.get_transcript("dQw4w9WgXcQ")
            print(transcript.full_text)

            captions = await client.youtube.transcript.get_captions("dQw4w9WgXcQ")
            for track in captions.tracks:
                print(track.language, track.language_name)
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize transcript client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def get_transcript(
        self,
        video_id: str,
        *,
        language: str | None = None,
        gl: str | None = None,
        hl: str | None = None,
    ) -> Transcript:
        """Get a video transcript in the selected language.

        Args:
            video_id: The YouTube video id.
            language: BCP-47 language code to prefer (e.g. "en", "es").
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Transcript with timed segments, full text, and SRT/VTT renderings.

        Raises:
            NotFoundError: If the video doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            transcript = await client.youtube.transcript.get_transcript(
                "dQw4w9WgXcQ", language="en"
            )
            for seg in transcript.segments:
                print(seg.start_time_text, seg.text)
            ```
        """
        params: dict[str, Any] = {"language": language, "gl": gl, "hl": hl}
        response = await self._client.get(
            f"/v1/youtube/videos/{video_id}/transcript", params=params
        )
        return Transcript.model_validate(response)

    async def get_captions(
        self,
        video_id: str,
        *,
        gl: str | None = None,
        hl: str | None = None,
    ) -> CaptionsResponse:
        """List the available caption tracks for a video.

        Args:
            video_id: The YouTube video id.
            gl: Content region (US, GB, DE…).
            hl: UI language.

        Returns:
            Captions response with caption tracks and translation languages.

        Example:
            ```python
            captions = await client.youtube.transcript.get_captions("dQw4w9WgXcQ")
            for track in captions.tracks:
                print(track.language, track.type)
            ```
        """
        params: dict[str, Any] = {"gl": gl, "hl": hl}
        response = await self._client.get(f"/v1/youtube/videos/{video_id}/captions", params=params)
        return CaptionsResponse.model_validate(response)
