from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routes_to_researcher_first() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    result = SupervisorAgent().run(state)
    assert result.route_history == ["researcher"]
    assert result.iteration == 1


def test_supervisor_routes_by_missing_state_fields() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        research_notes="research done",
    )
    result = SupervisorAgent().run(state)
    assert result.route_history == ["analyst"]

    result.analysis_notes = "analysis done"
    result = SupervisorAgent().run(result)
    assert result.route_history[-1] == "writer"

    result.final_answer = "final answer done"
    result = SupervisorAgent().run(result)
    assert result.route_history[-1] == "done"
