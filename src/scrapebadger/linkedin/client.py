"""LinkedIn API client.

LinkedIn endpoints cover the public, no-auth (logged-out) surface only: the
guest **Jobs** API (``jobs_search``, ``get_job``, ``company_jobs``), public SSR
entity pages parsed from JSON-LD (``get_company``, ``get_school``,
``get_profile``, ``get_post``, ``get_article``, ``get_course``) and a
``geo_suggest`` id helper. All methods are async and return strongly-typed
Pydantic models. LinkedIn hard-blocks datacenter IPs, so requests egress via
residential exits — SSR pages occasionally take a few seconds because the client
retries past LinkedIn's intermittent 999 auth-wall on a fresh IP.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class LinkedInClient:
    """Client for all LinkedIn API operations.

    Covers LinkedIn's public **no-auth** surface (no login, no cookies): the
    guest Jobs API, public company/school/profile SSR pages (JSON-LD), public
    posts / Pulse articles / Learning courses, and a geo/company id helper.
    Deep logged-in data (full experience, activity feed, follower lists) is
    auth-gated and not available.

    Example:
        ```python
        from scrapebadger import ScrapeBadger

        async with ScrapeBadger(api_key="your-key") as client:
            # Search jobs
            jobs = await client.linkedin.jobs_search(
                keywords="software engineer", location="New York"
            )
            for card in jobs.jobs:
                print(card.job_id, card.title, card.company)

            # Company / profile pages
            company = await client.linkedin.get_company("microsoft")
            profile = await client.linkedin.get_profile("williamhgates")

            # Resolve a geo id for filtered job search
            geo = await client.linkedin.geo_suggest("London")
        ```

    Note:
        This client is not instantiated directly. Instead, access it through
        the ``linkedin`` property of the main ``ScrapeBadger`` client.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize LinkedIn client.

        Args:
            client: The base HTTP client for making API requests.
        """
        self._client = client

    async def jobs_search(
        self,
        *,
        keywords: str | None = None,
        location: str | None = None,
        geo_id: str | None = None,
        company_id: str | None = None,
        date_posted: str | None = None,
        experience: str | None = None,
        job_type: str | None = None,
        workplace: str | None = None,
        sort: str | None = None,
        start: int = 0,
        country: str = "us",
    ) -> JobsSearchResponse:
        """Search public LinkedIn job postings (guest API, no login).

        Provide at least one of ``keywords``, ``location``, ``geo_id`` or
        ``company_id``.

        Args:
            keywords: Job title / keywords.
            location: Location text, e.g. "New York".
            geo_id: LinkedIn numeric geo id (from ``geo_suggest``; overrides
                ``location``).
            company_id: Restrict to a company (numeric id).
            date_posted: ``past_24h`` | ``past_week`` | ``past_month`` | ``any``.
            experience: ``internship``|``entry``|``associate``|``mid_senior``|
                ``director``|``executive`` (comma-separated).
            job_type: ``full_time``|``part_time``|``contract``|``temporary``|
                ``internship``|``volunteer``|``other`` (comma-separated).
            workplace: ``onsite``|``remote``|``hybrid`` (comma-separated).
            sort: ``relevant`` | ``recent``.
            start: Pagination offset (0, 25, 50, ...). Defaults to 0.
            country: Residential proxy country. Defaults to "us".

        Returns:
            Search response with matching job cards and pagination metadata.
        """
        params: dict[str, Any] = {
            "keywords": keywords,
            "location": location,
            "geo_id": geo_id,
            "company_id": company_id,
            "date_posted": date_posted,
            "experience": experience,
            "job_type": job_type,
            "workplace": workplace,
            "sort": sort,
            "start": start,
            "country": country,
        }
        response = await self._client.get("/v1/linkedin/jobs/search", params=params)
        return JobsSearchResponse.model_validate(response)

    async def get_job(self, job_id: str, *, country: str = "us") -> JobDetail:
        """Get full detail for one job posting (guest ``jobPosting`` API).

        Args:
            job_id: Numeric LinkedIn job id.
            country: Residential proxy country. Defaults to "us".

        Returns:
            The job detail.
        """
        params: dict[str, Any] = {"country": country}
        response = await self._client.get(f"/v1/linkedin/jobs/{job_id}", params=params)
        return JobDetail.model_validate(response)

    async def company_jobs(
        self, company_id: str, *, start: int = 0, country: str = "us"
    ) -> JobsSearchResponse:
        """Get a company's public job postings.

        Args:
            company_id: Numeric LinkedIn company id (from ``get_company``).
            start: Pagination offset (0, 25, 50, ...). Defaults to 0.
            country: Residential proxy country. Defaults to "us".

        Returns:
            Search response with the company's job cards and pagination.
        """
        params: dict[str, Any] = {"start": start, "country": country}
        response = await self._client.get(
            f"/v1/linkedin/companies/{company_id}/jobs", params=params
        )
        return JobsSearchResponse.model_validate(response)

    async def get_company(self, universal_name: str, *, country: str = "us") -> Company:
        """Get a public company page (industry, size, HQ, specialties).

        Args:
            universal_name: The company's vanity name (the ``/company/{name}``
                slug), e.g. "microsoft".
            country: Residential proxy country. Defaults to "us".

        Returns:
            The company profile.
        """
        params: dict[str, Any] = {"country": country}
        response = await self._client.get(f"/v1/linkedin/companies/{universal_name}", params=params)
        return Company.model_validate(response)

    async def get_school(self, universal_name: str, *, country: str = "us") -> School:
        """Get a public school page (name, description, website, counts).

        Args:
            universal_name: The school's vanity name (the ``/school/{name}``
                slug), e.g. "harvard-university".
            country: Residential proxy country. Defaults to "us".

        Returns:
            The school profile.
        """
        params: dict[str, Any] = {"country": country}
        response = await self._client.get(f"/v1/linkedin/schools/{universal_name}", params=params)
        return School.model_validate(response)

    async def get_profile(self, public_id: str, *, country: str = "us") -> Profile:
        """Get a public profile by vanity id (the ``/in/{public_id}`` slug).

        Returns the logged-out subset — name, headline, location, about, image,
        follower count, current role, experience and education. Deep
        logged-in sections are auth-gated.

        Args:
            public_id: The profile vanity id, e.g. "williamhgates".
            country: Residential proxy country. Defaults to "us".

        Returns:
            The public profile.
        """
        params: dict[str, Any] = {"country": country}
        response = await self._client.get(f"/v1/linkedin/profiles/{public_id}", params=params)
        return Profile.model_validate(response)

    async def get_post(self, post_slug: str, *, country: str = "us") -> Post:
        """Get a public activity share (``/posts/{slug}``).

        Args:
            post_slug: The full post slug, e.g.
                ``vanity_words-activity-7213954867470336000-abcd``.
            country: Residential proxy country. Defaults to "us".

        Returns:
            The post — text, author, reactions, comments.
        """
        params: dict[str, Any] = {"country": country}
        response = await self._client.get(f"/v1/linkedin/posts/{post_slug}", params=params)
        return Post.model_validate(response)

    async def get_article(self, article_slug: str, *, country: str = "us") -> Post:
        """Get a public Pulse article (``/pulse/{slug}``).

        Args:
            article_slug: The Pulse article slug.
            country: Residential proxy country. Defaults to "us".

        Returns:
            The article — title, body, author, reactions.
        """
        params: dict[str, Any] = {"country": country}
        response = await self._client.get(f"/v1/linkedin/articles/{article_slug}", params=params)
        return Post.model_validate(response)

    async def get_course(self, course_slug: str, *, country: str = "us") -> LearningCourse:
        """Get a public LinkedIn Learning course.

        Args:
            course_slug: The ``/learning/{slug}`` course slug.
            country: Residential proxy country. Defaults to "us".

        Returns:
            The course — provider, workload, instructors, rating.
        """
        params: dict[str, Any] = {"country": country}
        response = await self._client.get(f"/v1/linkedin/learning/{course_slug}", params=params)
        return LearningCourse.model_validate(response)

    async def geo_suggest(self, query: str, *, type: str = "geo") -> GeoSuggestResponse:
        """Resolve a name to LinkedIn ids (job-search ``geo_id``/``company_id``).

        Args:
            query: Location or company text, e.g. "London".
            type: ``geo`` | ``company``. Defaults to "geo".

        Returns:
            Suggestions with their LinkedIn ids.
        """
        params: dict[str, Any] = {"query": query, "type": type}
        response = await self._client.get("/v1/linkedin/geo/suggest", params=params)
        return GeoSuggestResponse.model_validate(response)

    async def health(self) -> dict[str, Any]:
        """Check the LinkedIn scraper service health.

        Returns:
            The raw health payload.
        """
        return await self._client.get("/v1/linkedin/health")
