"""LinkedIn API module for ScrapeBadger SDK.

This module provides an async client for public LinkedIn data plus the
separately labelled authenticated full-profile projection. All methods return
strongly-typed Pydantic models.

Example:
    ```python
    from scrapebadger import ScrapeBadger

    async with ScrapeBadger(api_key="your-key") as client:
        jobs = await client.linkedin.jobs_search(keywords="python", location="Berlin")
        company = await client.linkedin.get_company("microsoft")
        profile = await client.linkedin.get_profile("williamhgates")
        full_profile = await client.linkedin.get_full_profile("williamhgates")
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
    ProfileActivity,
    ProfileAward,
    ProfileEducation,
    ProfileEntry,
    ProfileExperience,
    ProfileInstructorCourse,
    ProfileLanguage,
    ProfileRecommendation,
    ProfileSectionCount,
    ProfileSimilar,
    ProfileVolunteering,
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
    "ProfileActivity",
    "ProfileAward",
    "ProfileEducation",
    "ProfileEntry",
    "ProfileExperience",
    "ProfileInstructorCourse",
    "ProfileLanguage",
    "ProfileRecommendation",
    "ProfileSectionCount",
    "ProfileSimilar",
    "ProfileVolunteering",
    "School",
]
