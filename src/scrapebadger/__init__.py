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
from scrapebadger.ebay.client import EbayClient
from scrapebadger.ebay.models import (
    AutocompleteResponse as EbayAutocompleteResponse,
)
from scrapebadger.ebay.models import (
    AutocompleteSuggestion as EbayAutocompleteSuggestion,
)
from scrapebadger.ebay.models import (
    CategoriesResponse as EbayCategoriesResponse,
)
from scrapebadger.ebay.models import (
    CategoryInfo as EbayCategoryInfo,
)
from scrapebadger.ebay.models import (
    CategoryResponse as EbayCategoryResponse,
)
from scrapebadger.ebay.models import (
    EbayImage,
    EbayPrice,
    FeedbackBreakdown,
    ReturnsPolicy,
    ShippingOption,
)
from scrapebadger.ebay.models import (
    FeedbackEntry as EbayFeedbackEntry,
)
from scrapebadger.ebay.models import (
    Item as EbayItem,
)
from scrapebadger.ebay.models import (
    ItemDetailResponse as EbayItemDetailResponse,
)
from scrapebadger.ebay.models import (
    ItemSeller as EbayItemSeller,
)
from scrapebadger.ebay.models import (
    MarketInfo as EbayMarketInfo,
)
from scrapebadger.ebay.models import (
    MarketsResponse as EbayMarketsResponse,
)
from scrapebadger.ebay.models import (
    Pagination as EbayPagination,
)
from scrapebadger.ebay.models import (
    RatingHistogram as EbayRatingHistogram,
)
from scrapebadger.ebay.models import (
    Review as EbayReview,
)
from scrapebadger.ebay.models import (
    ReviewsResponse as EbayReviewsResponse,
)
from scrapebadger.ebay.models import (
    SearchResponse as EbaySearchResponse,
)
from scrapebadger.ebay.models import (
    SearchResult as EbaySearchResult,
)
from scrapebadger.ebay.models import (
    Seller as EbaySeller,
)
from scrapebadger.ebay.models import (
    SellerFeedbackResponse as EbaySellerFeedbackResponse,
)
from scrapebadger.ebay.models import (
    SellerItemsResponse as EbaySellerItemsResponse,
)
from scrapebadger.ebay.models import (
    SellerProfileResponse as EbaySellerProfileResponse,
)
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
from scrapebadger.youtube.client import YoutubeClient
from scrapebadger.youtube.models import (
    AudioTrack as YoutubeAudioTrack,
)
from scrapebadger.youtube.models import (
    AutocompleteResponse as YoutubeAutocompleteResponse,
)
from scrapebadger.youtube.models import (
    BatchResponse as YoutubeBatchResponse,
)
from scrapebadger.youtube.models import (
    CaptionsResponse as YoutubeCaptionsResponse,
)
from scrapebadger.youtube.models import (
    CaptionTrack as YoutubeCaptionTrack,
)
from scrapebadger.youtube.models import (
    CategoriesResponse as YoutubeCategoriesResponse,
)
from scrapebadger.youtube.models import (
    Channel as YoutubeChannel,
)
from scrapebadger.youtube.models import (
    ChannelAbout as YoutubeChannelAbout,
)
from scrapebadger.youtube.models import (
    ChannelLink as YoutubeChannelLink,
)
from scrapebadger.youtube.models import (
    ChannelTabResponse as YoutubeChannelTabResponse,
)
from scrapebadger.youtube.models import (
    ChannelVideosResponse as YoutubeChannelVideosResponse,
)
from scrapebadger.youtube.models import (
    Chapter as YoutubeChapter,
)
from scrapebadger.youtube.models import (
    Comment as YoutubeComment,
)
from scrapebadger.youtube.models import (
    CommentsResponse as YoutubeCommentsResponse,
)
from scrapebadger.youtube.models import (
    CommunityPost as YoutubeCommunityPost,
)
from scrapebadger.youtube.models import (
    CommunityResponse as YoutubeCommunityResponse,
)
from scrapebadger.youtube.models import (
    Format as YoutubeFormat,
)
from scrapebadger.youtube.models import (
    HashtagResponse as YoutubeHashtagResponse,
)
from scrapebadger.youtube.models import (
    HeatMarker as YoutubeHeatMarker,
)
from scrapebadger.youtube.models import (
    HomeResponse as YoutubeHomeResponse,
)
from scrapebadger.youtube.models import (
    LanguagesResponse as YoutubeLanguagesResponse,
)
from scrapebadger.youtube.models import (
    LiveChatMessage as YoutubeLiveChatMessage,
)
from scrapebadger.youtube.models import (
    LiveChatResponse as YoutubeLiveChatResponse,
)
from scrapebadger.youtube.models import (
    LiveStreamingDetails as YoutubeLiveStreamingDetails,
)
from scrapebadger.youtube.models import (
    MarketInfo as YoutubeMarketInfo,
)
from scrapebadger.youtube.models import (
    MarketsResponse as YoutubeMarketsResponse,
)
from scrapebadger.youtube.models import (
    OEmbed as YoutubeOEmbed,
)
from scrapebadger.youtube.models import (
    Playlist as YoutubePlaylist,
)
from scrapebadger.youtube.models import (
    PlaylistItem as YoutubePlaylistItem,
)
from scrapebadger.youtube.models import (
    PlaylistItemsResponse as YoutubePlaylistItemsResponse,
)
from scrapebadger.youtube.models import (
    PollChoice as YoutubePollChoice,
)
from scrapebadger.youtube.models import (
    ReferenceRow as YoutubeReferenceRow,
)
from scrapebadger.youtube.models import (
    RegionRestriction as YoutubeRegionRestriction,
)
from scrapebadger.youtube.models import (
    RegionsResponse as YoutubeRegionsResponse,
)
from scrapebadger.youtube.models import (
    RelatedResponse as YoutubeRelatedResponse,
)
from scrapebadger.youtube.models import (
    RepliesResponse as YoutubeRepliesResponse,
)
from scrapebadger.youtube.models import (
    ResolveResult as YoutubeResolveResult,
)
from scrapebadger.youtube.models import (
    SearchChip as YoutubeSearchChip,
)
from scrapebadger.youtube.models import (
    SearchResponse as YoutubeSearchResponse,
)
from scrapebadger.youtube.models import (
    SearchResult as YoutubeSearchResult,
)
from scrapebadger.youtube.models import (
    ShoppingResult as YoutubeShoppingResult,
)
from scrapebadger.youtube.models import (
    Short as YoutubeShort,
)
from scrapebadger.youtube.models import (
    StreamingData as YoutubeStreamingData,
)
from scrapebadger.youtube.models import (
    SubscriberCount as YoutubeSubscriberCount,
)
from scrapebadger.youtube.models import (
    Thumbnail as YoutubeThumbnail,
)
from scrapebadger.youtube.models import (
    Transcript as YoutubeTranscript,
)
from scrapebadger.youtube.models import (
    TranscriptSegment as YoutubeTranscriptSegment,
)
from scrapebadger.youtube.models import (
    TrendingItem as YoutubeTrendingItem,
)
from scrapebadger.youtube.models import (
    TrendingResponse as YoutubeTrendingResponse,
)
from scrapebadger.youtube.models import (
    Video as YoutubeVideo,
)

