"""Google AI Mode client (udm=50 generative answers)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AiModeClient:
    """Client for Google AI Mode (generative answer responses).

    Example:
        ```python
        answer = await client.google.ai_mode.search("what is kubernetes?")
        for block in answer["text_blocks"]:
            print(block["snippet"])
        for ref in answer["references"]:
            print(ref["title"], ref["link"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        gl: str = "us",
        hl: str = "en",
    ) -> dict[str, Any]:
        """Get an AI-generated answer from Google's AI Mode (udm=50)."""
        params: dict[str, Any] = {"q": q, "gl": gl, "hl": hl}
        return await self._client.get("/v1/google/ai-mode/search", params=params)
