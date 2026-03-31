# Vinted API

The ScrapeBadger Vinted API provides access to Vinted marketplace data including item search, item details, user profiles, and reference data (brands, colors, statuses, markets). All methods are available via `client.vinted`.

[Back to main README](../README.md)

## Usage Examples

### Search Items

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Basic search
    results = await client.vinted.search.search("nike air max")
    for item in results.items:
        print(f"{item.title}: {item.price.amount} {item.price.currency_code}")

    # Search with filters
    results = await client.vinted.search.search(
        "vintage jacket",
        market="de",
        page=1,
        per_page=40,
        price_from="20",
        price_to="100",
        brand_ids="53,72",
        color_ids="1,2",
        status_ids="6",
        order="newest_first",
    )
    print(f"Found {results.pagination.total_entries} items")
    for item in results.items:
        print(f"  {item.title} - {item.price.amount} {item.price.currency_code}")
```

### Item Details

```python
async with ScrapeBadger(api_key="your-key") as client:
    result = await client.vinted.items.get(123456789, market="fr")
    item = result.item
    print(f"{item.title}")
    print(f"Price: {item.price.amount} {item.price.currency_code}")
    print(f"Condition: {item.status}")
    print(f"Description: {item.description}")
    print(f"Seller: {item.seller.login} (rep: {item.seller.feedback_reputation})")
    print(f"Photos: {len(item.photos)}")
```

### User Profiles

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Get user profile
    result = await client.vinted.users.get_profile(12345, market="fr")
    user = result.user
    print(f"{user.login} from {user.city}, {user.country_code}")
    print(f"Reputation: {user.feedback_reputation}")
    print(f"Items: {user.item_count}")
    print(f"Followers: {user.followers_count}")

    # Get user's listed items
    items_result = await client.vinted.users.get_items(12345, page=1, per_page=40)
    print(f"Page {items_result.pagination.current_page}/{items_result.pagination.total_pages}")
    for item in items_result.items:
        print(f"  {item.title} - {item.price.amount} {item.price.currency_code}")
```

### Reference Data

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Get available markets
    markets = await client.vinted.reference.markets()
    for m in markets.markets:
        print(f"{m.code}: {m.name} ({m.currency})")

    # Search brands
    brands = await client.vinted.reference.brands("nike", market="fr")
    for b in brands.brands:
        print(f"{b.title} (id={b.id}, items={b.item_count})")

    # Get colors for a market
    colors = await client.vinted.reference.colors(market="de")
    for c in colors.colors:
        print(f"{c.title}: #{c.hex}")

    # Get item condition statuses
    statuses = await client.vinted.reference.statuses(market="fr")
    for s in statuses.statuses:
        print(f"{s.id}: {s.title}")
```

## API Reference

| Category | Methods |
|----------|---------|
| **Search** | `search` |
| **Items** | `get` |
| **Users** | `get_profile`, `get_items` |
| **Reference** | `brands`, `colors`, `statuses`, `markets` |

## Response Models

All responses use strongly-typed Pydantic models:

| Model | Description |
|-------|-------------|
| `SearchResponse` | Search results with items and pagination |
| `ItemDetailResponse` | Detailed item data with seller info |
| `UserProfileResponse` | Full user profile with reputation data |
| `UserItemsResponse` | User's listed items with pagination |
| `BrandsResponse` | List of matching brands |
| `ColorsResponse` | Available color options |
| `StatusesResponse` | Available item condition statuses |
| `MarketsResponse` | Available Vinted markets |
| `VintedItemSummary` | Item as seen in search results |
| `VintedItemDetail` | Full item details including description, seller, and metadata |
| `VintedUserProfile` | Complete user profile with feedback stats |
| `VintedPrice` | Price with amount and currency code |
| `VintedPhoto` | Photo with URL, dimensions, and dominant color |
| `VintedBrand` | Brand with item count and luxury flag |
| `VintedColor` | Color with hex code |
| `VintedStatus` | Item condition status |
| `VintedMarket` | Market with code, domain, country, and currency |
| `VintedPagination` | Pagination metadata (current page, total pages, total entries) |

See the [full API documentation](https://docs.scrapebadger.com) for complete details.

---

[Back to main README](../README.md)
