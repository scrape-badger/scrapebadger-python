"""LinkedIn API module for ScrapeBadger SDK.

This module provides an async client for scraping LinkedIn's public, no-auth
(logged-out) surface through the ScrapeBadger API: the guest Jobs API, public
company/school/profile SSR pages, public posts / Pulse articles / Learning
courses, and a geo/company id helper. All methods are async and return
strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        jobs = await client.linkedin.jobs_search(keywords="python", location="Berlin")
        company = await client.linkedin.get_company("microsoft")
        profile = await client.linkedin.get_profile("williamhgates")
    ```
"""

from scrapebadger.linkedin.client import LinkedInClient
from scrapebadger.linkedin.models import (
    Address,
    Company,
    CourseInstructor,
    GeoSuggestion,
    GeoSuggestResponse,
    JobCard,
    JobDetail,
    JobsSearchMeta,
    JobsSearchResponse,
    LearningCourse,
    Post,
    PostComment,
    Profile,
    ProfileEducation,
    ProfileExperience,
    School,
)

__all__ = [
    "Address",
    "Company",
    "CourseInstructor",
    "GeoSuggestResponse",
    "GeoSuggestion",
    "JobCard",
    "JobDetail",
    "JobsSearchMeta",
    "JobsSearchResponse",
    "LearningCourse",
    "LinkedInClient",
    "Post",
    "PostComment",
    "Profile",
    "ProfileEducation",
    "ProfileExperience",
    "School",
]
