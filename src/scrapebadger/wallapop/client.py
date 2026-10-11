"""Wallapop API client.

Wallapop endpoints: search (listings with Wallapop's own filters, including
the cars vertical), get_item (full listing detail), get_user (seller profile),
get_user_items / get_user_reviews (a seller's listings and reviews),
autocomplete, list_categories, list_filters, list_filter_options and
list_markets. All methods are async and return strongly-typed Pydantic models.
Markets: es (default), it, pt.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.wallapop.models import (
    AutocompleteResponse,
    CategoriesResponse,
    FilterOptionsResponse,
    FiltersResponse,
    ItemDetail,
    MarketsResponse,
    ReviewsResponse,
    SearchResponse,
    UserItemsResponse,
    UserProfile,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

OrderBy = Literal["most_relevance", "newest", "closest", "price_low_to_high", "price_high_to_low"]
TimeFilter = Literal["today", "lastWeek", "lastMonth"]
Gearbox = Literal["manual", "automatic"]


def _set(params: dict[str, Any]) -> dict[str, Any]:
    """Drop unset params (``None``) and boolean filters left at ``False``."""
    return {k: v for k, v in params.items() if v is not None and v is not False}


class WallapopClient:
    """Client for all Wallapop API operations.

    Wallapop is a second-hand marketplace for Spain, Italy and Portugal,
    selected by ``market`` (es, it, pt). Search, user listings and user
    reviews return 40 results per page with cursor pagination: pass the
    response's ``next_page`` back as ``next_page`` to get the next page.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search listings
            results = await client.wallapop.search("iphone 14", max_price=400)
            for item in results.items:
                print(f"{item.title} — {item.price} {item.currency}")

            # Next page
            if results.next_page:
                page2 = await client.wallapop.search(next_page=results.next_page)

            # Full listing detail
            item = await client.wallapop.get_item("nzxeknm5x562")

            # Seller profile, listings and reviews
            user = await client.wallapop.get_user("dqjwdd53wwzo")
            listings = await client.wallapop.get_user_items("dqjwdd53wwzo")
            reviews = await client.wallapop.get_user_reviews("dqjwdd53wwzo")
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `wallapop` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Wallapop client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def search(
        self,
        query: str | None = None,
        *,
        market: str = "es",
        latitude: float | None = None,
        longitude: float | None = None,
        distance_km: int | None = None,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        condition: str | None = None,
        brand: str | None = None,
        model: str | None = None,
        color: str | None = None,
        time_filter: TimeFilter | None = None,
        shippable: bool = False,
        has_warranty: bool = False,
        refurbished: bool = False,
        min_year: int | None = None,
        max_year: int | None = None,
        min_km: int | None = None,
        max_km: int | None = None,
        gearbox: Gearbox | None = None,
        min_horsepower: int | None = None,
        max_horsepower: int | None = None,
        order_by: OrderBy | None = None,
        next_page: str | None = None,
    ) -> SearchResponse:
        """Search Wallapop listings (40 per page).

        Provide a ``query``, a ``category_id``, or both — or a ``next_page``
        cursor, in which case the other filters are ignored.

        Args:
            query: Search text, e.g. "iphone 14".
            market: Market code (es, it, pt). Defaults to "es".
            latitude: Search centre latitude (defaults to the market capital).
            longitude: Search centre longitude.
            distance_km: Radius around the centre, 1-500 km.
            category_id: Category id (see `list_categories`).
            min_price: Minimum price.
            max_price: Maximum price.
            condition: Comma-separated: un_opened, in_box, new, as_good_as_new,
                good, fair, has_given_it_all.
            brand: Brand, e.g. "Apple" (see `list_filter_options("brand")`).
            model: Model, e.g. "iPhone 14".
            color: Colour id, e.g. "black".
            time_filter: Listed within: today, lastWeek, lastMonth.
            shippable: Only listings that ship.
            has_warranty: Only listings with a warranty.
            refurbished: Only refurbished listings.
            min_year: Cars: earliest model year.
            max_year: Cars: latest model year.
            min_km: Cars: minimum mileage.
            max_km: Cars: maximum mileage.
            gearbox: Cars: manual or automatic.
            min_horsepower: Cars: minimum horsepower.
            max_horsepower: Cars: maximum horsepower.
            order_by: most_relevance (API default), newest, closest,
                price_low_to_high, price_high_to_low.
            next_page: Cursor from the previous page's ``next_page``.

        Returns:
            Search response with listings and the next-page cursor.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If neither query, category_id nor next_page is
                given, or a parameter is out of range.

        Example:
            ```python
            cars = await client.wallapop.search(
                category_id=100,
                brand="SEAT",
                min_year=2015,
                max_km=100000,
                gearbox="manual",
                order_by="price_low_to_high",
            )
            print(cars.total_results)
            ```
        """
        params = _set(
            {
                "query": query,
                "market": market,
                "latitude": latitude,
                "longitude": longitude,
                "distance_km": distance_km,
                "category_id": category_id,
                "min_price": min_price,
                "max_price": max_price,
                "condition": condition,
                "brand": brand,
                "model": model,
                "color": color,
                "time_filter": time_filter,
                "shippable": shippable,
                "has_warranty": has_warranty,
                "refurbished": refurbished,
                "min_year": min_year,
                "max_year": max_year,
                "min_km": min_km,
                "max_km": max_km,
                "gearbox": gearbox,
                "min_horsepower": min_horsepower,
                "max_horsepower": max_horsepower,
                "order_by": order_by,
                "next_page": next_page,
            }
        )
        response = await self._client.get("/v1/wallapop/search", params=params)
        return SearchResponse.model_validate(response)

    async def get_item(self, item_id: str, *, market: str = "es") -> ItemDetail:
        """Get a Wallapop listing's full detail.

        Args:
            item_id: Listing id (e.g. "nzxeknm5x562") or slug.
            market: Market code (es, it, pt). Defaults to "es".

        Returns:
            Listing detail with attributes, views, favourites and location.

        Raises:
            NotFoundError: If the listing doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            item = await client.wallapop.get_item("nzxeknm5x562")
            print(item.title, item.price, item.views)
            ```
        """
        response = await self._client.get(
            f"/v1/wallapop/items/{item_id}", params={"market": market}
        )
        return ItemDetail.model_validate(response)

    async def get_user(self, user_id: str, *, market: str = "es") -> UserProfile:
        """Get a Wallapop user's profile.

        Args:
            user_id: User id (e.g. "dqjwdd53wwzo") or profile slug
                (e.g. "alexc-25115753").
            market: Market code (es, it, pt). Defaults to "es".

        Returns:
            Profile with ratings, sales counters, response rate and
            verifications.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            user = await client.wallapop.get_user("alexc-25115753")
            print(user.name, user.rating_average, user.sold_count)
            ```
        """
        response = await self._client.get(
            f"/v1/wallapop/users/{user_id}", params={"market": market}
        )
        return UserProfile.model_validate(response)

    async def get_user_items(
        self,
        user_id: str,
        *,
        market: str = "es",
        next_page: str | None = None,
    ) -> UserItemsResponse:
        """Get a Wallapop user's live listings (40 per page).

        Args:
            user_id: User id or profile slug.
            market: Market code (es, it, pt). Defaults to "es".
            next_page: Cursor from the previous page's ``next_page``.

        Returns:
            The seller's listings and the next-page cursor.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            listings = await client.wallapop.get_user_items("dqjwdd53wwzo")
            for item in listings.items:
                print(item.title, item.price)
            ```
        """
        response = await self._client.get(
            f"/v1/wallapop/users/{user_id}/items",
            params=_set({"market": market, "next_page": next_page}),
        )
        return UserItemsResponse.model_validate(response)

    async def get_user_reviews(
        self,
        user_id: str,
        *,
        market: str = "es",
        next_page: str | None = None,
    ) -> ReviewsResponse:
        """Get the reviews a Wallapop user received, newest first (40 per page).

        Args:
            user_id: User id or profile slug.
            market: Market code (es, it, pt). Defaults to "es".
            next_page: Cursor from the previous page's ``next_page``.

        Returns:
            Reviews and the next-page cursor.

        Raises:
            NotFoundError: If the user doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            reviews = await client.wallapop.get_user_reviews("dqjwdd53wwzo")
            for r in reviews.reviews:
                print(r.rating, r.comment)
            ```
        """
        response = await self._client.get(
            f"/v1/wallapop/users/{user_id}/reviews",
            params=_set({"market": market, "next_page": next_page}),
        )
        return ReviewsResponse.model_validate(response)

    async def autocomplete(self, query: str, *, market: str = "es") -> AutocompleteResponse:
        """Get Wallapop's search-box suggestions for a partial query.

        Args:
            query: Partial search text, e.g. "bici".
            market: Market code (es, it, pt). Defaults to "es".

        Returns:
            Autocomplete response with suggestions.

        Example:
            ```python
            result = await client.wallapop.autocomplete("bici")
            print([s.text for s in result.suggestions])
            ```
        """
        response = await self._client.get(
            "/v1/wallapop/autocomplete", params={"query": query, "market": market}
        )
        return AutocompleteResponse.model_validate(response)

    async def list_categories(self, *, market: str = "es") -> CategoriesResponse:
        """Get the full Wallapop category tree.

        Args:
            market: Market code (es, it, pt) — localises category names.
                Defaults to "es".

        Returns:
            Category tree; ids are usable as the search ``category_id``.

        Example:
            ```python
            result = await client.wallapop.list_categories()
            for c in result.categories:
                print(c.id, c.name, len(c.subcategories))
            ```
        """
        response = await self._client.get("/v1/wallapop/categories", params={"market": market})
        return CategoriesResponse.model_validate(response)

    async def list_filters(
        self,
        *,
        category_id: int | None = None,
        query: str | None = None,
        market: str = "es",
    ) -> FiltersResponse:
        """Get the search filters Wallapop offers for a category/query.

        Args:
            category_id: Category the filters apply to.
            query: Search text the filters apply to.
            market: Market code (es, it, pt). Defaults to "es".

        Returns:
            Filters with their option ids. Filters flagged
            ``options_endpoint`` serve their options via
            `list_filter_options`.

        Example:
            ```python
            result = await client.wallapop.list_filters(category_id=24200)
            for f in result.filters:
                print(f.id, f.type, f.params)
            ```
        """
        response = await self._client.get(
            "/v1/wallapop/filters",
            params=_set({"category_id": category_id, "query": query, "market": market}),
        )
        return FiltersResponse.model_validate(response)

    async def list_filter_options(
        self,
        filter_id: str,
        *,
        category_id: int | None = None,
        query: str | None = None,
        market: str = "es",
    ) -> FilterOptionsResponse:
        """Get a filter's long option list (e.g. brands, models).

        Args:
            filter_id: Filter id flagged ``options_endpoint`` in
                `list_filters`, e.g. "brand".
            category_id: Category the options apply to.
            query: Search text the options apply to.
            market: Market code (es, it, pt). Defaults to "es".

        Returns:
            The filter's options.

        Raises:
            ValidationError: If ``filter_id`` is not a valid filter id.

        Example:
            ```python
            brands = await client.wallapop.list_filter_options(
                "brand", query="iphone"
            )
            print([o.id for o in brands.options])
            ```
        """
        response = await self._client.get(
            f"/v1/wallapop/filters/{filter_id}/options",
            params=_set({"category_id": category_id, "query": query, "market": market}),
        )
        return FilterOptionsResponse.model_validate(response)

    async def list_markets(self) -> MarketsResponse:
        """Get all supported Wallapop markets.

        Returns:
            Markets with currency, language and default search location.

        Example:
            ```python
            result = await client.wallapop.list_markets()
            for m in result.markets:
                print(f"{m.code}: {m.name} ({m.currency})")
            ```
        """
        response = await self._client.get("/v1/wallapop/markets")
        return MarketsResponse.model_validate(response)
