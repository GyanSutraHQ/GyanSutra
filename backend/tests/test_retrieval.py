import asyncio
from unittest.mock import AsyncMock

from gyansutra.cache import CapacityBudget, ServiceError
from gyansutra.rag import RagService
from gyansutra.retrieval import (
    LexicalIndex,
    fuse_results,
    local_records,
    requested_sources,
    select_evidence,
    strong_evidence,
)
from gyansutra.text import tokenize, unsupported_references
from tests.conftest import VERSE


def test_bm25_recovers_keyword_only_evidence_without_faking_cosine():
    index = LexicalIndex(
        [
            {**VERSE, "similarity": 0, "translationEnglish": "duty action fruits"},
            {**VERSE, "id": "other", "translationEnglish": "sleep and rest"},
        ]
    )
    result = index.search("action fruits", 2)
    assert result[0]["id"] == VERSE["id"]
    assert result[0]["similarity"] == 0 and strong_evidence(result[0], 0.55)
    assert not strong_evidence(index.search("duty", 1)[0], 0.55)
    assert not index.search("unknown words", 2)


def test_unicode_marks_and_book_constraints():
    assert not requested_sources("digital meditation notes")
    assert "कर्मण्येवाधिकारस्ते" in tokenize("कर्मण्येवाधिकारस्ते")
    assert "তোমার" in tokenize("তোমার কর্তব্য")
    index = LexicalIndex(
        [
            {**VERSE, "translationHindi": "कर्म फल"},
            {
                **VERSE,
                "id": "vishnu-purana_1_1_1",
                "source_id": "vishnu-purana",
                "partNumber": 1,
                "translationHindi": "कर्म फल कर्म फल",
            },
        ]
    )
    assert [r["id"] for r in index.search("गीता कर्म फल", sources=requested_sources("गीता"))] == [
        VERSE["id"]
    ]


def test_fusion_rewards_agreement_and_preserves_remote_authority():
    a = {**VERSE, "id": "a", "similarity": 0.8}
    b = {**VERSE, "id": "b", "similarity": 0.9}
    lexical = [{**a, "similarity": 0, "lexicalScore": 9, "translationEnglish": "old"}]
    fused = fuse_results([b, a], lexical)
    assert [r["id"] for r in fused] == ["a", "b"]
    assert fused[0]["similarity"] == 0.8
    assert fused[0]["translationEnglish"] == VERSE["translationEnglish"]
    assert len(fuse_results([a, a], lexical)) == 1
    stale = [
        {
            **a,
            "translationEnglish": "tortoise withdraws limbs",
            "similarity": 0,
            "lexicalMatches": 3,
            "lexicalCoverage": 1,
        }
    ]
    merged = fuse_results([{**a, "similarity": 0.2}], stale, query="tortoise withdraws limbs")
    assert not strong_evidence(merged[0], 0.55)


def test_diversity_skips_duplicate_passages():
    records = [
        {"id": "a", "translationEnglish": "duty action", "fusionScore": 1},
        {"id": "b", "translationEnglish": "duty action", "fusionScore": 0.99},
        {"id": "c", "translationEnglish": "anger destroys wisdom", "fusionScore": 0.9},
    ]
    assert [r["id"] for r in select_evidence(records, 2)] == ["a", "c"]


def test_real_source_keyword_recall():
    index = LexicalIndex(local_records())
    results = index.search("right action fruits Gita", 5, {"bhagavad-gita"})
    assert results[0]["id"] == "bhagavad-gita_2_47"
    dhruva = index.search("Dhruva Vishnu Purana", 5, {"vishnu-purana"})
    assert dhruva and all(r["id"].startswith("vishnu-purana_1_12_") for r in dhruva)
    assert strong_evidence(dhruva[0], 0.55)


async def test_context_reserves_space_for_later_sources(store, embeddings, provider):
    factory, _, _ = provider
    rag = RagService(store, embeddings, factory())
    values = [
        {
            **VERSE,
            "id": f"vishnu-purana_1_1_{i}",
            "book": "vishnu-purana",
            "translationEnglish": ("Source facts. " * 800),
            "passageNumber": i,
        }
        for i in range(1, 5)
    ]
    text, selected = rag.build_context(values, "en")
    assert len(selected) == 4 and all(f"[S{i}]" in text for i in range(1, 5))
    assert len(text) <= rag.max_chars
    await rag.close()


async def test_keyword_survives_dense_timeout(store, embeddings, provider, monkeypatch):
    factory, _, _ = provider
    monkeypatch.setenv("RAG_HYBRID_ENABLED", "true")
    rag = RagService(store, embeddings, factory())
    await rag.lexical.close()
    rag.lexical = AsyncMock()
    rag.lexical.search.return_value = [
        {**VERSE, "similarity": 0, "lexicalMatches": 2, "lexicalCoverage": 1}
    ]
    rag.timeout = 0.01

    async def hang(*args):
        await asyncio.Event().wait()

    store.nearest.side_effect = hang
    candidates, _ = await rag.retrieve("action fruits")
    assert candidates[0]["id"] == VERSE["id"]
    assert candidates[0]["_retrievalErrors"] == ["TimeoutError"]
    assert not rag.retrievals  # Do not cache a partially failed retrieval.
    await rag.close()


