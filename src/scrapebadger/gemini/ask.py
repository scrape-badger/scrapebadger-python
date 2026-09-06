"""Gemini Ask API client.

Sends a prompt to the real gemini.google.com and returns the answer as
structured JSON, including the web sources Gemini cited.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from scrapebadger.gemini.models import AskResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

WebSearchMode = Literal["auto", "force", "off"]


class AskClient:
    """Client for the Gemini ask endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            result = await client.gemini.ask.ask("best running shoes 2026")
            print(result.answer)
            for citation in result.citations:
                print(f"{citation.domain}: {citation.url}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize ask client.

        Args:
            client: The base HTTP client.
        """
        self._client = client

    async def ask(
        self,
        prompt: str,
        *,
        country: str = "US",
        web_search: WebSearchMode = "auto",
        image_url: str | None = None,
    ) -> AskResponse:
        """Ask Gemini a question and get the answer with its sources.

        Args:
            prompt: The prompt to send. Maximum 4096 characters.
            country: ISO-3166 alpha-2 egress country. Defaults to "US".
            web_search: Whether Gemini should ground the answer with a web
                search — "auto", "force", or "off". Defaults to "auto".
            image_url: NOT SUPPORTED — returns 422 and is never billed.
                Signed-out Gemini accepts the upload and then refuses to answer
                about it (PERMISSION_DENIED from its own generate call), so the
                API fails fast rather than charging for a request that cannot
                succeed. Use ``chatgpt.ask`` for image input. Gemini will not
                generate an image either: anonymous gemini.google.com gates that
                behind a login.

        Returns:
            The answer, its citations, and the full retrieved search set.

        Example:
            ```python
            result = await client.gemini.ask.ask(
                "what is the best CRM for a 10-person startup?",
                country="GB",
                web_search="force",
            )
            print(result.web_search_triggered, result.model)
            for source in result.search_results:
                print(f"{'*' if source.cited else ' '} {source.url}")
            ```
        """
        params: dict[str, object] = {
            "prompt": prompt,
            "country": country,
            "web_search": web_search,
        }
        if image_url is not None:
            params["image_url"] = image_url
        response = await self._client.get("/v1/gemini/ask", params=params)
        return AskResponse.model_validate(response)
