"""Supervisor / router."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route.

        Routes:
        - researcher: no research notes yet
        - analyst: research exists but analysis is missing
        - writer: analysis exists but final answer is missing
        - done: final answer exists or max iteration guardrail is reached
        """

        settings = get_settings()

        if state.iteration >= settings.max_iterations:
            next_route = "done"
            reason = "max_iterations_reached"
        elif not state.research_notes:
            next_route = "researcher"
            reason = "missing_research_notes"
        elif not state.analysis_notes:
            next_route = "analyst"
            reason = "missing_analysis_notes"
        elif not state.final_answer:
            next_route = "writer"
            reason = "missing_final_answer"
        else:
            next_route = "done"
            reason = "final_answer_ready"

        state.record_route(next_route)
        state.add_trace_event(
            "supervisor",
            {
                "decision": next_route,
                "reason": reason,
                "iteration": state.iteration,
            },
        )
        logger.info("Supervisor route=%s reason=%s", next_route, reason)
        return state
