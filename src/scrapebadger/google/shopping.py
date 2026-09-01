"""Google Shopping client (search and product detail)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ShoppingClient:
    """Client for Google Shopping search.

    Exposes `search`: product listings with prices, ratings, thumbnails,
    filters, and Google's native ``gpcid`` / ``catalog_id`` /
    ``headline_offer_docid`` / ``mid`` on every tile. Pipe any tile into
    :meth:`ProductsClient.detail` for full specs + offers.

    Example:
        ```python
        products = await client.google.shopping.search("laptop", max_price=1000)
        first = products["results"][0]
        detail = await client.google.products.detail(
            first["gpcid"],
            q="laptop",
            include_offers=True,  # merchant URLs come from /async/piu_ps
        )
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
        domain: str = "google.com",
        page: int = 0,
        min_price: int | None = None,
        max_price: int | None = None,
        sort_by: str | None = None,
        free_shipping: bool = False,
        on_sale: bool = False,
        safe: str = "off",
        nfpr: int = 0,
        lr: str | None = None,
        tbs: str | None = None,
        shoprs: str | None = None,
    ) -> dict[str, Any]:
        """Search Google Shopping for products.

        Args:
            q: Product search query.
            gl: Country code.
            hl: Language code.
            domain: Google domain.
            page: Zero-based page index (each page ≈ 60 tiles).
            min_price / max_price: Price filters.
            sort_by: ``"price_low"`` / ``"price_high"`` / ``"rating"`` /
                ``"reviews"``.
            free_shipping: Restrict to free-shipping offers.
            on_sale: Restrict to on-sale offers.
            safe: ``"off"`` or ``"active"``.
            nfpr: ``1`` disables auto-correction.
            lr: Language restrict (``"lang_en"`` …).
            tbs: Raw Google ``tbs`` filter string.
            shoprs: Google internal ``shoprs`` helper token.

        Returns:
            Response with ``results`` (title, price.value + extracted_price,
            source, rating, reviews, thumbnail, product_id, click_link,
            delivery, on_sale/old_price/tag), ``filters``, ``ads``,
            ``pagination``.
        """
        params: dict[str, Any] = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "domain": domain,
            "page": page,
            "safe": safe,
        }
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if sort_by:
            params["sort_by"] = sort_by
        if free_shipping:
            params["free_shipping"] = "true"
        if on_sale:
            params["on_sale"] = "true"
        if nfpr:
            params["nfpr"] = nfpr
        if lr:
            params["lr"] = lr
        if tbs:
            params["tbs"] = tbs
        if shoprs:
            params["shoprs"] = shoprs
        return await self._client.get("/v1/google/shopping/search", params=params)

    async def product(
        self,
        product_id: str,
        *,
        gl: str = "us",
        hl: str = "en",
        domain: str = "google.com",
    ) -> dict[str, Any]:
        """Fetch the Google Shopping product detail page.

        Args:
            product_id: Google Shopping product ID (from search results).
            gl: Country code.
            hl: Language code.
            domain: Google domain.
        """
        params: dict[str, Any] = {
            "product_id": product_id,
            "gl": gl,
            "hl": hl,
            "domain": domain,
        }
        return await self._client.get("/v1/google/shopping/product", params=params)

    async def offers(
        self,
        barcode: str | None = None,
        *,
        gl: str | None = None,
        hl: str = "en",
        catalog_id: str | None = None,
    ) -> dict[str, Any]:
        """Multi-seller Google Shopping prices for a product by barcode or catalog id.

        Pass either ``barcode`` (resolved to a product via Google web search
        first) or ``catalog_id`` (Google Shopping ``catalogid`` — the
        ``catalog_id`` on ``shopping.search`` tiles or ``prds=catalogid:…`` in
        a Google Shopping URL; sellers read straight off Google's product
        page). Costs 14 credits.

        Args:
            barcode: Product barcode — a GTIN-8/UPC-A/EAN-13/GTIN-14.
            gl: Country code (ISO-3166 alpha-2).
            hl: Language code.
            catalog_id: Google Shopping catalog id. Exactly one of
                ``barcode`` / ``catalog_id`` is required.

        Returns:
            Response with ``barcode`` or ``catalog_id`` (+ ``total_offers``),
            ``resolved_query``, ``product_title``, and ``offers`` (each with
            title, source, price.value/currency/extracted, link, delivery, ...).

        Raises:
            Returns a 400 unless exactly one identifier is passed, 422 for an
            invalid/checksum-failing barcode, 404 if nothing resolves.
        """
        params: dict[str, Any] = {"hl": hl}
        if barcode is not None:
            params["barcode"] = barcode
        if catalog_id is not None:
            params["catalog_id"] = catalog_id
        if gl is not None:
            params["gl"] = gl
        return await self._client.get("/v1/google/shopping/offers", params=params)

    async def click(
        self,
        *,
        title: str,
        source: str,
        q: str,
        product_id: str | None = None,
    ) -> dict[str, Any]:
        """Resolve the direct merchant URL for a Shopping product tile.

        Uses Google's "I'm Feeling Lucky" redirect (``btnI=1``) scoped to
        the card's ``source`` merchant via the ``site:`` operator — so you
        get the actual merchant product page URL without going through
        Google's tracking redirect.

        Args:
            title: Product title from the original search result.
            source: Merchant source name from the search result.
            q: Original search query (helps Google disambiguate).
            product_id: Optional product ID for correlation in the response.
        """
        params: dict[str, Any] = {
            "title": title,
            "source": source,
            "q": q,
        }
        if product_id is not None:
            params["product_id"] = product_id
        return await self._client.get("/v1/google/shopping/product/click", params=params)
