# Lab 20: Multi-Agent Research System

This project implements a LangGraph-based multi-agent research assistant with a shared Pydantic state.

## Architecture

```text
User Query
  |
  v
Supervisor
  |-- Researcher -> sources, research_notes
  |-- Analyst ----> analysis_notes
  |-- Writer -----> final_answer
  v
done
```

The default workflow uses four core agents:

| Agent | Role |
|---|---|
| Supervisor | Routes the workflow based on missing state fields and max-iteration guardrail |
| Researcher | Searches for sources and creates research notes |
| Analyst | Converts research notes into structured analysis |
| Writer | Produces the final Markdown answer |

An optional `CriticAgent` is implemented for review, but it is not part of the default graph.

## Implemented Features

- OpenAI-compatible `LLMClient` with retry, timeout, token metadata, and safe fallback.
- Tavily-backed `SearchClient` with local fallback when no search key is configured.
- Rule-based supervisor routing.
- LangGraph `StateGraph` workflow with conditional edges.
- Agent result metadata and trace events in shared state.
- Benchmark helpers for latency, estimated cost, heuristic quality, and run notes.
- Provider-neutral tracing helper.
- Unit tests for routing, service fallbacks, state, report rendering, and workflow fallback.

## Environment

Create `.env` from `.env.example` and configure the keys you want to use.

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=

TAVILY_API_KEY=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=multi-agent-research-lab
```

Notes:

- `OPENAI_BASE_URL` is optional and can point to OpenAI-compatible providers such as DeepSeek.
- Without `OPENAI_API_KEY`, the LLM client returns a safe fallback message.
- Without `TAVILY_API_KEY`, search uses local fallback context.

## Commands To Run

Run these after dependencies and `.env` are configured.

```powershell
python -m compileall -q src tests
python -m pytest -q
python -m multi_agent_research_lab.cli baseline --query "Research LangGraph multi-agent workflow"
python -m multi_agent_research_lab.cli multi-agent --query "Research LangGraph multi-agent workflow and summarize it"
```

## Project Structure

```text
src/multi_agent_research_lab/
  agents/
  core/
  graph/
  services/
  evaluation/
  observability/
  cli.py
docs/
reports/
tests/
```

## Deliverables

- Source code for the multi-agent system.
- Design explanation in `docs/design_template.md`.
- Lab guide in `docs/lab_guide.md`.
- Benchmark report draft in `reports/benchmark_report.md`.
- Failure mode analysis in `reports/failure_modes.md`.

The benchmark report should be updated with real metrics after running the project with configured API keys.
