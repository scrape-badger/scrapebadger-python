"""Twitter API client combining all sub-clients.

This module provides the main TwitterClient class that serves as the
entry point for all Twitter API operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scrapebadger.twitter.communities import CommunitiesClient
from scrapebadger.twitter.geo import GeoClient
from scrapebadger.twitter.lists import ListsClient
from scrapebadger.twitter.stream import StreamClient
from scrapebadger.twitter.trends import TrendsClient
from scrapebadger.twitter.tweets import TweetsClient
from scrapebadger.twitter.users import UsersClient

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class TwitterClient:
    """Client for all Twitter API operations.

    This class provides access to all Twitter scraping endpoints through
    organized sub-clients for different resource types.

    Attributes:
        tweets: Client for tweet-related operations.
        users: Client for user-related operations.
        lists: Client for Twitter lists operations.
        communities: Client for Twitter communities operations.
        trends: Client for trending topics operations.
        geo: Client for geographic/places operations.
        stream: Client for real-time stream monitor management and WebSocket streaming.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Access Twitter through the twitter property
            twitter = client.twitter

            # Get a user profile
            user = await twitter.users.get_by_username("elonmusk")
            print(f"{user.name} (@{user.username})")
            print(f"Followers: {user.followers_count:,}")

            # Get user's recent tweets
            tweets = await twitter.tweets.get_user_tweets("elonmusk")
            for tweet in tweets.data:
                print(f"- {tweet.text[:100]}...")

            # Search for tweets
            results = await twitter.tweets.search("python programming")
            print(f"Found {len(results.data)} tweets")

            # Get followers with automatic pagination
            async for follower in twitter.users.get_followers_all(
                "elonmusk",
                max_items=100
            ):
                print(f"  @{follower.username}")
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `twitter` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Twitter client with all sub-clients.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

        # Initialize sub-clients
        self._tweets = TweetsClient(client)
        self._users = UsersClient(client)
        self._lists = ListsClient(client)
        self._communities = CommunitiesClient(client)
        self._trends = TrendsClient(client)
        self._geo = GeoClient(client)
        self._stream = StreamClient(client)

    @property
    def tweets(self) -> TweetsClient:
        """Access tweet-related endpoints.

        Returns:
            TweetsClient for fetching tweets, searching, and getting engagement data.

        Example:
            ```python
            # Get a tweet by ID
            tweet = await client.twitter.tweets.get_by_id("1234567890")

            # Search tweets
            results = await client.twitter.tweets.search("python")

            # Get all search results with auto-pagination
            async for tweet in client.twitter.tweets.search_all("python"):
                print(tweet.text)
            ```
        """
        return self._tweets

    @property
    def users(self) -> UsersClient:
        """Access user-related endpoints.

        Returns:
            UsersClient for fetching profiles, followers, and following.

        Example:
            ```python
            # Get user by username
            user = await client.twitter.users.get_by_username("elonmusk")

            # Get followers
            followers = await client.twitter.users.get_followers("elonmusk")

            # Search users
            results = await client.twitter.users.search("python developer")
            ```
        """
        return self._users

    @property
    def lists(self) -> ListsClient:
        """Access Twitter lists endpoints.

        Returns:
            ListsClient for fetching lists, members, and list tweets.

        Example:
            ```python
            # Search for lists
            lists = await client.twitter.lists.search("tech leaders")

            # Get list tweets
            tweets = await client.twitter.lists.get_tweets("123456")

            # Get list members
            members = await client.twitter.lists.get_members("123456")
            ```
        """
        return self._lists

    @property
    def communities(self) -> CommunitiesClient:
        """Access Twitter communities endpoints.

        Returns:
            CommunitiesClient for fetching communities, members, and tweets.

        Example:
            ```python
            # Search communities
            communities = await client.twitter.communities.search("python")

            # Get community details
            community = await client.twitter.communities.get_detail("123456")

            # Get community tweets
            tweets = await client.twitter.communities.get_tweets("123456")
            ```
        """
        return self._communities

    @property
    def trends(self) -> TrendsClient:
        """Access trending topics endpoints.

        Returns:
            TrendsClient for fetching trends and trend locations.

        Example:
            ```python
            # Get global trends
            trends = await client.twitter.trends.get_trends()

            # Get US trends
            us_trends = await client.twitter.trends.get_place_trends(23424977)

            # Get available locations
            locations = await client.twitter.trends.get_available_locations()
            ```
        """
        return self._trends

    @property
    def geo(self) -> GeoClient:
        """Access geographic/places endpoints.

        Returns:
            GeoClient for fetching place details and searching locations.

        Example:
            ```python
            # Search places
            places = await client.twitter.geo.search(query="San Francisco")

            # Search by coordinates
            places = await client.twitter.geo.search(lat=37.7749, long=-122.4194)

            # Get place details
            place = await client.twitter.geo.get_detail("5a110d312052166f")
            ```
        """
        return self._geo

    @property
    def stream(self) -> StreamClient:
        """Access Twitter Streams -- real-time monitor management and WebSocket streaming.

        Returns:
            StreamClient for creating monitors and connecting to the live tweet stream.

        Example:
            ```python
            # Create a monitor
            monitor = await client.twitter.stream.create_monitor(
                name="Breaking News",
                usernames=["cnnbrk", "bbcbreaking"],
                poll_interval_seconds=5.0,
            )

            # Stream live tweets
            async with client.twitter.stream.connect() as events:
                async for event in events:
                    if isinstance(event, TweetEvent):
                        print(f"@{event.author_username}: {event.tweet.text}")
            ```
        """
        return self._stream
