"""Pydantic models for TikTok API responses.

These models mirror the backend ``tiktok_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Conventions (matching the backend):
- Snake_case public field names even though the upstream source is camelCase.
- Every datetime ships in BOTH forms: ``*_utc`` (Unix int) AND ``*_at``
  (ISO 8601 UTC string).
- Nullable scalars are ``T | None``; arrays default to empty lists.
"""

from __future__ import annotations

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
# Shared sub-models
# =============================================================================


class TikTokAuthor(_BaseModel):
    """Author summary embedded in a video, comment, or search result."""

    id: str = ""
    sec_uid: str | None = None
    unique_id: str = ""  # @handle
    nickname: str | None = None
    avatar_thumb: str | None = None
    avatar_medium: str | None = None
    avatar_larger: str | None = None
    signature: str | None = None  # bio
    verified: bool = False
    private_account: bool | None = None
    follower_count: int | None = None
    following_count: int | None = None
    heart_count: int | None = None  # total likes received
    video_count: int | None = None
    digg_count: int | None = None  # likes given
    region: str | None = None
    sec_uid_present: bool = False
    short_id: str | None = None
    verify_reason: str | None = None
    verification_type: int | None = None
    account_region: str | None = None
    language: str | None = None
    original_musician: bool | None = None
    is_star: bool | None = None
    ins_id: str | None = None
    twitter_name: str | None = None
    youtube_channel_title: str | None = None
    room_id: str | None = None
    commerce_user_level: int | None = None
    with_shop_entry: bool | None = None


class TikTokStats(_BaseModel):
    """Engagement statistics for a video."""

    play_count: int = 0  # views
    digg_count: int = 0  # likes
    comment_count: int = 0
    share_count: int = 0
    collect_count: int = 0  # saves / bookmarks
    download_count: int | None = None
    forward_count: int | None = None
    whatsapp_share_count: int | None = None
    repost_count: int | None = None


class TikTokVideoMeta(_BaseModel):
    """Playable-media metadata for a video."""

    height: int | None = None
    width: int | None = None
    duration: int | None = None  # seconds
    ratio: str | None = None
    format: str | None = None
    definition: str | None = None
    codec_type: str | None = None
    encoded_type: str | None = None
    bitrate: int | None = None
    cover: str | None = None
    origin_cover: str | None = None
    dynamic_cover: str | None = None
    animated_cover: str | None = None
    ai_dynamic_cover: str | None = None
    share_cover: str | None = None
    play_addr: str | None = None
    download_addr: str | None = None
    download_no_watermark_addr: str | None = None
    has_watermark: bool | None = None
    volume_loudness: float | None = None
    volume_peak: float | None = None


class TikTokMusic(_BaseModel):
    """Sound / music attached to a video, or a standalone music entity."""

    id: str = ""
    title: str | None = None
    author_name: str | None = None
    album: str | None = None
    duration: int | None = None  # seconds
    play_url: str | None = None
    cover_thumb: str | None = None
    cover_medium: str | None = None
    cover_large: str | None = None
    original: bool | None = None
    is_copyrighted: bool | None = None
    mid: str | None = None
    owner_id: str | None = None
    owner_nickname: str | None = None
    is_commerce_music: bool | None = None
    is_original_sound: bool | None = None
    video_count: int | None = None
    user_count: int | None = None


class TikTokChallenge(_BaseModel):
    """A hashtag/challenge as referenced from a video."""

    id: str = ""
    title: str = ""  # hashtag text, no '#'
    desc: str | None = None
    cover: str | None = None
    is_commerce: bool | None = None


class TikTokEffectSticker(_BaseModel):
    """An effect / sticker applied to a video."""

    id: str = ""
    name: str | None = None
    photo_url: str | None = None


class TikTokTextExtra(_BaseModel):
    """An entity (hashtag mention or @user mention) inside the caption."""

    type: str | None = None  # "hashtag" | "mention"
    hashtag_name: str | None = None
    user_unique_id: str | None = None
    user_id: str | None = None
    start: int | None = None
    end: int | None = None


