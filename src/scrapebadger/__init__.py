"""ScrapeBadger Python SDK.

The official Python SDK for ScrapeBadger - async web scraping APIs
for Twitter and more.

Example:
    ```python
    import asyncio
    from scrapebadger import ScrapeBadger

    async def main():
        async with ScrapeBadger(api_key="your-api-key") as client:
            # Get a user profile
            user = await client.twitter.users.get_by_username("elonmusk")
            print(f"{user.name} has {user.followers_count:,} followers")

            # Search tweets
            tweets = await client.twitter.tweets.search("python programming")
            for tweet in tweets.data:
                print(f"@{tweet.username}: {tweet.text[:100]}...")

            # Iterate through all results
            async for tweet in client.twitter.tweets.search_all("python"):
                print(tweet.text)

    asyncio.run(main())
    ```

For more information, see https://docs.scrapebadger.com
"""

from scrapebadger._internal.config import ClientConfig
from scrapebadger._internal.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    NotFoundError,
    RateLimitError,
    ScrapeBadgerError,
    ServerError,
    ValidationError,
    WebSocketStreamError,
)
from scrapebadger._internal.pagination import PaginatedResponse
from scrapebadger.amazon.client import AmazonClient
from scrapebadger.amazon.models import (
    AmazonPrice,
    Bestseller,
    BestsellersResponse,
    CategoriesResponse,
    CategoryResponse,
    Deal,
    DealsResponse,
    MarketInfo,
    NewReleasesResponse,
    Offer,
    OffersResponse,
    Product,
    ProductDetailResponse,
    Review,
    ReviewsResponse,
    Seller,
    SellerFeedbackResponse,
    SellerProductsResponse,
    SellerProfileResponse,
)
from scrapebadger.amazon.models import (
    AutocompleteResponse as AmazonAutocompleteResponse,
)
from scrapebadger.amazon.models import (
    CategoryInfo as AmazonCategoryInfo,
)
from scrapebadger.amazon.models import (
    MarketsResponse as AmazonMarketsResponse,
)
from scrapebadger.amazon.models import (
    Pagination as AmazonPagination,
)
from scrapebadger.amazon.models import (
    SearchResponse as AmazonSearchResponse,
)
from scrapebadger.amazon.models import (
    SearchResult as AmazonSearchResult,
)
from scrapebadger.client import ScrapeBadger
from scrapebadger.google.client import GoogleClient
from scrapebadger.reddit.models import (
    PostCommentsResponse,
    PostDetailResponse,
    PostDuplicatesResponse,
    RedditAward,
    RedditComment,
    RedditModeratedSubreddit,
    RedditPost,
    RedditRule,
    RedditSubreddit,
    RedditTrophy,
    RedditUser,
    RedditUserSubreddit,
    RedditWikiPage,
    SearchPostsResponse,
    SearchUsersResponse,
    SubredditDetailResponse,
    SubredditPostsResponse,
    SubredditRulesResponse,
    SubredditsListResponse,
    SubredditWikiPageResponse,
    SubredditWikiPagesResponse,
    TrendingPostsResponse,
    UserCommentsResponse,
    UserModeratedResponse,
    UserPostsResponse,
    UserTrophiesResponse,
)
from scrapebadger.reddit.models import (
    UserProfileResponse as RedditUserProfileResponse,
)
from scrapebadger.tiktok.client import TikTokClient
from scrapebadger.tiktok.models import (
    AdLibraryPage,
    AdLibrarySearchResponse,
    RegionInfo,
    TikTokAd,
    TikTokAdVideo,
    TikTokAuthor,
    TikTokComment,
    TikTokCursorPage,
    TikTokHashtag,
    TikTokMusic,
    TikTokOEmbed,
    TikTokStats,
    TikTokTrendingHashtag,
    TikTokTrendingSong,
    TikTokUser,
    TikTokUserStats,
    TikTokVideo,
    TikTokVideoMeta,
)
from scrapebadger.tiktok.models import (
    CommentListResponse as TikTokCommentListResponse,
)
from scrapebadger.tiktok.models import (
    HashtagResponse as TikTokHashtagResponse,
)
from scrapebadger.tiktok.models import (
    HashtagSearchResponse as TikTokHashtagSearchResponse,
)
from scrapebadger.tiktok.models import (
    MusicResponse as TikTokMusicResponse,
)
from scrapebadger.tiktok.models import (
    ProfileResponse as TikTokProfileResponse,
)
from scrapebadger.tiktok.models import (
    RegionsResponse as TikTokRegionsResponse,
)
from scrapebadger.tiktok.models import (
    TranscriptResponse as TikTokTranscriptResponse,
)
from scrapebadger.tiktok.models import (
    TrendingHashtagsResponse as TikTokTrendingHashtagsResponse,
)
from scrapebadger.tiktok.models import (
    TrendingSongsResponse as TikTokTrendingSongsResponse,
)
from scrapebadger.tiktok.models import (
    UserListResponse as TikTokUserListResponse,
)
from scrapebadger.tiktok.models import (
    UserSearchResponse as TikTokUserSearchResponse,
)
from scrapebadger.tiktok.models import (
    VideoListResponse as TikTokVideoListResponse,
)
from scrapebadger.tiktok.models import (
    VideoResponse as TikTokVideoResponse,
)
from scrapebadger.vinted.models import (
    BrandsResponse,
    ColorsResponse,
    ItemDetailResponse,
    MarketsResponse,
    SearchResponse,
    StatusesResponse,
    UserItemsResponse,
    UserProfileResponse,
    VintedBrand,
    VintedColor,
    VintedItemDetail,
    VintedItemSummary,
    VintedMarket,
    VintedPagination,
    VintedPhoto,
    VintedPrice,
    VintedSellerSummary,
    VintedStatus,
    VintedUserProfile,
    VintedUserSummary,
)
from scrapebadger.web.models import DetectResult, ScrapeResult

