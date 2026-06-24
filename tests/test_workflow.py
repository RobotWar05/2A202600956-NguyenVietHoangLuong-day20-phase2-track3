from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow


def test_workflow_completes_with_safe_fallbacks(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("TAVILY_API_KEY", "")
    get_settings.cache_clear()

    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems for technical learners")
    )
    result = MultiAgentWorkflow().run(state)

    assert result.route_history == ["researcher", "analyst", "writer", "done"]
    assert result.research_notes
    assert result.analysis_notes
    assert result.final_answer
