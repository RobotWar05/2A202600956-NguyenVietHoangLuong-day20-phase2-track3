"""Benchmark helpers for single-agent vs multi-agent runs."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency, estimated cost, simple quality, and run notes."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started

    estimated_cost = 0.0
    has_cost = False
    for result in state.agent_results:
        cost = result.metadata.get("cost_usd")
        if isinstance(cost, int | float):
            estimated_cost += float(cost)
            has_cost = True

    quality_score = _estimate_quality(state)
    notes = (
        f"sources={len(state.sources)}, "
        f"errors={len(state.errors)}, "
        f"answer_chars={len(state.final_answer or '')}"
    )
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=estimated_cost if has_cost else None,
        quality_score=quality_score,
        notes=notes,
    )
    return state, metrics


def _estimate_quality(state: ResearchState) -> float:
    score = 0.0
    if state.research_notes:
        score += 2.0
    if state.analysis_notes:
        score += 2.0
    if state.final_answer:
        score += 3.0
    if state.sources:
        score += 1.5
    if state.final_answer and len(state.final_answer) >= 500:
        score += 1.0
    if not state.errors:
        score += 0.5
    return min(score, 10.0)