class TikTokSubtitle(_BaseModel):
    """A subtitle/caption track for a video."""

    language: str | None = None
    language_code: str | None = None
    url: str | None = None
    source: str | None = None  # ASR vs creator
    version: str | None = None
    format: str | None = None


class TikTokVideoStatus(_BaseModel):
    """Moderation / availability state of a post."""

    is_delete: bool | None = None
    allow_share: bool | None = None
    allow_comment: bool | None = None
    private_status: int | None = None  # 0 public, 1 friends, 2 private
    in_reviewing: bool | None = None
    reviewed: bool | None = None
    is_prohibited: bool | None = None
    download_status: int | None = None
    self_see: bool | None = None


class TikTokVideoControl(_BaseModel):
    """Per-post interaction permissions."""

    allow_download: bool | None = None
    allow_duet: bool | None = None
    allow_stitch: bool | None = None
    allow_react: bool | None = None
    allow_comment: bool | None = None
    share_type: int | None = None
    prevent_download: bool | None = None


class TikTokAnchor(_BaseModel):
    """A link/shopping/POI anchor attached to a post."""

    id: str | None = None
    type: int | None = None
    keyword: str | None = None
    url: str | None = None
    icon: str | None = None


# =============================================================================
# Video / Post
# =============================================================================


class TikTokVideo(_BaseModel):
    """A TikTok post (video or photo slideshow) with full metadata."""

    id: str
    description: str = ""  # caption text
    text_language: str | None = None
    create_time_utc: int | None = None
    create_time_at: str | None = None
    region: str | None = None  # locationCreated
    url: str = ""  # web video URL
    share_url: str | None = None  # canonical share link
    group_id: str | None = None
    aweme_type: int | None = None  # 0 video, 150 photo/slideshow, …
    content_type: str | None = None
    author: TikTokAuthor | None = None
    music: TikTokMusic | None = None
    stats: TikTokStats = Field(default_factory=TikTokStats)
    video: TikTokVideoMeta | None = None
    status: TikTokVideoStatus | None = None
    video_control: TikTokVideoControl | None = None
    anchors: list[TikTokAnchor] = Field(default_factory=list)

    # Caption entities
    hashtags: list[str] = Field(default_factory=list)
    mentions: list[str] = Field(default_factory=list)
    text_extra: list[TikTokTextExtra] = Field(default_factory=list)
    challenges: list[TikTokChallenge] = Field(default_factory=list)
    effect_stickers: list[TikTokEffectSticker] = Field(default_factory=list)

    # Photo / slideshow posts
    is_slideshow: bool = False
    image_urls: list[str] = Field(default_factory=list)

    # Flags & settings
    is_ad: bool = False
    is_aigc: bool | None = None
    aigc_description: str | None = None
    is_pinned: bool = False
    is_muted: bool | None = None
    secret: bool | None = None
    private_item: bool | None = None
    duet_enabled: bool | None = None
    stitch_enabled: bool | None = None
    share_enabled: bool | None = None
    comment_status: str | None = None
    can_repost: bool | None = None
    is_paid_content: bool | None = None
    is_on_this_day: bool | None = None
    support_danmaku: bool | None = None  # supports bullet comments

    # Transcript (only on the transcript endpoint, else empty)
    subtitles: list[TikTokSubtitle] = Field(default_factory=list)
    voice_to_text: str | None = None

    # Diversification / categorization
    diversification_labels: list[str] = Field(default_factory=list)
    suggested_words: list[str] = Field(default_factory=list)


# =============================================================================
# User / Profile
# =============================================================================


class TikTokUserStats(_BaseModel):
    """Aggregate counts for a user profile."""

    follower_count: int = 0
    following_count: int = 0
    heart_count: int = 0  # total likes received
    video_count: int = 0
    digg_count: int = 0  # likes given
    friend_count: int | None = None


