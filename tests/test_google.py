"""Unit tests for the Google SDK sub-clients.

Each sub-client forwards its arguments to the underlying `BaseClient.get`.
We mock BaseClient and assert the correct path + params are sent.
"""

from __future__ import annotations

import copy
from collections.abc import Iterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapebadger.google.ads import AdsClient
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


GOTO = "https://www.google.com/goto?url=abc"


def redirect_row(position: int, token: str | None = None, wait: int = 0) -> dict[str, Any]:
    """An organic result whose link is still a Google redirect."""
    return {
        "position": position,
        "title": f"Result {position}",
        "link": GOTO,
        "link_token": token or f"tok-{position}",
        "retry_after_seconds": wait,
    }


def resolved_row(position: int) -> dict[str, Any]:
    """The same result once resolved: the real link and no token."""
    return {
        "position": position,
        "title": f"Result {position}",
        "link": f"https://example.com/{position}",
    }


def sent_rows(mock_base_client: MagicMock) -> list[list[dict[str, Any]]]:
    """The rows of every POST /v1/google/resolve made so far."""
    for call in mock_base_client.post.await_args_list:
        assert call.args == ("/v1/google/resolve",)
    return [call.kwargs["json"]["results"] for call in mock_base_client.post.await_args_list]


class FakeClock:
    """Time moves only when the code under test sleeps."""

    def __init__(self) -> None:
        self.now = 1000.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture
