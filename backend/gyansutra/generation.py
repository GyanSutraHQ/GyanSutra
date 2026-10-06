"""LangChain chat chains with application-owned provider and capacity budgets."""

import asyncio
import hashlib
import os
import time
from collections import OrderedDict

import httpx
import regex as re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from .cache import CapacityBudget, ServiceError
from .config import integer, names
from .text import modernize

ENDPOINTS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "grok": "https://api.x.ai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}


def clean_response(raw) -> str:
    text = str(raw or "").strip()
    text = re.sub(r"<(thinking|think|reasoning)>[\s\S]*?</\1>", "", text, flags=re.I)
    text = re.sub(r"^User Safety:\s*safe\s*|^Assistant:\s*", "", text, flags=re.I).strip()
    teaching = re.search(r"(?:^|\n)(?:###\s*)?(?:📖\s*)?(?:The Teaching|शिक्षा)", text, re.I)
    if teaching and teaching.start() > 0:
        text = text[teaching.start() :].strip()
    return modernize(re.sub(r"[\p{Extended_Pictographic}\uFE0F]", "", text).strip())


class CompatibleChatModel(ChatOpenAI):
    """Keep max_tokens on the providers' compatible Chat Completions endpoint."""

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        if "max_completion_tokens" in payload:
            payload["max_tokens"] = payload.pop("max_completion_tokens")
        return payload


