"""Repository routing and additive/false/zero field preservation."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.github.client import GithubClient


@pytest.mark.asyncio
async def test_repository_route_and_raw_fields():
    payload = {
        "repository": {
            "name": "project",
            "full_name": "owner/project",
            "link": "https://github.com/owner/project",
            "owner": {"login": "owner"},
            "is_empty": False,
            "watchers": 0,
        },
        "files": [],
        "metadata_available": False,
        "additive": {"ready": False},
    }
    base = MagicMock()
    base.get = AsyncMock(return_value=payload)
    result = await GithubClient(base).get_repository("owner/a", "project+?#")
    base.get.assert_awaited_once_with("/v1/github/repositories/owner%2Fa/project%2B%3F%23")
    assert result == payload
    assert "readme" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "owner,repo", [(".", "project"), ("..", "project"), ("owner", "."), ("owner", "..")]
)
async def test_dot_segments_never_reach_http(owner, repo):
    base = MagicMock()
    base.get = AsyncMock()
    with pytest.raises(ValueError, match="dot path"):
        await GithubClient(base).get_repository(owner, repo)
    base.get.assert_not_awaited()


@pytest.mark.asyncio
async def test_existing_profile_signature_and_raw_output_are_preserved():
    base = MagicMock()
    base.get = AsyncMock(return_value={"profile": {"login": "octocat"}})
    assert (
        await GithubClient(base).get_profile("octocat", tab="repositories", page="2")
        == base.get.return_value
    )
    base.get.assert_awaited_once_with(
        "/v1/github/profiles/octocat", params={"tab": "repositories", "page": "2"}
    )
