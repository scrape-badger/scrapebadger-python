"""Exercise GitHub repository detail through the public SDK and HTTP transport."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from scrapebadger import ScrapeBadger

BASE = "https://api.test.scrapebadger.com"


@respx.mock
async def test_repository_detail_encodes_segments_and_keeps_native_payload(
    client: ScrapeBadger,
) -> None:
    # The adapter returns the raw response: false, zero, empty and null values in
    # nested native groups must arrive unchanged, as must fields added later.
    payload: dict[str, Any] = {
        "repository": {
            "name": "project",
            "full_name": "owner/project",
            "link": "https://github.com/owner/project",
            "owner": {"login": "owner", "is_verified": False},
            "is_empty": False,
            "is_fork": True,
            "fork_comparison": {
                "ahead": 0,
                "behind": 0,
                "base_branch": "main",
                "current_ref": "main",
                "is_tracking_branch": False,
            },
            "is_archived": False,
            "license": None,
            "topics": [],
            "stars": 0,
            "forks": 0,
            "watchers": 0,
        },
        "latest_commit": {
            "sha": "0" * 40,
            "link": "https://github.com/owner/project/commit/" + "0" * 40,
            "message": "Initial commit",
            "authors": [],
            "checks": {"state": "none"},
            "is_spoofed": False,
        },
        "readme": None,
        "files": [],
        "languages": [],
        "latest_release": None,
        "contributors": [],
        "contributors_truncated": False,
        "dependents": [],
        "dependents_truncated": False,
        "funding": None,
        "community_files": [],
        "metadata_available": False,
        "additive": {"nested": {"count": 0, "enabled": False}},
    }
    route = respx.get(url__startswith=f"{BASE}/v1/github/repositories/").mock(
        return_value=httpx.Response(200, json=payload, headers={"X-Credits-Used": "10"})
    )

    result = await client.github.get_repository("owner/a", "project+?#")

    assert route.call_count == 1
    request = route.calls.last.request
    assert request.url.raw_path == b"/v1/github/repositories/owner%2Fa/project%2B%3F%23"
    assert request.url.query == b""
    assert request.headers["x-api-key"] == "test_api_key_12345"
    assert result == payload


@pytest.mark.parametrize("owner,repo", [("..", "project"), ("owner", ".")])
@respx.mock
async def test_repository_dot_segments_never_reach_transport(
    client: ScrapeBadger, owner: str, repo: str
) -> None:
    route = respx.route().mock(return_value=httpx.Response(200, json={}))

    with pytest.raises(ValueError, match="dot path"):
        await client.github.get_repository(owner, repo)

    assert route.call_count == 0
