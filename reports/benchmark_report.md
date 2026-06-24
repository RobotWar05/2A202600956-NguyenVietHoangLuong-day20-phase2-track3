# Benchmark Report

## Scope

This report documents the planned comparison between:

- Single-agent baseline: one LLM call from the CLI baseline command.
- Multi-agent workflow: Supervisor, Researcher, Analyst, Writer coordinated by LangGraph.

## Current Implementation Status

| Area | Status |
|---|---|
| Baseline command | Implemented |
| Multi-agent workflow | Implemented |
| Latency measurement | Implemented in `evaluation/benchmark.py` |
| Cost estimate | Implemented when LLM token metadata is available |
| Heuristic quality score | Implemented |
| Trace events | Implemented in `ResearchState.trace` |
| Real API benchmark run | Pending user-run with configured `.env` |

## Metrics

| Metric | How It Is Measured |
|---|---|
| Latency | Wall-clock runtime in seconds |
| Estimated cost | Sum of per-agent `cost_usd` metadata |
| Quality score | Heuristic score based on completed fields, sources, answer length, and errors |
| Error count | Number of entries in `state.errors` |
| Source count | Number of `SourceDocument` entries |

## Commands To Run

Run these after installing dependencies and configuring `.env`.

```powershell
python -m compileall -q src tests
python -m pytest -q
python -m multi_agent_research_lab.cli baseline --query "Research LangGraph multi-agent workflow"
python -m multi_agent_research_lab.cli multi-agent --query "Research LangGraph multi-agent workflow and summarize it"
```

## Result Table

Fill this table after running with real API keys.

| Run | Latency (s) | Estimated Cost (USD) | Quality | Sources | Errors | Notes |
|---|---:|---:|---:|---:|---:|---|
| baseline | Pending | Pending | Pending | Pending | Pending | Requires user-run |
| multi-agent | Pending | Pending | Pending | Pending | Pending | Requires user-run |

## Expected Interpretation

The multi-agent workflow is expected to have higher latency than the baseline because it performs multiple agent steps. The benefit should be better traceability, clearer intermediate artifacts, and easier failure diagnosis.

Do not claim quality improvement until real outputs are reviewed.
