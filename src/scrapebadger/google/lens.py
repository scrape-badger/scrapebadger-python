"""Google Lens client (visual image search)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class LensClient:
    """Client for Google Lens visual search by image URL.

    Returns ``lens_results`` (Scrapingdog-parity alias) carrying
    ``title``, ``source``, ``source_favicon``, ``thumbnail``, ``rating``,
    ``reviews`` and ``in_stock``. Shoppable matches also carry ``price``
    (``{value, currency, extracted}``) plus the raw ``tag`` chip it is
    parsed from. ``related_searches`` chips come alongside. Legacy
    ``results`` alias retained for backwards compat.

    Example:
        ```python
        results = await client.google.lens.search(
            url="https://example.com/photo.jpg",
            product=True,  # bias towards shoppable matches
        )
        for match in results["lens_results"]:
            price = match.get("price") or {}
            print(match["title"], price.get("value"), price.get("currency"))
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        url: str,
        *,
        query: str | None = None,
        country: str | None = None,
        language: str | None = None,
        gl: str = "us",
        hl: str = "en",
        product: bool = False,
        visual_matches: bool = True,
        exact_matches: bool = False,
    ) -> dict[str, Any]:
        """Search Google Lens with a public image URL.

        Args:
            url: Public URL of the image to search visually.
            query: Optional text refinement (e.g. ``"pizza"``) to bias
                Lens towards a specific category.
            country: ISO country code — Scrapingdog-parity alias for
                ``gl``. When supplied, takes precedence.
            language: Language code — Scrapingdog-parity alias for
                ``hl``. When supplied, takes precedence.
            gl: Native country code (default ``"us"``).
            hl: Native language code (default ``"en"``).
            product: NOT YET SUPPORTED. Accepted for API compatibility
                and echoed in the response's ``warnings`` list; it does
                not change the results.
            visual_matches: Visual matches are the only surface this
                endpoint serves, so they are always returned. ``False``
                is echoed in ``warnings``.
            exact_matches: Return just the pages hosting this image,
                each flagged ``exact_match``, instead of the broad visual
                grid — what a copyright or provenance check needs. Google
                exposes this set for most images but not all (6-7 of 10
                in our sampling); when it is unavailable the full grid is
                returned and ``warnings`` says the filter was not
                applied, so you never have to guess which you got.

        The response carries a ``warnings`` list naming every parameter
        that could not be applied. Check it rather than assuming a filter
        took effect.
        """
        params: dict[str, Any] = {"url": url, "gl": gl, "hl": hl}
        if query:
            params["query"] = query
        if country:
            params["country"] = country
        if language:
            params["language"] = language
        if product:
            params["product"] = "true"
        # Emit visual_matches explicitly so the backend knows the toggle
        # state rather than relying on a default.
        params["visual_matches"] = "true" if visual_matches else "false"
        if exact_matches:
            params["exact_matches"] = "true"
        return await self._client.get("/v1/google/lens/search", params=params)
