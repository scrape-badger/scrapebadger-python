"""Google Finance client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class FinanceClient:
    """Client for Google Finance quotes.

    Powered by the same ``mKsvE`` batchexecute RPC the Google Finance
    SPA uses internally. Returns price / change / change% /
    previous_close / after-hours / market hours / timezone /
    currency / country / alternate exchange listings in ~1 s.

    Example:
        ```python
        quote = await client.google.finance.quote("AAPL:NASDAQ")
        print(quote["price"], quote["currency"], quote["after_hours"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def quote(
        self,
        q: str,
        *,
        hl: str = "en",
        gl: str = "us",
    ) -> dict[str, Any]:
        """Get a stock, index, crypto, or forex quote.

        Args:
            q: Ticker, optionally with exchange (``"AAPL"``,
                ``"AAPL:NASDAQ"``, ``"BTC-USD"``, ``"EURUSD"``).
                Bare tickers auto-route to the primary exchange;
                alternate listings ride along under ``other_exchanges``.
            hl: Language code (e.g. ``"en"``).
            gl: Country code (e.g. ``"us"``).
        """
        params: dict[str, Any] = {"q": q, "hl": hl, "gl": gl}
        return await self._client.get("/v1/google/finance/quote", params=params)
