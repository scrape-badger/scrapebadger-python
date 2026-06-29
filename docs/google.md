# Google API

The ScrapeBadger Google API provides structured JSON access to **16 Google product APIs** across 30 endpoints: Search, Maps, News, Hotels, Trends, Jobs, Shopping, Patents, Scholar, Autocomplete, Images, Videos, Finance, AI Mode, Lens, and immersive Products. All methods are available via `client.google`.

The service handles SearchGuard, proxy rotation, cookie warmup, and IP rotation on 429s automatically — you just call the endpoint.

[Back to main README](../README.md)

## Usage Examples

### Web Search (SERP)

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Basic search
    serp = await client.google.search.search("python 3.13")
    for result in serp["organic_results"]:
        print(result["title"], result["link"])

    # Search with advanced parameters (21 supported)
    serp = await client.google.search.search(
        "best laptops 2026",
        gl="gb",
        hl="en",
        num=20,
        start=10,
        domain="google.co.uk",  # any of 185 Google domains
        device="mobile",
        tbs="qdr:w",  # past week
        safe="off",
    )
    # Structured sections:
    #   serp["organic_results"]      — position, title, link, snippet, displayed_link
    #   serp["knowledge_graph"]      — title, type, description, attributes
    #   serp["ai_overview"]          — text_blocks, references, videos
    #   serp["related_questions"]    — People Also Ask
    #   serp["related_searches"]     — query, link
    #   serp["pagination"]           — current, next, page_no map
    print(f"About {serp['search_information']['total_results']:,} results "
          f"in {serp['search_information']['time_taken']}s")
```

### Maps (Search, Place, Reviews, Photos, Posts)

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Search for places
    places = await client.google.maps.search(
        "coffee shops in san francisco",
        ll="@37.7749,-122.4194,14z",
    )
    for place in places["results"]:
        print(f"{place['title']} — {place['rating']}★ ({place['reviews_count']} reviews)")

    # Place details
    detail = await client.google.maps.place(data_id="0x808580a2:0x123abc")

    # Reviews (sorted + paginated)
    reviews = await client.google.maps.reviews(
        "0x808580a2:0x123abc",
        sort_by="newestFirst",
        results=20,
    )

    # Photos + business posts
    photos = await client.google.maps.photos("0x808580a2:0x123abc")
    posts = await client.google.maps.posts("0x808580a2:0x123abc")
```

### News (Search, Topics, Trending)

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Article search
    articles = await client.google.news.search("openai gpt-5", max_results=20)
    for a in articles["articles"]:
        print(f"[{a['source']['name']}] {a['title']} ({a['published_at']})")

    # News by predefined topic
    tech = await client.google.news.topics("TECHNOLOGY")

    # Trending stories (real-time)
    trending = await client.google.news.trending(gl="US")
```

### Hotels

```python
async with ScrapeBadger(api_key="your-key") as client:
    hotels = await client.google.hotels.search(
        "Paris",
        check_in="2026-05-01",
        check_out="2026-05-05",
        adults=2,
        currency="EUR",
    )
    for prop in hotels["properties"]:
        rate = prop.get("rate_per_night", {}).get("extracted")
        print(f"{prop['name']} — {rate} {hotels.get('currency', 'EUR')}")

    # Detailed property info using the property_token from search
    detail = await client.google.hotels.details(
        hotels["properties"][0]["property_token"],
        check_in="2026-05-01",
        check_out="2026-05-05",
    )
```

### Trends (Interest, Regions, Related, Trending)

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Interest over time — up to 5 comma-separated terms
    interest = await client.google.trends.interest(
        "python,javascript,rust,go,java",
        geo="US",
        date="today 12-m",
    )
    for point in interest["timeline"]:
        print(point["date"], point["values"])

    # Interest by region
    regions = await client.google.trends.regions("python", geo="")

    # Related topics + queries
    related = await client.google.trends.related("python")
    print("Rising queries:", [q["query"] for q in related["related_queries"]["rising"]])

    # Real-time trending
    trending = await client.google.trends.trending(geo="US")
```

### Jobs

```python
async with ScrapeBadger(api_key="your-key") as client:
    jobs = await client.google.jobs.search(
        "software engineer",
        location="San Francisco, CA",
        job_type="FULLTIME",
        date_posted="week",
    )
    for job in jobs["jobs"]:
        print(f"{job['title']} @ {job['company_name']} — {job['location']}")
```