class TikTokUser(_BaseModel):
    """A full TikTok user profile."""

    id: str = ""
    sec_uid: str = ""  # needed to call list endpoints
    unique_id: str = ""  # @handle
    nickname: str | None = None
    signature: str | None = None  # bio
    bio_link: str | None = None
    verified: bool = False
    verify_reason: str | None = None
    verification_type: int | None = None
    private_account: bool = False
    is_commerce_account: bool | None = None
    is_seller: bool | None = None  # TikTok Shop seller
    is_organization: bool | None = None
    original_musician: bool | None = None
    is_star: bool | None = None
    region: str | None = None
    language: str | None = None
    ins_id: str | None = None
    twitter_name: str | None = None
    youtube_channel_title: str | None = None

    avatar_thumb: str | None = None
    avatar_medium: str | None = None
    avatar_larger: str | None = None

    stats: TikTokUserStats = Field(default_factory=TikTokUserStats)

    # Privacy / interaction settings
    open_favorite: bool | None = None
    comment_setting: int | None = None
    duet_setting: int | None = None
    stitch_setting: int | None = None
    download_setting: int | None = None
    following_visibility: int | None = None

    # Live
    is_live: bool | None = None
    room_id: str | None = None

    # Commerce
    commerce_category: str | None = None
    commerce_user_level: int | None = None
    with_shop_entry: bool | None = None

    create_time_utc: int | None = None
    create_time_at: str | None = None

    profile_url: str = ""


# =============================================================================
# Comment
# =============================================================================


class TikTokComment(_BaseModel):
    """A comment (or reply) on a video."""

    id: str  # cid
    text: str = ""
    aweme_id: str | None = None  # parent video id
    parent_comment_id: str | None = None
    digg_count: int = 0
    reply_count: int = 0
    create_time_utc: int | None = None
    create_time_at: str | None = None
    liked_by_author: bool | None = None
    pinned_by_author: bool | None = None
    comment_language: str | None = None
    status: int | None = None
    mentions: list[str] = Field(default_factory=list)  # @users in the comment
    text_extra: list[TikTokTextExtra] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)  # comment sticker/images
    author: TikTokAuthor | None = None
    replies: list[TikTokComment] = Field(default_factory=list)


# =============================================================================
# Hashtag detail
# =============================================================================


class TikTokHashtag(_BaseModel):
    """A hashtag / challenge detail."""

    id: str = ""
    title: str = ""  # name without '#'
    description: str | None = None
    cover: str | None = None
    profile_larger: str | None = None
    video_count: int | None = None
    view_count: int | None = None
    is_commerce: bool | None = None
    url: str = ""


# =============================================================================
# Trending
# =============================================================================


class TikTokTrendingHashtag(_BaseModel):
    """A trending hashtag entry."""

    name: str = ""
    id: str | None = None
    rank: int | None = None
    rank_diff: int | None = None
    country_code: str | None = None
    industry: str | None = None
    publish_count: int | None = None  # videos using it
    view_count: int | None = None
    user_count: int | None = None  # distinct creators using it
    is_promoted: bool | None = None
    is_new: bool | None = None
    url: str | None = None


class TikTokTrendingSong(_BaseModel):
    """A trending song / sound entry."""

    title: str = ""
    id: str | None = None
    author: str | None = None
    rank: int | None = None
    rank_diff: int | None = None
    country_code: str | None = None
    duration: int | None = None
    user_count: int | None = None  # videos using this sound
    cover: str | None = None
    play_url: str | None = None
    is_new: bool | None = None
    link: str | None = None


# =============================================================================
# oEmbed
# =============================================================================


class TikTokOEmbed(_BaseModel):
    """oEmbed metadata for a TikTok URL."""

    version: str = "1.0"
    type: str = "video"
    title: str | None = None
    author_name: str | None = None
    author_url: str | None = None
    provider_name: str = "TikTok"
    provider_url: str = "https://www.tiktok.com"
    html: str | None = None
    thumbnail_url: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None
    embed_product_id: str | None = None
    embed_type: str | None = None


# =============================================================================
# Pagination + response envelopes
# =============================================================================


