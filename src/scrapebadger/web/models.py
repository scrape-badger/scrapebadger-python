"""Pydantic models for web scraping API responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScrapeResult(BaseModel):
    """Result from a web scrape request."""

    model_config = ConfigDict(frozen=True)

    content: str = ""
    status_code: int = 0
    url: str = ""
    engine_used: str | None = None
    credits_used: int = 0
    processing_time_ms: float | None = None
    anti_bot_detected: bool = False
    anti_bot_provider: str | None = None
    captcha_solved: bool = False
    session_id: str | None = None
    session_reused: bool = False


class ScreenshotResult(BaseModel):
    """Result from a screenshot request."""

    model_config = ConfigDict(frozen=True)

    image_data: str = ""
    format: str = "png"
    url: str = ""
    credits_used: int = 0


class ExtractResult(BaseModel):
    """Result from a data extraction request."""

    model_config = ConfigDict(frozen=True)

    data: dict[str, Any] = Field(default_factory=dict)
    url: str = ""
    credits_used: int = 0


class BatchResult(BaseModel):
    """Result from a batch scraping request."""

    model_config = ConfigDict(frozen=True)

    results: list[ScrapeResult] = Field(default_factory=list)
    total: int = 0
    successful: int = 0
    failed: int = 0


class SessionInfo(BaseModel):
    """Session information from create/reuse operations."""

    model_config = ConfigDict(frozen=True)

    session_id: str = ""
    domain: str = ""
    reused: bool = False
    fingerprint_id: str | None = None
