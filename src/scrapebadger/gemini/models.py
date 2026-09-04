"""Pydantic models for Gemini API responses.

These models mirror the backend ``gemini_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility.

Answers come from the real gemini.google.com web surface (not the Gemini
API), anonymously — no Google account or API key is involved.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Base Configuration
# =============================================================================


class _BaseModel(BaseModel):
    """Base model with common configuration.

    Note: ``str_strip_whitespace`` is deliberately NOT set. Citations carry
    ``start_index``/``end_index`` offsets into ``answer``, and stripping
    whitespace would shift every offset by the number of leading characters
    removed.
    """

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
    )


# =============================================================================
# Sources
# =============================================================================


class Citation(_BaseModel):
    """A web source Gemini actually referenced in its answer.

    Attributes:
        url: Source URL.
        title: Page title.
        snippet: Snippet of the source text.
        domain: Bare domain of the source (e.g. "reuters.com").
        attribution: Publisher attribution string, when Gemini provides one.
        start_index: Character offset into ``answer`` where the supported span begins.
        end_index: Character offset into ``answer`` where the supported span ends.
        matched_text: The answer substring this source supports.
    """

    url: str | None = None
    title: str | None = None
    snippet: str | None = None
    domain: str | None = None
    attribution: str | None = None
    start_index: int | None = None
    end_index: int | None = None
    matched_text: str | None = None


class SearchResult(_BaseModel):
    """One entry of the FULL set Gemini retrieved — cited or not.

    Attributes:
        url: Result URL.
        title: Page title.
        snippet: Snippet of the result text.
        domain: Bare domain of the result.
        attribution: Publisher attribution string, when present.
        cited: Whether this result was actually referenced in the answer.
    """

    url: str | None = None
    title: str | None = None
    snippet: str | None = None
    domain: str | None = None
    attribution: str | None = None
    cited: bool = False


# =============================================================================
# Ask
# =============================================================================


class MediaItem(_BaseModel):
    """An image the answer itself displayed.

    Never a GENERATED image — anonymous gemini.google.com gates image generation
    behind a login, so this is only ever a picture the answer showed.

    Attributes:
        url: Image URL.
        title: Alt text, when one was supplied.
    """

    url: str
    title: str | None = None


class AskResponse(_BaseModel):
    """A Gemini answer with its sources.

    Attributes:
        prompt: The prompt that was sent.
        answer: The answer as plain text.
        answer_markdown: The answer as markdown, when available.
        citations: Sources Gemini actually referenced.
        search_results: The full retrieved set, cited or not.
        source_domains: Distinct domains across the sources.
        images: Images the answer displayed. Never generated — anonymous
            gemini.google.com will not draw one.
        truncated: True when the render budget expired while Gemini was still
            writing, so ``answer`` is the partial text produced so far.
        web_search_triggered: Whether Gemini ACTUALLY grounded the answer
            with a web search.
        model: Model slug that answered (e.g. a Gemini Flash-Lite build).
        conversation_id: Gemini conversation identifier.
        message_id: Gemini message identifier.
        country: ISO-3166 alpha-2 egress country used.
        answer_length: Length of ``answer`` in characters.
        citation_count: Number of citations.
        latency_ms: End-to-end latency in milliseconds.
        created_utc: Creation time as a Unix timestamp.
        created_at: Creation time as an ISO-8601 Z string.
    """

    prompt: str
    answer: str
    answer_markdown: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    search_results: list[SearchResult] = Field(default_factory=list)
    source_domains: list[str] = Field(default_factory=list)
    images: list[MediaItem] = Field(default_factory=list)
    truncated: bool = False
    web_search_triggered: bool = False
    model: str | None = None
    conversation_id: str | None = None
    message_id: str | None = None
    country: str = ""
    answer_length: int = 0
    citation_count: int = 0
    latency_ms: int = 0
    created_utc: float | None = None
    created_at: str | None = None


# =============================================================================
# Brand visibility
# =============================================================================


class CompetitorMention(_BaseModel):
    """How one competitor fared in the same answer.

    Attributes:
        name: Competitor name as supplied in the request.
        mentioned: Whether the competitor appears in the answer.
        mention_count: Number of mentions.
        first_position: Character offset of the first mention.
        cited: Whether a competitor URL is cited as a source.
        cited_urls: Cited URLs attributed to this competitor.
    """

    name: str
    mentioned: bool = False
    mention_count: int = 0
    first_position: int | None = None
    cited: bool = False
    cited_urls: list[str] = Field(default_factory=list)


class BrandVisibilityResponse(_BaseModel):
    """AEO/GEO brand analysis of a Gemini answer.

    Attributes:
        prompt: The prompt that was sent.
        brand: The brand that was analysed.
        domain: The brand's domain, when supplied.
        mentioned: Whether the brand appears in the answer.
        mention_count: Number of brand mentions.
        first_position: Character offset of the first brand mention.
        position_score: 1.0 = named at the very start, 0.0 = absent.
        share_of_voice_pct: Brand mentions / (brand + competitor mentions).
        cited: Whether the brand's domain is cited as a source.
        cited_urls: Cited URLs on the brand's domain.
        citation_rank: 1-based rank of the first cited brand URL.
        competitors: Per-competitor breakdown.
        excerpt: Answer text around the first brand mention.
        answer: The answer as plain text.
        citations: Sources Gemini actually referenced.
        web_search_triggered: Whether Gemini ACTUALLY grounded the answer
            with a web search.
        model: Model slug that answered.
        country: ISO-3166 alpha-2 egress country used.
        latency_ms: End-to-end latency in milliseconds.
        created_utc: Creation time as a Unix timestamp.
        created_at: Creation time as an ISO-8601 Z string.
    """

    prompt: str
    brand: str
    domain: str | None = None
    mentioned: bool = False
    mention_count: int = 0
    first_position: int | None = None
    position_score: float = 0.0
    share_of_voice_pct: float = 0.0
    cited: bool = False
    cited_urls: list[str] = Field(default_factory=list)
    citation_rank: int | None = None
    competitors: list[CompetitorMention] = Field(default_factory=list)
    excerpt: str | None = None
    answer: str = ""
    citations: list[Citation] = Field(default_factory=list)
    web_search_triggered: bool = False
    model: str | None = None
    country: str = ""
    latency_ms: int = 0
    created_utc: float | None = None
    created_at: str | None = None
