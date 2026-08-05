"""ChatGPT Ask API client.

Sends a prompt to the real chatgpt.com and returns the answer as structured
JSON, including the web sources ChatGPT cited.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from scrapebadger.chatgpt.models import AskResponse

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient

WebSearchMode = Literal["auto", "force", "off"]


class AskClient:
    """Client for the ChatGPT ask endpoint.

    Example:
        ```python
        async with ScrapeBadger(api_key="key") as client:
            result = await client.chatgpt.ask.ask("best running shoes 2026")
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
    ) -> AskResponse:
        """Ask ChatGPT a question and get the answer with its sources.

        Costs 20 credits. Typical latency is 20-25s ungrounded, 30-70s with web search.

        Args:
            prompt: The prompt to send. Maximum 4096 characters.
            country: ISO-3166 alpha-2 egress country. Defaults to "US".
            web_search: Whether ChatGPT should browse — "auto", "force", or
                "off". Defaults to "auto".

        Returns:
            The answer, its citations, and the full retrieved search set.

        Example:
            ```python
            result = await client.chatgpt.ask.ask(
                "what is the best CRM for a 10-person startup?",
                country="GB",
                web_search="force",
            )
            print(result.web_search_triggered, result.model)
            for source in result.search_results:
                print(f"{'*' if source.cited else ' '} {source.url}")
            ```
        """
        response = await self._client.get(
            "/v1/chatgpt/ask",
            params={
                "prompt": prompt,
                "country": country,
                "web_search": web_search,
            },
        )
        return AskResponse.model_validate(response)
