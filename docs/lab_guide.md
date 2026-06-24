# Lab Guide: Multi-Agent Research System

## Scenario

Repo này triển khai một research assistant gồm `Supervisor`, `Researcher`, `Analyst`, `Writer` và một `Critic` optional. Hệ thống nhận câu hỏi nghiên cứu, thu thập nguồn hoặc fallback context, phân tích thông tin, rồi viết câu trả lời cuối cùng.

## Architecture

```text
User Query
  |
  v
Supervisor
  |-- Researcher -> research_notes, sources
  |-- Analyst ----> analysis_notes
  |-- Writer -----> final_answer
  v
done
```

## Milestone 1: Baseline

Implemented files:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

Result:

- Baseline command calls `LLMClient`.
- `LLMClient` supports OpenAI-compatible providers through `OPENAI_API_KEY`, `OPENAI_MODEL`, and optional `OPENAI_BASE_URL`.
- Missing API key returns a safe message instead of crashing.

## Milestone 2: Supervisor

Implemented files:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

Routing policy:

- No `research_notes` -> `researcher`.
- Has research but no `analysis_notes` -> `analyst`.
- Has analysis but no `final_answer` -> `writer`.
- Has final answer -> `done`.
- Reaches `MAX_ITERATIONS` -> `done`.

## Milestone 3: Worker Agents

Implemented files:

- `src/multi_agent_research_lab/agents/researcher.py`
- `src/multi_agent_research_lab/agents/analyst.py`
- `src/multi_agent_research_lab/agents/writer.py`
- `src/multi_agent_research_lab/agents/critic.py`

Behavior:

- `Researcher` uses `SearchClient`, saves `sources`, and writes `research_notes`.
- `Analyst` reads `research_notes` and writes `analysis_notes`.
- `Writer` reads `analysis_notes` and writes `final_answer`.
- `Critic` can review the final answer but is not wired into the default graph.

## Milestone 4: Trace and Benchmark

Implemented files:

- `src/multi_agent_research_lab/observability/tracing.py`
- `src/multi_agent_research_lab/evaluation/benchmark.py`
- `src/multi_agent_research_lab/evaluation/report.py`

Minimum metrics:

| Metric | Implementation |
|---|---|
| Latency | Wall-clock timing in `run_benchmark` |
| Cost | Sum of `cost_usd` metadata from agent results when available |
| Quality | Heuristic score based on completed state fields, sources, answer length, errors |
| Citation coverage | Supported by source references in prompts; real scoring should be reviewed manually |
| Failure rate | Derived from `state.errors` across benchmark runs |

## Commands For User To Run

Do not run these until dependencies and `.env` are configured.

```powershell
python -m compileall -q src tests
python -m pytest -q
python -m multi_agent_research_lab.cli multi-agent --query "Research LangGraph multi-agent workflow and summarize it"
```

## Exit Ticket

1. Multi-agent is useful when the task has separable stages, needs traceability, and benefits from role-specific prompts.
2. Multi-agent is not useful for short, low-risk questions where extra routing increases latency and complexity without improving quality.
