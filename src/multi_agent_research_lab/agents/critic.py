"""Optional critic agent for answer quality review."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a strict reviewer.
Evaluate the final answer against the research and analysis notes.
Return:
SCORE: X/10
STRENGTHS:
RISKS:
FIXES:
Do not invent evidence."""


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self) -> None:
        self._llm = LLMClient(temperature=0.0)

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings.

        This agent is optional and is not wired into the default 4-agent graph.
        """

        try:
            user_prompt = (
                f"Query:\n{state.request.query}\n\n"
                f"Research notes:\n{state.research_notes or '(missing)'}\n\n"
                f"Analysis notes:\n{state.analysis_notes or '(missing)'}\n\n"
                f"Final answer:\n{state.final_answer or '(missing)'}"
            )
            response = self._llm.complete(_SYSTEM_PROMPT, user_prompt)
            if response.error:
                state.errors.append(f"Critic LLM fallback: {response.error}")
            state.critic_review = response.content
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.CRITIC,
                    content=response.content,
                    metadata={
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "cost_usd": response.cost_usd,
                        "llm_error": response.error,
                    },
                )
            )
            state.add_trace_event("critic", {"review_length": len(response.content)})
        except Exception as exc:
            logger.exception("Critic failed")
            state.errors.append(f"Critic failed safely: {exc}")
            state.critic_review = "Critic review unavailable."
            state.add_trace_event("critic", {"error": str(exc)})

        return state
