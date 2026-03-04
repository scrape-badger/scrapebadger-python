"""Unit tests for filter rule methods on StreamClient and related models.

Tests are organised into:
- TestFilterRuleModels: Pydantic model construction and validation
- TestStreamClientFilterRules: CRUD and utility methods via mocked HTTP client
- TestFilterRuleStatusEnum: FilterRuleStatus enum values
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.twitter.stream import StreamClient
from scrapebadger.twitter.stream_models import (
    FilterRuleDeliveryLog,
    FilterRuleDeliveryLogList,
    FilterRulePricingTier,
    FilterRulePricingTierList,
    FilterRuleQueryValidation,
    FilterRuleResponse,
    FilterRuleResponseList,
    FilterRuleStatus,
)


# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

FILTER_RULE_RESPONSE: dict[str, Any] = {
    "id": "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
    "tag": "Python news",
    "query": "#python lang:en -is:retweet",
    "interval_seconds": 60.0,
    "status": "active",
    "status_reason": None,
    "webhook_url": "https://example.com/hook",
    "webhook_secret_set": True,
    "max_results_per_poll": 10,
    "credits_per_rule_per_day": 48.0,
    "pricing_tier": "Standard",
    "created_at": "2026-03-03T10:00:00+00:00",
    "updated_at": "2026-03-03T10:00:00+00:00",
}

FILTER_RULE_RESPONSE_LIST: dict[str, Any] = {
    "rules": [FILTER_RULE_RESPONSE],
    "total": 1,
    "limit": 20,
    "offset": 0,
}

FILTER_RULE_DELIVERY_LOG: dict[str, Any] = {
    "id": "log-1111-2222-3333",
    "rule_id": "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
    "rule_tag": "Python news",
    "tweet_id": "1895234567890123456",
    "author_username": "gvanrossum",
    "tweet_text_preview": "New Python release is out!",
    "tweet_url": "https://twitter.com/gvanrossum/status/1895234567890123456",
    "tweet_published_at": "2026-03-03T09:59:57+00:00",
    "detected_at": "2026-03-03T10:00:00+00:00",
    "latency_ms": 3000,
    "latency_badge": "green",
    "delivery_status": "webhook_delivered",
    "webhook_status_code": 200,
    "webhook_attempts": 1,
}

FILTER_RULE_DELIVERY_LOG_LIST: dict[str, Any] = {
    "logs": [FILTER_RULE_DELIVERY_LOG],
    "total": 1,
    "limit": 20,
    "offset": 0,
}

PRICING_TIER: dict[str, Any] = {
    "id": "tier-uuid-0001",
    "tier_label": "Standard",
    "max_interval_seconds": 300.0,
    "credits_per_rule_per_day": 48.0,
    "display_order": 3,
}

PRICING_TIER_LIST: dict[str, Any] = {
    "tiers": [PRICING_TIER],
}

QUERY_VALIDATION_VALID: dict[str, Any] = {
    "valid": True,
    "error": None,
    "sample_results": 42,
}

QUERY_VALIDATION_INVALID: dict[str, Any] = {
    "valid": False,
    "error": "Unsupported operator: badop:",
    "sample_results": 0,
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_base_client() -> MagicMock:
    """Return a mock BaseClient with AsyncMock methods."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client._request = AsyncMock()
    client.config.api_key = "test_api_key_12345"
    client.config.base_url = "https://api.test.scrapebadger.com"
    return client


@pytest.fixture
def stream_client(mock_base_client: MagicMock) -> StreamClient:
    """Return a StreamClient backed by a mock base client."""
    return StreamClient(mock_base_client)


# ===========================================================================
# TestFilterRuleModels
# ===========================================================================


