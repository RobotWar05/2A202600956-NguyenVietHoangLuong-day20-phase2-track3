from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


def test_llm_client_returns_safe_message_without_api_key(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()

    response = LLMClient().complete("system", "user")

    assert response.content
    assert response.error == "missing_openai_api_key"
    assert "OPENAI_API_KEY" in response.content


def test_search_client_returns_local_fallback_without_tavily_key(monkeypatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "")
    get_settings.cache_clear()

    results = SearchClient().search("Explain multi-agent systems", max_results=0)

    assert len(results) == 1
    assert results[0].metadata["provider"] == "local_fallback"
