"""Google AI Mode client (udm=50 generative answers)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class AiModeClient:
    """Client for Google AI Mode (generative answer responses).

    The response carries the structured answer and several views of it:

    * ``text_blocks`` — ordered blocks of type ``paragraph``, ``heading``,
      ``list`` and ``table`` (a table block has ``header`` + ``rows``)
    * ``references`` — flat list of cited sources
    * ``markdown`` — a compact Markdown rendering of the whole answer
    * ``answer_html`` — the raw answer body HTML (omitted when
      ``include_html=False``)

    Example:
        ```python
        answer = await client.google.ai_mode.search("Top Hotels in New York")
        print(answer["markdown"])  # the whole answer as Markdown
        for block in answer["text_blocks"]:
            if block["type"] == "table":
                print(block["header"], block["rows"])
            else:
                print(block.get("snippet") or block.get("text"))
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
        include_html: bool = True,
    ) -> dict[str, Any]:
        """Get an AI-generated answer from Google's AI Mode (udm=50).

        Args:
            q: The query / prompt.
            gl: Country code (ISO 3166 alpha-2).
            hl: Language code.
            include_html: Include the raw ``answer_html`` body in the
                response. It can be 100s of KB — set ``False`` when you
                only need ``text_blocks`` / ``markdown``.
        """
        params: dict[str, Any] = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "include_html": include_html,
        }
        return await self._client.get("/v1/google/ai-mode/search", params=params)
