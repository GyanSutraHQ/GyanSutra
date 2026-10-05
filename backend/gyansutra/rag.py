"""Bounded, source-grounded LangChain RAG, preserving scripture policies."""

import asyncio
import hashlib
import os
import time
from datetime import datetime, timezone
from typing import Any

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from .cache import SingleFlight, TTLCache
from .config import enabled, integer, number
from .firestore import retrieved
from .text import (
    POLICY,
    classify_guardrail,
    context_ids,
    direct_request,
    explicit_references,
    follow_up,
    modernize,
    normalize_question,
    rerank,
    retrieval_query,
    truncate,
    unsupported_references,
    verse_reference,
)

LANGUAGES = {
    "en": "English",
    "hi": "natural Devanagari Hindi",
    "bn": "natural Bengali",
    "mr": "natural Devanagari Marathi",
    "te": "natural Telugu",
    "ta": "natural Tamil",
}
CITATION_FIELDS = "id chapterNumber verseNumber book kanda kandaNumber sarga shlokaNumber partNumber partTitle sectionNumber passageNumber storyTitle sanskrit transliteration translationEnglish translationHindi similarity tags".split()


def source_explanation(verse) -> str:
    verse = verse or {}
    commentary = next(
        (
            v.get("explanation")
            for v in (verse.get("detailedExplanations") or [])
            if v.get("explanation") and "english" in str(v.get("language") or "english").lower()
        ),
        "",
    )
    return modernize(verse.get("explanationEnglish") or verse.get("comments") or commentary)


def extractive_answer(question, verses, reason="generation_unavailable", language="en") -> str:
    words = POLICY["fallback"][language]
    if not verses:
        return words["noEvidence"] + "\n\n" + words["example"]
    if reason != "direct_text":
        explanation = source_explanation(verses[0])
        return (
            truncate(explanation, 480) + " [S1]"
            if explanation and language == "en"
            else POLICY["unavailable"][language]
        )
    labels = POLICY["referenceWords"][language]
    passages = []
    for index, verse in enumerate(verses[:2]):
        if verse.get("book") == "vishnu-purana" or verse.get("partNumber"):
            ref = f"Vishnu Purana, Part {verse.get('partNumber')}, Section {verse.get('sectionNumber')}"
        elif verse.get("book") == "ramayana" or verse.get("kandaNumber"):
            ref = f"{labels[1]}, {labels[4]} {verse.get('kandaNumber')}, {labels[5]} {verse.get('sarga')}, {labels[6]} {verse.get('shlokaNumber')}"
        else:
            ref = f"{labels[0]}, {labels[2]} {verse.get('chapterNumber')}, {labels[3]} {verse.get('verseNumber')}"
        value = (
            verse.get("translationHindi")
            if language == "hi"
            else modernize(verse.get("translationEnglish"))
            if language == "en"
            else verse.get("sanskrit")
        )
        meaning = truncate(
            value
            or (
                verse.get("sanskrit")
                if language == "hi"
                else modernize(verse.get("translationEnglish"))
            )
            or verse.get("sanskrit"),
            550,
        )
        text = (
            "\n\n".join(
                filter(
                    None,
                    [
                        truncate(verse["sanskrit"], 700),
                        "" if meaning == verse["sanskrit"] else meaning,
                    ],
                )
            )
            if verse.get("sanskrit")
            else meaning
        )
        passages.append(f"**{ref}** [S{index + 1}]: {text}")
    return words["direct"] + "\n\n" + "\n\n".join(passages)


class ScriptureRetriever(BaseRetriever):
    store: Any
    embeddings: Any
    top_k: int
    timeout: float

    def _get_relevant_documents(self, query, *, run_manager):
        raise RuntimeError("Use asynchronous retrieval with ainvoke.")

    async def _aget_relevant_documents(self, query, *, run_manager):
        vector = await asyncio.wait_for(self.embeddings.aembed_query(query), self.timeout)
        verses = await asyncio.wait_for(self.store.nearest(vector, self.top_k), self.timeout)
        return [
            Document(
                id=v["id"],
                page_content="\n".join(
                    v.get(k) or "" for k in ("translationEnglish", "translationHindi", "sanskrit")
                ),
                metadata=v,
            )
            for v in verses
        ]


