"""TikTok API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping TikTok data
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models.

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
        for v in results.videos:
            print(v.description)
    ```
"""

from scrapebadger.tiktok.client import TikTokClient
from scrapebadger.tiktok.models import (
    AdAdvertiser,
    AdDetailResponse,
    AdLibraryPage,
    AdLibrarySearchResponse,
    AdTargeting,
    AdTargetingBreakdown,
    AdTargetingLocation,
    AdTargetingRegion,
    AdvertiserSearchResponse,
    AdvertiserSuggestion,
    CommentListResponse,
    HashtagResponse,
    HashtagSearchResponse,
    MusicResponse,
    ProfileResponse,
    RegionInfo,
    RegionsResponse,
    TikTokAd,
    TikTokAdVideo,
    TikTokAnchor,
    TikTokAuthor,
    TikTokChallenge,
    TikTokComment,
    TikTokCursorPage,
    TikTokEffectSticker,
    TikTokHashtag,
    TikTokMusic,
    TikTokOEmbed,
    TikTokStats,
    TikTokSubtitle,
    TikTokTextExtra,
    TikTokTrendingHashtag,
    TikTokTrendingSong,
    TikTokUser,
    TikTokUserStats,
    TikTokVideo,
    TikTokVideoControl,
    TikTokVideoMeta,
    TikTokVideoStatus,
    TranscriptResponse,
    TrendingHashtagsResponse,
    TrendingSongsResponse,
    UserListResponse,
    UserSearchResponse,
    VideoListResponse,
    VideoResponse,
)

__all__ = [
    # Ad library
    "AdAdvertiser",
    "AdDetailResponse",
    "AdLibraryPage",
    "AdLibrarySearchResponse",
    "AdTargeting",
    "AdTargetingBreakdown",
    "AdTargetingLocation",
    "AdTargetingRegion",
    "AdvertiserSearchResponse",
    "AdvertiserSuggestion",
    # Response envelopes
    "CommentListResponse",
    "HashtagResponse",
    "HashtagSearchResponse",
    "MusicResponse",
    "ProfileResponse",
    "RegionInfo",
    "RegionsResponse",
    # Core models
    "TikTokAd",
    "TikTokAdVideo",
    "TikTokAnchor",
    "TikTokAuthor",
    "TikTokChallenge",
    # Client
    "TikTokClient",
    "TikTokComment",
    "TikTokCursorPage",
    "TikTokEffectSticker",
    "TikTokHashtag",
    "TikTokMusic",
    "TikTokOEmbed",
    "TikTokStats",
    "TikTokSubtitle",
    "TikTokTextExtra",
    "TikTokTrendingHashtag",
    "TikTokTrendingSong",
    "TikTokUser",
    "TikTokUserStats",
    "TikTokVideo",
    "TikTokVideoControl",
    "TikTokVideoMeta",
    "TikTokVideoStatus",
    "TranscriptResponse",
    "TrendingHashtagsResponse",
    "TrendingSongsResponse",
    "UserListResponse",
    "UserSearchResponse",
    "VideoListResponse",
    "VideoResponse",
]
