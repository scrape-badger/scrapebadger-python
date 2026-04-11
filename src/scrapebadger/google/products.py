"""Google Products client (immersive product detail)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ProductsClient:
    """Client for Google's immersive product detail endpoint.

    Example:
        ```python
        detail = await client.google.products.detail("1234567890")
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def detail(
        self,
        product_id: str,
        *,
        gl: str = "us",
        hl: str = "en",
    ) -> dict[str, Any]:
        """Get deep product details from Google's immersive product page.

        Args:
            product_id: Google Shopping product ID.
            gl: Country code.
            hl: Language code.
        """
        params: dict[str, Any] = {"product_id": product_id, "gl": gl, "hl": hl}
        return await self._client.get("/v1/google/products/detail", params=params)