### Shopping (Search + Product Detail + Merchant URL Enrichment)

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Step 1: search
    products = await client.google.shopping.search(
        "laptop",
        min_price=500,
        max_price=2000,
        sort_by="price_low",
    )
    for p in products["results"]:
        print(f"{p['title']} — {p['price']['extracted']} from {p['source']} "
              f"({p['rating']}★, {p['reviews']})")

    # Step 2: per-product merchant URL enrichment (billed per call)
    # Google has removed direct merchant links from organic Shopping HTML.
    # The click endpoint uses an "I'm Feeling Lucky" redirect (scoped to
    # the card's source merchant via the site: operator) to materialize
    # the real product page URL. Mirrors 
    # immersive product link pattern.
    first = products["results"][0]
    enriched = await client.google.shopping.click(
        title=first["title"],
        source=first["source"],     # scope: "site:walmart.com"
        product_id=first["product_id"],
    )
    print("Merchant URL:", enriched["merchant_url"])
    # https://www.walmart.com/ip/Lenovo-IdeaPad-5-16IRU9-...

    # Get detailed product information + seller list
    detail = await client.google.shopping.product(first["product_id"])

    # Multi-seller prices by barcode (GTIN-8/UPC-A/EAN-13/GTIN-14).
    # Resolves the barcode to a product, then returns its Shopping offers.
    offers = await client.google.shopping.offers("0190198001751", gl="us")
    print(offers["product_title"])
    for o in offers["offers"]:
        print(f"{o['source']} — {o['price']['extracted']}")
```

### Patents

```python
async with ScrapeBadger(api_key="your-key") as client:
    results = await client.google.patents.search(
        "distributed lock manager",
        assignee="Google",
        sort="new",
    )
    for patent in results["results"]:
        print(f"{patent['patent_id']}: {patent['title']}")

    # Full patent detail (abstract, claims, citations, classifications)
    detail = await client.google.patents.detail("US10123456B2")
    print(detail["abstract"])
    print("Claims:", len(detail["claims"]))
```

### Scholar

```python
async with ScrapeBadger(api_key="your-key") as client:
    papers = await client.google.scholar.search(
        "transformer attention mechanism",
        as_ylo=2020,
        as_yhi=2024,
        num=20,
    )
    for paper in papers["results"]:
        print(f"{paper['title']} ({paper.get('cited_by_count', 0)} citations)")
```

### Autocomplete, Images, Videos

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Search suggestions
    suggestions = await client.google.autocomplete.get("pyth")
    print(suggestions["suggestions"])

    # Image search with size + color filters
    images = await client.google.images.search(
        "golden retriever",
        imgsz="l",        # large
        imgcolor="color",
        imgtype="photo",
    )

    # Video search
    videos = await client.google.videos.search("python async tutorial", tbs="qdr:w")
```

### Finance, AI Mode, Lens, Products

```python
async with ScrapeBadger(api_key="your-key") as client:
    # Stock / index / crypto quotes
    quote = await client.google.finance.quote("AAPL:NASDAQ")
    print(f"{quote['symbol']}: {quote['price']} ({quote['change']}%)")

    # AI-generated answers (udm=50)
    ai_answer = await client.google.ai_mode.search("what is kubernetes?")
    for block in ai_answer["text_blocks"]:
        print(block["snippet"])
    for ref in ai_answer["references"]:
        print("Source:", ref["title"], ref["link"])

    # Visual image search by URL
    lens = await client.google.lens.search("https://example.com/photo.jpg")

    # Immersive product detail (by product_id)
    product = await client.google.products.detail("1234567890")
```

## API Reference

### Sub-clients

| Sub-client | Description |
|---|---|
| `client.google.search` | Google web search (SERP) |
| `client.google.maps` | Maps: search, place, reviews, photos, posts |
| `client.google.news` | News: search, topics, trending |
| `client.google.hotels` | Hotels: search, details |
| `client.google.trends` | Trends: interest, regions, related, trending |
| `client.google.jobs` | Job listings search |
| `client.google.shopping` | Shopping: search, product, click enrichment |
| `client.google.patents` | Patents: search, detail |
| `client.google.scholar` | Academic paper search |
| `client.google.autocomplete` | Search suggestion lookup |
| `client.google.images` | Image search |
| `client.google.videos` | Video search |
| `client.google.finance` | Stock / index / crypto quotes |
| `client.google.ai_mode` | Generative AI answers (udm=50) |
| `client.google.lens` | Visual image search by URL |
| `client.google.products` | Immersive product detail |

### Methods

