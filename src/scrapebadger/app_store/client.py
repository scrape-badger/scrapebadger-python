"""Apple App Store API client.

App Store endpoints: search, get_app (iTunes lookup merged with storefront
enrichment), get_reviews, get_developer (profile + catalogue), charts,
list_genres and list_markets. All methods are async and return strongly-typed
Pydantic models.

Everything is storefront-scoped: the ``us`` and ``de`` feeds for the same app
are different data sets, not translations of one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.app_store.models import (
    App,
    ChartsResponse,
    DeveloperResponse,
    GenresResponse,
    MarketsResponse,
    ReviewsResponse,
    SearchResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

Entity = Literal["software", "iPadSoftware", "macSoftware"]
ReviewSort = Literal["mostRecent", "mostHelpful"]
ChartType = Literal["top-free", "top-paid", "top-grossing"]
ChartEntity = Literal["apps", "ipad"]


class AppStoreClient:
    """Client for all Apple App Store API operations.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search
            results = await client.app_store.search("slack", country="us")
            for app in results.apps:
                print(f"{app.app_id} — {app.name} ({app.rating})")

            # Full app detail, by track id or bundle id
            app = await client.app_store.get_app("618783545")
            print(app.name, app.extras.rating_histogram.five_star)

            # Reviews (50 per page, pages 1-10)
            reviews = await client.app_store.get_reviews("618783545", page=1)

            # Top charts
            chart = await client.app_store.charts(country="us", type="top-free")

            # Reference
            genres = await client.app_store.list_genres()
            markets = await client.app_store.list_markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `app_store` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize App Store client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def search(
        self,
        query: str,
        *,
        country: str = "us",
        entity: Entity = "software",
        limit: int = 50,
        offset: int = 0,
        lang: str | None = None,
    ) -> SearchResponse:
        """Search the App Store full-text.

        Returns the complete iTunes record for every hit — the same ~40 fields
        the detail endpoint returns, so a search result rarely needs a
        follow-up lookup.

        Args:
            query: Search term, e.g. "slack".
            country: Storefront country code, e.g. "us". Defaults to "us".
            entity: Which catalogue to search — "software" (iPhone),
                "iPadSoftware" or "macSoftware". These are separate catalogues,
                not filters: a Mac-only app is absent from "software" entirely.
            limit: Results to return (1-200). Defaults to 50.
            offset: Results to skip. Applied by the service, not by Apple —
                paging is a slice of one 200-result response, and
                ``offset + limit`` is capped at 200.
            lang: Result language, e.g. "en_us" or "de_de". Defaults to the
                storefront's own language.

        Returns:
            Search response with matching apps.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            results = await client.app_store.search("photo editor", country="gb")
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "country": country,
            "entity": entity,
            "limit": limit,
            "offset": offset,
            "lang": lang,
        }
        response = await self._client.get("/v1/app-store/search", params=params)
        return SearchResponse.model_validate(response)

    async def get_app(
        self,
        app_id: str,
        *,
        country: str = "us",
        lang: str | None = None,
        include_extras: bool = True,
    ) -> App:
        """Get full detail for one app, by track id or bundle id.

        Merges two sources: the iTunes lookup (core fields, always present) and
        the storefront product page (``extras``, best-effort — a storefront
        failure degrades the response rather than failing it).

        Args:
            app_id: Numeric track id (e.g. "618783545") or bundle id (e.g.
                "com.tinyspeck.chatlyio"). A value containing a dot is treated
                as a bundle id.
            country: Storefront country code, e.g. "us". Defaults to "us".
            lang: Result language, e.g. "en_us".
            include_extras: Fetch the storefront page for the rating histogram,
                in-app-purchase list, full-resolution screenshots and App
                Privacy detail. Set False to skip that second fetch when only
                the core iTunes fields are needed.

        Returns:
            Full app detail.

        Raises:
            NotFoundError: If the app doesn't exist in the storefront.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            app = await client.app_store.get_app("com.tinyspeck.chatlyio")
            print(app.app_id, app.version, app.rating_count)
            ```
        """
        params: dict[str, Any] = {
            "country": country,
            "lang": lang,
            "include_extras": include_extras,
        }
        response = await self._client.get(f"/v1/app-store/apps/{app_id}", params=params)
        return App.model_validate(response)

    async def get_reviews(
        self,
        app_id: str,
        *,
        country: str = "us",
        page: int = 1,
        sort: ReviewSort = "mostRecent",
    ) -> ReviewsResponse:
        """Get customer reviews for an app — 50 per page, pages 1-10.

        Args:
            app_id: Numeric track id, e.g. "618783545". Apple's review feed has
                no bundle-id form — resolve a bundle id through ``get_app``
                first and use its ``app_id``.
            country: Storefront country code, e.g. "us". Defaults to "us".
            page: Page number (1-10). Defaults to 1.
            sort: Review ordering — "mostRecent" or "mostHelpful".

        Returns:
            Reviews response with a page of reviews.

        Raises:
            NotFoundError: If the app doesn't exist.
            ValidationError: If the app id is not numeric, or the page is
                beyond Apple's 10-page ceiling.

        Note:
            Reviews are per-storefront: the "us" and "de" feeds for the same
            app are different review sets, not translations of one set.

        Example:
            ```python
            reviews = await client.app_store.get_reviews(
                "618783545", country="de", sort="mostHelpful"
            )
            ```
        """
        params: dict[str, Any] = {"country": country, "page": page, "sort": sort}
        response = await self._client.get(f"/v1/app-store/apps/{app_id}/reviews", params=params)
        return ReviewsResponse.model_validate(response)

    async def get_developer(
        self,
        developer_id: str,
        *,
        country: str = "us",
        limit: int = 50,
    ) -> DeveloperResponse:
        """Get a developer and every app they publish in the storefront.

        Args:
            developer_id: Numeric artist id, e.g. "284882218".
            country: Storefront country code, e.g. "us". Defaults to "us".
            limit: Apps to return (1-200). Defaults to 50.

        Returns:
            Developer response with the profile and their catalogue.

        Raises:
            NotFoundError: If the developer doesn't exist in the storefront.
            ValidationError: If the developer id is not numeric.

        Example:
            ```python
            dev = await client.app_store.get_developer("284882218")
            print(dev.developer.name, dev.result_count)
            ```
        """
        params: dict[str, Any] = {"country": country, "limit": limit}
        response = await self._client.get(f"/v1/app-store/developers/{developer_id}", params=params)
        return DeveloperResponse.model_validate(response)

    async def charts(
        self,
        *,
        country: str = "us",
        type: ChartType = "top-free",
        genre: int | None = None,
        limit: int = 50,
        entity: ChartEntity = "apps",
    ) -> ChartsResponse:
        """Get the top charts for a storefront, optionally scoped to one genre.

        Args:
            country: Storefront country code, e.g. "us". Defaults to "us".
            type: Chart to read — "top-free", "top-paid" or "top-grossing".
            genre: Optional genre id to scope the chart, e.g. 6014 (Games).
                See ``list_genres``.
            limit: Entries to return (1-200). Defaults to 50.
            entity: Device chart — "apps" (iPhone) or "ipad".

        Returns:
            Charts response with ranked entries. ``rank`` is the app's position
            in the feed — Apple does not send an explicit rank field.

        Raises:
            ValidationError: If the chart type, entity or genre id is unknown.

        Example:
            ```python
            games = await client.app_store.charts(
                country="us", type="top-grossing", genre=6014
            )
            ```
        """
        params: dict[str, Any] = {
            "country": country,
            "type": type,
            "genre": genre,
            "limit": limit,
            "entity": entity,
        }
        response = await self._client.get("/v1/app-store/charts", params=params)
        return ChartsResponse.model_validate(response)

    async def list_genres(self) -> GenresResponse:
        """Get the App Store genre ids, for use with ``charts(genre=...)``.

        Returns:
            Genres response. Every id listed is verified to return a non-empty
            chart.

        Example:
            ```python
            result = await client.app_store.list_genres()
            for genre in result.genres:
                print(genre.genre_id, genre.name)
            ```
        """
        response = await self._client.get("/v1/app-store/genres")
        return GenresResponse.model_validate(response)

    async def list_markets(self) -> MarketsResponse:
        """Get the supported App Store storefronts.

        Returns:
            Markets response with all supported storefronts. Informational —
            the endpoints accept any well-formed 2-letter code and let Apple
            arbitrate, so a storefront missing from this list still works.

        Example:
            ```python
            result = await client.app_store.list_markets()
            for market in result.markets:
                print(f"{market.code}: {market.name}")
            ```
        """
        response = await self._client.get("/v1/app-store/markets")
        return MarketsResponse.model_validate(response)
