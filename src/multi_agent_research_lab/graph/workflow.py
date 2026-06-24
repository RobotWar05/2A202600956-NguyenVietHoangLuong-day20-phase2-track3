"""LangGraph workflow."""

import logging
from time import perf_counter

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        self._supervisor = SupervisorAgent()
        self._researcher = ResearcherAgent()
        self._analyst = AnalystAgent()
        self._writer = WriterAgent()

    @staticmethod
    def _route_from_supervisor(state: ResearchState) -> str:
        return state.route_history[-1] if state.route_history else "done"

    def build(self) -> object:
        """Create a LangGraph graph.

        Nodes:
        - supervisor: rule-based router
        - researcher: search + research notes
        - analyst: structured analysis
        - writer: final answer
        """

        try:
            from langgraph.graph import END, StateGraph
        except ImportError as exc:
            raise RuntimeError(
                "LangGraph is not installed. Install the optional LLM dependencies "
                "to run the compiled graph."
            ) from exc

        builder = StateGraph(ResearchState)
        builder.add_node("supervisor", self._supervisor.run)
        builder.add_node("researcher", self._researcher.run)
        builder.add_node("analyst", self._analyst.run)
        builder.add_node("writer", self._writer.run)

        builder.set_entry_point("supervisor")
        builder.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "done": END,
            },
        )
        builder.add_edge("researcher", "supervisor")
        builder.add_edge("analyst", "supervisor")
        builder.add_edge("writer", "supervisor")

        return builder.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state.

        If LangGraph is unavailable in the local environment, a manual loop is used
        as a safe fallback so the state machine can still be exercised.
        """

        started = perf_counter()
        settings = get_settings()
        try:
            app = self.build()
        except RuntimeError as exc:
            logger.warning("Falling back to manual workflow runner: %s", exc)
            final_state = self._run_manual(state)
        else:
            try:
                result = app.invoke(
                    state,
                    {"recursion_limit": max(settings.max_iterations * 3, 10)},
                )
                final_state = (
                    result if isinstance(result, ResearchState) else ResearchState(**result)
                )
            except Exception as exc:
                logger.exception("Workflow failed")
                state.errors.append(f"Workflow failed safely: {exc}")
                final_state = state

        final_state.add_trace_event(
            "workflow",
            {"event": "complete", "total_seconds": perf_counter() - started},
        )
        return final_state

    def _run_manual(self, state: ResearchState) -> ResearchState:
        settings = get_settings()
        workers = {
            "researcher": self._researcher.run,
            "analyst": self._analyst.run,
            "writer": self._writer.run,
        }

        started = perf_counter()
        while state.iteration < settings.max_iterations:
            state = self._supervisor.run(state)
            route = self._route_from_supervisor(state)
            if route == "done":
                break

            worker = workers.get(route)
            if worker is None:
                state.errors.append(f"Unknown route from supervisor: {route}")
                break

            state = worker(state)
            if perf_counter() - started > settings.timeout_seconds:
                state.errors.append(f"Workflow timeout after {settings.timeout_seconds}s")
                state.add_trace_event("workflow", {"event": "timeout"})
                break

        if not state.route_history or state.route_history[-1] != "done":
            state = self._supervisor.run(state)

        return state
