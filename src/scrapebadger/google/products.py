"""Google Products client (immersive product detail via /async/oapv RPC)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ProductsClient:
    """Client for Google's immersive product detail endpoint.

    Backed by Google's ``/async/oapv`` JSON RPC — the same endpoint the
    Shopping drawer fires when a tile is clicked. Returns full product
    payload (title, brand, price, rating, images, specs) in ~2s via
    warm-session curl_cffi, falling back to a browser warmup on cold
    sessions.

    Example:
        ```python
        # Typical flow: search first, then pipe the gpcid into detail.
        results = await client.google.shopping.search("running shoes")
        first = results["results"][0]
        detail = await client.google.products.detail(
            first["gpcid"],  # Google Shopping's real product ID
            q="running shoes",
            include_offers=True,  # Also fetch merchant offers
        )
        print(detail["title"], detail["price"]["extracted"])
        for spec, value in detail["specs"].items():
            print(f"  {spec}: {value}")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def detail(
        self,
        product_id: str,
        *,
        q: str | None = None,
        gl: str = "us",
        hl: str = "en",
        domain: str = "google.com",
        catalog_id: str | None = None,
        image_docid: str | None = None,
        headline_offer_docid: str | None = None,
        mid: str | None = None,
        include_offers: bool = False,
        include_variants: bool = False,
        resolve_deep_urls: bool = False,
    ) -> dict[str, Any]:
        """Get deep product details from Google's immersive product page.

        Args:
            product_id: Google Shopping ``gpcid``. Shopping search results
                expose this as the ``gpcid`` field on each tile (falling
                back to a hash when Google didn't surface one).
            q: Original search query text — optional; when provided it
                helps build the ``/async/oapv`` context blob for richer
                responses, but the backend accepts lookups by product_id
                alone.
            gl: Country code (ISO 3166 alpha-2).
            hl: Language code.
            domain: Google domain used to localise the SERP that yields the
                ``/async/oapv`` session tokens (``google.com`` /
                ``google.co.uk`` / …).
            catalog_id, image_docid, headline_offer_docid, mid: Extra
                identifiers Google surfaces on each Shopping tile.
                Passing them through improves routing accuracy.
            include_offers: When True, also fetches ``/async/piu_ps`` for
                the merchant offers list (doubles latency).
            include_variants: When True, also fetches ``/async/toy_v`` for
                size/colour variants.
            resolve_deep_urls: Only meaningful with ``include_offers=True``.
                When True, browser-renders the Shopping SERP so additional
                merchant deep URLs surface from the rendered HTML. Adds
                ~5-8 s latency. Best-effort: catalog-feed retailers (DSW,
                Famous Footwear, etc.) get deep URLs; paid-Shopping-Ads
                merchants (Zappos, GOAT, Academy, …) still get their
                homepage because their click-through URLs are signed by
                Google's aclk redirect and can't be reproduced server-side.

        Returns:
            Response with ``title``, ``brand``, ``rating``,
            ``reviews_count``, ``price`` (``{value, currency, extracted}``),
            ``images``, ``specs`` (attribute→value map), ``categories``,
            plus optional ``offers`` and ``variants`` when requested.
        """
        params: dict[str, Any] = {
            "product_id": product_id,
            "gl": gl,
            "hl": hl,
            "domain": domain,
        }
        if q is not None:
            params["q"] = q
        if catalog_id:
            params["catalog_id"] = catalog_id
        if image_docid:
            params["image_docid"] = image_docid
        if headline_offer_docid:
            params["headline_offer_docid"] = headline_offer_docid
        if mid:
            params["mid"] = mid
        if include_offers:
            params["include_offers"] = "true"
        if include_variants:
            params["include_variants"] = "true"
        if resolve_deep_urls:
            params["resolve_deep_urls"] = "true"
        return await self._client.get("/v1/google/products/detail", params=params)
