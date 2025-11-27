"""Google search provider (scraping and API)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from ..utils import to_toon
from .base import BaseProvider, ProviderMetadata, ProviderResult


@dataclass
class SearchResult:
    """Google search result."""

    title: str
    url: str
    snippet: str

    def as_dict(self) -> Dict[str, str]:
        return {"title": self.title, "url": self.url, "snippet": self.snippet}


class GoogleProvider(BaseProvider):
    """Provider for Google search (HTML scraping and Custom Search API)."""

    def get_metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="google",
            description="Google search (scraping and API fallback)",
            expose_as_tool=True,
            tool_names=["google_search"],
            supports_library_search=True,
            required_env_vars=[],
            optional_env_vars=["GOOGLE_API_KEY", "GOOGLE_CSE_ID"],
        )

    async def search_library(self, library: str, limit: int = 5) -> ProviderResult:
        """Search Google for library documentation (used by aggregator)."""
        try:
            results = await self._search_google(
                f"{library} python documentation", limit=limit
            )
            data = [r.as_dict() for r in results]
            return ProviderResult(success=True, data=data, provider_name="google")
        except httpx.HTTPStatusError as exc:
            error_msg = f"Google returned {exc.response.status_code}"
            return ProviderResult(success=False, error=error_msg, provider_name="google")
        except httpx.HTTPError as exc:
            error_msg = f"Google request failed: {exc}"
            return ProviderResult(success=False, error=error_msg, provider_name="google")
        except Exception as exc:
            error_msg = f"Google parsing failed: {exc}"
            return ProviderResult(success=False, error=error_msg, provider_name="google")

    async def _search_google(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Scrape Google search result cards. Lightweight and dependency-free."""
        async with await self._http_client() as client:
            resp = await client.get("https://www.google.com/search", params={"q": query})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

        results: List[SearchResult] = []
        for block in soup.select("div.g"):
            anchor = block.find("a")
            if not anchor or not anchor.get("href"):
                continue
            title = anchor.get_text(" ", strip=True)
            snippet = block.get_text(" ", strip=True)
            results.append(SearchResult(title=title, url=anchor["href"], snippet=snippet))
            if len(results) >= limit:
                break

        return results

    async def _search_google_custom(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Use Google Custom Search JSON API when API key + CSE ID are provided."""
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")

        if not api_key or not cse_id:
            raise RuntimeError("Google API key or CSE ID missing")

        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": str(min(limit, 10)),
        }
        async with await self._http_client() as client:
            resp = await client.get(
                "https://www.googleapis.com/customsearch/v1", params=params
            )
            resp.raise_for_status()
            payload = resp.json()

        hits: List[SearchResult] = []
        for item in payload.get("items", []):
            hits.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                )
            )
            if len(hits) >= limit:
                break
        return hits

    def get_tools(self) -> Dict[str, Callable]:
        """Return MCP tool functions."""

        async def google_search(query: str, limit: int = 5, use_api: bool = False) -> str:
            """Run a Google search and return result cards. Supports API (GOOGLE_API_KEY/GOOGLE_CSE_ID) or HTML scrape fallback. Returns data in TOON format."""
            hits: List[SearchResult] = []
            api_error: Optional[str] = None

            if use_api:
                try:
                    hits = await self._search_google_custom(query, limit=limit)
                except Exception as exc:
                    api_error = str(exc)

            if not hits:
                hits = await self._search_google(query, limit=limit)
                if api_error:
                    # Surface API failure in the first result snippet for observability
                    hits.append(
                        SearchResult(title="google-api-error", url="", snippet=api_error)
                    )

            result = [hit.as_dict() for hit in hits]
            return to_toon(result)

        return {"google_search": google_search}
