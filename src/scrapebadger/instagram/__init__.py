"""Instagram API module for ScrapeBadger SDK.

Async client for scraping Instagram data through the ScrapeBadger API. All
methods are async and return frozen Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        profile = await client.instagram.users.get("instagram")
        print(f"@{profile.username}: {profile.follower_count:,} followers")

        posts = await client.instagram.users.posts("instagram", amount=12)
        for media in posts.items:
            print(media.code, media.like_count)
    ```
"""

from scrapebadger.instagram.client import InstagramClient
from scrapebadger.instagram.models import (
    Audio,
    BioLink,
    Comment,
    Hashtag,
    Highlight,
    Location,
    Media,
    Oembed,
    Paginated,
    Resource,
    User,
    UserAbout,
    UserShort,
)

__all__ = [
    "Audio",
    "BioLink",
    "Comment",
    "Hashtag",
    "Highlight",
    "InstagramClient",
    "Location",
    "Media",
    "Oembed",
    "Paginated",
    "Resource",
    "User",
    "UserAbout",
    "UserShort",
]
