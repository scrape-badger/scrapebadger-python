"""Google Play Store API client.

Google Play endpoints: search, get_app (full detail), get_reviews, get_permissions,
get_similar, get_developer (a publisher's catalogue), browse_category,
get_collection (top charts), list_categories and list_markets. All methods are
async and return strongly-typed Pydantic models.

Play is one global host localised by two INDEPENDENT parameters: ``country``
(``gl`` — pricing, availability, chart ranking) and ``lang`` (``hl`` — the
language of descriptions and reviews).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from scrapebadger.google_play.models import (
    App,
    AppListResponse,
    CategoriesResponse,
    MarketsResponse,
    PermissionsResponse,
    ReviewsResponse,
)

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

ReviewSort = Literal["helpfulness", "newest", "rating"]
PriceFilter = Literal["free", "paid"]
Collection = Literal["topselling_free", "topselling_paid", "topgrossing"]


class GooglePlayClient:
    """Client for all Google Play Store API operations.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search
            results = await client.google_play.search("puzzle", country="US")
            for card in results.apps:
                print(f"{card.app_id} — {card.title} ({card.score})")

            # Full app detail
            app = await client.google_play.get_app("com.whatsapp")
            print(app.title, app.installs, app.developer.legal_name)

            # Reviews (token pagination)
            page = await client.google_play.get_reviews("com.whatsapp", sort="newest")
            more = await client.google_play.get_reviews(
                "com.whatsapp", page_token=page.next_page_token
            )

            # Reference
            categories = await client.google_play.list_categories()
            markets = await client.google_play.list_markets()
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the `google_play` property of the main `ScrapeBadger` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize Google Play client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def search(
        self,
        query: str,
        *,
        country: str = "US",
        lang: str = "en",
        price: PriceFilter | None = None,
    ) -> AppListResponse:
        """Search Google Play for apps and games.

        Args:
            query: Search keywords, e.g. "puzzle".
            country: Play storefront country (``gl``), ISO 3166-1 alpha-2.
                Defaults to "US".
            lang: Play content language (``hl``), e.g. "en" or "pt-BR".
                Defaults to "en".
            price: Restrict by price — "free" or "paid". Both when omitted.

        Returns:
            App list response with the ~30 results Play renders server-side.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If the parameters are invalid.

        Note:
            There is no ``page`` parameter — Play's search page has no page
            number, and its infinite-scroll continuation is not reachable.
            Use ``get_similar`` or ``get_developer`` to widen a result set.

        Example:
            ```python
            results = await client.google_play.search("puzzle", price="free")
            print(results.result_count)
            ```
        """
        params: dict[str, Any] = {
            "query": query,
            "country": country,
            "lang": lang,
            "price": price,
        }
        response = await self._client.get("/v1/google-play/search", params=params)
        return AppListResponse.model_validate(response)

    async def get_app(
        self,
        app_id: str,
        *,
        country: str = "US",
        lang: str = "en",
    ) -> App:
        """Get full detail for one app.

        One fetch returns the description, ratings histogram, install bands,
        pricing and IAP range, developer contact and legal entity, media,
        release/update timestamps, the Data Safety declaration, the permission
        tree and the similar-apps rail.

        Args:
            app_id: Android package id, e.g. "com.whatsapp".
            country: Play storefront country (``gl``). Defaults to "US".
            lang: Play content language (``hl``). Defaults to "en".

        Returns:
            Full app detail.

        Raises:
            NotFoundError: If the app doesn't exist.
            AuthenticationError: If the API key is invalid.

        Example:
            ```python
            app = await client.google_play.get_app("com.whatsapp")
            print(app.title, app.min_installs, app.histogram.five_star)
            ```
        """
        params: dict[str, Any] = {"country": country, "lang": lang}
        response = await self._client.get(f"/v1/google-play/apps/{app_id}", params=params)
        return App.model_validate(response)

    async def get_reviews(
        self,
        app_id: str,
        *,
        country: str = "US",
        lang: str = "en",
        sort: ReviewSort = "newest",
        count: int = 40,
        page_token: str | None = None,
    ) -> ReviewsResponse:
        """Get paginated user reviews, with developer replies where they exist.

        Args:
            app_id: Android package id, e.g. "com.whatsapp".
            country: Play storefront country (``gl``). Defaults to "US".
            lang: Play content language (``hl``). Defaults to "en".
            sort: Review ordering — "helpfulness", "newest" or "rating".
                Defaults to "newest".
            count: Reviews per page (1-150). Defaults to 40.
            page_token: Continuation token from a previous response's
                ``next_page_token``. Play paginates reviews by token only —
                there is no page number.

        Returns:
            Reviews response with a page of reviews and the next page token.

        Raises:
            NotFoundError: If the app doesn't exist.
            ValidationError: If the parameters are invalid.

        Example:
            ```python
            page = await client.google_play.get_reviews("com.whatsapp", count=150)
            while page.next_page_token:
                page = await client.google_play.get_reviews(
                    "com.whatsapp", page_token=page.next_page_token
                )
            ```
        """
        params: dict[str, Any] = {
            "country": country,
            "lang": lang,
            "sort": sort,
            "count": count,
            "page_token": page_token,
        }
        response = await self._client.get(f"/v1/google-play/apps/{app_id}/reviews", params=params)
        return ReviewsResponse.model_validate(response)

    async def get_permissions(
        self,
        app_id: str,
        *,
        country: str = "US",
        lang: str = "en",
    ) -> PermissionsResponse:
        """Get every Android permission the app declares, grouped as Play groups them.

        Args:
            app_id: Android package id, e.g. "com.whatsapp".
            country: Play storefront country (``gl``). Defaults to "US".
            lang: Play content language (``hl``). Defaults to "en".

        Returns:
            Permissions response with the full permission tree.

        Raises:
            NotFoundError: If the app doesn't exist.

        Example:
            ```python
            perms = await client.google_play.get_permissions("com.whatsapp")
            for group in perms.permission_groups:
                print(group.group, len(group.permissions))
            ```
        """
        params: dict[str, Any] = {"country": country, "lang": lang}
        response = await self._client.get(
            f"/v1/google-play/apps/{app_id}/permissions", params=params
        )
        return PermissionsResponse.model_validate(response)

    async def get_similar(
        self,
        app_id: str,
        *,
        country: str = "US",
        lang: str = "en",
    ) -> AppListResponse:
        """Get the apps Play recommends alongside this one.

        Args:
            app_id: Android package id, e.g. "com.whatsapp".
            country: Play storefront country (``gl``). Defaults to "US".
            lang: Play content language (``hl``). Defaults to "en".

        Returns:
            App list response with the detail page's "Similar apps" rail.

        Raises:
            NotFoundError: If the app doesn't exist.

        Note:
            Play caps the rail at roughly a dozen entries. The full list behind
            its "See more" link is ``App.similar_apps_url``.

        Example:
            ```python
            similar = await client.google_play.get_similar("com.whatsapp")
            ```
        """
        params: dict[str, Any] = {"country": country, "lang": lang}
        response = await self._client.get(f"/v1/google-play/apps/{app_id}/similar", params=params)
        return AppListResponse.model_validate(response)

    async def get_developer(
        self,
        developer: str,
        *,
        country: str = "US",
        lang: str = "en",
    ) -> AppListResponse:
        """Get a developer's published apps.

        Args:
            developer: Developer id — either the numeric id from an app's
                ``developer.developer_id`` (e.g. "5700313618786177705") or the
                display name from ``developer.name`` (e.g. "WhatsApp LLC").
            country: Play storefront country (``gl``). Defaults to "US".
            lang: Play content language (``hl``). Defaults to "en".

        Returns:
            App list response with the developer's catalogue.

        Raises:
            NotFoundError: If the developer has no apps.

        Note:
            Play server-renders only the first rail of a large catalogue —
            around 10 apps for a publisher with dozens.

        Example:
            ```python
            apps = await client.google_play.get_developer("WhatsApp LLC")
            ```
        """
        params: dict[str, Any] = {"country": country, "lang": lang}
        response = await self._client.get(f"/v1/google-play/developers/{developer}", params=params)
        return AppListResponse.model_validate(response)

    async def get_collection(
        self,
        collection: Collection,
        *,
        category: str = "APPLICATION",
        country: str = "US",
        lang: str = "en",
    ) -> AppListResponse:
        """Get a top chart for a category and country.

        Args:
            collection: Top chart — "topselling_free", "topselling_paid" or
                "topgrossing".
            category: Category to rank within, e.g. "GAME" or "SOCIAL".
                Defaults to "APPLICATION" (all apps).
            country: Play storefront country (``gl``). Defaults to "US".
            lang: Play content language (``hl``). Defaults to "en".

        Returns:
            App list response with the ranked chart.

        Raises:
            ValidationError: If the collection is unknown, or if Play renders
                the chart client-side and no server-side ranking is available.

        Example:
            ```python
            chart = await client.google_play.get_collection(
                "topselling_free", category="GAME"
            )
            ```
        """
        params: dict[str, Any] = {"category": category, "country": country, "lang": lang}
        response = await self._client.get(
            f"/v1/google-play/collections/{collection}", params=params
        )
        return AppListResponse.model_validate(response)

    async def browse_category(
        self,
        category_id: str,
        *,
        country: str = "US",
        lang: str = "en",
    ) -> AppListResponse:
        """Browse a Play category.

        Args:
            category_id: Play category id, e.g. "GAME_PUZZLE" or "SOCIAL".
                See ``list_categories``.
            country: Play storefront country (``gl``). Defaults to "US".
            lang: Play content language (``hl``). Defaults to "en".

        Returns:
            App list response with every app across the category page's
            editorial rails, deduped and in the order Play ranked them.

        Raises:
            NotFoundError: If the category has no apps.

        Example:
            ```python
            apps = await client.google_play.browse_category("GAME_PUZZLE")
            ```
        """
        params: dict[str, Any] = {"country": country, "lang": lang}
        response = await self._client.get(
            f"/v1/google-play/categories/{category_id}", params=params
        )
        return AppListResponse.model_validate(response)

    async def list_categories(self) -> CategoriesResponse:
        """Get every Play app and game category id.

        Returns:
            Categories response with all category ids.

        Example:
            ```python
            result = await client.google_play.list_categories()
            for category in result.categories:
                print(category.category_id, category.name)
            ```
        """
        response = await self._client.get("/v1/google-play/categories")
        return CategoriesResponse.model_validate(response)

    async def list_markets(self) -> MarketsResponse:
        """Get supported storefront countries (``gl``) and content languages (``hl``).

        Returns:
            Markets response with countries and languages. The two are
            independent — ``gl`` selects pricing, availability and chart
            ranking, ``hl`` selects the language of descriptions and reviews.

        Example:
            ```python
            result = await client.google_play.list_markets()
            print(len(result.markets), len(result.languages))
            ```
        """
        response = await self._client.get("/v1/google-play/markets")
        return MarketsResponse.model_validate(response)
