"""Pydantic models for YouTube API responses.

These models mirror the backend ``youtube_scraper`` response schema field-for-field.
All models are immutable (frozen) and ignore unknown fields for forward
compatibility. YouTube list endpoints paginate via an opaque ``continuation``
token (no page numbers); ``gl`` selects the content region and ``hl`` the UI
language. Every datetime field ships in BOTH ``*_utc`` (Unix float) and ``*_at``
(ISO-8601 Z string).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Base Configuration
# =============================================================================


class _BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
    )


# =============================================================================
# Shared / common models
# =============================================================================


class Thumbnail(_BaseModel):
    """A single image variant."""

    url: str
    width: int | None = None
    height: int | None = None


class ResolveResult(_BaseModel):
    """Result of resolving a handle / custom URL to canonical ids."""

    input: str
    type: str | None = None  # channel | video | playlist
    channel_id: str | None = None
    channel_username: str | None = None
    video_id: str | None = None
    playlist_id: str | None = None
    canonical_url: str | None = None


class ReferenceRow(_BaseModel):
    """A reference lookup row (category / language / region)."""

    id: str
    title: str


class OEmbed(_BaseModel):
    """YouTube public oEmbed response (https://www.youtube.com/oembed)."""

    type: str | None = None
    version: str | None = None
    title: str | None = None
    author_name: str | None = None
    author_url: str | None = None
    provider_name: str | None = None
    provider_url: str | None = None
    thumbnail_url: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None
    width: int | None = None
    height: int | None = None
    html: str | None = None


# =============================================================================
# Video / Short / streaming
# =============================================================================


class Chapter(_BaseModel):
    """A video chapter (from ``next`` macroMarkersListRenderer — manual or auto)."""

    title: str | None = None
    start_seconds: int | None = None
    start_time_text: str | None = None
    thumbnail: str | None = None


class HeatMarker(_BaseModel):
    """A most-replayed graph point (from ``next`` heatMarkers)."""

    start_seconds: float | None = None
    duration_seconds: float | None = None
    intensity: float | None = None  # 0.0-1.0 normalized score


class AudioTrack(_BaseModel):
    """A multi-language audio track (auto-dubbing / original)."""

    id: str | None = None
    display_name: str | None = None
    language: str | None = None
    is_default: bool | None = None
    is_original: bool | None = None


class Format(_BaseModel):
    """A single streaming format (muxed or adaptive)."""

    itag: int | None = None
    mime_type: str | None = None
    codecs: str | None = None
    bitrate: int | None = None
    average_bitrate: int | None = None
    width: int | None = None
    height: int | None = None
    fps: int | None = None
    quality: str | None = None
    quality_label: str | None = None
    audio_quality: str | None = None
    audio_sample_rate: int | None = None
    audio_channels: int | None = None
    is_drc: bool | None = None  # stable-volume (dynamic range compression) audio
    loudness_db: float | None = None
    audio_track: AudioTrack | None = None
    content_length: int | None = None
    approx_duration_ms: int | None = None
    url: str | None = None  # may require a PO token (best-effort)
    signature_cipher: str | None = None
    projection_type: str | None = None


class StreamingData(_BaseModel):
    """Streaming metadata from ``player.streamingData`` (best-effort URLs)."""

    expires_in_seconds: int | None = None
    hls_manifest_url: str | None = None
    dash_manifest_url: str | None = None
    formats: list[Format] = Field(default_factory=list)
    adaptive_formats: list[Format] = Field(default_factory=list)


class ShoppingResult(_BaseModel):
    """A product shelf entry attached to a video."""

    title: str | None = None
    price: str | None = None
    vendor: str | None = None
    thumbnail: str | None = None
    link: str | None = None


class LiveStreamingDetails(_BaseModel):
    """Live/premiere timing details."""

    actual_start_at: str | None = None
    actual_start_utc: float | None = None
    actual_end_at: str | None = None
    actual_end_utc: float | None = None
    scheduled_start_at: str | None = None
    scheduled_start_utc: float | None = None
    scheduled_end_at: str | None = None
    scheduled_end_utc: float | None = None
    concurrent_viewers: int | None = None
    active_live_chat_id: str | None = None


class RegionRestriction(_BaseModel):
    """Allowed/blocked country lists for a video."""

    allowed: list[str] = Field(default_factory=list)
    blocked: list[str] = Field(default_factory=list)


class Video(_BaseModel):
    """Full video detail — merged ``player`` + ``next`` (the flagship entity)."""

    # Core identity
    video_id: str
    title: str | None = None
    url: str | None = None
    description: str | None = None
    description_links: list[dict[str, Any]] = Field(default_factory=list)
    length_seconds: int | None = None
    duration: str | None = None  # HH:MM:SS

    # Engagement
    view_count: int | None = None
    view_count_text: str | None = None
    like_count: int | None = None
    like_count_text: str | None = None
    comment_count: int | None = None
    dislike_count: int | None = None  # private platform-wide since 2021 (null)

    # Channel
    channel_id: str | None = None
    channel_name: str | None = None
    channel_username: str | None = None
    channel_url: str | None = None
    channel_thumbnail: str | None = None
    channel_is_verified: bool | None = None
    is_official_artist: bool | None = None
    number_of_subscribers: int | None = None
    subscriber_count_text: str | None = None

    # Dates
    published_at: str | None = None
    published_utc: float | None = None
    upload_at: str | None = None
    upload_utc: float | None = None
    published_time_text: str | None = None

    # Classification
    keywords: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    category: str | None = None
    category_id: str | None = None
    topic_categories: list[str] = Field(default_factory=list)

    # Media
    thumbnails: list[Thumbnail] = Field(default_factory=list)
    thumbnail: str | None = None
    storyboards: dict[str, Any] | None = None
    chapters: list[Chapter] = Field(default_factory=list)
    heatmap: list[HeatMarker] = Field(default_factory=list)

    # Live / premiere
    is_live_content: bool | None = None
    live_now: bool | None = None
    is_upcoming: bool | None = None
    is_post_live_dvr: bool | None = None
    premiere_utc: float | None = None
    premiere_at: str | None = None
    live_streaming_details: LiveStreamingDetails | None = None

    # Status / safety
    is_family_safe: bool | None = None
    is_age_restricted: bool | None = None
    is_members_only: bool | None = None
    is_unlisted: bool | None = None
    is_private: bool | None = None
    is_crawlable: bool | None = None
    is_shorts_eligible: bool | None = None
    is_short: bool | None = None
    allow_ratings: bool | None = None
    is_monetized: bool | None = None
    comments_turned_off: bool | None = None
    has_paid_product_placement: bool | None = None
    available_countries: list[str] = Field(default_factory=list)
    region_restriction: RegionRestriction | None = None
    playability_status: str | None = None
    playability_reason: str | None = None

    # Technical
    definition: str | None = None  # hd / sd
    dimension: str | None = None  # 2d / 3d
    projection: str | None = None  # rectangular / 360
    captions_available: bool | None = None
    caption_languages: list[str] = Field(default_factory=list)

    # Rich shelves (from next)
    shopping_results: list[ShoppingResult] = Field(default_factory=list)
    additional_info: list[dict[str, Any]] = Field(default_factory=list)
    game_info: dict[str, Any] | None = None
    end_screen_videos: list[dict[str, Any]] = Field(default_factory=list)
    related_videos: list[dict[str, Any]] = Field(default_factory=list)
    related_videos_continuation: str | None = None

    # Sound (shorts)
    sound_id: str | None = None
    sound_title: str | None = None
    sound_artist: str | None = None

    # Streams (only when requested)
    streams: StreamingData | None = None
    embed_url: str | None = None

    scraped_at: str | None = None
    scraped_utc: float | None = None


class Short(Video):
    """A Shorts (vertical reel) — Video subtype with ``is_short=True``."""

    thumbnail_vertical: str | None = None


# =============================================================================
# Search / autocomplete / feed
# =============================================================================


class SearchResult(_BaseModel):
    """A polymorphic search/feed result (keyed by ``type``)."""

    type: str  # video | channel | playlist | movie | short
    position: int | None = None

    # video / short / movie
    video_id: str | None = None
    title: str | None = None
    url: str | None = None
    thumbnails: list[Thumbnail] = Field(default_factory=list)
    thumbnail: str | None = None
    duration: str | None = None
    length_seconds: int | None = None
    view_count: int | None = None
    view_count_text: str | None = None
    short_view_count_text: str | None = None
    published_time_text: str | None = None
    published_at: str | None = None
    published_utc: float | None = None
    description_snippet: str | None = None
    badges: list[str] = Field(default_factory=list)
    extensions: list[str] = Field(default_factory=list)
    is_live: bool | None = None
    is_short: bool | None = None
    is_members_only: bool | None = None

    # channel association (for video/playlist results)
    channel_id: str | None = None
    channel_name: str | None = None
    channel_url: str | None = None
    channel_thumbnail: str | None = None
    channel_is_verified: bool | None = None

    # channel result
    subscriber_count_text: str | None = None
    number_of_subscribers: int | None = None
    video_count_text: str | None = None
    channel_username: str | None = None
    is_verified: bool | None = None

    # playlist result
    playlist_id: str | None = None
    video_count: int | None = None
    first_video_id: str | None = None


class SearchChip(_BaseModel):
    """A search filter chip / refinement."""

    title: str | None = None
    is_selected: bool | None = None
    continuation: str | None = None


class SearchResponse(_BaseModel):
    """A page of search results (search, music search, channel search)."""

    query: str | None = None
    results: list[SearchResult] = Field(default_factory=list)
    total_results: int | None = None
    estimated_results: int | None = None
    chips: list[SearchChip] = Field(default_factory=list)
    did_you_mean: str | None = None
    showing_results_for: str | None = None
    refinements: list[str] = Field(default_factory=list)
    related_searches: list[dict[str, Any]] = Field(default_factory=list)
    continuation: str | None = None


class AutocompleteResponse(_BaseModel):
    """Keyword suggestions for a query prefix."""

    query: str
    suggestions: list[str] = Field(default_factory=list)


class RelatedResponse(_BaseModel):
    """Related videos for a video (secondaryResults)."""

    video_id: str | None = None
    results: list[SearchResult] = Field(default_factory=list)
    continuation: str | None = None


class HashtagResponse(_BaseModel):
    """Videos under a hashtag."""

    tag: str
    results: list[SearchResult] = Field(default_factory=list)
    continuation: str | None = None


class HomeResponse(_BaseModel):
    """Guest home / recommendations feed (non-deterministic, best-effort)."""

    results: list[SearchResult] = Field(default_factory=list)
    continuation: str | None = None


class ChannelVideosResponse(_BaseModel):
    """A page of a channel's videos / shorts / streams."""

    channel_id: str | None = None
    videos: list[SearchResult] = Field(default_factory=list)
    continuation: str | None = None


class ChannelTabResponse(_BaseModel):
    """A generic page of a channel tab (videos/shorts/streams/playlists)."""

    channel_id: str | None = None
    tab: str | None = None
    items: list[SearchResult] = Field(default_factory=list)
    continuation: str | None = None


# =============================================================================
# Channel
# =============================================================================


class ChannelLink(_BaseModel):
    """An external link from a channel's about page / header."""

    title: str | None = None
    url: str | None = None


class Channel(_BaseModel):
    """Full channel detail (browse About tab + header)."""

    channel_id: str
    title: str | None = None
    channel_name: str | None = None
    channel_username: str | None = None  # @handle
    custom_url: str | None = None
    channel_url: str | None = None
    description: str | None = None
    description_links: list[ChannelLink] = Field(default_factory=list)

    number_of_subscribers: int | None = None
    subscriber_count_text: str | None = None
    hidden_subscriber_count: bool | None = None
    channel_total_videos: int | None = None
    channel_total_videos_text: str | None = None
    channel_total_views: int | None = None
    channel_total_views_text: str | None = None

    joined_at: str | None = None
    joined_utc: float | None = None
    country: str | None = None
    channel_location: str | None = None

    keywords: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    is_verified: bool | None = None
    is_age_restricted: bool | None = None
    is_family_safe: bool | None = None
    is_monetized: bool | None = None
    is_auto_generated: bool | None = None
    made_for_kids: bool | None = None

    avatar: str | None = None
    banner: str | None = None
    tv_banner: str | None = None
    mobile_banner: str | None = None
    avatar_thumbnails: list[Thumbnail] = Field(default_factory=list)
    banner_thumbnails: list[Thumbnail] = Field(default_factory=list)

    external_links: list[ChannelLink] = Field(default_factory=list)
    tabs: list[str] = Field(default_factory=list)
    available_countries: list[str] = Field(default_factory=list)

    related_channels: list[dict[str, Any]] = Field(default_factory=list)
    latest_videos: list[dict[str, Any]] = Field(default_factory=list)

    scraped_at: str | None = None
    scraped_utc: float | None = None


class ChannelAbout(_BaseModel):
    """Lightweight channel about payload."""

    channel_id: str
    description: str | None = None
    links: list[ChannelLink] = Field(default_factory=list)
    number_of_subscribers: int | None = None
    subscriber_count_text: str | None = None
    channel_total_views: int | None = None
    channel_total_videos: int | None = None
    joined_at: str | None = None
    joined_utc: float | None = None
    country: str | None = None


class SubscriberCount(_BaseModel):
    """Fast subscriber-count-only response."""

    channel_id: str
    number_of_subscribers: int | None = None
    subscriber_count_text: str | None = None


# =============================================================================
# Playlist
# =============================================================================


class PlaylistItem(_BaseModel):
    """A single entry in a playlist."""

    position: int | None = None
    video_id: str
    title: str | None = None
    url: str | None = None
    length_seconds: int | None = None
    duration: str | None = None
    channel_id: str | None = None
    channel_name: str | None = None
    channel_url: str | None = None
    thumbnails: list[Thumbnail] = Field(default_factory=list)
    thumbnail: str | None = None
    view_count: int | None = None
    view_count_text: str | None = None
    published_time_text: str | None = None
    is_playable: bool | None = None
    set_video_id: str | None = None  # per-playlist-entry id


class Playlist(_BaseModel):
    """Full playlist detail + first page of items."""

    playlist_id: str
    title: str | None = None
    description: str | None = None
    playlist_url: str | None = None
    video_count: int | None = None
    view_count: int | None = None
    view_count_text: str | None = None
    last_updated_text: str | None = None
    channel_id: str | None = None
    channel_name: str | None = None
    channel_url: str | None = None
    channel_is_verified: bool | None = None
    thumbnails: list[Thumbnail] = Field(default_factory=list)
    thumbnail: str | None = None
    privacy_status: str | None = None
    is_mix: bool | None = None
    videos: list[PlaylistItem] = Field(default_factory=list)
    continuation: str | None = None
    scraped_at: str | None = None
    scraped_utc: float | None = None


class PlaylistItemsResponse(_BaseModel):
    """A continuation page of playlist items."""

    playlist_id: str | None = None
    items: list[PlaylistItem] = Field(default_factory=list)
    continuation: str | None = None


# =============================================================================
# Comments
# =============================================================================


class Comment(_BaseModel):
    """A single comment or reply (from ``commentEntityPayload`` + thread)."""

    comment_id: str
    text: str | None = None
    published_time_text: str | None = None
    published_utc: float | None = None
    author: str | None = None
    author_channel_id: str | None = None
    author_channel_url: str | None = None
    author_thumbnail: str | None = None
    author_is_verified: bool | None = None
    author_is_artist: bool | None = None
    author_is_channel_owner: bool | None = None
    author_badges: list[str] = Field(default_factory=list)
    like_count: int | None = None
    reply_count: int | None = None
    has_creator_heart: bool | None = None
    is_pinned: bool | None = None
    is_reply: bool | None = None
    reply_to_cid: str | None = None
    replies_continuation: str | None = None
    paid_comment_amount: str | None = None  # Super Thanks purchase amount
    video_id: str | None = None


class CommentsResponse(_BaseModel):
    """A page of top-level comments (video or community post)."""

    video_id: str | None = None
    comments: list[Comment] = Field(default_factory=list)
    comment_count: int | None = None
    sorting_tokens: list[dict[str, Any]] = Field(default_factory=list)
    continuation: str | None = None


class RepliesResponse(_BaseModel):
    """A page of replies to a comment."""

    comment_id: str | None = None
    replies: list[Comment] = Field(default_factory=list)
    continuation: str | None = None


# =============================================================================
# Transcript / captions
# =============================================================================


class TranscriptSegment(_BaseModel):
    """A single timed transcript line."""

    start_ms: int | None = None
    end_ms: int | None = None
    duration_ms: int | None = None
    start_time_text: str | None = None
    text: str | None = None


class Transcript(_BaseModel):
    """A full video transcript in the selected language."""

    video_id: str
    language: str | None = None
    language_name: str | None = None
    type: str | None = None  # asr | manual
    is_translatable: bool | None = None
    available_transcripts: list[dict[str, Any]] = Field(default_factory=list)
    translation_languages: list[dict[str, Any]] = Field(default_factory=list)
    segments: list[TranscriptSegment] = Field(default_factory=list)
    full_text: str | None = None
    srt: str | None = None
    vtt: str | None = None


class CaptionTrack(_BaseModel):
    """An available caption track (from player captions tracklist)."""

    language: str | None = None
    language_name: str | None = None
    type: str | None = None  # asr | manual
    is_translatable: bool | None = None
    base_url: str | None = None


class CaptionsResponse(_BaseModel):
    """The list of available caption tracks for a video."""

    video_id: str
    tracks: list[CaptionTrack] = Field(default_factory=list)
    translation_languages: list[dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Trending
# =============================================================================


class TrendingItem(_BaseModel):
    """A trending video / short."""

    position: int | None = None
    category: str | None = None  # Now | Music | Gaming | Movies
    video_id: str | None = None
    title: str | None = None
    url: str | None = None
    thumbnails: list[Thumbnail] = Field(default_factory=list)
    thumbnail: str | None = None
    duration: str | None = None
    length_seconds: int | None = None
    view_count: int | None = None
    view_count_text: str | None = None
    published_time_text: str | None = None
    description_snippet: str | None = None
    channel_id: str | None = None
    channel_name: str | None = None
    channel_url: str | None = None
    channel_thumbnail: str | None = None
    channel_is_verified: bool | None = None
    badges: list[str] = Field(default_factory=list)
    is_live: bool | None = None
    is_short: bool | None = None


class TrendingResponse(_BaseModel):
    """A page of trending items."""

    gl: str | None = None
    type: str | None = None
    items: list[TrendingItem] = Field(default_factory=list)
    continuation: str | None = None


# =============================================================================
# Community / live chat
# =============================================================================


class PollChoice(_BaseModel):
    """A single poll option on a community post."""

    text: str | None = None
    percentage: float | None = None
    votes: int | None = None
    image: str | None = None


class CommunityPost(_BaseModel):
    """A channel community / posts-tab entry."""

    post_id: str
    post_url: str | None = None
    post_type: str | None = None  # text | poll | image | video | shared
    text: str | None = None
    text_links: list[dict[str, Any]] = Field(default_factory=list)
    channel_id: str | None = None
    channel_name: str | None = None
    channel_url: str | None = None
    channel_thumbnail: str | None = None
    published_time_text: str | None = None
    published_utc: float | None = None
    like_count: int | None = None
    like_count_text: str | None = None
    comment_count: int | None = None
    poll_choices: list[PollChoice] = Field(default_factory=list)
    poll_total_votes: int | None = None
    images: list[Thumbnail] = Field(default_factory=list)
    attached_video: dict[str, Any] | None = None
    shared_post: dict[str, Any] | None = None
    scraped_at: str | None = None
    scraped_utc: float | None = None


class CommunityResponse(_BaseModel):
    """A page of community posts."""

    channel_id: str | None = None
    posts: list[CommunityPost] = Field(default_factory=list)
    continuation: str | None = None


class LiveChatMessage(_BaseModel):
    """A single live-chat / chat-replay message."""

    message_id: str | None = None
    message_type: str | None = None  # text | super_chat | super_sticker | membership
    text: str | None = None
    author: str | None = None
    author_channel_id: str | None = None
    author_thumbnail: str | None = None
    author_badges: list[str] = Field(default_factory=list)
    is_moderator: bool | None = None
    is_member: bool | None = None
    is_verified: bool | None = None
    timestamp_usec: int | None = None
    timestamp_text: str | None = None
    video_offset_time_msec: int | None = None
    purchase_amount: str | None = None  # super chat / sticker amount
    body_background_color: str | None = None


class LiveChatResponse(_BaseModel):
    """A page of live-chat messages."""

    video_id: str | None = None
    messages: list[LiveChatMessage] = Field(default_factory=list)
    continuation: str | None = None
    is_replay: bool | None = None


# =============================================================================
# Batch + reference response envelopes
# =============================================================================


class BatchResponse(_BaseModel):
    """Response for POST /videos/batch."""

    videos: list[Video] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    count: int = 0


class CategoriesResponse(_BaseModel):
    """Response for /categories."""

    gl: str
    categories: list[ReferenceRow] = Field(default_factory=list)


class LanguagesResponse(_BaseModel):
    """Response for /languages."""

    languages: list[ReferenceRow] = Field(default_factory=list)


class RegionsResponse(_BaseModel):
    """Response for /regions."""

    regions: list[ReferenceRow] = Field(default_factory=list)


class MarketInfo(_BaseModel):
    """A single supported scraper market (for /markets)."""

    gl: str
    hl: str
    name: str


class MarketsResponse(_BaseModel):
    """Response for /markets."""

    markets: list[MarketInfo] = Field(default_factory=list)
