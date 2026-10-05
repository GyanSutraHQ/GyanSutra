import asyncio
import json

import httpx
import pytest

from gyansutra.cache import ServiceError, SingleFlight
from gyansutra.rag import RagService
from tests.conftest import VERSE


@pytest.mark.parametrize(
    "question",
    [
        "How are you",
        "Question: How are you?",
        "Who are you?",
        "What can you do, Sarathi?",
        "What is python",
    ],
)
async def test_guardrails_skip_every_external_stage(question, store, embeddings, provider):
    factory, calls, _ = provider
    rag = RagService(store, embeddings, factory())
    result = await rag.ask(question)
    assert result["reason"].startswith("guardrail_")
    store.get_doc.assert_not_called()
    store.nearest.assert_not_called()
    embeddings.aembed_query.assert_not_called()
    assert not calls


async def test_exact_missing_and_follow_up(store, embeddings, provider):
    factory, calls, _ = provider
    rag = RagService(store, embeddings, factory())
    store.get_doc.return_value = VERSE.copy()
    result = await rag.ask("Show Gita 2.47")
    assert result["reason"] == "direct_source_response"
    assert result["citations"][0]["id"] == VERSE["id"]
    assert "कर्मण्येवाधिकारस्ते" in result["answer"]
    store.get_doc.return_value = None
    missing = await rag.ask("Explain Gita 2.999")
    assert missing["reason"] == "no_strong_evidence"
    store.get_doc.return_value = VERSE.copy()
    follow = await rag.ask(
        "Explain that more", [{"role": "user", "content": "What is duty?"}], [VERSE["id"]]
    )
    assert follow["citations"][0]["id"] == VERSE["id"]
    store.nearest.assert_not_called()
    embeddings.aembed_query.assert_not_called()
    assert not calls


async def test_threshold_and_provider_unavailable(store, embeddings, provider):
    factory, calls, _ = provider
    rag = RagService(store, embeddings, factory())
    store.nearest.return_value = [{**VERSE, "similarity": 0.3}]
    assert (await rag.ask("Explain duty"))["reason"] == "no_strong_evidence"
    store.nearest.return_value = [VERSE.copy()]
    result = await rag.ask("Explain duty in the Gita")
    assert result["reason"] == "NO_AI_PROVIDER" and result["degraded"]
    assert not result["answered"] and "cannot give a reliable explanation" in result["answer"]
    assert not calls


@pytest.mark.parametrize(
    "provider_name,key,endpoint,model",
    [
        ("gemini", "GEMINI_API_KEY", "generativelanguage.googleapis.com", "gemini-3.8-flash"),
        ("grok", "XAI_API_KEY", "api.x.ai", "grok-4.7"),
        ("openrouter", "OPENROUTER_API_KEY", "openrouter.ai", "openrouter/free"),
    ],
)
async def test_real_langchain_transport_settings(
    provider_name, key, endpoint, model, monkeypatch, provider
):
    # The provider fixture runs the actual LangChain model and SDK against HTTPX transport.
    factory, calls, _ = provider
    monkeypatch.setenv(key, "test-key")
    monkeypatch.setenv("RAG_PROVIDER_ORDER", provider_name)
    service = factory()
    messages = [
        {"role": "system", "content": 'SOURCE_DATA: {"duty": true}'},
        {"role": "user", "content": "Explain duty"},
    ]
    result = await service.generate(messages, 2000)
    assert result["usage"] == {"inputTokens": 10, "outputTokens": 8, "totalTokens": 18}
    assert len(calls) == 1 and calls[0].url.host == endpoint
    body = json.loads(calls[0].content)
    assert body["messages"] == messages and body["model"] == model and body["max_tokens"] == 2000
    assert calls[0].headers["authorization"] == "Bearer test-key"
    assert body.get("reasoning_effort") == ("low" if provider_name == "gemini" else None)
    if provider_name == "gemini":
        assert "temperature" not in body
    else:
        assert body["temperature"] == 0.1


async def test_generation_cache_grounding_and_fallback(store, embeddings, provider, monkeypatch):
    factory, calls, responses = provider
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    rag = RagService(store, embeddings, factory())
    result = await rag.ask("What does duty mean?")
    assert result["reason"] == "generated"
    assert (await rag.ask("  WHAT does duty mean? "))["cached"]
    assert len(calls) == 1
    responses.append(
        httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": "Gita Chapter 18 Verse 66 says surrender [S1].",
                        },
                    }
                ]
            },
        )
    )
    rejected = await rag.ask("What is responsible action?")
    assert rejected["reason"] == "grounding_validation_failed" and rejected["degraded"]
    assert "18 Verse 66" not in rejected["answer"]


async def test_independent_provider_fallback_and_terminal_no_retries(provider, monkeypatch):
    factory, calls, responses = provider
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("XAI_API_KEY", "xai-key")
    responses.append(
        httpx.Response(429, json={"error": {"message": "Quota exceeded", "type": "rate_limit"}})
    )
    result = await factory().generate([{"role": "user", "content": "Explain duty"}])
    assert result["provider"] == "grok"
    assert len(calls) == 2
    assert result["attempts"][0]["outcome"] == 429


async def test_generation_timeout_cancellation_releases_slot(provider, monkeypatch):
    factory, _, _ = provider
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("RAG_MAX_MODEL_ATTEMPTS", "1")
    service = factory()
    service.model_timeout = 0.01
    cancelled = asyncio.Event()

    async def hang(*args, **kwargs):
        try:
            await asyncio.sleep(10)
        finally:
            cancelled.set()

    service.chain = lambda *args: type("Chain", (), {"ainvoke": staticmethod(hang)})()
    with pytest.raises(ServiceError) as caught:
        await service.generate([{"role": "user", "content": "Explain duty"}])
    assert caught.value.attempts[0]["outcome"] == "MODEL_TIMEOUT"
    assert cancelled.is_set() and not service.capacity.locked()


async def test_singleflight_survives_one_cancelled_caller():
    flight = SingleFlight()
    started, finish = asyncio.Event(), asyncio.Event()

    async def work():
        started.set()
        await finish.wait()
        return 42

    first = asyncio.create_task(flight.run("same", work))
    await started.wait()
    second = asyncio.create_task(flight.run("same", work))
    first.cancel()
    await asyncio.gather(first, return_exceptions=True)
    finish.set()
    assert await second == 42
    await flight.close()
