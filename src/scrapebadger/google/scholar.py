"""Google Scholar client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


class ScholarClient:
    """Client for Google Scholar search.

    Example:
        ```python
        papers = await client.google.scholar.search(
            "transformer neural networks",
            as_ylo=2020,
            as_yhi=2024,
        )
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        q: str,
        *,
        hl: str = "en",
        as_ylo: int | None = None,
        as_yhi: int | None = None,
        as_sdt: str = "0",
        page: int = 0,
        num: int = 10,
    ) -> dict[str, Any]:
        """Search Google Scholar for scholarly articles.

        Args:
            q: Search query.
            hl: Language code.
            as_ylo: Year lower bound (e.g. 2020).
            as_yhi: Year upper bound (e.g. 2024).
            as_sdt: Search type — "0" excludes patents, "7" includes them.
            page: Page number (0-based).
            num: Results per page (1-20).
        """
        params: dict[str, Any] = {
            "q": q,
            "hl": hl,
            "as_sdt": as_sdt,
            "page": page,
            "num": num,
        }
        if as_ylo is not None:
            params["as_ylo"] = as_ylo
        if as_yhi is not None:
            params["as_yhi"] = as_yhi
        return await self._client.get("/v1/google/scholar/search", params=params)

    async def profiles(
        self,
        mauthors: str,
        *,
        hl: str = "en",
        after_author: str | None = None,
        before_author: str | None = None,
    ) -> dict[str, Any]:
        """Search Google Scholar for author profiles by name.

        Args:
            mauthors: Author name query (e.g. "Geoffrey Hinton").
            hl: Language code.
            after_author: Next-page pagination token from a previous response.
            before_author: Previous-page pagination token.
        """
        params: dict[str, Any] = {"mauthors": mauthors, "hl": hl}
        if after_author is not None:
            params["after_author"] = after_author
        if before_author is not None:
            params["before_author"] = before_author
        return await self._client.get("/v1/google/scholar/profiles", params=params)

    async def author(
        self,
        author_id: str,
        *,
        hl: str = "en",
        cstart: int = 0,
        pagesize: int = 20,
    ) -> dict[str, Any]:
        """Get a full Google Scholar author profile.

        Returns profile info (name, affiliations, interests), articles list,
        citation stats (all / since-year), h-index, i10-index, and co-authors.

        Args:
            author_id: Scholar user ID (the `user` query parameter).
            hl: Language code.
            cstart: Articles pagination offset.
            pagesize: Articles per page.
        """
        params: dict[str, Any] = {
            "author_id": author_id,
            "hl": hl,
            "cstart": cstart,
            "pagesize": pagesize,
        }
        return await self._client.get("/v1/google/scholar/author", params=params)

    async def author_citation(
        self,
        author_id: str,
        *,
        hl: str = "en",
    ) -> dict[str, Any]:
        """Return the citations-per-year chart for a Scholar author.

        Args:
            author_id: Scholar user ID.
            hl: Language code.
        """
        params: dict[str, Any] = {"author_id": author_id, "hl": hl}
        return await self._client.get("/v1/google/scholar/author/citation", params=params)

    async def cite(
        self,
        q: str,
        *,
        hl: str = "en",
    ) -> dict[str, Any]:
        """Return MLA, APA, Chicago, Harvard, and Vancouver citation formats.

        Also returns export links (BibTeX, RIS, EndNote, RefWorks) from
        Scholar's cite dialog.

        Args:
            q: Cluster ID from a Scholar search result.
            hl: Language code.
        """
        params: dict[str, Any] = {"q": q, "hl": hl}
        return await self._client.get("/v1/google/scholar/cite", params=params)