class TestFilterRuleModels:
    """Pydantic model construction and validation tests for filter rule types."""

    def test_filter_rule_response_validates_active(self) -> None:
        rule = FilterRuleResponse.model_validate(FILTER_RULE_RESPONSE)
        assert rule.id == "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        assert rule.tag == "Python news"
        assert rule.query == "#python lang:en -is:retweet"
        assert rule.interval_seconds == 60.0
        assert rule.status == FilterRuleStatus.ACTIVE
        assert rule.status_reason is None
        assert rule.webhook_url == "https://example.com/hook"
        assert rule.webhook_secret_set is True
        assert rule.max_results_per_poll == 10
        assert rule.credits_per_rule_per_day == 48.0
        assert rule.pricing_tier == "Standard"
        assert rule.created_at == "2026-03-03T10:00:00+00:00"
        assert rule.updated_at == "2026-03-03T10:00:00+00:00"

    def test_filter_rule_response_paused_status(self) -> None:
        data = {
            **FILTER_RULE_RESPONSE,
            "status": "paused",
            "status_reason": "Insufficient credits",
        }
        rule = FilterRuleResponse.model_validate(data)
        assert rule.status == FilterRuleStatus.PAUSED
        assert rule.status_reason == "Insufficient credits"

    def test_filter_rule_response_error_status(self) -> None:
        data = {**FILTER_RULE_RESPONSE, "status": "error"}
        rule = FilterRuleResponse.model_validate(data)
        assert rule.status == FilterRuleStatus.ERROR

    def test_filter_rule_response_inactive_status(self) -> None:
        data = {**FILTER_RULE_RESPONSE, "status": "inactive"}
        rule = FilterRuleResponse.model_validate(data)
        assert rule.status == FilterRuleStatus.INACTIVE

    def test_filter_rule_response_is_frozen(self) -> None:
        rule = FilterRuleResponse.model_validate(FILTER_RULE_RESPONSE)
        with pytest.raises(Exception):  # noqa: B017
            rule.tag = "mutated"  # type: ignore[misc]

    def test_filter_rule_response_optional_webhook_url_none(self) -> None:
        data = {**FILTER_RULE_RESPONSE, "webhook_url": None, "webhook_secret_set": False}
        rule = FilterRuleResponse.model_validate(data)
        assert rule.webhook_url is None
        assert rule.webhook_secret_set is False

    def test_filter_rule_response_list_validates(self) -> None:
        result = FilterRuleResponseList.model_validate(FILTER_RULE_RESPONSE_LIST)
        assert result.total == 1
        assert result.limit == 20
        assert result.offset == 0
        assert len(result.rules) == 1
        assert result.rules[0].tag == "Python news"

    def test_filter_rule_response_list_empty(self) -> None:
        result = FilterRuleResponseList.model_validate(
            {"rules": [], "total": 0, "limit": 20, "offset": 0}
        )
        assert result.total == 0
        assert result.rules == []

    def test_filter_rule_delivery_log_validates(self) -> None:
        log = FilterRuleDeliveryLog.model_validate(FILTER_RULE_DELIVERY_LOG)
        assert log.id == "log-1111-2222-3333"
        assert log.rule_id == "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        assert log.rule_tag == "Python news"
        assert log.tweet_id == "1895234567890123456"
        assert log.author_username == "gvanrossum"
        assert log.tweet_text_preview == "New Python release is out!"
        assert log.latency_ms == 3000
        assert log.latency_badge == "green"
        assert log.delivery_status == "webhook_delivered"
        assert log.webhook_status_code == 200
        assert log.webhook_attempts == 1

    def test_filter_rule_delivery_log_optional_fields(self) -> None:
        data = {
            **FILTER_RULE_DELIVERY_LOG,
            "tweet_text_preview": None,
            "webhook_status_code": None,
            "webhook_attempts": 0,
        }
        log = FilterRuleDeliveryLog.model_validate(data)
        assert log.tweet_text_preview is None
        assert log.webhook_status_code is None
        assert log.webhook_attempts == 0

    def test_filter_rule_delivery_log_is_frozen(self) -> None:
        log = FilterRuleDeliveryLog.model_validate(FILTER_RULE_DELIVERY_LOG)
        with pytest.raises(Exception):  # noqa: B017
            log.tweet_id = "mutated"  # type: ignore[misc]

    def test_filter_rule_delivery_log_list_validates(self) -> None:
        result = FilterRuleDeliveryLogList.model_validate(FILTER_RULE_DELIVERY_LOG_LIST)
        assert result.total == 1
        assert result.limit == 20
        assert result.offset == 0
        assert len(result.logs) == 1

    def test_filter_rule_pricing_tier_validates(self) -> None:
        tier = FilterRulePricingTier.model_validate(PRICING_TIER)
        assert tier.id == "tier-uuid-0001"
        assert tier.tier_label == "Standard"
        assert tier.max_interval_seconds == 300.0
        assert tier.credits_per_rule_per_day == 48.0
        assert tier.display_order == 3

    def test_filter_rule_pricing_tier_is_frozen(self) -> None:
        tier = FilterRulePricingTier.model_validate(PRICING_TIER)
        with pytest.raises(Exception):  # noqa: B017
            tier.tier_label = "mutated"  # type: ignore[misc]

    def test_filter_rule_pricing_tier_list_validates(self) -> None:
        result = FilterRulePricingTierList.model_validate(PRICING_TIER_LIST)
        assert len(result.tiers) == 1
        assert result.tiers[0].tier_label == "Standard"

    def test_filter_rule_pricing_tier_list_empty(self) -> None:
        result = FilterRulePricingTierList.model_validate({"tiers": []})
        assert result.tiers == []

    def test_filter_rule_query_validation_valid(self) -> None:
        result = FilterRuleQueryValidation.model_validate(QUERY_VALIDATION_VALID)
        assert result.valid is True
        assert result.error is None
        assert result.sample_results == 42

    def test_filter_rule_query_validation_invalid(self) -> None:
        result = FilterRuleQueryValidation.model_validate(QUERY_VALIDATION_INVALID)
        assert result.valid is False
        assert result.error == "Unsupported operator: badop:"
        assert result.sample_results == 0

    def test_filter_rule_query_validation_is_frozen(self) -> None:
        result = FilterRuleQueryValidation.model_validate(QUERY_VALIDATION_VALID)
        with pytest.raises(Exception):  # noqa: B017
            result.valid = False  # type: ignore[misc]


