# Amazon API

The ScrapeBadger Amazon API provides access to Amazon product data across 14 endpoints: keyword search, autocomplete, product detail, offers, reviews, bestsellers, new releases, deals, category browse, seller profile/products/feedback, and reference data (markets, categories). All methods are available via `client.amazon`.

[Back to main README](../README.md)

## Sub-clients

| Sub-client | Methods | Endpoints |
|------------|---------|-----------|
| `client.amazon.search` | `search`, `autocomplete` | `/v1/amazon/search`, `/v1/amazon/autocomplete` |
| `client.amazon.products` | `get`, `offers`, `reviews` | `/v1/amazon/products/{asin}`, `.../offers`, `.../reviews` |
| `client.amazon.listings` | `bestsellers`, `new_releases`, `deals`, `category` | `/v1/amazon/bestsellers`, `/new-releases`, `/deals`, `/category` |
| `client.amazon.sellers` | `get`, `products`, `feedback` | `/v1/amazon/sellers/{id}`, `.../products`, `.../feedback` |
| `client.amazon.reference` | `markets`, `categories` | `/v1/amazon/markets`, `/v1/amazon/categories` |

## Usage Examples

### Search

```python
async with ScrapeBadger(api_key="your-key") as client:
    results = await client.amazon.search.search(
        "wireless headphones",
        domain="com",
        min_price=20,
        max_price=200,
        sort_by="price_low_to_high",
    )
    for item in results.results:
        price = item.price.raw if item.price else "N/A"
        print(f"{item.position}. {item.title} - {price}")

    # Autocomplete
    suggestions = await client.amazon.search.autocomplete("lapt")
    for s in suggestions.suggestions:
        print(s.value)
```

### Product Detail / Offers / Reviews

```python
async with ScrapeBadger(api_key="your-key") as client:
    detail = await client.amazon.products.get("B08N5WRWNW", domain="com")
    product = detail.product
    print(f"{product.title} by {product.brand}")
    print(f"Rating: {product.rating} ({product.ratings_total} ratings)")

    offers = await client.amazon.products.offers("B08N5WRWNW")
    print(f"{offers.total_offers} offers")

    reviews = await client.amazon.products.reviews(
        "B08N5WRWNW", sort_by="recent", verified_only=True,
    )
    for r in reviews.reviews:
        print(f"{r.rating}* {r.title}")
```

### Listings (bestsellers / new releases / deals / category)

```python
async with ScrapeBadger(api_key="your-key") as client:
    top = await client.amazon.listings.bestsellers(category="electronics")
    new = await client.amazon.listings.new_releases(category="books")
    deals = await client.amazon.listings.deals()
    cat = await client.amazon.listings.category("172282", sort_by="featured")
```

### Sellers

```python
async with ScrapeBadger(api_key="your-key") as client:
    profile = await client.amazon.sellers.get("A2L77EE7U53NWQ")
    print(f"{profile.seller.name}: {profile.seller.rating}*")

    products = await client.amazon.sellers.products("A2L77EE7U53NWQ", page=1)
    feedback = await client.amazon.sellers.feedback("A2L77EE7U53NWQ")
```

### Reference Data

```python
async with ScrapeBadger(api_key="your-key") as client:
    markets = await client.amazon.reference.markets()
    for m in markets.markets:
        print(f"{m.code}: {m.domain} ({m.currency})")

    categories = await client.amazon.reference.categories()
    for c in categories.categories:
        print(f"{c.name} -> {c.alias}")
```
