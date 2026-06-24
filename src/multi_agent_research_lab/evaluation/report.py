"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""

    lines = [
        "# Benchmark Report",
        "",
        "## Summary",
        "",
        "This report compares research-system runs by latency, estimated API cost, "
        "heuristic quality score, and execution notes.",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        lines.append(f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | {item.notes} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Latency shows runtime cost.",
            "- Cost is estimated from available agent token metadata.",
            "- Quality is a lightweight heuristic, not a human evaluation.",
            "- Notes should be inspected together with trace events for failure analysis.",
        ]
    )
    return "\n".join(lines) + "\n"
