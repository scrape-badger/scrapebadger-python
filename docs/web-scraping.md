# Web Scraping API

The ScrapeBadger Web Scraping API lets you scrape any website with JavaScript rendering, anti-bot bypass, and AI-powered data extraction. All methods are available via `client.web`.

[Back to main README](../README.md)

## Usage Examples

### Basic Scrape

```python
async with ScrapeBadger(api_key="your-key") as client:
    result = await client.web.scrape("https://scrapebadger.com", format="markdown")
    print(result.content)
    print(f"Credits used: {result.credits_used}")
```

### JavaScript Rendering

```python
result = await client.web.scrape(
    "https://spa-website.com",
    render_js=True,
    wait_for="#dynamic-content",
    wait_timeout=10000,
)
```

### Anti-Bot Bypass with Escalation

```python
result = await client.web.scrape(
    "https://protected-site.com",
    escalate=True,
    anti_bot=True,
    country="US",
    max_cost=20,
)
```

### AI Data Extraction

```python
result = await client.web.extract(
    "https://scrapebadger.com/pricing",
    prompt="Extract all pricing plan names and prices as a JSON array",
    format="markdown",
)
print(result.ai_extraction)  # Structured data from LLM
```

### Screenshots

```python
shot = await client.web.screenshot(
    "https://scrapebadger.com",
    full_page=True,  # whole scrollable page, not just the viewport
    width=1280,
)
shot.save("page.png")  # or shot.png for the raw bytes
```

`scrape(..., screenshot=True)` takes the equivalent `screenshot_full_page`,
`window_width` and `window_height` options and returns the PNG as a `data:` URI
in `screenshot_url`.

### Selector and AI Extraction

```python
result = await client.web.extract_data(
    "https://news.ycombinator.com",
    extract_rules={
        "top_story": ".titleline a",
        "links": {"selector": ".titleline a::attr(href)", "all": True},
    },
    ai_query="What is the top story about, in one sentence?",
)
print(result.data)           # {"top_story": "...", "links": [...]}
print(result.ai_extraction)  # {"answer": "..."}
```

A selector starting with `/` or `(` is XPath; anything else is CSS. Pass
`ai_extract_rules={"field": "description"}` to have the AI return exactly those
keys.

### Detect Anti-Bot Protection

```python
detection = await client.web.detect("https://protected-site.com")
for system in detection.antibot_systems:
    print(f"{system['system']}: confidence {system['confidence']}")
print(f"Recommendation: {detection.recommendation}")
```

### Browser Automation

```python
result = await client.web.scrape(
    "https://scrapebadger.com",
    render_js=True,
    js_scenario=[
        {"type": "click", "selector": "#load-more"},
        {"type": "wait", "milliseconds": 2000},
        {"type": "scroll", "direction": "down", "amount": 1000},
    ],
)
```

## API Reference

| Method | Description |
|--------|-------------|
| `scrape` | Scrape a URL with optional JS rendering, anti-bot bypass, screenshots, video, and AI extraction |
| `extract` | Convenience wrapper -- scrapes with AI extraction enabled |
| `screenshot` | Render a URL in the browser and return a PNG (`full_page`, `width`, `height`) |
| `extract_data` | Extract fields with CSS/XPath `extract_rules`, `ai_extract_rules` and/or `ai_query` |
| `detect` | Detect anti-bot and CAPTCHA systems on a URL |
| `submit_batch_scraping_job`, `get_batch_job_status` | **Deprecated** -- batch is not available (`501`); send concurrent `scrape` calls |

## Response Models

### ScrapeResult

Full scrape response with content, metadata, blocking info, and AI extraction.

| Field | Description |
|-------|-------------|
| `content` | The scraped page content in the requested format |
| `credits_used` | Number of credits consumed by this request |
| `ai_extraction` | Structured data from AI extraction (when using `extract`) |
| `metadata` | Page metadata (title, description, etc.) |
| `blocking_info` | Details about anti-bot systems encountered |

### ScreenshotResult

| Field | Description |
|-------|-------------|
| `screenshot` | The PNG, base64-encoded |
| `png` | The decoded PNG bytes (property) |
| `save(path)` | Write the PNG to a file |
| `credits_used` | Number of credits consumed by this request |

### ExtractResult

| Field | Description |
|-------|-------------|
| `data` | One key per `extract_rules` field (first match, a list with `all`, or `None`) |
| `ai_extraction` | The AI's JSON answer to `ai_extract_rules` / `ai_query` |
| `ai_error` | Why AI extraction failed, when it did |
| `credits_used` | Number of credits consumed by this request |

### DetectResult

Protection detection results with system list and recommendation.

| Field | Description |
|-------|-------------|
| `antibot_systems` | List of detected anti-bot/CAPTCHA systems with confidence scores |
| `recommendation` | Suggested scraping strategy based on detected protections |

---

[Back to main README](../README.md)