class GenerationService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http = http_client
        self.sync_http = httpx.Client()
        self.model_timeout = integer("RAG_MODEL_TIMEOUT_MS", 10000, 1000, 30000) / 1000
        self.deadline = integer("RAG_GENERATION_DEADLINE_MS", 24000, 2000, 45000) / 1000
        self.maximum_attempts = integer("RAG_MAX_MODEL_ATTEMPTS", 3, 1, 3)
        self.queue_timeout = integer("RAG_MODEL_QUEUE_TIMEOUT_MS", 10000, 0, 30000) / 1000
        self.output_tokens = integer("RAG_MAX_OUTPUT_TOKENS", 1200, 256, 2000)
        self.budget = CapacityBudget(
            integer("RAG_MAX_CONCURRENT_GENERATIONS", 4, 1, 20),
            integer("RAG_MAX_QUEUED_GENERATIONS", 24, 0, 200),
            self.queue_timeout,
            "RAG_BUSY",
        )
        self.capacity = self.budget.semaphore
        self.effort = os.getenv("GEMINI_REASONING_EFFORT", "low")
        if self.effort not in {"low", "medium", "high"}:
            self.effort = "low"
        self.order = [
            p
            for p in names("RAG_PROVIDER_ORDER", ["gemini", "grok", "openrouter"])
            if p in ENDPOINTS
        ]
        self.models = {
            "gemini": names(
                "GEMINI_GENERATION_MODELS", ["gemini-3.8-flash", "gemini-3.1-flash-lite"]
            ),
            "grok": names("GROK_MODELS", ["grok-4.7"]),
            "openrouter": names("OPENROUTER_MODELS", ["openrouter/free"]),
        }
        self.circuits: dict[str, tuple[int, float]] = {}
        self.chains = OrderedDict()

    def attempts(self) -> list[dict]:
        legacy = os.getenv("GEMINI_API_KEY", "")
        keys = {
            "gemini": "" if legacy.startswith("sk-or-") else legacy,
            "grok": os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY", ""),
            "openrouter": os.getenv("OPENROUTER_API_KEY")
            or (legacy if legacy.startswith("sk-or-") else ""),
        }
        attempts = []
        for index in range(max((len(self.models[p]) for p in self.order), default=0)):
            for provider in self.order:
                if keys[provider] and index < len(self.models[provider]):
                    attempts.append(
                        {
                            "provider": provider,
                            "model": self.models[provider][index],
                            "apiKey": keys[provider],
                        }
                    )
                if len(attempts) >= self.maximum_attempts:
                    return attempts
        return attempts

    def chain(self, attempt: dict, tokens: int):
        provider = attempt["provider"]
        key = (
            provider,
            attempt["model"],
            hashlib.sha256(attempt["apiKey"].encode()).hexdigest(),
            tokens,
        )
        if key not in self.chains:
            options = dict(
                model=attempt["model"],
                api_key=attempt["apiKey"],
                base_url=ENDPOINTS[provider],
                max_retries=0,
                timeout=self.model_timeout,
                max_tokens=tokens,
                use_responses_api=False,
                http_async_client=self.http,
                http_client=self.sync_http,
                streaming=False,
                stream_usage=False,
            )
            if provider == "gemini":
                options.update(temperature=None, reasoning_effort=self.effort)
            else:
                options.update(temperature=0.1)
            if provider == "openrouter":
                options["default_headers"] = {
                    "HTTP-Referer": "https://gyansutraapp.pages.dev/",
                    "X-Title": "Gyan Sutra",
                }
            model = CompatibleChatModel(**options)
            self.chains[key] = (
                ChatPromptTemplate.from_messages([MessagesPlaceholder("messages")]) | model
            )
            if len(self.chains) > 100:
                self.chains.popitem(last=False)
        return self.chains[key]

    def close(self) -> None:
        self.chains.clear()
        self.sync_http.close()

    async def generate(self, messages: list[dict], max_output_tokens=None) -> dict:
        attempts = self.attempts()
        if not attempts:
            raise ServiceError("No AI provider is configured.", "NO_AI_PROVIDER")
        tokens = (
            min(max(max_output_tokens, 256), 2500)
            if type(max_output_tokens) is int
            else self.output_tokens
        )
        async with self.budget.slot() as queue_ms:
            return await self._generate(messages, tokens, attempts, queue_ms)

    async def _generate(self, messages, tokens, attempts, queue_ms):
        started = time.monotonic()
        log, tried, terminal = [], set(), set()
        for attempt in attempts:
            provider = attempt["provider"]
            entry = {"provider": provider, "model": attempt["model"]}
            if provider in terminal:
                log.append({**entry, "outcome": "terminal_error"})
                continue
            circuit = self.circuits.get(provider)
            if provider not in tried and circuit and circuit[1] > time.monotonic():
                log.append({**entry, "outcome": "circuit_open"})
                continue
            if circuit and circuit[1] <= time.monotonic():
                self.circuits.pop(provider, None)
            tried.add(provider)
            remaining = self.deadline - (time.monotonic() - started)
            if remaining < 0.5:
                break
            try:
                response = await asyncio.wait_for(
                    self.chain(attempt, tokens).ainvoke({"messages": messages}),
                    min(self.model_timeout, remaining),
                )
                answer = clean_response(await StrOutputParser().ainvoke(response))
                if len(answer) < 20:
                    raise ServiceError(
                        "The model returned an empty response.", "EMPTY_MODEL_RESPONSE"
                    )
                if response.response_metadata.get("finish_reason") == "length":
                    raise ServiceError(
                        "The model response reached its output limit.", "MODEL_OUTPUT_LIMIT"
                    )
                usage = response.usage_metadata or {}
                self.circuits.pop(provider, None)
                log.append({**entry, "outcome": "success"})
                return {
                    "answer": answer,
                    **entry,
                    "usage": {
                        "inputTokens": usage.get("input_tokens", 0),
                        "outputTokens": usage.get("output_tokens", 0),
                        "totalTokens": usage.get("total_tokens", 0),
                    },
                    "attempts": log,
                    "queueMs": queue_ms,
                }
            except Exception as error:
                status = getattr(error, "status_code", None) or getattr(error, "status", None)
                outcome = (
                    "MODEL_TIMEOUT"
                    if isinstance(error, TimeoutError)
                    else getattr(error, "code", None) or status or "failed"
                )
                failures = min(self.circuits.get(provider, (0, 0))[0] + 1, 6)
                delay = (
                    600
                    if status in {401, 403, 404}
                    else 60
                    if status == 429
                    else min(5 * 2 ** (failures - 1), 60)
                )
                self.circuits[provider] = (failures, time.monotonic() + delay)
                if status in {400, 401, 403, 404, 422, 429} or outcome == "MODEL_OUTPUT_LIMIT":
                    terminal.add(provider)
                log.append({**entry, "outcome": outcome, "errorType": type(error).__name__})
        raise ServiceError(
            "All bounded model attempts were unavailable.", "AI_ATTEMPTS_EXHAUSTED", log
        )