__version__ = "0.13.1"

__all__ = [
    # TikTok core models
    "AdLibraryPage",
    "AdLibrarySearchResponse",
    # Amazon
    "AmazonAutocompleteResponse",
    "AmazonCategoryInfo",
    "AmazonClient",
    "AmazonMarketsResponse",
    "AmazonPagination",
    "AmazonPrice",
    "AmazonSearchResponse",
    "AmazonSearchResult",
    "AuthenticationError",
    "Bestseller",
    "BestsellersResponse",
    # Vinted response envelopes
    "BrandsResponse",
    "CategoriesResponse",
    "CategoryResponse",
    # Configuration
    "ClientConfig",
    "ColorsResponse",
    "Deal",
    "DealsResponse",
    # Web scraping
    "DetectResult",
    # Google Scraper
    "GoogleClient",
    "InsufficientCreditsError",
    "ItemDetailResponse",
    "MarketInfo",
    "MarketsResponse",
    "NewReleasesResponse",
    "NotFoundError",
    "Offer",
    "OffersResponse",
    # Pagination
    "PaginatedResponse",
    # Reddit response envelopes
    "PostCommentsResponse",
    "PostDetailResponse",
    "PostDuplicatesResponse",
    "Product",
    "ProductDetailResponse",
    "RateLimitError",
    # Reddit core models
    "RedditAward",
    "RedditComment",
    "RedditModeratedSubreddit",
    "RedditPost",
    "RedditRule",
    "RedditSubreddit",
    "RedditTrophy",
    "RedditUser",
    "RedditUserProfileResponse",
    "RedditUserSubreddit",
    "RedditWikiPage",
    "RegionInfo",
    "Review",
    "ReviewsResponse",
    # Main client
    "ScrapeBadger",
    # Exceptions
    "ScrapeBadgerError",
    "ScrapeResult",
    "SearchPostsResponse",
    "SearchResponse",
    "SearchUsersResponse",
    "Seller",
    "SellerFeedbackResponse",
    "SellerProductsResponse",
    "SellerProfileResponse",
    "ServerError",
    "StatusesResponse",
    "SubredditDetailResponse",
    "SubredditPostsResponse",
    "SubredditRulesResponse",
    "SubredditWikiPageResponse",
    "SubredditWikiPagesResponse",
    "SubredditsListResponse",
    "TikTokAd",
    "TikTokAdVideo",
    "TikTokAuthor",
    # TikTok client
    "TikTokClient",
    "TikTokComment",
    # TikTok response envelopes
    "TikTokCommentListResponse",
    "TikTokCursorPage",
    "TikTokHashtag",
    "TikTokHashtagResponse",
    "TikTokHashtagSearchResponse",
    "TikTokMusic",
    "TikTokMusicResponse",
    "TikTokOEmbed",
    "TikTokProfileResponse",
    "TikTokRegionsResponse",
    "TikTokStats",
    "TikTokTranscriptResponse",
    "TikTokTrendingHashtag",
    "TikTokTrendingHashtagsResponse",
    "TikTokTrendingSong",
    "TikTokTrendingSongsResponse",
    "TikTokUser",
    "TikTokUserListResponse",
    "TikTokUserSearchResponse",
    "TikTokUserStats",
    "TikTokVideo",
    "TikTokVideoListResponse",
    "TikTokVideoMeta",
    "TikTokVideoResponse",
    "TrendingPostsResponse",
    "UserCommentsResponse",
    "UserItemsResponse",
    "UserModeratedResponse",
    "UserPostsResponse",
    "UserProfileResponse",
    "UserTrophiesResponse",
    "ValidationError",
    # Vinted reference models
    "VintedBrand",
    "VintedColor",
    # Vinted core models
    "VintedItemDetail",
    "VintedItemSummary",
    "VintedMarket",
    # Vinted pagination
    "VintedPagination",
    # Vinted nested models
    "VintedPhoto",
    "VintedPrice",
    "VintedSellerSummary",
    "VintedStatus",
    "VintedUserProfile",
    "VintedUserSummary",
    # Stream exceptions
    "WebSocketStreamError",
    # Version
    "__version__",
]
