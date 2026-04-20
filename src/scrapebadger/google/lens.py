"""Google Lens client (visual image search)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class LensClient:
    """Client for Google Lens visual search by image URL.

    Returns ``lens_results`` (Scrapingdog-parity alias) carrying
    ``title``, ``source``, ``source_favicon``, ``thumbnail``, ``tag``
    (price chip when shopping-match), and ``in_stock``, plus
    ``related_searches`` chips. Legacy ``results`` alias retained for
    backwards compat.

    Example:
        ```python
        results = await client.google.lens.search(
            url="https://example.com/photo.jpg",
            product=True,  # bias towards shoppable matches
        )
        for match in results["lens_results"]:
            print(match["title"], match.get("tag"))
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
            product: When True, bias Google towards shoppable product
                matches.
            visual_matches: Include the visual-matches carousel
                (default True — matches Scrapingdog's default bucket).
            exact_matches: Restrict to exact-match results only.
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
