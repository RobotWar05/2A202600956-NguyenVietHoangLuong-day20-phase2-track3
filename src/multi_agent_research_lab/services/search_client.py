"""Search client abstraction for ResearcherAgent."""

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument

logger = logging.getLogger(__name__)


class SearchClient:
    """Provider-agnostic search client with Tavily and local fallback support."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.

        Uses Tavily when configured. If no search provider is available, returns
        a safe local context document so the workflow can continue.
        """

        settings = get_settings()
        max_results = max(1, min(max_results, 20))
        if settings.tavily_api_key:
            try:
                return self._search_tavily(query, max_results, settings.tavily_api_key)
            except Exception as exc:
                logger.warning("Tavily search failed, falling back to local context: %s", exc)

        return [
            SourceDocument(
                title="Local fallback context",
                url=None,
                snippet=(
                    "No external search provider is configured or reachable. "
                    f"Use the user query as the primary research context: {query}"
                ),
                metadata={"provider": "local_fallback"},
            )
        ]

    @staticmethod
    def _search_tavily(query: str, max_results: int, api_key: str) -> list[SourceDocument]:
        payload = json.dumps(
            {
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
                "include_answer": False,
            }
        ).encode("utf-8")
        request = Request(
            "https://api.tavily.com/search",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=get_settings().timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"search provider error: {exc}") from exc

        documents: list[SourceDocument] = []
        for item in data.get("results", [])[:max_results]:
            documents.append(
                SourceDocument(
                    title=item.get("title") or "Untitled source",
                    url=item.get("url"),
                    snippet=item.get("content") or item.get("snippet") or "",
                    metadata={"provider": "tavily", "score": item.get("score")},
                )
            )
        return documents
