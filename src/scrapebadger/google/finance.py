"""Google Finance client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class FinanceClient:
    """Client for Google Finance quotes.

    Example:
        ```python
        quote = await client.google.finance.quote("AAPL:NASDAQ")
        print(quote["price"], quote["currency"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def quote(
        self,
        q: str,
        *,
        hl: str = "en",
    ) -> dict[str, Any]:
        """Get a stock/index/crypto quote.

        Args:
            q: Ticker and exchange (e.g. "AAPL:NASDAQ", "BTC-USD", ".DJI:INDEXDJX").
            hl: Language code.
        """
        params: dict[str, Any] = {"q": q, "hl": hl}
        return await self._client.get("/v1/google/finance/quote", params=params)
