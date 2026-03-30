# Twitter API

The ScrapeBadger Twitter API provides access to 37+ endpoints covering tweets, users, lists, communities, trending topics, geographic places, and real-time streams. All methods are available via `client.twitter`.

[Back to main README](../README.md)

## Usage Examples

### Users

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Get user by username
    user = await client.twitter.users.get_by_username("elonmusk")
    print(f"{user.name} (@{user.username})")
    print(f"Followers: {user.followers_count:,}")
    print(f"Following: {user.following_count:,}")
    print(f"Bio: {user.description}")

    # Get user by ID
    user = await client.twitter.users.get_by_id("44196397")

    # Get extended "About" information
    about = await client.twitter.users.get_about("elonmusk")
    print(f"Account based in: {about.account_based_in}")
    print(f"Username changes: {about.username_changes}")
```

### Tweets

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Get a single tweet
    tweet = await client.twitter.tweets.get_by_id("1234567890")
    print(f"@{tweet.username}: {tweet.text}")
    print(f"Likes: {tweet.favorite_count:,}, Retweets: {tweet.retweet_count:,}")

    # Get multiple tweets
    tweets = await client.twitter.tweets.get_by_ids([
        "1234567890",
        "0987654321"
    ])

    # Search tweets
    from scrapebadger.twitter import QueryType

    results = await client.twitter.tweets.search(
        "python programming",
        query_type=QueryType.LATEST  # TOP, LATEST, or MEDIA
    )

    # Get user's timeline
    tweets = await client.twitter.tweets.get_user_tweets("elonmusk")
```

### Automatic Pagination

All paginated endpoints support both manual pagination and automatic iteration:

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Manual pagination
    followers = await client.twitter.users.get_followers("elonmusk")
    for user in followers.data:
        print(f"@{user.username}")

    if followers.has_more:
        more = await client.twitter.users.get_followers(
            "elonmusk",
            cursor=followers.next_cursor
        )

    # Automatic pagination with async iterator
    async for follower in client.twitter.users.get_followers_all(
        "elonmusk",
        max_items=1000  # Optional limit
    ):
        print(f"@{follower.username}")

    # Collect all results into a list
    all_followers = [
        user async for user in client.twitter.users.get_followers_all(
            "elonmusk",
            max_pages=10
        )
    ]
```

### Lists

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Search for lists
    lists = await client.twitter.lists.search("tech leaders")
    for lst in lists.data:
        print(f"{lst.name}: {lst.member_count} members")

    # Get list details
    lst = await client.twitter.lists.get_detail("123456")

    # Get list tweets
    tweets = await client.twitter.lists.get_tweets("123456")

    # Get list members
    members = await client.twitter.lists.get_members("123456")
```

### Communities

```python
async with ScrapeBadger(api_key="your-key") as client:
    from scrapebadger.twitter import CommunityTweetType

    # Search communities
    communities = await client.twitter.communities.search("python developers")

    # Get community details
    community = await client.twitter.communities.get_detail("123456")
    print(f"{community.name}: {community.member_count:,} members")
    print(f"Rules: {len(community.rules or [])}")

    # Get community tweets
    tweets = await client.twitter.communities.get_tweets(
        "123456",
        tweet_type=CommunityTweetType.LATEST
    )

    # Get members
    members = await client.twitter.communities.get_members("123456")
```

### Trending Topics

```python
async with ScrapeBadger(api_key="your-key") as client:
    from scrapebadger.twitter import TrendCategory

    # Get global trends
    trends = await client.twitter.trends.get_trends()
    for trend in trends.data:
        count = f"{trend.tweet_count:,}" if trend.tweet_count else "N/A"
        print(f"{trend.name}: {count} tweets")

    # Get trends by category
    news = await client.twitter.trends.get_trends(category=TrendCategory.NEWS)
    sports = await client.twitter.trends.get_trends(category=TrendCategory.SPORTS)

    # Get trends for a specific location (WOEID)
    us_trends = await client.twitter.trends.get_place_trends(23424977)  # US
    print(f"Trends in {us_trends.name}:")
    for trend in us_trends.trends:
        print(f"  - {trend.name}")

    # Get available trend locations
    locations = await client.twitter.trends.get_available_locations()
    us_cities = [loc for loc in locations.data if loc.country_code == "US"]
```

