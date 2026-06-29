"""Unit tests for the Google SDK sub-clients.

Each sub-client forwards its arguments to the underlying `BaseClient.get`.
We mock BaseClient and assert the correct path + params are sent.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.google.ai_mode import AiModeClient
from scrapebadger.google.autocomplete import AutocompleteClient
from scrapebadger.google.client import GoogleClient
from scrapebadger.google.finance import FinanceClient
from scrapebadger.google.hotels import HotelsClient
from scrapebadger.google.images import ImagesClient
from scrapebadger.google.jobs import JobsClient
from scrapebadger.google.lens import LensClient
from scrapebadger.google.maps import MapsClient
from scrapebadger.google.news import NewsClient
from scrapebadger.google.patents import PatentsClient
from scrapebadger.google.products import ProductsClient
from scrapebadger.google.scholar import ScholarClient
from scrapebadger.google.search import SearchClient
from scrapebadger.google.shopping import ShoppingClient
from scrapebadger.google.trends import TrendsClient
from scrapebadger.google.videos import VideosClient


@pytest.fixture
def mock_base_client() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock(return_value={"ok": True})
    client.post = AsyncMock()
    return client


@pytest.fixture
def google(mock_base_client: MagicMock) -> GoogleClient:
    return GoogleClient(mock_base_client)


class TestGoogleClientWiring:
    def test_sub_clients_lazy_and_typed(self, google: GoogleClient) -> None:
        assert isinstance(google.search, SearchClient)
        assert isinstance(google.maps, MapsClient)
        assert isinstance(google.news, NewsClient)
        assert isinstance(google.hotels, HotelsClient)
        assert isinstance(google.trends, TrendsClient)
        assert isinstance(google.jobs, JobsClient)
        assert isinstance(google.shopping, ShoppingClient)
        assert isinstance(google.patents, PatentsClient)
        assert isinstance(google.scholar, ScholarClient)
        assert isinstance(google.autocomplete, AutocompleteClient)
        assert isinstance(google.images, ImagesClient)
        assert isinstance(google.videos, VideosClient)
        assert isinstance(google.finance, FinanceClient)
        assert isinstance(google.ai_mode, AiModeClient)
        assert isinstance(google.lens, LensClient)
        assert isinstance(google.products, ProductsClient)

    def test_sub_clients_cached(self, google: GoogleClient) -> None:
        assert google.search is google.search
        assert google.maps is google.maps


class TestSearchClient:
    @pytest.mark.asyncio
    async def test_search_forwards_params(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        await google.search.search(
            "python",
            gl="us",
            hl="en",
            num=20,
            start=10,
            domain="google.co.uk",
            device="mobile",
        )
        mock_base_client.get.assert_awaited_once()
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/search"
        params = kwargs["params"]
        assert params["q"] == "python"
        assert params["gl"] == "us"
        assert params["num"] == 20
        assert params["start"] == 10
        assert params["domain"] == "google.co.uk"
        assert params["device"] == "mobile"


class TestMapsClient:
    @pytest.mark.asyncio
    async def test_search(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.maps.search("pizza", ll="@40.7,-74.0,12z", gl="us")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/maps/search"
        assert kwargs["params"]["q"] == "pizza"
        assert kwargs["params"]["ll"] == "@40.7,-74.0,12z"

    @pytest.mark.asyncio
    async def test_place_requires_id(self, google: GoogleClient) -> None:
        with pytest.raises(ValueError, match="place_id or data_id"):
            await google.maps.place()

    @pytest.mark.asyncio
    async def test_place_with_data_id(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        await google.maps.place(data_id="0x80859a6b:0x12345")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/maps/place"
        assert kwargs["params"]["data_id"] == "0x80859a6b:0x12345"
        assert "place_id" not in kwargs["params"]

    @pytest.mark.asyncio
    async def test_reviews(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.maps.reviews(
            "data:123",
            sort_by="newestFirst",
            next_page_token="tok1",
            results=15,
        )
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/maps/reviews"
        assert kwargs["params"]["data_id"] == "data:123"
        assert kwargs["params"]["sort_by"] == "newestFirst"
        assert kwargs["params"]["next_page_token"] == "tok1"
        assert kwargs["params"]["results"] == 15

    @pytest.mark.asyncio
    async def test_photos(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.maps.photos("data:456")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/maps/photos"
        assert kwargs["params"]["data_id"] == "data:456"

    @pytest.mark.asyncio
    async def test_posts(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.maps.posts("data:789", next_page_token="x")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/maps/posts"
        assert kwargs["params"]["next_page_token"] == "x"


class TestNewsClient:
    @pytest.mark.asyncio
    async def test_search(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.news.search("openai", max_results=20)
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/news/search"
        assert kwargs["params"]["q"] == "openai"
        assert kwargs["params"]["max_results"] == 20

    @pytest.mark.asyncio
    async def test_topics(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.news.topics("TECHNOLOGY")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/news/topics"
        assert kwargs["params"]["topic"] == "TECHNOLOGY"

    @pytest.mark.asyncio
    async def test_trending(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.news.trending(gl="GB")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/news/trending"
        assert kwargs["params"]["gl"] == "GB"


class TestHotelsClient:
    @pytest.mark.asyncio
    async def test_search(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.hotels.search(
            "Paris",
            check_in="2026-05-01",
            check_out="2026-05-05",
            adults=2,
            currency="EUR",
        )
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/hotels/search"
        assert kwargs["params"]["check_in"] == "2026-05-01"
        assert kwargs["params"]["currency"] == "EUR"

    @pytest.mark.asyncio
    async def test_details(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.hotels.details("PTOKEN", check_in="2026-05-01", check_out="2026-05-05")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/hotels/details"
        assert kwargs["params"]["property_token"] == "PTOKEN"


class TestTrendsClient:
    @pytest.mark.asyncio
    async def test_interest(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.trends.interest("python,javascript", geo="US", date="today 12-m")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/trends/interest"
        assert kwargs["params"]["q"] == "python,javascript"

    @pytest.mark.asyncio
    async def test_regions(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.trends.regions("python")
        args, _kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/trends/regions"

    @pytest.mark.asyncio
    async def test_related(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.trends.related("python")
        args, _kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/trends/related"

    @pytest.mark.asyncio
    async def test_trending(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.trends.trending(geo="US")
        args, _kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/trends/trending"


class TestJobsClient:
    @pytest.mark.asyncio
    async def test_search_with_filters(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        await google.jobs.search(
            "software engineer",
            location="San Francisco",
            job_type="FULLTIME",
            date_posted="week",
        )
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/jobs/search"
        assert kwargs["params"]["location"] == "San Francisco"
        assert kwargs["params"]["job_type"] == "FULLTIME"
        assert kwargs["params"]["date_posted"] == "week"


class TestShoppingClient:
    @pytest.mark.asyncio
    async def test_search(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.shopping.search(
            "laptop",
            min_price=500,
            max_price=2000,
            sort_by="price_low",
        )
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/shopping/search"
        assert kwargs["params"]["min_price"] == 500
        assert kwargs["params"]["sort_by"] == "price_low"

    @pytest.mark.asyncio
    async def test_product(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.shopping.product("abc123")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/shopping/product"
        assert kwargs["params"]["product_id"] == "abc123"

    @pytest.mark.asyncio
    async def test_offers(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.shopping.offers("0190198001751", gl="us")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/shopping/offers"
        params = kwargs["params"]
        assert params["barcode"] == "0190198001751"
        assert params["gl"] == "us"
        assert params["hl"] == "en"

    @pytest.mark.asyncio
    async def test_offers_default_no_gl(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        await google.shopping.offers("0190198001751")
        _, kwargs = mock_base_client.get.call_args
        assert "gl" not in kwargs["params"]

    @pytest.mark.asyncio
    async def test_click(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.shopping.click(
            title='Razer Blade 14"',
            source="Razer.com",
            q="gaming laptop",
            product_id="pid123",
        )
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/shopping/product/click"
        params = kwargs["params"]
        assert params["title"] == 'Razer Blade 14"'
        assert params["source"] == "Razer.com"
        assert params["q"] == "gaming laptop"
        assert params["product_id"] == "pid123"


class TestPatentsClient:
    @pytest.mark.asyncio
    async def test_search(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.patents.search("distributed lock", inventor="Smith", assignee="Acme")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/patents/search"
        assert kwargs["params"]["inventor"] == "Smith"
        assert kwargs["params"]["assignee"] == "Acme"

    @pytest.mark.asyncio
    async def test_detail(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.patents.detail("US10123456B2")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/patents/detail"
        assert kwargs["params"]["patent_id"] == "US10123456B2"


class TestOtherClients:
    @pytest.mark.asyncio
    async def test_scholar(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.scholar.search("transformer", as_ylo=2020, as_yhi=2024)
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/scholar/search"
        assert kwargs["params"]["as_ylo"] == 2020
        assert kwargs["params"]["as_yhi"] == 2024

    @pytest.mark.asyncio
    async def test_autocomplete(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.autocomplete.get("pyth")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/autocomplete"
        assert kwargs["params"]["q"] == "pyth"

    @pytest.mark.asyncio
    async def test_images(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.images.search("dog", imgsz="l", imgcolor="color")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/images/search"
        assert kwargs["params"]["imgsz"] == "l"
        assert kwargs["params"]["imgcolor"] == "color"

    @pytest.mark.asyncio
    async def test_videos(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.videos.search("python tutorial", tbs="qdr:w")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/videos/search"
        assert kwargs["params"]["tbs"] == "qdr:w"

    @pytest.mark.asyncio
    async def test_finance(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.finance.quote("AAPL:NASDAQ")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/finance/quote"
        assert kwargs["params"]["q"] == "AAPL:NASDAQ"

    @pytest.mark.asyncio
    async def test_ai_mode(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.ai_mode.search("what is kubernetes")
        args, _kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/ai-mode/search"

    @pytest.mark.asyncio
    async def test_lens(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.lens.search("https://example.com/dog.jpg")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/lens/search"
        assert kwargs["params"]["url"] == "https://example.com/dog.jpg"

    @pytest.mark.asyncio
    async def test_products(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.products.detail("pid1")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/products/detail"
        assert kwargs["params"]["product_id"] == "pid1"


class TestImportability:
    def test_public_imports(self) -> None:
        from scrapebadger.google import (
            AiModeClient,
            AutocompleteClient,
            FinanceClient,
            GoogleClient,
            HotelsClient,
            ImagesClient,
            JobsClient,
            LensClient,
            MapsClient,
            NewsClient,
            PatentsClient,
            ProductsClient,
            ScholarClient,
            SearchClient,
            ShoppingClient,
            TrendsClient,
            VideosClient,
        )

        assert all(
            cls.__name__.endswith("Client")
            for cls in (
                AiModeClient,
                AutocompleteClient,
                FinanceClient,
                GoogleClient,
                HotelsClient,
                ImagesClient,
                JobsClient,
                LensClient,
                MapsClient,
                NewsClient,
                PatentsClient,
                ProductsClient,
                ScholarClient,
                SearchClient,
                ShoppingClient,
                TrendsClient,
                VideosClient,
            )
        )

    def test_scrapebadger_google_property(self) -> None:
        from scrapebadger import ScrapeBadger

        sb = ScrapeBadger(api_key="test")
        assert isinstance(sb.google, GoogleClient)
        # Lazy + cached
        assert sb.google is sb.google
