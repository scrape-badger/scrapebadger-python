"""YouTube API module for ScrapeBadger SDK.

This module provides a comprehensive async client for scraping YouTube data
through the ScrapeBadger API. All methods are async and return strongly-typed
Pydantic models. List endpoints paginate via an opaque ``continuation`` token
(no page numbers); ``gl`` selects the content region and ``hl`` the UI language.

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
        print(f"{channel.title}: {channel.number_of_subscribers:,} subscribers")
    ```
"""

from scrapebadger.youtube.client import YoutubeClient
from scrapebadger.youtube.models import (
    AudioTrack,
    AutocompleteResponse,
    BatchResponse,
    CaptionsResponse,
    CaptionTrack,
    CategoriesResponse,
    Channel,
    ChannelAbout,
    ChannelLink,
    ChannelTabResponse,
    ChannelVideosResponse,
    Chapter,
    Comment,
    CommentsResponse,
    CommunityPost,
    CommunityResponse,
    Format,
    HashtagResponse,
    HeatMarker,
    HomeResponse,
    LanguagesResponse,
    LiveChatMessage,
    LiveChatResponse,
    LiveStreamingDetails,
    MarketInfo,
    MarketsResponse,
    OEmbed,
    Playlist,
    PlaylistItem,
    PlaylistItemsResponse,
    PollChoice,
    ReferenceRow,
    RegionRestriction,
    RegionsResponse,
    RelatedResponse,
    RepliesResponse,
    ResolveResult,
    SearchChip,
    SearchResponse,
    SearchResult,
    ShoppingResult,
    Short,
    StreamingData,
    SubscriberCount,
    Thumbnail,
    Transcript,
    TranscriptSegment,
    TrendingItem,
    TrendingResponse,
    Video,
)

__all__ = [
    # Video / streaming
    "AudioTrack",
    # Search
    "AutocompleteResponse",
    "BatchResponse",
    # Transcript
    "CaptionTrack",
    "CaptionsResponse",
    # Reference
    "CategoriesResponse",
    # Channel
    "Channel",
    "ChannelAbout",
    "ChannelLink",
    "ChannelTabResponse",
    "ChannelVideosResponse",
    "Chapter",
    # Comments
    "Comment",
    "CommentsResponse",
    # Community
    "CommunityPost",
    "CommunityResponse",
    "Format",
    "HashtagResponse",
    "HeatMarker",
    "HomeResponse",
    "LanguagesResponse",
    "LiveChatMessage",
    "LiveChatResponse",
    "LiveStreamingDetails",
    "MarketInfo",
    "MarketsResponse",
    "OEmbed",
    # Playlist
    "Playlist",
    "PlaylistItem",
    "PlaylistItemsResponse",
    "PollChoice",
    "ReferenceRow",
    "RegionRestriction",
    "RegionsResponse",
    "RelatedResponse",
    "RepliesResponse",
    "ResolveResult",
    "SearchChip",
    "SearchResponse",
    "SearchResult",
    "ShoppingResult",
    "Short",
    "StreamingData",
    "SubscriberCount",
    # Shared
    "Thumbnail",
    "Transcript",
    "TranscriptSegment",
    # Trending
    "TrendingItem",
    "TrendingResponse",
    "Video",
    # Client
    "YoutubeClient",
]
