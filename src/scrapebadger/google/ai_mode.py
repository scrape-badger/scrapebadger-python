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
    * ``location`` — only on located requests (``location``, ``uule`` or
      ``lat``/``lon``): what was requested and what it resolved to

    Example:
        ```python
        answer = await client.google.ai_mode.search("Top Hotels in New York")
        print(answer["markdown"])  # the whole answer as Markdown
        for block in answer["text_blocks"]:
            if block["type"] == "table":
                print(block["header"], block["rows"])
            else:
                print(block.get("snippet") or block.get("text"))

        # Answer "near me" questions as if the user were in Wonju, South Korea
        local = await client.google.ai_mode.search(
            "best coffee near me", location="Wonju-si,Gangwon-do,South Korea", hl="ko"
        )
        print(local["location"]["resolved"], local["country"])  # ..., "kr"
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        gl: str | None = None,
        hl: str = "en",
        include_html: bool = True,
        location: str | None = None,
        uule: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """Get an AI-generated answer from Google's AI Mode (udm=50).

        ``location``, ``uule`` and ``lat``/``lon`` localise the answer
        ("near me", local results) to that place, down to the city or
        district, wherever the request exits from. Use only one of them;
        the API answers 422 otherwise, and also when ``lat`` comes without
        ``lon``, the location is unknown or ambiguous (the error lists
        candidate names), or ``uule`` is not in ``w+``/``j+`` form. A located
        request that cannot be answered right now fails with an unbilled 503;
        retry it.

        Args:
            q: The query / prompt.
            gl: Google country (market) code, e.g. ``"us"``. It shapes the
                answer; it does not pick the exit IP's country. When omitted
                it is ``"us"``, or the location's country when ``location``
                is set.
            hl: Language code.
            include_html: Include the raw ``answer_html`` body in the
                response. It can be 100s of KB — set ``False`` when you
                only need ``text_blocks`` / ``markdown``.
            location: Answer as if the user were here: a Google canonical
                location name (e.g. ``"Wonju-si,Gangwon-do,South Korea"``),
                a Google criteria ID (e.g. ``"1009889"``), or an unambiguous
                short name within ``gl``.
            uule: A Google UULE value in its ``w+`` (canonical name) or
                ``j+`` (coordinates) form.
            lat: Latitude of the user's location, -90 to 90 (with ``lon``).
            lon: Longitude of the user's location, -180 to 180 (with ``lat``).

        Returns:
            The answer dict. Located answers also carry ``location``:
            ``{"requested", "resolved", "latitude", "longitude", "uule"}``,
            and ``country`` is the effective ``gl``.
        """
        if gl is None and location is None:
            gl = "us"  # unlocated requests are sent exactly as before 0.77.0
        params: dict[str, Any] = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "include_html": include_html,
            "location": location,
            "uule": uule,
            "lat": lat,
            "lon": lon,
        }
        return await self._client.get("/v1/google/ai-mode/search", params=params)
