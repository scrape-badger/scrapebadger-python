"""Pydantic models for Instagram API responses.

All models are immutable (frozen) and ignore unknown fields (``extra="ignore"``)
so backend responses can be passed straight through ``model_validate`` without a
mapping layer. Field names, types, and defaults mirror the canonical instagrapi
entities returned by the ScrapeBadger backend.

Every datetime ships in two forms: a Unix ``*_utc`` number and an ISO-8601
string (``taken_at``, ``created_at``, ...).

Paginated endpoints share one envelope shape: :class:`Paginated`
(``{items, count, next_cursor, has_more}``).
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class _BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
        str_strip_whitespace=True,
    )


# =============================================================================
# Reference / nested models
# =============================================================================


class BioLink(_BaseModel):
    """A link in a user's bio (element of ``bio_links``)."""

    url: str = ""
    title: str = ""
    link_type: str | None = None
    lynx_url: str | None = None


class UserShort(_BaseModel):
    """A lightweight user reference (followers, likers, tags, authors)."""

    pk: str
    username: str = ""
    full_name: str = ""
    profile_pic_url: str | None = None
    is_private: bool = False
    is_verified: bool = False


class Hashtag(_BaseModel):
    """An Instagram hashtag."""

    id: str | None = None
    name: str
    media_count: int = 0
    profile_pic_url: str | None = None


class Location(_BaseModel):
    """An Instagram location / place."""

    pk: str | None = None
    name: str = ""
    address: str | None = None
    city: str | None = None
    lng: float | None = None
    lat: float | None = None
    external_id: str | None = None
    external_id_source: str | None = None


class Audio(_BaseModel):
    """An Instagram audio / music track."""

    id: str | None = None
    audio_cluster_id: str | None = None
    title: str = ""
    subtitle: str | None = None
    display_artist: str | None = None
    duration_in_ms: int | None = None
    cover_artwork_uri: str | None = None
    is_explicit: bool = False


class Resource(_BaseModel):
    """A single resource inside a carousel/album media."""

    pk: str | None = None
    video_url: str | None = None
    thumbnail_url: str | None = None
    media_type: int = 0


class Highlight(_BaseModel):
    """A user story highlight reel."""

    pk: str | None = None
    id: str | None = None
    title: str = ""
    media_count: int = 0
    cover_media_url: str | None = None


class Oembed(_BaseModel):
    """oEmbed metadata for a media permalink."""

    version: str | None = None
    title: str | None = None
    author_name: str | None = None
    author_url: str | None = None
    author_id: str | None = None
    provider_name: str | None = None
    provider_url: str | None = None
    type: str | None = None
    width: int | None = None
    height: int | None = None
    html: str | None = None
    thumbnail_url: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None


# =============================================================================
# Core Models
# =============================================================================


class User(_BaseModel):
    """A full Instagram user profile."""

    pk: str
    username: str = ""
    full_name: str = ""
    is_private: bool = False
    is_verified: bool = False
    profile_pic_url: str | None = None
    profile_pic_url_hd: str | None = None
    media_count: int = 0
    follower_count: int = 0
    following_count: int = 0
    biography: str = ""
    bio_links: list[BioLink] = Field(default_factory=list)
    external_url: str | None = None
    account_type: int | None = None
    is_business: bool = False
    is_professional_account: bool = False
    public_email: str | None = None
    contact_phone_number: str | None = None
    category: str | None = None
    city_name: str | None = None
    address_street: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class UserAbout(_BaseModel):
    """ "About this account" metadata for a user."""

    username: str = ""
    country: str | None = None
    date_joined: str | None = None
    date_joined_utc: float | None = None
    former_username_count: int = 0
    is_verified: bool = False
    shared_follower_count: int = 0


class Media(_BaseModel):
    """An Instagram media (photo, video, album, reel, IGTV)."""

    pk: str
    id: str = ""
    code: str = ""
    taken_at: str | None = None
    taken_at_utc: float | None = None
    media_type: int = 0
    product_type: str | None = None
    caption_text: str = ""
    like_count: int = 0
    comment_count: int = 0
    play_count: int | None = None
    view_count: int | None = None
    video_url: str | None = None
    thumbnail_url: str | None = None
    image_versions2: dict[str, Any] = Field(default_factory=dict)
    usertags: list[dict[str, Any]] = Field(default_factory=list)
    coauthor_producers: list[UserShort] = Field(default_factory=list)
    location: Location | None = None
    user: UserShort | None = None
    resources: list[Resource] = Field(default_factory=list)
    url: str = ""
    hashtags: list[str] = Field(default_factory=list)
    mentions: list[str] = Field(default_factory=list)


class Comment(_BaseModel):
    """A comment on an Instagram media."""

    pk: str
    text: str = ""
    user: UserShort | None = None
    created_at: str | None = None
    created_at_utc: float | None = None
    like_count: int = 0
    has_liked: bool = False


# =============================================================================
# Pagination envelope
# =============================================================================


class Paginated(_BaseModel, Generic[T]):
    """Cursor-paginated list envelope.

    Attributes:
        items: The page of results.
        count: Number of items in this page.
        next_cursor: Cursor to pass as ``cursor`` for the next page (``None``
            when there are no more pages).
        has_more: Whether another page is available.
    """

    items: list[T] = Field(default_factory=list)
    count: int = 0
    next_cursor: str | None = None
    has_more: bool = False