class RagService:
    def __init__(self, store, embeddings, generation):
        self.store, self.embeddings, self.generation = store, embeddings, generation
        self.threshold = number("RAG_SIMILARITY_THRESHOLD", 0.55, 0, 1)
        self.top_k = integer("RAG_TOP_K", 12, 1, 20)
        self.top_context = integer("RAG_TOP_CONTEXT", 4, 1, 6)
        self.max_chars = integer("RAG_MAX_CONTEXT_CHARS", 7000, 2000, 14000)
        self.max_commentaries = integer("RAG_MAX_COMMENTARIES", 2, 0, 4)
        self.commentary_chars = integer("RAG_MAX_COMMENTARY_CHARS", 650, 100, 1500)
        self.timeout = integer("RAG_RETRIEVAL_TIMEOUT_MS", 8000, 1000, 30000) / 1000
        size = integer("RAG_CACHE_MAX_ENTRIES", 250, 10, 2000)
        self.responses = TTLCache(
            size, integer("RAG_RESPONSE_CACHE_TTL_SECONDS", 21600, 30, 604800)
        )
        self.retrievals = TTLCache(
            size, integer("RAG_RETRIEVAL_CACHE_TTL_SECONDS", 3600, 30, 86400)
        )
        self.cache_enabled = enabled("RAG_CACHE_ENABLED")
        self.corpus = os.getenv("RAG_CORPUS_VERSION", "gita-ramayana-vishnu-purana-v1")
        self.response_flight, self.retrieval_flight = SingleFlight(), SingleFlight()
        self.retriever = ScriptureRetriever(
            store=store, embeddings=embeddings, top_k=self.top_k, timeout=self.timeout
        )

    def build_context(self, verses, language):
        selected, blocks = [], []
        remaining, commentary_count = self.max_chars, 0
        for verse in verses[: self.top_context]:
            lines = [f"[S{len(selected) + 1}] {verse_reference(verse)}"]
            for key, label, limit in [
                ("sanskrit", "Sanskrit", 700),
                ("transliteration", "Transliteration", 500),
                (
                    "translationEnglish",
                    "English translation",
                    4000 if verse.get("book") == "vishnu-purana" else 900,
                ),
                ("translationHindi", "Hindi translation", 900),
                ("explanationEnglish", "Source explanation", 900),
                ("comments", "Source notes", 550),
            ]:
                if verse.get(key):
                    text = (
                        modernize(verse[key])
                        if key in {"translationEnglish", "explanationEnglish", "comments"}
                        else verse[key]
                    )
                    lines.append(f"{label}: {truncate(text, limit)}")
            meanings = ", ".join(
                f"{v.get('word') or ''} = {v.get('meaning') or ''}"
                for v in (verse.get("wordMeanings") or [])[:14]
                if v and (v.get("word") or v.get("meaning"))
            )
            if meanings:
                lines.append("Selected word meanings: " + truncate(meanings, 550))
            commentaries = [
                c
                for c in (verse.get("detailedExplanations") or [])
                if isinstance(c.get("explanation"), str) and c["explanation"].strip()
            ]
            preferred = "hindi" if language == "hi" else "english"
            commentaries.sort(
                key=lambda v: preferred in str(v.get("language", "")).lower(), reverse=True
            )
            for commentary in commentaries:
                if commentary_count >= self.max_commentaries:
                    break
                lines.append(
                    f"Commentary by {commentary.get('author') or 'Traditional teacher'}: {truncate(modernize(commentary['explanation']), self.commentary_chars)}"
                )
                commentary_count += 1
            block = "\n".join(lines)
            if len(block) > remaining:
                block = truncate(block, remaining)
            if len(block) < 80:
                break
            blocks.append(block)
            selected.append(verse)
            remaining -= len(block) + 30
            if remaining < 200:
                break
        return "\n\n---\n\n".join(blocks), selected

    async def retrieve(self, query):
        key = hashlib.sha256(
            f"{self.corpus}\0{self.top_k}\0{normalize_question(query)}".encode()
        ).hexdigest()
        if self.cache_enabled and key in self.retrievals:
            return self.retrievals[key], True

        async def fetch():
            docs = await self.retriever.ainvoke(query)
            candidates = [doc.metadata for doc in docs]
            if self.cache_enabled:
                self.retrievals[key] = candidates
            return candidates

        return await self.retrieval_flight.run(key, fetch), False

    async def execute(self, question, history, ids, language):
        started = time.monotonic()
        timings, exact, failed, hit = {}, [], False, False
        refs = explicit_references(question)
        exact_ids = (
            [r["id"] for r in refs] if refs else context_ids(ids) if follow_up(question) else []
        )
        if exact_ids:
            stage = time.monotonic()
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(
                        *(self.store.get_doc("verses", doc_id) for doc_id in exact_ids),
                        return_exceptions=True,
                    ),
                    self.timeout,
                )
                failed = any(isinstance(v, Exception) for v in results)
                exact = [retrieved(v) for v in results if isinstance(v, dict)]
            except Exception:
                failed = True
            timings["exactLookupMs"] = round((time.monotonic() - stage) * 1000)
        candidates = exact
        if not candidates and not refs:
            stage = time.monotonic()
            try:
                candidates, hit = await self.retrieve(retrieval_query(question, history))
            except Exception:
                failed = True
            timings["retrievalMs"] = round((time.monotonic() - stage) * 1000)
        ranked = rerank(candidates, question)
        top = ranked[0].get("similarity", 0) if ranked else 0
        text, selected = self.build_context(
            [v for v in ranked if v.get("similarity", 0) >= self.threshold], language
        )
        citations = [
            {
                k: modernize(v[k]) if k == "translationEnglish" else v[k]
                for k in CITATION_FIELDS
                if k in v
            }
            for v in selected
        ]
        diagnostics = {"timings": timings, "retrievalCacheHit": hit, "generationAttempts": []}

        def result(answer, answered, in_context, degraded, reason):
            timings["totalMs"] = round((time.monotonic() - started) * 1000)
            return {
                "answer": answer,
                "answered": bool(answered),
                "inContext": in_context,
                "degraded": degraded,
                "reason": reason,
                "citations": citations,
                "topSimilarity": top,
                "cached": False,
                "_diagnostics": diagnostics,
            }

        if not selected:
            return result(
                extractive_answer(question, [], language=language),
                False,
                False,
                failed,
                "retrieval_unavailable" if failed else "no_strong_evidence",
            )
        if refs and direct_request(question):
            return result(
                extractive_answer(question, selected, "direct_text", language),
                True,
                True,
                False,
                "direct_source_response",
            )
        messages = [
            {
                "role": "system",
                "content": f"{POLICY['systemPrompt']}\n\nRESPONSE LANGUAGE: Respond exclusively in {LANGUAGES[language]}. Do not mix interface prose from another language.\n\nSOURCE PACK:\n{text}",
            }
        ]
        messages += [
            {
                "role": "assistant" if m["role"] == "sarathi" else "user",
                "content": truncate(m["content"], 1000),
            }
            for m in history[-4:]
        ]
        messages.append({"role": "user", "content": question})
        stage = time.monotonic()
        explainable = language == "en" and bool(source_explanation(selected[0]))
        try:
            generated = await self.generation.generate(messages)
            diagnostics.update(
                provider=generated["provider"],
                model=generated["model"],
                usage=generated["usage"],
                generationAttempts=generated["attempts"],
            )
            timings["generationMs"] = round((time.monotonic() - stage) * 1000)
            if unsupported_references(
                generated["answer"], [v["id"] for v in selected], len(selected)
            ):
                return result(
                    extractive_answer(question, selected, language=language),
                    explainable,
                    True,
                    True,
                    "grounding_validation_failed",
                )
            return result(generated["answer"], True, True, False, "generated")
        except Exception as error:
            timings["generationMs"] = round((time.monotonic() - stage) * 1000)
            diagnostics["generationAttempts"] = getattr(error, "attempts", [])
            return result(
                extractive_answer(question, selected, language=language),
                explainable,
                True,
                True,
                getattr(error, "code", "generation_unavailable"),
            )

    async def ask(self, question, history=None, ids=None, language="en"):
        history, ids = history or [], ids or []
        language = language if language in LANGUAGES else "en"
        guardrail = classify_guardrail(question, language)
        if guardrail:
            return {
                "answered": True,
                "inContext": False,
                "answer": guardrail["answer"],
                "citations": [],
                "topSimilarity": 0,
                "cached": False,
                "degraded": False,
                "reason": f"guardrail_{guardrail['type']}",
                "_diagnostics": {
                    "timings": {"totalMs": 0},
                    "guardrail": guardrail["type"],
                    "generationAttempts": [],
                },
            }
        cacheable = self.cache_enabled and not history and not context_ids(ids)
        key = f"{language}:{normalize_question(question)}"
        if cacheable and key in self.responses:
            cached = self.responses[key]
            return {
                **cached,
                "cached": True,
                "_diagnostics": {
                    **cached["_diagnostics"],
                    "responseCacheHit": True,
                    "timings": {"totalMs": 0},
                },
            }

        async def fetch():
            value = await self.execute(question, history, ids, language)
            if cacheable and not value["degraded"]:
                self.responses[key] = value
            return value

        return await self.response_flight.run(key, fetch) if cacheable else await fetch()

    async def log(self, question, result):
        diagnostics = result.get("_diagnostics", {})
        try:
            await self.store.log(
                {
                    "question": question,
                    "retrievedVerseIds": [v["id"] for v in result["citations"]],
                    "wasAnswered": result["answered"],
                    "degraded": result["degraded"],
                    "reason": result["reason"],
                    "cacheHit": bool(
                        diagnostics.get("responseCacheHit") or diagnostics.get("retrievalCacheHit")
                    ),
                    "provider": diagnostics.get("provider"),
                    "model": diagnostics.get("model"),
                    "usage": diagnostics.get("usage"),
                    "timings": diagnostics.get("timings"),
                    "generationAttempts": diagnostics.get("generationAttempts", []),
                    "timestamp": datetime.now(timezone.utc),
                }
            )
        except Exception:
            pass  # Analytics must never affect an API response.

    async def close(self):
        await self.response_flight.close()
        await self.retrieval_flight.close()
