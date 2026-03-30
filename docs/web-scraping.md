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
| `detect` | Detect anti-bot and CAPTCHA systems on a URL |

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

### DetectResult

Protection detection results with system list and recommendation.

| Field | Description |
|-------|-------------|
| `antibot_systems` | List of detected anti-bot/CAPTCHA systems with confidence scores |
| `recommendation` | Suggested scraping strategy based on detected protections |

---

[Back to main README](../README.md)