def clock() -> Iterator[FakeClock]:
    fake = FakeClock()
    with (
        patch("scrapebadger.google.search.monotonic", fake.monotonic),
        patch("scrapebadger.google.search.asyncio.sleep", fake.sleep),
    ):
        yield fake


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
        assert isinstance(google.ads, AdsClient)

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
        assert "expand_related_questions" not in params

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("value", "sent"),
        [(True, "true"), (2, 2), (99, 99)],
    )
    async def test_search_expand_related_questions(
        self,
        google: GoogleClient,
        mock_base_client: MagicMock,
        value: bool | int,
        sent: str | int,
    ) -> None:
        await google.search.search("noise cancelling headphones", expand_related_questions=value)
        _, kwargs = mock_base_client.get.call_args
        assert kwargs["params"]["expand_related_questions"] == sent

    @pytest.mark.asyncio
    @pytest.mark.parametrize("value", [None, False, 0])
    async def test_search_expand_related_questions_off_is_omitted(
        self, google: GoogleClient, mock_base_client: MagicMock, value: bool | int | None
    ) -> None:
        await google.search.search("python", expand_related_questions=value)
        _, kwargs = mock_base_client.get.call_args
        assert "expand_related_questions" not in kwargs["params"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("value", [-1, 100])
    async def test_search_expand_related_questions_out_of_range(
        self, google: GoogleClient, mock_base_client: MagicMock, value: int
    ) -> None:
        with pytest.raises(ValueError, match="expand_related_questions"):
            await google.search.search("python", expand_related_questions=value)
        mock_base_client.get.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_light_uses_dedicated_endpoint(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        await google.search.light(
            "python", gl="gb", num=20, start=10, domain="google.co.uk", tbs="qdr:w"
        )
        mock_base_client.get.assert_awaited_once()
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/light/search"
        params = kwargs["params"]
        assert params["q"] == "python"
        assert params["gl"] == "gb"
        assert params["num"] == 20
        assert params["start"] == 10
        assert params["domain"] == "google.co.uk"
        assert params["tbs"] == "qdr:w"
        # Light cannot be upgraded to full Search, so none of its controls are sent.
        for key in ("mode", "ai_overview", "expand_related_questions"):
            assert key not in params

    @pytest.mark.asyncio
    async def test_resolve_posts_results(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        rows = [redirect_row(1), redirect_row(2, wait=6)]
        answer = {
            "results": [resolved_row(1), redirect_row(2, "tok-2b", wait=6)],
            "retry_after_seconds": 6,
        }
        mock_base_client.post.return_value = answer

        out = await google.search.resolve(rows)

        mock_base_client.post.assert_awaited_once_with("/v1/google/resolve", json={"results": rows})
        assert out is answer

    @pytest.mark.asyncio
    async def test_resolve_all_resolved_on_first_call(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        mock_base_client.post.return_value = {
            "results": [resolved_row(1), resolved_row(2)],
            "retry_after_seconds": None,
        }

        out = await google.search.resolve_all([redirect_row(1), redirect_row(2)])

        assert out == [resolved_row(1), resolved_row(2)]
        assert sent_rows(mock_base_client) == [[redirect_row(1), redirect_row(2)]]
        assert clock.sleeps == []

    @pytest.mark.asyncio
    async def test_resolve_all_retries_not_ready_row_with_new_token(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        mock_base_client.post.side_effect = [
            {
                "results": [resolved_row(1), redirect_row(2, "tok-2-new", wait=7)],
                "retry_after_seconds": 7,
            },
            {"results": [resolved_row(2)], "retry_after_seconds": None},
        ]

        out = await google.search.resolve_all([redirect_row(1), redirect_row(2)])

        assert out == [resolved_row(1), resolved_row(2)]
        first, second = sent_rows(mock_base_client)
        assert [row["link_token"] for row in first] == ["tok-1", "tok-2"]
        # Only the row that was not ready goes out again, with the token from the answer.
        assert second == [redirect_row(2, "tok-2-new", wait=7)]
        assert clock.sleeps == [7]

    @pytest.mark.asyncio
    async def test_resolve_all_sleeps_at_least_one_second(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        mock_base_client.post.side_effect = [
            {"results": [redirect_row(1, wait=0)], "retry_after_seconds": 0},
            {"results": [redirect_row(1)], "retry_after_seconds": None},
            {"results": [resolved_row(1)], "retry_after_seconds": None},
        ]

        out = await google.search.resolve_all([redirect_row(1)])

        assert out == [resolved_row(1)]
        # A wait of 0 and a missing wait both become 1 second.
        assert clock.sleeps == [1, 1]

    @pytest.mark.asyncio
    async def test_resolve_all_does_not_resend_failed_row(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        failed = {**redirect_row(2), "error": "link could not be resolved"}
        del failed["retry_after_seconds"]
        mock_base_client.post.side_effect = [
            {"results": [redirect_row(1, wait=3), failed], "retry_after_seconds": 3},
            {"results": [resolved_row(1)], "retry_after_seconds": None},
        ]

        out = await google.search.resolve_all([redirect_row(1), redirect_row(2)])

        assert out == [resolved_row(1), failed]
        assert out[1]["link_token"] == "tok-2"
        first, second = sent_rows(mock_base_client)
        assert [row["position"] for row in first] == [1, 2]
        assert [row["position"] for row in second] == [1]
        assert clock.sleeps == [3]

    @pytest.mark.asyncio
    async def test_resolve_all_never_sends_row_that_already_has_error(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        failed = {**redirect_row(1), "error": "link could not be resolved"}

        out = await google.search.resolve_all([failed])

        assert out == [failed]
        mock_base_client.post.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_resolve_all_sends_chunks_of_25(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        async def answer(_path: str, *, json: dict[str, Any]) -> dict[str, Any]:
            return {
                "results": [resolved_row(row["position"]) for row in json["results"]],
                "retry_after_seconds": None,
            }

        mock_base_client.post.side_effect = answer

        out = await google.search.resolve_all([redirect_row(n) for n in range(1, 61)])

        chunks = sent_rows(mock_base_client)
        assert [len(chunk) for chunk in chunks] == [25, 25, 10]
        assert [row["position"] for chunk in chunks for row in chunk] == list(range(1, 61))
        assert out == [resolved_row(n) for n in range(1, 61)]
        assert clock.sleeps == []

    @pytest.mark.asyncio
    async def test_resolve_all_sleeps_smallest_wait_of_all_chunks(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        waits = iter([9, 4])
        calls = 0

        async def answer(_path: str, *, json: dict[str, Any]) -> dict[str, Any]:
            nonlocal calls
            calls += 1
            if calls > 2:  # second round: everything resolves
                return {
                    "results": [resolved_row(row["position"]) for row in json["results"]],
                    "retry_after_seconds": None,
                }
            wait = next(waits)
            return {
                "results": [redirect_row(row["position"], wait=wait) for row in json["results"]],
                "retry_after_seconds": wait,
            }

        mock_base_client.post.side_effect = answer

        out = await google.search.resolve_all([redirect_row(n) for n in range(1, 31)])

        assert [len(chunk) for chunk in sent_rows(mock_base_client)] == [25, 5, 25, 5]
        assert out == [resolved_row(n) for n in range(1, 31)]
        assert clock.sleeps == [4]

    @pytest.mark.asyncio
    async def test_resolve_all_returns_waiting_rows_at_deadline(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        calls = 0

        async def answer(_path: str, *, json: dict[str, Any]) -> dict[str, Any]:
            nonlocal calls
            calls += 1
            return {
                "results": [
                    redirect_row(row["position"], f"tok-{row['position']}-v{calls}", wait=7)
                    for row in json["results"]
                ],
                "retry_after_seconds": 7,
            }

        mock_base_client.post.side_effect = answer

        out = await google.search.resolve_all([redirect_row(1), redirect_row(2)], max_wait=10)

        # No exception: the rows come back with their latest token and wait.
        assert out == [redirect_row(1, "tok-1-v3", wait=7), redirect_row(2, "tok-2-v3", wait=7)]
        # The second sleep is cut to what is left of max_wait, then one last request.
        assert clock.sleeps == [7, 3]
        assert calls == 3

    @pytest.mark.asyncio
    async def test_resolve_all_max_wait_zero_sends_once(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        mock_base_client.post.return_value = {
            "results": [redirect_row(1, "tok-1-new", wait=5)],
            "retry_after_seconds": 5,
        }

        out = await google.search.resolve_all([redirect_row(1)], max_wait=0)

        assert out == [redirect_row(1, "tok-1-new", wait=5)]
        mock_base_client.post.assert_awaited_once()
        assert clock.sleeps == []

    @pytest.mark.asyncio
    async def test_resolve_all_skips_rows_without_token(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        real_null = {
            "position": 1,
            "link": "https://example.com/real-1",
            "link_token": None,
            "retry_after_seconds": None,
        }
        real_bare = {"position": 3, "link": "https://example.com/real-3"}
        mock_base_client.post.return_value = {
            "results": [resolved_row(2), resolved_row(4)],
            "retry_after_seconds": None,
        }

        out = await google.search.resolve_all(
            [real_null, redirect_row(2), real_bare, redirect_row(4)]
        )

        assert sent_rows(mock_base_client) == [[redirect_row(2), redirect_row(4)]]
        assert out == [real_null, resolved_row(2), real_bare, resolved_row(4)]

    @pytest.mark.asyncio
    async def test_resolve_all_nothing_to_resolve_makes_no_request(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        rows = [{"position": 1, "link": "https://example.com/1", "link_token": None}]

        assert await google.search.resolve_all(rows) == rows
        assert await google.search.resolve_all([]) == []
        mock_base_client.post.assert_not_awaited()
        assert clock.sleeps == []

    @pytest.mark.asyncio
    async def test_resolve_all_does_not_mutate_input(
        self, google: GoogleClient, mock_base_client: MagicMock, clock: FakeClock
    ) -> None:
        rows = [
            {"position": 1, "link": "https://example.com/1", "link_token": None},
            {**redirect_row(2), "sitelinks": [{"title": "Docs"}]},
            redirect_row(3),
        ]
        before = copy.deepcopy(rows)
        row_ids = [id(row) for row in rows]
        mock_base_client.post.side_effect = [
            {
                "results": [resolved_row(2), redirect_row(3, "tok-3-new", wait=2)],
                "retry_after_seconds": 2,
            },
            {"results": [resolved_row(3)], "retry_after_seconds": None},
        ]

        out = await google.search.resolve_all(rows)

        assert rows == before
        assert [id(row) for row in rows] == row_ids
        assert out is not rows
        assert all(new is not old for new, old in zip(out, rows, strict=True))
        assert out == [before[0], resolved_row(2), resolved_row(3)]


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
        assert "catalog_id" not in params

    @pytest.mark.asyncio
    async def test_offers_by_catalog_id(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        await google.shopping.offers(catalog_id="762120719996356571", gl="de", hl="de")
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/shopping/offers"
        params = kwargs["params"]
        assert params["catalog_id"] == "762120719996356571"
        assert "barcode" not in params
        assert (params["gl"], params["hl"]) == ("de", "de")

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


class TestAdsClient:
    @pytest.mark.asyncio
    async def test_search_defaults(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.ads.search("tesla.com")
        mock_base_client.get.assert_called_once_with(
            "/v1/google/ads/search", params={"region": "US", "num": 40, "query": "tesla.com"}
        )

    @pytest.mark.asyncio
    async def test_search_forwards_filters(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        await google.ads.search(
            advertiser_id="AR01614014350098432001",
            region="anywhere",
            platform="YOUTUBE",
            format="VIDEO",
            start_date="2026-01-01",
            end_date="2026-02-01",
            political=True,
            num=100,
            cursor="tok",
        )
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/ads/search"
        assert kwargs["params"] == {
            "region": "anywhere",
            "num": 100,
            "advertiser_id": "AR01614014350098432001",
            "platform": "YOUTUBE",
            "format": "VIDEO",
            "start_date": "2026-01-01",
            "end_date": "2026-02-01",
            "political": True,
            "cursor": "tok",
        }

    @pytest.mark.asyncio
    async def test_search_advertisers(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        await google.ads.search_advertisers("rufwear", num=3000, num_domains=0, fuzzy=True)
        args, kwargs = mock_base_client.get.call_args
        assert args[0] == "/v1/google/ads/advertisers"
        assert kwargs["params"] == {
            "query": "rufwear",
            "num": 3000,
            "num_domains": 0,
            "region": "US",
            "fuzzy": True,
        }

    @pytest.mark.asyncio
    async def test_search_advertisers_country_and_cursor(
        self, google: GoogleClient, mock_base_client: MagicMock
    ) -> None:
        await google.ads.search_advertisers("nike", country="DE", cursor="next")
        params = mock_base_client.get.call_args.kwargs["params"]
        assert params["country"] == "DE"
        assert params["cursor"] == "next"
        assert "fuzzy" not in params

    @pytest.mark.asyncio
    async def test_advertiser(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.ads.advertiser(
            "AR01614014350098432001", region="GB", start_date="2026-09-01", end_date="2026-09-30"
        )
        mock_base_client.get.assert_called_once_with(
            "/v1/google/ads/advertiser",
            params={
                "advertiser_id": "AR01614014350098432001",
                "region": "GB",
                "start_date": "2026-09-01",
                "end_date": "2026-09-30",
            },
        )

    @pytest.mark.asyncio
    async def test_creative(self, google: GoogleClient, mock_base_client: MagicMock) -> None:
        await google.ads.creative(
            "AR01614014350098432001", "CR10484731423840108545", political=True
        )
        mock_base_client.get.assert_called_once_with(
            "/v1/google/ads/creative",
            params={
                "advertiser_id": "AR01614014350098432001",
                "creative_id": "CR10484731423840108545",
                "region": "US",
                "political": True,
            },
        )


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
            AdsClient,
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
                AdsClient,
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
