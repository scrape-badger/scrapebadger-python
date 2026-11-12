"""Pydantic models for LinkedIn API responses.

These models mirror the backend ``linkedin_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Public data comes from LinkedIn's logged-out ``/jobs-guest`` APIs and SSR
pages. The separately labelled full-profile route uses a server-owned
authenticated projection when configured.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Base Configuration
# =============================================================================


class _BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
    )


# =============================================================================
# Jobs
# =============================================================================


class JobCard(_BaseModel):
    """One job posting as it appears in a guest search result list."""

    job_id: str
    title: str | None = None
    job_url: str | None = None
    company: str | None = None
    company_url: str | None = None
    company_logo: str | None = None
    location: str | None = None
    posted_at: str | None = None
    posted_relative: str | None = None
    is_new: bool = False
    benefits: list[str] = Field(default_factory=list)


class JobsSearchMeta(_BaseModel):
    """Pagination metadata for a job search or company-jobs grid."""

    result_count: int = 0
    start: int = 0
    has_more: bool = False


class JobsSearchResponse(_BaseModel):
    jobs: list[JobCard] = Field(default_factory=list)
    meta: JobsSearchMeta


class JobDetail(_BaseModel):
    """Full detail for one job posting (guest ``jobPosting/{id}`` fragment)."""

    job_id: str
    title: str | None = None
    job_url: str | None = None
    company: str | None = None
    company_url: str | None = None
    company_logo: str | None = None
    location: str | None = None
    posted_relative: str | None = None
    applicants: str | None = None
    applicants_count: int | None = None
    description_html: str | None = None
    description_text: str | None = None
    salary: str | None = None
    seniority_level: str | None = None
    employment_type: str | None = None
    job_functions: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    apply_url: str | None = None


# =============================================================================
# Profile (public or separately authenticated)
# =============================================================================


class ProfileExperience(_BaseModel):
    title: str | None = None
    company: str | None = None
    company_url: str | None = None
    location: str | None = None
    employment_type: str | None = None
    description: str | None = None
    date_range: str | None = None
    duration: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    is_current: bool | None = None


class ProfileEducation(_BaseModel):
    school: str | None = None
    school_url: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    description: str | None = None
    date_range: str | None = None
    start_year: int | None = None
    end_year: int | None = None


class ProfileLanguage(_BaseModel):
    name: str
    proficiency: str | None = None


class ProfileAward(_BaseModel):
    title: str
    issuer: str | None = None
    issued_on: str | None = None
    url: str | None = None
    description: str | None = None


class ProfileVolunteering(_BaseModel):
    title: str
    organization: str | None = None
    organization_url: str | None = None
    date_range: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    description: str | None = None


class ProfileRecommendation(_BaseModel):
    author_name: str | None = None
    author_url: str | None = None
    text: str


class ProfileInstructorCourse(_BaseModel):
    title: str
    url: str | None = None
    instructor: str | None = None
    duration: str | None = None
    viewers: str | None = None


class ProfileActivity(_BaseModel):
    type: str
    url: str | None = None
    title: str | None = None
    text: str | None = None
    published_at: str | None = None
    like_count: int | None = None
    comment_count: int | None = None
    author_name: str | None = None
    author_url: str | None = None


class ProfileEntry(_BaseModel):
    name: str | None = None
    title: str | None = None
    subtitle: str | None = None
    role: str | None = None
    organization: str | None = None
    issuer: str | None = None
    proficiency: str | None = None
    number: str | None = None
    score: str | None = None
    cause: str | None = None
    url: str | None = None
    date_range: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    issued_on: str | None = None
    published_on: str | None = None
    description: str | None = None


class ProfileSimilar(_BaseModel):
    name: str | None = None
    headline: str | None = None
    url: str
    follower_count: int | None = None
    location: str | None = None


class ProfileSectionCount(_BaseModel):
    shown: int
    total: int | None = None


class Profile(_BaseModel):
    """A LinkedIn profile from the public page or an authenticated projection."""

    public_id: str
    linkedin_url: str
    access_scope: str = "public"
    name: str | None = None
    headline: str | None = None
    location: str | None = None
    country: str | None = None
    about: str | None = None
    image: str | None = None
    cover_image: str | None = None
    follower_count: int | None = None
    connection_count: str | None = None
    badges: list[str] = Field(default_factory=list)
    websites: list[str] = Field(default_factory=list)
    job_titles: list[str] = Field(default_factory=list)
    current_company: str | None = None
    current_company_url: str | None = None
    experience: list[ProfileExperience] = Field(default_factory=list)
    education: list[ProfileEducation] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    language_details: list[ProfileLanguage] = Field(default_factory=list)
    awards: list[str] = Field(default_factory=list)
    award_details: list[ProfileAward] = Field(default_factory=list)
    volunteering: list[ProfileVolunteering] = Field(default_factory=list)
    recommendations: list[ProfileRecommendation] = Field(default_factory=list)
    instructor_courses: list[ProfileInstructorCourse] = Field(default_factory=list)
    recent_posts: list[ProfileActivity] = Field(default_factory=list)
    recent_articles: list[ProfileActivity] = Field(default_factory=list)
    similar_profiles: list[ProfileSimilar] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[ProfileEntry] = Field(default_factory=list)
    honors: list[ProfileEntry] = Field(default_factory=list)
    publications: list[ProfileEntry] = Field(default_factory=list)
    projects: list[ProfileEntry] = Field(default_factory=list)
    courses: list[ProfileEntry] = Field(default_factory=list)
    organizations: list[ProfileEntry] = Field(default_factory=list)
    patents: list[ProfileEntry] = Field(default_factory=list)
    test_scores: list[ProfileEntry] = Field(default_factory=list)
    counts: dict[str, ProfileSectionCount] = Field(default_factory=dict)
    partial_sections: list[str] = Field(default_factory=list)


# =============================================================================
# Company / School
# =============================================================================


class Address(_BaseModel):
    street: str | None = None
    city: str | None = None
    region: str | None = None
    postal_code: str | None = None
    country: str | None = None


class Company(_BaseModel):
    """A public company page (JSON-LD ``Organization`` + about-us module)."""

    universal_name: str
    linkedin_url: str
    name: str | None = None
    description: str | None = None
    website: str | None = None
    industry: str | None = None
    company_size: str | None = None
    company_type: str | None = None
    headquarters: str | None = None
    founded: int | None = None
    specialties: list[str] = Field(default_factory=list)
    employee_count: int | None = None
    follower_count: int | None = None
    logo: str | None = None
    address: Address | None = None


class School(_BaseModel):
    """A public school page (JSON-LD ``Organization``)."""

    universal_name: str
    linkedin_url: str
    name: str | None = None
    description: str | None = None
    website: str | None = None
    follower_count: int | None = None
    student_alumni_count: int | None = None
    logo: str | None = None
    address: Address | None = None


# =============================================================================
# Posts / articles
# =============================================================================


class PostComment(_BaseModel):
    author: str | None = None
    author_url: str | None = None
    text: str | None = None
    published_at: str | None = None
    like_count: int | None = None


class Post(_BaseModel):
    """A public post: an article (``/pulse/``) or an activity share (``/posts/``)."""

    post_id: str
    url: str | None = None
    type: str | None = None
    author_name: str | None = None
    author_url: str | None = None
    title: str | None = None
    text: str | None = None
    published_at: str | None = None
    like_count: int | None = None
    comment_count: int | None = None
    comments: list[PostComment] = Field(default_factory=list)


# =============================================================================
# Learning
# =============================================================================


class CourseInstructor(_BaseModel):
    name: str | None = None
    job_title: str | None = None
    url: str | None = None


class LearningCourse(_BaseModel):
    """A public LinkedIn Learning course (JSON-LD ``Course``)."""

    slug: str
    url: str
    name: str | None = None
    description: str | None = None
    provider: str | None = None
    workload: str | None = None
    rating_value: str | None = None
    rating_count: int | None = None
    instructors: list[CourseInstructor] = Field(default_factory=list)


# =============================================================================
# Reference / typeahead
# =============================================================================


class GeoSuggestion(_BaseModel):
    id: str
    display_name: str | None = None
    type: str | None = None


class GeoSuggestResponse(_BaseModel):
    query: str
    type: str
    suggestions: list[GeoSuggestion] = Field(default_factory=list)