# ===========================================================================
# TestFilterRuleStatusEnum
# ===========================================================================


class TestFilterRuleStatusEnum:
    """Tests for the FilterRuleStatus enum values."""

    def test_status_values(self) -> None:
        assert FilterRuleStatus.ACTIVE == "active"
        assert FilterRuleStatus.PAUSED == "paused"
        assert FilterRuleStatus.ERROR == "error"
        assert FilterRuleStatus.INACTIVE == "inactive"

    def test_status_is_string(self) -> None:
        # StrEnum instances should compare equal to plain strings
        assert FilterRuleStatus.ACTIVE == "active"
        assert "active" == FilterRuleStatus.ACTIVE


# ===========================================================================
# TestStreamClientFilterRules
# ===========================================================================


class TestStreamClientFilterRules:
    """Tests for StreamClient filter rule CRUD and utility methods."""

    # ------------------------------------------------------------------
    # create_filter_rule
    # ------------------------------------------------------------------

    async def test_create_filter_rule_minimal(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = FILTER_RULE_RESPONSE
        rule = await stream_client.create_filter_rule(
            tag="Python news",
            query="#python lang:en -is:retweet",
            interval_seconds=60.0,
        )
        assert isinstance(rule, FilterRuleResponse)
        assert rule.id == FILTER_RULE_RESPONSE["id"]
        assert rule.tag == "Python news"
        assert rule.query == "#python lang:en -is:retweet"
        assert rule.interval_seconds == 60.0

        mock_base_client.post.assert_called_once()
        call_args = mock_base_client.post.call_args
        assert call_args[0][0] == "/v1/twitter/stream/filter-rules"
        body = call_args[1]["json"]
        assert body["tag"] == "Python news"
        assert body["query"] == "#python lang:en -is:retweet"
        assert body["interval_seconds"] == 60.0
        assert "webhook_url" not in body
        assert "webhook_secret" not in body
        assert "max_results_per_poll" not in body

    async def test_create_filter_rule_with_webhook(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = FILTER_RULE_RESPONSE
        await stream_client.create_filter_rule(
            tag="Python news",
            query="#python",
            interval_seconds=60.0,
            webhook_url="https://example.com/hook",
            webhook_secret="s3cr3t",
        )
        body = mock_base_client.post.call_args[1]["json"]
        assert body["webhook_url"] == "https://example.com/hook"
        assert body["webhook_secret"] == "s3cr3t"

    async def test_create_filter_rule_with_max_results(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = FILTER_RULE_RESPONSE
        await stream_client.create_filter_rule(
            tag="Python news",
            query="#python",
            interval_seconds=60.0,
            max_results_per_poll=25,
        )
        body = mock_base_client.post.call_args[1]["json"]
        assert body["max_results_per_poll"] == 25

    async def test_create_filter_rule_returns_filter_rule_response(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = FILTER_RULE_RESPONSE
        rule = await stream_client.create_filter_rule(
            tag="test", query="query", interval_seconds=60.0
        )
        assert isinstance(rule, FilterRuleResponse)

    # ------------------------------------------------------------------
    # list_filter_rules
    # ------------------------------------------------------------------

    async def test_list_filter_rules_default_params(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_RESPONSE_LIST
        result = await stream_client.list_filter_rules()
        assert isinstance(result, FilterRuleResponseList)
        assert result.total == 1

        call_params = mock_base_client.get.call_args[1]["params"]
        assert call_params["limit"] == 20
        assert call_params["offset"] == 0
        assert "status" not in call_params

    async def test_list_filter_rules_with_status_filter(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_RESPONSE_LIST
        await stream_client.list_filter_rules(status="active", limit=10, offset=5)
        call_params = mock_base_client.get.call_args[1]["params"]
        assert call_params["status"] == "active"
        assert call_params["limit"] == 10
        assert call_params["offset"] == 5

    async def test_list_filter_rules_no_status_when_none(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_RESPONSE_LIST
        await stream_client.list_filter_rules()
        call_params = mock_base_client.get.call_args[1]["params"]
        assert "status" not in call_params

    async def test_list_filter_rules_calls_correct_path(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_RESPONSE_LIST
        await stream_client.list_filter_rules()
        called_path = mock_base_client.get.call_args[0][0]
        assert called_path == "/v1/twitter/stream/filter-rules"

    # ------------------------------------------------------------------
    # get_filter_rule
    # ------------------------------------------------------------------

    async def test_get_filter_rule_returns_rule(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_RESPONSE
        rule = await stream_client.get_filter_rule("aaaabbbb-cccc-dddd-eeee-ffffffffffff")
        assert isinstance(rule, FilterRuleResponse)
        assert rule.id == "aaaabbbb-cccc-dddd-eeee-ffffffffffff"

    async def test_get_filter_rule_calls_correct_path(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_RESPONSE
        await stream_client.get_filter_rule("aaaabbbb-cccc-dddd-eeee-ffffffffffff")
        mock_base_client.get.assert_called_once_with(
            "/v1/twitter/stream/filter-rules/aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        )

    # ------------------------------------------------------------------
    # update_filter_rule
    # ------------------------------------------------------------------

    async def test_update_filter_rule_partial_tag(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        updated = {**FILTER_RULE_RESPONSE, "tag": "Renamed Rule"}
        mock_base_client._request.return_value = updated
        rule = await stream_client.update_filter_rule(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
            tag="Renamed Rule",
        )
        assert rule.tag == "Renamed Rule"
        call_args = mock_base_client._request.call_args
        assert call_args[0][0] == "PATCH"
        body = call_args[1]["json"]
        assert body == {"tag": "Renamed Rule"}

    async def test_update_filter_rule_sends_only_provided_fields(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = FILTER_RULE_RESPONSE
        await stream_client.update_filter_rule(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
            interval_seconds=300.0,
        )
        body = mock_base_client._request.call_args[1]["json"]
        assert "interval_seconds" in body
        assert "tag" not in body
        assert "query" not in body
        assert "status" not in body

    async def test_update_filter_rule_status_field(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = {
            **FILTER_RULE_RESPONSE,
            "status": "paused",
        }
        rule = await stream_client.update_filter_rule(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
            status="paused",
        )
        body = mock_base_client._request.call_args[1]["json"]
        assert body["status"] == "paused"
        assert rule.status == FilterRuleStatus.PAUSED

    async def test_update_filter_rule_multiple_fields(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = FILTER_RULE_RESPONSE
        await stream_client.update_filter_rule(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
            tag="New tag",
            query="new query",
            interval_seconds=120.0,
            webhook_url="https://new.example.com/hook",
            webhook_secret="newsecret",
            max_results_per_poll=5,
        )
        body = mock_base_client._request.call_args[1]["json"]
        assert body["tag"] == "New tag"
        assert body["query"] == "new query"
        assert body["interval_seconds"] == 120.0
        assert body["webhook_url"] == "https://new.example.com/hook"
        assert body["webhook_secret"] == "newsecret"
        assert body["max_results_per_poll"] == 5

    async def test_update_filter_rule_calls_correct_path(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = FILTER_RULE_RESPONSE
        await stream_client.update_filter_rule(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
            tag="updated",
        )
        call_args = mock_base_client._request.call_args
        assert (
            call_args[0][1]
            == "/v1/twitter/stream/filter-rules/aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        )

    # ------------------------------------------------------------------
    # delete_filter_rule
    # ------------------------------------------------------------------

    async def test_delete_filter_rule_returns_none(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = {}
        result = await stream_client.delete_filter_rule(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        )
        assert result is None

    async def test_delete_filter_rule_calls_delete_method(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = {}
        await stream_client.delete_filter_rule("aaaabbbb-cccc-dddd-eeee-ffffffffffff")
        call_args = mock_base_client._request.call_args
        assert call_args[0][0] == "DELETE"
        assert "aaaabbbb-cccc-dddd-eeee-ffffffffffff" in call_args[0][1]

    # ------------------------------------------------------------------
    # pause_filter_rule / resume_filter_rule
    # ------------------------------------------------------------------

    async def test_pause_filter_rule_calls_update_with_paused(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = {
            **FILTER_RULE_RESPONSE,
            "status": "paused",
        }
        rule = await stream_client.pause_filter_rule(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        )
        assert rule.status == FilterRuleStatus.PAUSED
        body = mock_base_client._request.call_args[1]["json"]
        assert body["status"] == "paused"

    async def test_resume_filter_rule_calls_update_with_active(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client._request.return_value = FILTER_RULE_RESPONSE
        rule = await stream_client.resume_filter_rule(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        )
        assert rule.status == FilterRuleStatus.ACTIVE
        body = mock_base_client._request.call_args[1]["json"]
        assert body["status"] == "active"

    # ------------------------------------------------------------------
    # validate_filter_rule_query
    # ------------------------------------------------------------------

    async def test_validate_filter_rule_query_valid(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = QUERY_VALIDATION_VALID
        result = await stream_client.validate_filter_rule_query(
            "#python lang:en -is:retweet"
        )
        assert isinstance(result, FilterRuleQueryValidation)
        assert result.valid is True
        assert result.error is None
        assert result.sample_results == 42

    async def test_validate_filter_rule_query_invalid(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = QUERY_VALIDATION_INVALID
        result = await stream_client.validate_filter_rule_query("badop:value")
        assert result.valid is False
        assert result.error == "Unsupported operator: badop:"

    async def test_validate_filter_rule_query_calls_correct_path(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = QUERY_VALIDATION_VALID
        await stream_client.validate_filter_rule_query("#python")
        call_args = mock_base_client.post.call_args
        assert call_args[0][0] == "/v1/twitter/stream/filter-rules/validate"
        assert call_args[1]["json"] == {"query": "#python"}

    async def test_validate_filter_rule_query_sends_query_in_body(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.post.return_value = QUERY_VALIDATION_VALID
        query = "#python OR #django lang:en"
        await stream_client.validate_filter_rule_query(query)
        body = mock_base_client.post.call_args[1]["json"]
        assert body["query"] == query

    # ------------------------------------------------------------------
    # list_filter_rule_delivery_logs
    # ------------------------------------------------------------------

    async def test_list_filter_rule_delivery_logs_default_params(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_DELIVERY_LOG_LIST
        result = await stream_client.list_filter_rule_delivery_logs(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        )
        assert isinstance(result, FilterRuleDeliveryLogList)
        assert result.total == 1

        params = mock_base_client.get.call_args[1]["params"]
        assert params["limit"] == 20
        assert params["offset"] == 0
        assert params["sort"] == "desc"
        assert "delivery_status" not in params

    async def test_list_filter_rule_delivery_logs_with_filters(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_DELIVERY_LOG_LIST
        await stream_client.list_filter_rule_delivery_logs(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
            limit=50,
            offset=10,
            delivery_status="webhook_delivered",
            sort="asc",
        )
        params = mock_base_client.get.call_args[1]["params"]
        assert params["limit"] == 50
        assert params["offset"] == 10
        assert params["delivery_status"] == "webhook_delivered"
        assert params["sort"] == "asc"

    async def test_list_filter_rule_delivery_logs_no_status_when_none(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_DELIVERY_LOG_LIST
        await stream_client.list_filter_rule_delivery_logs(
            "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        )
        params = mock_base_client.get.call_args[1]["params"]
        assert "delivery_status" not in params

    async def test_list_filter_rule_delivery_logs_calls_correct_path(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = FILTER_RULE_DELIVERY_LOG_LIST
        rule_id = "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        await stream_client.list_filter_rule_delivery_logs(rule_id)
        called_path = mock_base_client.get.call_args[0][0]
        assert called_path == f"/v1/twitter/stream/filter-rules/{rule_id}/logs"

    # ------------------------------------------------------------------
    # get_filter_rule_pricing
    # ------------------------------------------------------------------

    async def test_get_filter_rule_pricing_returns_tier_list(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = PRICING_TIER_LIST
        result = await stream_client.get_filter_rule_pricing()
        assert isinstance(result, FilterRulePricingTierList)
        assert len(result.tiers) == 1
        assert result.tiers[0].tier_label == "Standard"

    async def test_get_filter_rule_pricing_calls_correct_path(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = PRICING_TIER_LIST
        await stream_client.get_filter_rule_pricing()
        mock_base_client.get.assert_called_once_with(
            "/v1/twitter/stream/filter-rules-pricing"
        )

    async def test_get_filter_rule_pricing_empty_tiers(
        self, stream_client: StreamClient, mock_base_client: MagicMock
    ) -> None:
        mock_base_client.get.return_value = {"tiers": []}
        result = await stream_client.get_filter_rule_pricing()
        assert result.tiers == []


# ===========================================================================
# TestFilterRuleImports
# ===========================================================================


class TestFilterRuleImports:
    """Tests that filter rule types are importable from the twitter package."""

    def test_filter_rule_response_importable(self) -> None:
        from scrapebadger.twitter import FilterRuleResponse as _  # noqa: F401

    def test_filter_rule_response_list_importable(self) -> None:
        from scrapebadger.twitter import FilterRuleResponseList as _  # noqa: F401

    def test_filter_rule_delivery_log_importable(self) -> None:
        from scrapebadger.twitter import FilterRuleDeliveryLog as _  # noqa: F401

    def test_filter_rule_delivery_log_list_importable(self) -> None:
        from scrapebadger.twitter import FilterRuleDeliveryLogList as _  # noqa: F401

    def test_filter_rule_pricing_tier_importable(self) -> None:
        from scrapebadger.twitter import FilterRulePricingTier as _  # noqa: F401

    def test_filter_rule_pricing_tier_list_importable(self) -> None:
        from scrapebadger.twitter import FilterRulePricingTierList as _  # noqa: F401

    def test_filter_rule_query_validation_importable(self) -> None:
        from scrapebadger.twitter import FilterRuleQueryValidation as _  # noqa: F401

    def test_filter_rule_status_importable(self) -> None:
        from scrapebadger.twitter import FilterRuleStatus as _  # noqa: F401
