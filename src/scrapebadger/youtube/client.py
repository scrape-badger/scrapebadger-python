"""YouTube API client combining all sub-clients.

This module provides the main YoutubeClient class that serves as the
entry point for all YouTube API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.youtube.channels import ChannelsClient
from scrapebadger.youtube.comments import CommentsClient
from scrapebadger.youtube.playlists import PlaylistsClient
from scrapebadger.youtube.reference import ReferenceClient
from scrapebadger.youtube.search import SearchClient
from scrapebadger.youtube.transcript import TranscriptClient
from scrapebadger.youtube.trending import TrendingClient
from scrapebadger.youtube.videos import VideosClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class YoutubeClient:
    """Client for all YouTube API operations.

    This class provides access to all YouTube scraping endpoints through
    organized sub-clients for different resource types. All YouTube list
    endpoints paginate via an opaque ``continuation`` token (no page numbers);
    ``gl`` selects the content region and ``hl`` the UI language.

    Attributes:
        search: Client for search, music search, autocomplete, hashtag, and home.
        videos: Client for video detail, batch, related, streams, live chat,
            oEmbed, and Shorts.
        channels: Client for channel detail, tabs, about, search, resolve, and posts.
        playlists: Client for playlist detail, items, and mixes.
        trending: Client for trending videos and trending Shorts.
        comments: Client for video comments, replies, and community post comments.
        transcript: Client for video transcripts and caption tracks.
        reference: Client for reference data (categories, languages, regions, markets).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search for videos
            results = await client.youtube.search.search("lofi hip hop")
            for r in results.results:
                print(f"{r.position}. {r.title}")

            # Get video detail
            video = await client.youtube.videos.get_video("dQw4w9WgXcQ")
            print(video.title)

            # Get a channel
            channel = await client.youtube.channels.get_channel("@mkbhd")

            # Get supported markets
            markets = await client.youtube.reference.list_markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `youtube` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize YouTube client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._search = SearchClient(client)
        self._videos = VideosClient(client)
        self._channels = ChannelsClient(client)
        self._playlists = PlaylistsClient(client)
        self._trending = TrendingClient(client)
        self._comments = CommentsClient(client)
        self._transcript = TranscriptClient(client)
        self._reference = ReferenceClient(client)

    @property
    def search(self) -> SearchClient:
        """Access search, music search, autocomplete, hashtag, and home endpoints.

        Returns:
            SearchClient for keyword search, YouTube Music, autocomplete, hashtags, and home.

        Example:
            ```python
            results = await client.youtube.search.search("python tutorial")
            songs = await client.youtube.search.music("daft punk")
            suggestions = await client.youtube.search.autocomplete("lofi")
            ```
        """
        return self._search

    @property
    def videos(self) -> VideosClient:
        """Access video detail, batch, related, streams, live chat, oEmbed, and Shorts.

        Returns:
            VideosClient for video and Shorts endpoints.

        Example:
            ```python
            video = await client.youtube.videos.get_video("dQw4w9WgXcQ")
            related = await client.youtube.videos.get_related("dQw4w9WgXcQ")
            batch = await client.youtube.videos.batch(["id1", "id2"])
            ```
        """
        return self._videos

    @property
    def channels(self) -> ChannelsClient:
        """Access channel detail, tabs, about, search, resolve, and post endpoints.

        Returns:
            ChannelsClient for channel endpoints.

        Example:
            ```python
            channel = await client.youtube.channels.get_channel("@mkbhd")
            videos = await client.youtube.channels.get_videos("@mkbhd")
            resolved = await client.youtube.channels.resolve(handle="@mkbhd")
            ```
        """
        return self._channels

    @property
    def playlists(self) -> PlaylistsClient:
        """Access playlist detail, items, and mix endpoints.

        Returns:
            PlaylistsClient for playlist and mix endpoints.

        Example:
            ```python
            playlist = await client.youtube.playlists.get_playlist("PLxxxx")
            page = await client.youtube.playlists.get_items("PLxxxx")
            mix = await client.youtube.playlists.get_mix("RDxxxx")
            ```
        """
        return self._playlists

    @property
    def trending(self) -> TrendingClient:
        """Access trending videos and trending Shorts endpoints.

        Returns:
            TrendingClient for trending feeds.

        Example:
            ```python
            trending = await client.youtube.trending.trending(type="music")
            shorts = await client.youtube.trending.shorts(gl="US")
            ```
        """
        return self._trending

    @property
    def comments(self) -> CommentsClient:
        """Access video comments, replies, and community post comment endpoints.

        Returns:
            CommentsClient for comment endpoints.

        Example:
            ```python
            comments = await client.youtube.comments.get_comments("dQw4w9WgXcQ")
            replies = await client.youtube.comments.get_replies(
                "dQw4w9WgXcQ", "commentId", continuation="token"
            )
            ```
        """
        return self._comments

    @property
    def transcript(self) -> TranscriptClient:
        """Access transcript and caption-track endpoints.

        Returns:
            TranscriptClient for transcript and caption endpoints.

        Example:
            ```python
            transcript = await client.youtube.transcript.get_transcript("dQw4w9WgXcQ")
            captions = await client.youtube.transcript.get_captions("dQw4w9WgXcQ")
            ```
        """
        return self._transcript

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for categories, languages, regions, and markets.

        Example:
            ```python
            categories = await client.youtube.reference.list_categories()
            markets = await client.youtube.reference.list_markets()
            ```
        """
        return self._reference
