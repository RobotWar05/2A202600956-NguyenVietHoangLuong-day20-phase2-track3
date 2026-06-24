"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

import logging
from dataclasses import dataclass

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from multi_agent_research_lab.core.config import get_settings

logger = logging.getLogger(__name__)

_COST_PER_1M_INPUT = 0.15
_COST_PER_1M_OUTPUT = 0.60


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None
    error: str | None = None


class LLMClient:
    """Provider-agnostic LLM client for OpenAI-compatible chat models."""

    def __init__(self, model: str | None = None, temperature: float = 0.2) -> None:
        settings = get_settings()
        self._model = model or settings.openai_model
        self._temperature = temperature

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        Keep retry, timeout, and token logging here rather than inside agents.
        """

        settings = get_settings()
        if not settings.openai_api_key:
            return LLMResponse(
                content=(
                    "LLM unavailable: OPENAI_API_KEY is not configured. "
                    "Please configure the runtime environment before calling the LLM."
                ),
                error="missing_openai_api_key",
            )

        try:
            return self._complete_with_openai(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                model=self._model,
                temperature=self._temperature,
                timeout_seconds=settings.timeout_seconds,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        except ImportError:
            return LLMResponse(
                content=(
                    "LLM unavailable: the optional `openai` package is not installed. "
                    "Install the project's LLM dependencies before using this client."
                ),
                error="missing_openai_package",
            )
        except Exception as exc:
            return LLMResponse(content=f"LLM request failed safely: {exc}", error=str(exc))

    @staticmethod
    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _complete_with_openai(
        api_key: str,
        base_url: str | None,
        model: str,
        temperature: float,
        timeout_seconds: int,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:
        """Call an OpenAI-compatible chat completion endpoint."""

        from openai import OpenAI

        client_kwargs: dict[str, object] = {"api_key": api_key, "timeout": timeout_seconds}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = OpenAI(**client_kwargs)
        logger.info("LLM call: model=%s, temperature=%.2f", model, temperature)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

        message = completion.choices[0].message
        usage = completion.usage
        input_tokens = usage.prompt_tokens if usage else None
        output_tokens = usage.completion_tokens if usage else None
        cost_usd = None
        if input_tokens is not None and output_tokens is not None:
            cost_usd = (
                input_tokens * _COST_PER_1M_INPUT / 1_000_000
                + output_tokens * _COST_PER_1M_OUTPUT / 1_000_000
            )

        return LLMResponse(
            content=message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )
