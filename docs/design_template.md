# Design: Multi-Agent Research System

## Problem

Hệ thống cần nhận một câu hỏi nghiên cứu, thu thập ngữ cảnh liên quan, phân tích thông tin, rồi viết câu trả lời cuối cùng có cấu trúc rõ ràng. Mục tiêu không chỉ là trả lời nhanh, mà còn phải tách rõ từng bước để dễ kiểm soát chất lượng, debug và benchmark.

## Why Multi-Agent?

Single-agent phù hợp cho câu hỏi ngắn, nhưng dễ trộn lẫn các nhiệm vụ: tìm kiếm, phân tích, viết và tự kiểm soát chất lượng. Với bài toán research, cách tách multi-agent giúp:

- `Researcher` tập trung thu thập nguồn và ghi chú.
- `Analyst` tập trung đánh giá bằng chứng, mâu thuẫn và insight.
- `Writer` tập trung trình bày câu trả lời cuối.
- `Supervisor` kiểm soát luồng, tránh chạy vô hạn và quyết định khi nào kết thúc.

## Agent Roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Định tuyến bước tiếp theo theo state hiện tại | `ResearchState` | route: `researcher`, `analyst`, `writer`, `done` | Sai route hoặc vượt vòng lặp |
| Researcher | Tìm nguồn và tạo `research_notes` | query, `max_sources` | `sources`, `research_notes` | Search/LLM lỗi hoặc không có nguồn |
| Analyst | Phân tích ghi chú nghiên cứu | `research_notes`, `sources` | `analysis_notes` | Bằng chứng yếu, LLM trả rỗng |
| Writer | Viết câu trả lời cuối | query, `analysis_notes`, sources | `final_answer` | Câu trả lời thiếu citation hoặc LLM trả rỗng |
| Critic | Optional review chất lượng | final answer, notes | `critic_review` | Chưa wire vào default graph |

## Shared State

| Field | Purpose |
|---|---|
| `request` | Câu hỏi gốc, số nguồn tối đa, audience |
| `iteration` | Guardrail chống loop vô hạn |
| `route_history` | Trace route để debug workflow |
| `sources` | Danh sách nguồn tìm được hoặc fallback context |
| `research_notes` | Output của Researcher |
| `analysis_notes` | Output của Analyst |
| `final_answer` | Output cuối của Writer |
| `critic_review` | Review optional nếu bật Critic |
| `agent_results` | Metadata từng agent, token/cost nếu có |
| `trace` | Event-level trace |
| `errors` | Lỗi an toàn, không crash ngang |

## Routing Policy

```text
Supervisor
  |-- missing research_notes --> Researcher --> Supervisor
  |-- missing analysis_notes --> Analyst ----> Supervisor
  |-- missing final_answer ---> Writer ------> Supervisor
  |-- final answer exists ----> done
  |-- max_iterations reached -> done
```

## Guardrails

- Max iterations: `MAX_ITERATIONS`, mặc định 6.
- Timeout: `TIMEOUT_SECONDS`, dùng cho API timeout và manual fallback loop.
- Retry: `LLMClient` retry 3 lần với exponential backoff.
- Fallback:
  - Thiếu `OPENAI_API_KEY`: trả `LLMResponse` an toàn.
  - Thiếu `TAVILY_API_KEY`: dùng local fallback source.
  - LLM trả rỗng: agent tạo nội dung fallback non-empty và ghi `state.errors`.
- Validation: input/output chính đi qua Pydantic schema.

## Benchmark Plan

| Query | Metric | Expected outcome |
|---|---|---|
| "Research LangGraph multi-agent workflow and summarize it" | latency, cost, quality, errors | Multi-agent có trace rõ hơn baseline |
| "Compare single-agent and multi-agent research assistants" | citation coverage, final answer quality | Multi-agent phân tích có cấu trúc hơn |
| "Explain failure modes of LLM research agents" | failure rate, error notes | Workflow ghi lỗi vào state thay vì crash |

Benchmark thật cần người dùng tự chạy sau khi cấu hình `.env`, vì kết quả phụ thuộc API key, model, network và search provider.
