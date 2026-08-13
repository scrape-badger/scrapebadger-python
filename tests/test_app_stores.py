"""Unit tests for the Google Play, App Store and Google Ads SDK sub-clients.

These clients are thin path/param mappers over the gateway, so the thing that
can silently break is a wrong URL or a mis-spelled query key. Every method is
routed through a mocked BaseClient and asserted on both.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.app_store.client import AppStoreClient
from scrapebadger.app_store.models import App as AppStoreApp
from scrapebadger.google_ads.client import GoogleAdsClient
from scrapebadger.google_ads.models import AdsSearchResponse
from scrapebadger.google_play.client import GooglePlayClient
from scrapebadger.google_play.models import App as PlayApp

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_base_client() -> MagicMock:
    """Return a mock BaseClient with AsyncMock methods."""
    client = MagicMock()
    client.get = AsyncMock(return_value={})
    return client


@pytest.fixture
def play(mock_base_client: MagicMock) -> GooglePlayClient:
    return GooglePlayClient(mock_base_client)


@pytest.fixture
def store(mock_base_client: MagicMock) -> AppStoreClient:
    return AppStoreClient(mock_base_client)


@pytest.fixture
def ads(mock_base_client: MagicMock) -> GoogleAdsClient:
    return GoogleAdsClient(mock_base_client)


def called(mock_base_client: MagicMock) -> tuple[str, dict[str, Any]]:
    """Return the (path, params) the client sent."""
    args, kwargs = mock_base_client.get.call_args
    return args[0], kwargs.get("params", {})


# ===========================================================================
# Google Play
# ===========================================================================


class TestGooglePlayClient:
    async def test_search(self, play: GooglePlayClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"result_count": 0, "apps": []}
        await play.search("puzzle", country="DE", lang="de", price="free")
        path, params = called(mock_base_client)
        assert path == "/v1/google-play/search"
        assert params == {"query": "puzzle", "country": "DE", "lang": "de", "price": "free"}

    async def test_get_app(self, play: GooglePlayClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"app_id": "com.whatsapp"}
        result = await play.get_app("com.whatsapp")
        assert isinstance(result, PlayApp)
        path, params = called(mock_base_client)
        assert path == "/v1/google-play/apps/com.whatsapp"
        assert params == {"country": "US", "lang": "en"}

    async def test_get_reviews(self, play: GooglePlayClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {
            "app_id": "com.whatsapp",
            "sort": "rating",
            "result_count": 0,
            "reviews": [],
        }
        await play.get_reviews("com.whatsapp", sort="rating", count=150, page_token="tok")
        path, params = called(mock_base_client)
        assert path == "/v1/google-play/apps/com.whatsapp/reviews"
        assert params["sort"] == "rating"
        assert params["count"] == 150
        assert params["page_token"] == "tok"

    async def test_get_permissions(
        self, play: GooglePlayClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {
            "app_id": "com.whatsapp",
            "result_count": 0,
            "permission_groups": [],
        }
        await play.get_permissions("com.whatsapp")
        assert called(mock_base_client)[0] == "/v1/google-play/apps/com.whatsapp/permissions"

    async def test_get_similar(self, play: GooglePlayClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"result_count": 0, "apps": []}
        await play.get_similar("com.whatsapp")
        assert called(mock_base_client)[0] == "/v1/google-play/apps/com.whatsapp/similar"

    async def test_get_developer(self, play: GooglePlayClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"result_count": 0, "apps": []}
        await play.get_developer("WhatsApp LLC")
        assert called(mock_base_client)[0] == "/v1/google-play/developers/WhatsApp LLC"

    async def test_get_collection(
        self, play: GooglePlayClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {"result_count": 0, "apps": []}
        await play.get_collection("topgrossing", category="GAME")
        path, params = called(mock_base_client)
        assert path == "/v1/google-play/collections/topgrossing"
        assert params["category"] == "GAME"

    async def test_browse_category(
        self, play: GooglePlayClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {"result_count": 0, "apps": []}
        await play.browse_category("GAME_PUZZLE")
        assert called(mock_base_client)[0] == "/v1/google-play/categories/GAME_PUZZLE"

    async def test_reference(self, play: GooglePlayClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"result_count": 0}
        await play.list_categories()
        assert called(mock_base_client)[0] == "/v1/google-play/categories"
        await play.list_markets()
        assert called(mock_base_client)[0] == "/v1/google-play/markets"


# ===========================================================================
# App Store
# ===========================================================================


class TestAppStoreClient:
    async def test_search(self, store: AppStoreClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {
            "query": "slack",
            "country": "gb",
            "entity": "macSoftware",
            "result_count": 0,
            "apps": [],
        }
        await store.search("slack", country="gb", entity="macSoftware", limit=10, offset=5)
        path, params = called(mock_base_client)
        assert path == "/v1/app-store/search"
        assert params["entity"] == "macSoftware"
        assert params["limit"] == 10
        assert params["offset"] == 5

    async def test_get_app(self, store: AppStoreClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"app_id": 618783545}
        result = await store.get_app("618783545", include_extras=False)
        assert isinstance(result, AppStoreApp)
        path, params = called(mock_base_client)
        assert path == "/v1/app-store/apps/618783545"
        assert params["include_extras"] is False

    async def test_get_reviews(self, store: AppStoreClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {
            "app_id": "618783545",
            "country": "de",
            "page": 2,
            "sort": "mostHelpful",
            "result_count": 0,
            "reviews": [],
        }
        await store.get_reviews("618783545", country="de", page=2, sort="mostHelpful")
        path, params = called(mock_base_client)
        assert path == "/v1/app-store/apps/618783545/reviews"
        assert params == {"country": "de", "page": 2, "sort": "mostHelpful"}

    async def test_get_developer(self, store: AppStoreClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"country": "us", "result_count": 0, "apps": []}
        await store.get_developer("284882218", limit=200)
        path, params = called(mock_base_client)
        assert path == "/v1/app-store/developers/284882218"
        assert params["limit"] == 200

    async def test_charts(self, store: AppStoreClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {
            "country": "us",
            "type": "top-grossing",
            "entity": "ipad",
            "result_count": 0,
            "apps": [],
        }
        await store.charts(type="top-grossing", genre=6014, entity="ipad")
        path, params = called(mock_base_client)
        assert path == "/v1/app-store/charts"
        assert params["type"] == "top-grossing"
        assert params["genre"] == 6014
        assert params["entity"] == "ipad"

    async def test_reference(self, store: AppStoreClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"result_count": 0}
        await store.list_genres()
        assert called(mock_base_client)[0] == "/v1/app-store/genres"
        await store.list_markets()
        assert called(mock_base_client)[0] == "/v1/app-store/markets"


# ===========================================================================
# Google Ads Transparency
# ===========================================================================


class TestGoogleAdsClient:
    async def test_search_ads(self, ads: GoogleAdsClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"region": "DE"}
        result = await ads.search_ads(
            query="tesla.com", region="DE", format="IMAGE", start_date="2026-07-01", num=100
        )
        assert isinstance(result, AdsSearchResponse)
        # Uncalibrated upstream filters must report themselves as not honoured.
        assert result.filters_applied.platform is False
        path, params = called(mock_base_client)
        assert path == "/v1/google/ads/search"
        assert params["query"] == "tesla.com"
        assert params["format"] == "IMAGE"
        assert params["start_date"] == "2026-07-01"
        assert params["num"] == 100

    async def test_get_creative(self, ads: GoogleAdsClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"region": "US"}
        await ads.get_creative("AR01", "CR02", political=True)
        path, params = called(mock_base_client)
        assert path == "/v1/google/ads/creative"
        assert params == {
            "advertiser_id": "AR01",
            "creative_id": "CR02",
            "region": "US",
            "political": True,
        }

    async def test_search_advertisers(
        self, ads: GoogleAdsClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {"query": "tesla", "region": "US", "advertisers": []}
        await ads.search_advertisers("tesla", num=20)
        path, params = called(mock_base_client)
        assert path == "/v1/google/ads/advertisers"
        assert params == {"query": "tesla", "region": "US", "num": 20}

    async def test_get_advertiser(self, ads: GoogleAdsClient, mock_base_client: MagicMock) -> None:
        mock_base_client.get.return_value = {"advertiser_id": "AR01", "region": "US"}
        await ads.get_advertiser("AR01", start_date="2026-07-01", end_date="2026-07-31")
        path, params = called(mock_base_client)
        assert path == "/v1/google/ads/advertiser"
        assert params["advertiser_id"] == "AR01"
        assert params["start_date"] == "2026-07-01"
        assert params["end_date"] == "2026-07-31"


# ===========================================================================
# Public API
# ===========================================================================


class TestPublicApi:
    def test_clients_are_wired_and_models_exported(self) -> None:
        import scrapebadger as sb

        client = sb.ScrapeBadger(api_key="test")
        assert isinstance(client.google_play, GooglePlayClient)
        assert isinstance(client.app_store, AppStoreClient)
        assert isinstance(client.google_ads, GoogleAdsClient)
        for name in ("GooglePlayApp", "AppStoreApp", "GoogleAdsSearchResponse"):
            assert name in sb.__all__
            assert hasattr(sb, name)

    def test_models_are_frozen(self) -> None:
        app = PlayApp(app_id="com.whatsapp")
        with pytest.raises(Exception, match="frozen"):
            app.app_id = "com.other"  # type: ignore[misc]