async def test_missing_explicit_reference_does_not_generate_partial_comparison(
    store, embeddings, provider
):
    factory, calls, _ = provider
    store.get_doc.side_effect = [VERSE.copy(), None]
    rag = RagService(store, embeddings, factory())
    result = await rag.ask("Compare Gita 2.47 and 18.66")
    assert result["reason"] == "partial_reference_lookup"
    assert not result["answered"] and result["degraded"] and not calls
    store.nearest.assert_not_called()
    await rag.close()


async def test_followup_new_topic_retrieves_additional_evidence(store, embeddings, provider):
    factory, _, _ = provider
    store.get_doc.return_value = VERSE.copy()
    store.nearest.return_value = [
        {
            **VERSE,
            "id": "bhagavad-gita_2_63",
            "verseNumber": 63,
            "translationEnglish": "Anger leads to delusion.",
        }
    ]
    rag = RagService(store, embeddings, factory())
    result = await rag.ask(
        "What about anger?", [{"role": "user", "content": "What is duty?"}], [VERSE["id"]]
    )
    assert {v["id"] for v in result["citations"]} == {VERSE["id"], "bhagavad-gita_2_63"}
    store.nearest.assert_awaited_once()
    await rag.close()


async def test_real_hybrid_keyword_only_answer_has_provenance(
    store, embeddings, provider, monkeypatch
):
    factory, calls, _ = provider
    monkeypatch.setenv("RAG_HYBRID_ENABLED", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    store.nearest.return_value = []
    rag = RagService(store, embeddings, factory())
    result = await rag.ask("right action fruits Gita")
    assert result["reason"] == "generated" and len(calls) == 1
    assert result["citations"][0]["id"] == VERSE["id"]
    assert result["citations"][0]["translationSources"]["english"]["author"] == "Swami Sivananda"
    assert result["topSimilarity"] == 0  # Lexical relevance is not a fake cosine score.
    await rag.close()


async def test_wrong_output_script_falls_back(store, embeddings, provider, monkeypatch):
    factory, _, _ = provider
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    rag = RagService(store, embeddings, factory())
    store.get_doc.return_value = VERSE.copy()
    result = await rag.ask("Explain Gita 2.47", language="bn")
    assert result["reason"] == "response_language_validation_failed" and result["degraded"]
    await rag.close()


async def test_failed_evidence_is_not_negative_cached(store, embeddings, provider):
    factory, _, _ = provider
    store.nearest.return_value = []
    rag = RagService(store, embeddings, factory())
    assert not (await rag.ask("What is duty?"))["answered"]
    assert not rag.responses
    await rag.close()


async def test_total_request_deadline(store, embeddings, provider):
    factory, _, _ = provider
    rag = RagService(store, embeddings, factory())
    rag.request_timeout = 0.01

    async def hang(*args):
        await asyncio.Event().wait()

    rag.execute = hang
    result = await rag.ask("What is duty?")
    assert result["reason"] == "RAG_REQUEST_TIMEOUT" and result["degraded"]
    await rag.close()


async def test_capacity_bounds_burst_queue_and_releases_cancelled_waiters():
    budget = CapacityBudget(2, 3, 10, "BUSY")
    release, all_admitted = asyncio.Event(), asyncio.Event()
    active, peak, entered = 0, 0, 0

    async def work():
        nonlocal active, peak, entered
        async with budget.slot():
            active += 1
            entered += 1
            peak = max(peak, active)
            if entered == 2:
                all_admitted.set()
            try:
                await release.wait()
            finally:
                active -= 1

    jobs = [asyncio.create_task(work()) for _ in range(10)]
    await all_admitted.wait()
    await asyncio.sleep(0)
    assert budget.waiting == 3
    jobs[2].cancel()
    await asyncio.gather(jobs[2], return_exceptions=True)
    assert budget.waiting == 2
    release.set()
    results = await asyncio.gather(*jobs, return_exceptions=True)
    assert peak == 2 and sum(isinstance(r, ServiceError) for r in results) == 5
    assert budget.waiting == 0 and not budget.semaphore.locked()


async def test_generation_ten_users_have_four_slots(provider, monkeypatch):
    from langchain_core.messages import AIMessage

    factory, _, _ = provider
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    generation = factory()
    active, peak = 0, 0

    async def answer(*args):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        try:
            await asyncio.sleep(0.01)
            return AIMessage(content="Act with care and attention. [S1]")
        finally:
            active -= 1

    generation.chain = lambda *args: type("Chain", (), {"ainvoke": staticmethod(answer)})()
    results = await asyncio.gather(
        *(generation.generate([{"role": "user", "content": f"q{i}"}]) for i in range(10))
    )
    assert peak == 4 and len(results) == 10 and all(r["answer"] for r in results)
    assert not generation.capacity.locked() and generation.budget.waiting == 0


def test_hindi_scripture_reference_is_validated():
    assert unsupported_references("गीता १८.६६ [S1]", [VERSE["id"]], 1)
    assert not unsupported_references("गीता २.४७ [S1]", [VERSE["id"]], 1)
    assert unsupported_references("Act responsibly [S1] [S99x]", [VERSE["id"]], 1)
