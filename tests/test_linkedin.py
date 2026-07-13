"""Unit tests for the LinkedIn SDK client — endpoint routing via a mocked HTTP client."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapebadger.linkedin.client import LinkedInClient
from scrapebadger.linkedin.models import (
    Company,
    GeoSuggestResponse,
    JobDetail,
    JobsSearchResponse,
    LearningCourse,
    Post,
    Profile,
    School,
)

JOBS_RESPONSE: dict[str, Any] = {
    "jobs": [{"job_id": "123", "title": "SWE", "company": "Acme"}],
    "meta": {"result_count": 1, "start": 0, "has_more": False},
}
JOB_DETAIL: dict[str, Any] = {"job_id": "123", "title": "SWE", "job_url": "https://x/jobs/view/123"}
COMPANY: dict[str, Any] = {
    "universal_name": "microsoft",
    "linkedin_url": "https://www.linkedin.com/company/microsoft",
    "name": "Microsoft",
    "employee_count": 1000,
}
SCHOOL: dict[str, Any] = {
    "universal_name": "harvard-university",
    "linkedin_url": "https://www.linkedin.com/school/harvard-university",
    "name": "Harvard University",
}
PROFILE: dict[str, Any] = {
    "public_id": "williamhgates",
    "linkedin_url": "https://www.linkedin.com/in/williamhgates",
    "name": "Bill Gates",
}
POST: dict[str, Any] = {"post_id": "p1", "type": "social", "text": "hi"}
COURSE: dict[str, Any] = {
    "slug": "learning-python",
    "url": "https://x/learning/c",
    "name": "Learning Python",
}
GEO: dict[str, Any] = {"query": "New York", "type": "geo", "suggestions": [{"id": "102571732"}]}


@pytest.fixture
def mock_base_client() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock()
    return client


@pytest.fixture
def linkedin(mock_base_client: MagicMock) -> LinkedInClient:
    return LinkedInClient(mock_base_client)


async def test_jobs_search(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = JOBS_RESPONSE
    result = await linkedin.jobs_search(keywords="swe", location="NY", experience="entry")
    assert isinstance(result, JobsSearchResponse)
    call = mock_base_client.get.call_args
    assert call[0][0] == "/v1/linkedin/jobs/search"
    params = call[1]["params"]
    assert params["keywords"] == "swe"
    assert params["location"] == "NY"
    assert params["experience"] == "entry"
    assert params["start"] == 0
    assert params["country"] == "us"


async def test_get_job(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = JOB_DETAIL
    result = await linkedin.get_job("123")
    assert isinstance(result, JobDetail)
    assert mock_base_client.get.call_args[0][0] == "/v1/linkedin/jobs/123"


async def test_company_jobs(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = JOBS_RESPONSE
    await linkedin.company_jobs("1035", start=25)
    call = mock_base_client.get.call_args
    assert call[0][0] == "/v1/linkedin/companies/1035/jobs"
    assert call[1]["params"]["start"] == 25


async def test_get_company(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = COMPANY
    result = await linkedin.get_company("microsoft")
    assert isinstance(result, Company)
    assert mock_base_client.get.call_args[0][0] == "/v1/linkedin/companies/microsoft"


async def test_get_school(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = SCHOOL
    result = await linkedin.get_school("harvard-university")
    assert isinstance(result, School)
    assert mock_base_client.get.call_args[0][0] == "/v1/linkedin/schools/harvard-university"


async def test_get_profile(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = PROFILE
    result = await linkedin.get_profile("williamhgates")
    assert isinstance(result, Profile)
    assert mock_base_client.get.call_args[0][0] == "/v1/linkedin/profiles/williamhgates"


async def test_get_post_and_article(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = POST
    assert isinstance(await linkedin.get_post("slug-activity-1-x"), Post)
    assert mock_base_client.get.call_args[0][0] == "/v1/linkedin/posts/slug-activity-1-x"
    assert isinstance(await linkedin.get_article("a-slug"), Post)
    assert mock_base_client.get.call_args[0][0] == "/v1/linkedin/articles/a-slug"


async def test_get_course(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = COURSE
    result = await linkedin.get_course("learning-python")
    assert isinstance(result, LearningCourse)
    assert mock_base_client.get.call_args[0][0] == "/v1/linkedin/learning/learning-python"


async def test_geo_suggest(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = GEO
    result = await linkedin.geo_suggest("New York")
    assert isinstance(result, GeoSuggestResponse)
    call = mock_base_client.get.call_args
    assert call[0][0] == "/v1/linkedin/geo/suggest"
    assert call[1]["params"] == {"query": "New York", "type": "geo"}


async def test_health(linkedin: LinkedInClient, mock_base_client: MagicMock) -> None:
    mock_base_client.get.return_value = {"status": "ok"}
    assert await linkedin.health() == {"status": "ok"}
    assert mock_base_client.get.call_args[0][0] == "/v1/linkedin/health"


def test_import_from_package() -> None:
    from scrapebadger import LinkedInClient as Exported

    assert Exported is LinkedInClient