### Geographic Places

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Search places by name
    places = await client.twitter.geo.search(query="San Francisco")
    for place in places.data:
        print(f"{place.full_name} ({place.place_type})")

    # Search by coordinates
    places = await client.twitter.geo.search(
        lat=37.7749,
        long=-122.4194,
        granularity="city"
    )

    # Get place details
    place = await client.twitter.geo.get_detail("5a110d312052166f")
```

### Streams (Real-Time Monitoring)

Monitor Twitter accounts in real-time with WebSocket delivery:

```python
import asyncio
from scrapebadger import ScrapeBadger

async def main():
    async with ScrapeBadger(api_key="your-key") as client:
        # Create a stream monitor
        monitor = await client.twitter.stream.create_monitor(
            name="Tech CEOs",
            usernames=["elonmusk", "sama", "naval"],
            poll_interval_seconds=5.0,
        )
        print(f"Monitor '{monitor.name}' created (tier: {monitor.pricing_tier})")
        print(f"Estimated cost: {monitor.estimated_credits_per_hour:.0f} credits/hour")

        # List monitors
        result = await client.twitter.stream.list_monitors(status="active")
        print(f"{result.total} active monitors")

        # Stream tweets via WebSocket
        async with client.twitter.stream.connect(reconnect=True) as events:
            async for event in events:
                if event.type == "tweet":
                    print(f"@{event.author_username}: {event.tweet.text}")
                    print(f"  Detected in {event.latency_ms}ms")
                elif event.type == "connected":
                    print(f"Connected (id: {event.connection_id})")

        # Pause/resume/delete
        await client.twitter.stream.pause_monitor(monitor.id)
        await client.twitter.stream.delete_monitor(monitor.id)

asyncio.run(main())
```

### Webhook Verification

Verify incoming webhook signatures in your receiver:

```python
from scrapebadger.twitter.stream import verify_webhook_signature

@app.post("/webhook")
async def handle_webhook(request):
    signature = request.headers["x-scrapebadger-signature"]
    body = await request.body()
    if not verify_webhook_signature("your-secret", body, signature):
        return JSONResponse({"error": "Invalid signature"}, status_code=401)
    event = json.loads(body)
    # Process event...
```

## API Reference

| Category | Methods |
|----------|---------|
| **Tweets** | `get_by_id`, `get_by_ids`, `search`, `search_all`, `get_user_tweets`, `get_user_tweets_all`, `get_replies`, `get_retweeters`, `get_favoriters`, `get_similar` |
| **Users** | `get_by_id`, `get_by_username`, `get_about`, `search`, `search_all`, `get_followers`, `get_followers_all`, `get_following`, `get_following_all`, `get_follower_ids`, `get_following_ids`, `get_latest_followers`, `get_latest_following`, `get_verified_followers`, `get_followers_you_know`, `get_subscriptions`, `get_highlights` |
| **Lists** | `get_detail`, `search`, `get_tweets`, `get_tweets_all`, `get_members`, `get_members_all`, `get_subscribers`, `get_my_lists` |
| **Communities** | `get_detail`, `search`, `get_tweets`, `get_tweets_all`, `get_members`, `get_moderators`, `search_tweets`, `get_timeline` |
| **Trends** | `get_trends`, `get_place_trends`, `get_available_locations` |
| **Geo** | `get_detail`, `search` |
| **Streams** | `create_monitor`, `list_monitors`, `get_monitor`, `update_monitor`, `pause_monitor`, `resume_monitor`, `delete_monitor`, `list_delivery_logs`, `list_billing_logs`, `connect` |

## Response Models

All responses use strongly-typed Pydantic models:

| Model | Description |
|-------|-------------|
| `Tweet` | Tweet data with text, metrics, media, polls, etc. |
| `User` | User profile with bio, metrics, verification status |
| `UserAbout` | Extended user information |
| `List` | Twitter list details |
| `Community` | Community with rules and admin info |
| `Trend` | Trending topic |
| `Place` | Geographic place |
| `PaginatedResponse[T]` | Wrapper for paginated results |
| `StreamMonitor` | Stream monitor configuration and status |
| `StreamMonitorList` | Paginated list of monitors |
| `TweetEvent` | Real-time tweet delivery event with latency |
| `ConnectedEvent`, `PingEvent`, `ErrorEvent` | WebSocket lifecycle events |
| `DeliveryLog`, `BillingLog` | Audit log records |

See the [full API documentation](https://docs.scrapebadger.com) for complete details.

---

[Back to main README](../README.md)