| Sub-client | Method | Description |
|---|---|---|
| `search` | `search(q, *, gl, hl, num, start, domain, device, ...)` | Web search with 21 parameters |
| `maps` | `search(q, *, ll, gl, hl, start)` | Place search by query |
| `maps` | `place(*, place_id, data_id, hl, gl)` | Place detail |
| `maps` | `reviews(data_id, *, sort_by, hl, next_page_token, results)` | Paginated reviews |
| `maps` | `photos(data_id, *, hl, next_page_token)` | Place photos |
| `maps` | `posts(data_id, *, next_page_token)` | Business posts |
| `news` | `search(q, *, hl, gl, max_results)` | News article search |
| `news` | `topics(topic, *, hl, gl, max_results)` | News by topic |
| `news` | `trending(*, hl, gl, max_results)` | Trending stories |
| `hotels` | `search(q, *, check_in, check_out, adults, currency, gl)` | Hotel search |
| `hotels` | `details(property_token, *, check_in, check_out)` | Property details |
| `trends` | `interest(q, *, geo, date)` | Interest over time |
| `trends` | `regions(q, *, geo)` | Interest by region |
| `trends` | `related(q, *, geo)` | Related topics + queries |
| `trends` | `trending(*, geo)` | Real-time trending |
| `jobs` | `search(q, *, location, gl, job_type, date_posted)` | Job listings |
| `shopping` | `search(q, *, gl, min_price, max_price, sort_by)` | Product search |
| `shopping` | `product(product_id, *, gl)` | Product detail + sellers |
| `shopping` | `click(title, *, source, q, product_id, gl, hl)` | Merchant URL enrichment |
| `shopping` | `offers(barcode, *, gl, hl)` | Multi-seller prices by barcode |
| `patents` | `search(q, *, page, num, sort, inventor, assignee)` | Patent search |
| `patents` | `detail(patent_id)` | Patent document |
| `scholar` | `search(q, *, hl, as_ylo, as_yhi, as_sdt, page, num)` | Academic papers |
| `autocomplete` | `get(q, *, hl, gl)` | Search suggestions |
| `images` | `search(q, *, gl, hl, tbs, imgsz, imgcolor, imgtype, safe, page)` | Image search |
| `videos` | `search(q, *, gl, hl, tbs, safe, page)` | Video search |
| `finance` | `quote(q, *, hl)` | Stock/index/crypto quote |
| `ai_mode` | `search(q, *, gl, hl)` | AI-generated answer |
| `lens` | `search(url, *, gl, hl)` | Visual search by URL |
| `products` | `detail(product_id, *, gl, hl)` | Immersive product |

All methods are async and return `dict[str, Any]` responses matching the documented JSON shapes.

## Credit Costs

| Endpoint | Credits |
|---|---|
| `search`, `images`, `videos`, `maps/search`, `shopping/search`, `jobs/search`, `scholar/search`, `patents/search`, `finance/quote`, `trends/*` (except trending) | **2** |
| `maps/place`, `maps/reviews`, `patents/detail`, `ai-mode/search`, `lens/search`, `hotels/search`, `products/detail` | **3** |
| `hotels/details`, `shopping/product` | **5** |
| `shopping/offers` | **14** |
| `news/*`, `autocomplete`, `trends/trending`, `maps/photos`, `maps/posts`, `shopping/product/click` | **1** |
| Failed requests | **0** |

## Anti-Bot Handling

Google deployed **SearchGuard** in January 2025 — a JavaScript challenge that blocks raw HTTP. The ScrapeBadger Google scraper handles it automatically:

1. First request attempts `curl_cffi` with cached cookies (~0.2s fast path)
2. On SearchGuard detection, a `patchright` browser warmup solves the challenge
3. Subsequent requests reuse the warm cookies for speed
4. On 429 or CAPTCHA, the cached residential proxy session is invalidated to rotate the exit IP (up to 3 rotations per request)

## Shopping Click Enrichment — Why It Exists

Google has removed direct merchant URLs from organic Shopping HTML — clicking a product card in the real Shopping UI opens a JavaScript modal that only fetches merchant info when you click "Visit site". Capturing that flow in a single synchronous scrape is impractical (~60-90s for 50 products).

Instead, the `shopping/product/click` endpoint exposes per-product merchant URL resolution as an **on-demand call** using Google's "I'm Feeling Lucky" redirect (`btnI=1`), scoped to the card's `source` merchant via a `site:` operator. You only pay for enrichment when you actually need the link — per-call credit cost is configured per-endpoint by admins (query `/public/pricing` for the live rate).

Known source → domain mappings include: Walmart, Best Buy, Amazon, Target, eBay, Newegg, Costco, Home Depot, Lowe's, Staples, Office Depot, Micro Center, Adorama, B&H Photo-Video-Pro Audio, HP, Dell, Lenovo, Apple, Razer, Asus, Acer, HyperX, MSI, Samsung. When the source is not in the map, the endpoint falls back to a bare-title query.

See the [full API documentation](https://docs.scrapebadger.com) for complete details on every endpoint, including Pydantic response schemas and all parameters.

---

[Back to main README](../README.md)