__version__ = "0.15.3"

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
    # eBay response envelopes / models
    "EbayAutocompleteResponse",
    "EbayAutocompleteSuggestion",
    "EbayCategoriesResponse",
    "EbayCategoryInfo",
    "EbayCategoryResponse",
    # eBay client
    "EbayClient",
    "EbayFeedbackEntry",
    # eBay shared models
    "EbayImage",
    "EbayItem",
    "EbayItemDetailResponse",
    "EbayItemSeller",
    "EbayMarketInfo",
    "EbayMarketsResponse",
    "EbayPagination",
    "EbayPrice",
    "EbayRatingHistogram",
    "EbayReview",
    "EbayReviewsResponse",
    "EbaySearchResponse",
    "EbaySearchResult",
    "EbaySeller",
    "EbaySellerFeedbackResponse",
    "EbaySellerItemsResponse",
    "EbaySellerProfileResponse",
    "FeedbackBreakdown",
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
    "ReturnsPolicy",
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
    "ShippingOption",
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
    "YoutubeAudioTrack",
    "YoutubeAutocompleteResponse",
    "YoutubeBatchResponse",
    "YoutubeCaptionTrack",
    "YoutubeCaptionsResponse",
    "YoutubeCategoriesResponse",
    "YoutubeChannel",
    "YoutubeChannelAbout",
    "YoutubeChannelLink",
    "YoutubeChannelTabResponse",
    "YoutubeChannelVideosResponse",
    "YoutubeChapter",
    "YoutubeClient",
    "YoutubeComment",
    "YoutubeCommentsResponse",
    "YoutubeCommunityPost",
    "YoutubeCommunityResponse",
    "YoutubeFormat",
    "YoutubeHashtagResponse",
    "YoutubeHeatMarker",
    "YoutubeHomeResponse",
    "YoutubeLanguagesResponse",
    "YoutubeLiveChatMessage",
    "YoutubeLiveChatResponse",
    "YoutubeLiveStreamingDetails",
    "YoutubeMarketInfo",
    "YoutubeMarketsResponse",
    "YoutubeOEmbed",
    "YoutubePlaylist",
    "YoutubePlaylistItem",
    "YoutubePlaylistItemsResponse",
    "YoutubePollChoice",
    "YoutubeReferenceRow",
    "YoutubeRegionRestriction",
    "YoutubeRegionsResponse",
    "YoutubeRelatedResponse",
    "YoutubeRepliesResponse",
    "YoutubeResolveResult",
    "YoutubeSearchChip",
    "YoutubeSearchResponse",
    "YoutubeSearchResult",
    "YoutubeShoppingResult",
    "YoutubeShort",
    "YoutubeStreamingData",
    "YoutubeSubscriberCount",
    "YoutubeThumbnail",
    "YoutubeTranscript",
    "YoutubeTranscriptSegment",
    "YoutubeTrendingItem",
    "YoutubeTrendingResponse",
    "YoutubeVideo",
    # Version
    "__version__",
]
