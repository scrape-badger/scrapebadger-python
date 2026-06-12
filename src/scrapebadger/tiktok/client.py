"""TikTok API client combining all sub-clients.

This module provides the main TikTokClient class that serves as the
entry point for all TikTok API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.tiktok.ads import AdsClient
from scrapebadger.tiktok.hashtags import HashtagsClient
from scrapebadger.tiktok.music import MusicClient
from scrapebadger.tiktok.reference import ReferenceClient
from scrapebadger.tiktok.search import SearchClient
from scrapebadger.tiktok.trending import TrendingClient
from scrapebadger.tiktok.users import UsersClient
from scrapebadger.tiktok.videos import VideosClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class TikTokClient:
    """Client for all TikTok API operations.

    This class provides access to all TikTok scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        users: Client for user profile, videos, followers, following, liked, reposts.
        videos: Client for video detail, comments, replies, related, transcript, oEmbed.
        search: Client for general, video, hashtag, and user search.
        music: Client for sound/music detail and the videos using a sound.
        hashtags: Client for hashtag detail and tagged videos.
        trending: Client for trending videos, hashtags, and songs.
        ads: Client for the EU Commercial Content Library (ad transparency).
        reference: Client for reference data (regions).

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Get a user profile
            profile = await client.tiktok.users.get_profile("charlidamelio")
            print(profile.user.nickname)

            # Get video detail
            video = await client.tiktok.videos.get_detail("7212345678901234567")
            print(video.video.description)

            # Search videos
            results = await client.tiktok.search.videos("cooking")

            # Trending songs
            songs = await client.tiktok.trending.songs(region="GB")

            # Supported regions
            regions = await client.tiktok.reference.regions()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `tiktok` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize TikTok client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._users = UsersClient(client)
        self._videos = VideosClient(client)
        self._search = SearchClient(client)
        self._music = MusicClient(client)
        self._hashtags = HashtagsClient(client)
        self._trending = TrendingClient(client)
        self._ads = AdsClient(client)
        self._reference = ReferenceClient(client)

    @property
    def users(self) -> UsersClient:
        """Access user profile, videos, followers, following, liked, reposts.

        Returns:
            UsersClient for user endpoints.

        Example:
            ```python
            profile = await client.tiktok.users.get_profile("charlidamelio")
            videos = await client.tiktok.users.get_videos("charlidamelio")
            ```
        """
        return self._users

    @property
    def videos(self) -> VideosClient:
        """Access video detail, comments, replies, related, transcript, oEmbed.

        Returns:
            VideosClient for video endpoints.

        Example:
            ```python
            detail = await client.tiktok.videos.get_detail("7212345678901234567")
            comments = await client.tiktok.videos.get_comments("7212345678901234567")
            ```
        """
        return self._videos

    @property
    def search(self) -> SearchClient:
        """Access general, video, hashtag, and user search.

        Returns:
            SearchClient for search endpoints.

        Example:
            ```python
            results = await client.tiktok.search.videos("cooking")
            users = await client.tiktok.search.users("gordon ramsay")
            ```
        """
        return self._search

    @property
    def music(self) -> MusicClient:
        """Access sound/music detail and the videos using a sound.

        Returns:
            MusicClient for music endpoints.

        Example:
            ```python
            music = await client.tiktok.music.get_detail("6745650783771970561")
            videos = await client.tiktok.music.get_videos("6745650783771970561")
            ```
        """
        return self._music

    @property
    def hashtags(self) -> HashtagsClient:
        """Access hashtag detail and tagged videos.

        Returns:
            HashtagsClient for hashtag endpoints.

        Example:
            ```python
            tag = await client.tiktok.hashtags.get_detail("fyp")
            videos = await client.tiktok.hashtags.get_videos("fyp")
            ```
        """
        return self._hashtags

    @property
    def trending(self) -> TrendingClient:
        """Access trending videos, hashtags, and songs.

        Returns:
            TrendingClient for trending endpoints.

        Example:
            ```python
            videos = await client.tiktok.trending.videos(region="GB")
            songs = await client.tiktok.trending.songs(region="GB")
            ```
        """
        return self._trending

    @property
    def ads(self) -> AdsClient:
        """Access the EU Commercial Content Library (ad transparency).

        Returns:
            AdsClient for ad library endpoints.

        Example:
            ```python
            ads = await client.tiktok.ads.search("sneakers", region="DE")
            ```
        """
        return self._ads

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Returns:
            ReferenceClient for fetching supported regions.

        Example:
            ```python
            regions = await client.tiktok.reference.regions()
            ```
        """
        return self._reference
