import asyncio
from unittest.mock import AsyncMock

from gyansutra.query import QueryBridge
from gyansutra.rag import RagService
from tests.conftest import VERSE


async def test_translation_cache_and_english_fast_path(monkeypatch):
    monkeypatch.setenv("RAG_MULTILINGUAL_QUERY_ENABLED", "true")
    generation = AsyncMock()
    generation.generate.return_value = {"answer": '{"query":"How should I perform my duty?"}'}
    bridge = QueryBridge(generation)
    assert await bridge.translate("How should I perform my duty?") == (
        "How should I perform my duty?",
        "original",
    )
    generation.generate.assert_not_called()
    translated, mode = await bridge.translate("मुझे अपना कर्तव्य कैसे करना चाहिए?")
    assert translated == "How should I perform my duty?" and mode == "translated"
    assert (await bridge.translate("मुझे अपना कर्तव्य कैसे करना चाहिए?"))[1] == "cached_translation"
    generation.generate.assert_awaited_once()
    await bridge.close()


async def test_bridge_rejects_invented_reference_and_recovers(monkeypatch):
    monkeypatch.setenv("RAG_MULTILINGUAL_QUERY_ENABLED", "true")
    generation = AsyncMock()
    generation.generate.side_effect = [
        {"answer": '{"query":"Explain Gita 18.66"}'},
        {"answer": '{"query":"What is duty?"}'},
    ]
    bridge = QueryBridge(generation)
    assert await bridge.translate("कर्तव्य क्या है?") == ("कर्तव्य क्या है?", "translation_unavailable")
    assert not bridge.cache
    assert await bridge.translate("कर्तव्य क्या है?") == ("What is duty?", "translated")
    await bridge.close()


async def test_bridge_timeout_cancels_provider_work(monkeypatch):
    monkeypatch.setenv("RAG_MULTILINGUAL_QUERY_ENABLED", "true")
    cancelled = asyncio.Event()

    async def hang(*args):
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    generation = AsyncMock()
    generation.generate.side_effect = hang
    bridge = QueryBridge(generation)
    bridge.timeout = 0.01
    assert (await bridge.translate("क्रोध क्या है?"))[1] == "translation_unavailable"
    assert cancelled.is_set()
    await bridge.close()


async def test_rag_translates_bengali_query_but_keeps_original_question(
    store, embeddings, provider, monkeypatch
):
    monkeypatch.setenv("RAG_MULTILINGUAL_QUERY_ENABLED", "true")
    generation = AsyncMock()
    generation.generate.side_effect = [
        {"answer": '{"query":"What is duty in the Gita?"}'},
        {
            "answer": "কর্তব্য পালন করো। [S1]",
            "provider": "test",
            "model": "test",
            "usage": {},
            "attempts": [],
        },
    ]
    rag = RagService(store, embeddings, generation)
    result = await rag.ask("গীতায় কর্তব্য কী?", language="bn")
    embeddings.aembed_query.assert_awaited_once_with("What is duty in the Gita?")
    assert result["reason"] == "generated" and result["citations"][0]["id"] == VERSE["id"]
    assert generation.generate.call_args.args[0][-1]["content"] == "গীতায় কর্তব্য কী?"
    assert result["_diagnostics"]["queryMode"] == "translated"
    await rag.close()
