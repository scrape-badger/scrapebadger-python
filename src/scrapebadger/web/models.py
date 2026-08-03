"""Pydantic models for web scraping API responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScrapeResult(BaseModel):
    """Result from a web scrape request."""

    model_config = ConfigDict(frozen=True)

    success: bool = True
    url: str = ""
    status_code: int = 0
    content: str | None = None
    content_base64: str | None = None
    """Base64 body for a binary target (image/PDF/archive). Set instead of
    ``content``, which is None there — binary bytes have no text form."""
    is_binary: bool = False
    content_type: str | None = None
    content_bytes: bytes | None = None
    """Undecoded response body. Only set when ``raw_content=True`` — that mode
    returns the body itself rather than a JSON envelope. Write it straight to a
    file; do not decode it, the payload may be an image or a PDF."""
    format: str = "html"
    engine_used: str | None = None
    credits_used: int = 0
    duration_ms: int = 0
    retries_used: int = 0
    content_length: int = 0
    screenshot_url: str | None = None
    video_url: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    blocking_detected: bool = False
    blocking_details: dict[str, Any] | None = None
    antibot_systems: list[dict[str, Any]] = Field(default_factory=list)
    captcha_systems: list[dict[str, Any]] = Field(default_factory=list)
    anti_bot_solved: bool = False
    solver_used: str | None = None
    ai_extraction: dict[str, Any] | str | list[Any] | None = None
    ai_model: str | None = None
    ai_error: str | None = None


class DetectResult(BaseModel):
    """Result from an anti-bot detection request."""

    model_config = ConfigDict(frozen=True)

    url: str = ""
    antibot_systems: list[dict[str, Any]] = Field(default_factory=list)
    captcha_systems: list[dict[str, Any]] = Field(default_factory=list)
    is_blocked: bool = False
    blocking_type: str | None = None
    recommendation: str | None = None
    credits_used: int = 0
    duration_ms: int = 0