class TikTokCursorPage(_BaseModel):
    """Cursor pagination metadata shared by all list endpoints."""

    has_more: bool = False
    cursor: str | None = None  # opaque; pass back as ?cursor=
    count: int = 0  # number of items in THIS page
    search_id: str | None = None  # search endpoints chain rid → search_id


class ProfileResponse(_BaseModel):
    """Response wrapper for a user profile."""

    user: TikTokUser
    region: str


class VideoResponse(_BaseModel):
    """Response wrapper for a single video."""

    video: TikTokVideo
    region: str


class VideoListResponse(_BaseModel):
    """Response wrapper for a paginated list of videos."""

    videos: list[TikTokVideo] = Field(default_factory=list)
    pagination: TikTokCursorPage = Field(default_factory=TikTokCursorPage)
    region: str


class CommentListResponse(_BaseModel):
    """Response wrapper for a paginated list of comments."""

    comments: list[TikTokComment] = Field(default_factory=list)
    pagination: TikTokCursorPage = Field(default_factory=TikTokCursorPage)
    region: str


class UserListResponse(_BaseModel):
    """Response wrapper for followers / following lists."""

    users: list[TikTokAuthor] = Field(default_factory=list)
    pagination: TikTokCursorPage = Field(default_factory=TikTokCursorPage)
    region: str


class HashtagResponse(_BaseModel):
    """Response wrapper for a hashtag detail."""

    hashtag: TikTokHashtag
    region: str


class MusicResponse(_BaseModel):
    """Response wrapper for a music / sound detail."""

    music: TikTokMusic
    region: str


class UserSearchResponse(_BaseModel):
    """Response wrapper for a user search."""

    users: list[TikTokAuthor] = Field(default_factory=list)
    pagination: TikTokCursorPage = Field(default_factory=TikTokCursorPage)
    region: str


class HashtagSearchResponse(_BaseModel):
    """Response wrapper for a hashtag search."""

    hashtags: list[TikTokHashtag] = Field(default_factory=list)
    pagination: TikTokCursorPage = Field(default_factory=TikTokCursorPage)
    region: str


class TranscriptResponse(_BaseModel):
    """Response wrapper for a video transcript."""

    video_id: str
    subtitles: list[TikTokSubtitle] = Field(default_factory=list)
    voice_to_text: str | None = None
    region: str


class TrendingHashtagsResponse(_BaseModel):
    """Response wrapper for trending hashtags."""

    hashtags: list[TikTokTrendingHashtag] = Field(default_factory=list)
    region: str


class TrendingSongsResponse(_BaseModel):
    """Response wrapper for trending songs."""

    songs: list[TikTokTrendingSong] = Field(default_factory=list)
    region: str


# =============================================================================
# Ad Library (EU Commercial Content Library, EU-DSA transparency)
# =============================================================================


class TikTokAdVideo(_BaseModel):
    """A creative video attached to a TikTok ad."""

    video_url: str | None = None
    cover_img: str | None = None


class TikTokAd(_BaseModel):
    """A TikTok ad from the Commercial Content Library."""

    id: str
    name: str | None = None  # advertiser name
    audit_status: str | None = None
    type: str | None = None
    first_shown_date: int | None = None  # epoch ms
    last_shown_date: int | None = None  # epoch ms
    videos: list[TikTokAdVideo] = Field(default_factory=list)


class AdLibraryPage(_BaseModel):
    """Offset pagination metadata for the Ad Library."""

    has_more: bool = False
    total: int | None = None
    search_id: str | None = None  # pass to the next page request
    offset: int = 0


class AdLibrarySearchResponse(_BaseModel):
    """Response wrapper for an Ad Library search."""

    ads: list[TikTokAd] = Field(default_factory=list)
    pagination: AdLibraryPage
    region: str


class RegionInfo(_BaseModel):
    """A single supported TikTok content region."""

    code: str
    country_code: str
    locale: str
    name: str


class RegionsResponse(_BaseModel):
    """Response wrapper for the supported-regions list."""

    regions: list[RegionInfo] = Field(default_factory=list)
