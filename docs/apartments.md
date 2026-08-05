# Apartments.com API

US rental listings from apartments.com, with **unit-level pricing**: every
rentable unit's rent, beds, baths, square footage and availability date.

Single market: apartments.com (US, USD, en-US).

## Search

```python
from scrapebadger import ScrapeBadger

async with ScrapeBadger(api_key="your-key") as client:
    page = await client.apartments.search("kansas-city-mo", beds=1, max_price=1500)
    print(f"{page.total_results} rentals, page {page.page} of {page.total_pages}")
    for card in page.results:
        print(card.name, card.address, card.pricing)
```

`location` is the apartments.com slug (`kansas-city-mo`, `new-york-ny`) or a
ZIP. 40 cards a page, `page` 1-28.

Filters — each verified to actually change the result count:

| filter | effect on `kansas-city-mo` (700 baseline) |
|---|---|
| `beds=0` (studios) | 145 |
| `beds=1` | 374 |
| `beds=2` | 490 |
| `max_price=1500` | 646 |
| `min_price=1000, max_price=1500` | 546 |
| `beds=1, max_price=1500` | 320 |

A pet filter exists on the site but returns the unfiltered total, so it is
deliberately not exposed.

## Property detail

```python
prop = await client.apartments.get_property(
    "https://www.apartments.com/urbane-kansas-city-mo/wcd6e5k/"
)
# or: await client.apartments.get_property(slug="urbane-kansas-city-mo", property_id="wcd6e5k")

print(prop.name, prop.city, prop.state, prop.rent_range_text)
for unit in prop.units:
    print(unit.unit_number, unit.rent, unit.beds, unit.sqft, unit.available_text)
```

### Use `rent`, not `max_term_rent`

`unit.rent` is the advertised price the site shows a renter. `unit.max_term_rent`
is apartments.com's raw `data-maxrent` attribute, which measures **roughly twice**
the advertised rent and appears to be an upper bound across lease terms. It is
exposed unparsed for completeness — do not treat it as the rent.

### Availability is text, not a date

`unit.available_text` is verbatim (`"Now"`, `"Sep 3"`). The site renders no
year, so converting to a timestamp would require guessing the rollover.

### Some properties list plans without units

`units_available == 0` with valid plan-level beds/baths/rent/sqft is the site's
own layout for those properties, not missing data.

## No JavaScript rendering needed

apartments.com is fully server-rendered. If you call the general Web Scraping
API against it directly, do **not** pass `render_js=True` — it forces the slow
browser path (100+ seconds) and can exceed the CDN timeout with a 524.

## Cost

5 credits per search page and per property.
