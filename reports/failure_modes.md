# Failure Mode Analysis

## 1. Missing LLM API Key

Failure:

- `OPENAI_API_KEY` is missing or empty.

Handling:

- `LLMClient.complete()` returns a safe `LLMResponse` explaining that the key is not configured.
- The workflow continues instead of crashing.

Fix:

- Configure `OPENAI_API_KEY`.
- Configure `OPENAI_MODEL`.
- Configure `OPENAI_BASE_URL` only when using an OpenAI-compatible provider that is not the default OpenAI endpoint.

## 2. Missing Search API Key

Failure:

- `TAVILY_API_KEY` is missing or empty.

Handling:

- `SearchClient.search()` returns one local fallback `SourceDocument`.
- The Researcher can still produce research notes from the query context.

Fix:

- Configure `TAVILY_API_KEY` for real web search.

## 3. LLM Returns Empty Content

Failure:

- Provider returns an empty message.

Handling:

- Researcher, Analyst, and Writer each create a non-empty fallback output.
- The agent appends a clear error message to `state.errors`.
- This prevents Supervisor from routing the same step repeatedly until `MAX_ITERATIONS`.

Fix:

- Inspect provider response and prompt.
- Lower prompt complexity.
- Check model availability.

## 4. Workflow Loop Risk

Failure:

- A required state field stays empty, causing repeated routing.

Handling:

- `SupervisorAgent` enforces `MAX_ITERATIONS`.
- Worker agents now guard against empty LLM output.

Fix:

- Inspect `route_history`, `trace`, and `errors`.

## 5. LangGraph Not Installed

Failure:

- Optional LangGraph dependency is unavailable.

Handling:

- `MultiAgentWorkflow.run()` falls back to a manual loop for local smoke checks.

Fix:

- Install the project optional LLM dependencies before the final real run.

## 6. Benchmark Without Real API Run

Failure:

- Benchmark report has no real latency/cost/quality values.

Handling:

- `reports/benchmark_report.md` is provided as a truth-preserving template.

Fix:

- Run the benchmark commands after `.env` is configured.
- Paste real numbers into the report table.
