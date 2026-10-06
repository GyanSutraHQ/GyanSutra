"""CPU-light BM25, reciprocal rank fusion, and diverse evidence selection.

Keyword scores and fusion scores are ranking signals, never cosine similarities.
The local index uses the same source records and IDs as Firestore ingestion.
"""

import asyncio
import heapq
import json
import math
from array import array
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import regex as re

from .config import ROOT
from .corpus import gita_records, vishnu_records
from .firestore import retrieved
from .text import normalize_question, terms, tokenize

SOURCE_TERMS = set("bhagavad gita bg valmiki ramayana vishnu purana गीता रामायण विष्णु पुराण".split())


def query_terms(query):
    return set(terms(query)) - SOURCE_TERMS


def requested_sources(query):
    value = normalize_question(query)
    return {
        source
        for source, aliases in {
            "bhagavad-gita": ("gita", "गीता", "গীতা", "கீதை", "గీత"),
            "valmiki-ramayana": ("ramayana", "रामायण", "রামায়ণ", "ராமாயணம்", "రామాయణ"),
            "vishnu-purana": ("vishnu purana", "विष्णु पुराण", "বিষ্ণু পুরাণ"),
        }.items()
        if any(
            re.search(r"(?<![\p{L}\p{M}])" + re.escape(alias) + r"(?![\p{L}\p{M}])", value)
            for alias in aliases
        )
    }


def source_id(record):
    return record.get("source_id") or (
        "vishnu-purana"
        if record.get("partNumber")
        else "valmiki-ramayana"
        if record.get("kandaNumber")
        else "bhagavad-gita"
    )


def evidence_text(record):
    return " ".join(
        str(record.get(k) or "")
        for k in (
            "sanskrit",
            "translationEnglish",
            "translationHindi",
            "transliteration",
            "explanationEnglish",
            "comments",
            "storyTitle",
            "storySummary",
        )
    )


def local_records(snapshot=None):
    for generator in (gita_records, vishnu_records):
        for doc_id, record, text in generator():
            if text:  # Index passages, not the duplicate full Purana sections.
                yield retrieved({"id": doc_id, **record}, 0)
    if snapshot:
        path = (ROOT / snapshot).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Lexical snapshot must be inside backend/.")
        # JSON Lines avoids retaining a decoded full file alongside the index.
        with path.open() as stream:
            for line in stream:
                if not line.strip():
                    continue
                record = json.loads(line)
                if not isinstance(record, dict) or not isinstance(record.get("id"), str):
                    raise ValueError("Each snapshot line needs a source record with an ID.")
                if not record.get("ragOnly") and record.get("book") == "vishnu-purana":
                    continue
                yield retrieved(record, 0)


class LexicalIndex:
    def __init__(self, records):
        self.records, self.lengths = [], []
        self.postings = defaultdict(lambda: array("I"))
        seen = set()
        for record in records:
            if record["id"] in seen:
                continue
            seen.add(record["id"])
            counts = Counter(terms(evidence_text(record)))
            if not counts:
                continue
            index = len(self.records)
            self.records.append(record)
            self.lengths.append(sum(counts.values()))
            for term, frequency in counts.items():
                self.postings[term].extend((index, frequency))
        self.average_length = sum(self.lengths) / max(1, len(self.lengths))

    def search(self, query, limit=12, sources=()):
        tokens = query_terms(query)
        scores, matched = defaultdict(float), defaultdict(set)
        n = len(self.records)
        for token in tokens:
            postings = self.postings.get(token, ())
            count = len(postings) // 2
            idf = math.log(1 + (n - count + 0.5) / (count + 0.5))
            for offset in range(0, len(postings), 2):
                index, frequency = postings[offset], postings[offset + 1]
                if sources and source_id(self.records[index]) not in sources:
                    continue
                norm = frequency + 1.2 * (0.25 + 0.75 * self.lengths[index] / self.average_length)
                scores[index] += idf * frequency * 2.2 / norm
                matched[index].add(token)
        best = heapq.nlargest(limit, scores, key=lambda i: (scores[i], -i))
        return [
            {
                **self.records[i],
                "similarity": 0,
                "lexicalScore": scores[i],
                "lexicalMatches": len(matched[i]),
                "lexicalCoverage": len(matched[i]) / max(1, len(tokens)),
                "lexicalTitleMatch": bool(tokens)
                and tokens <= tokenize(self.records[i].get("storyTitle", "")),
            }
            for i in best
        ]


class LexicalRetriever:
    """One index-build task and one dedicated CPU worker per API instance."""

    def __init__(self, snapshot=None):
        self.snapshot = snapshot
        self.index = None
        self._build = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="lexical")

    async def prewarm(self):
        if self.index is not None:
            return
        if self._build is None:
            self._build = asyncio.ensure_future(
                asyncio.get_running_loop().run_in_executor(
                    self._executor, lambda: LexicalIndex(local_records(self.snapshot))
                )
            )
        try:
            self.index = await asyncio.shield(self._build)
        except Exception:
            self._build = None
            raise

    async def search(self, query, limit=12, sources=()):
        await self.prewarm()
        return await asyncio.get_running_loop().run_in_executor(
            self._executor, self.index.search, query, limit, sources
        )

    async def close(self):
        if self._build:
            await asyncio.gather(self._build, return_exceptions=True)
        self._executor.shutdown(wait=True, cancel_futures=True)


def fuse_results(dense, lexical, rank_constant=60, query=None):
    records, scores = {}, defaultdict(float)
    # Copy keyword metadata first; remote source text takes precedence for duplicates.
    for values in (lexical, dense):
        seen = set()
        for rank, record in enumerate(values, 1):
            doc_id = record["id"]
            if doc_id in seen:
                continue
            seen.add(doc_id)
            records[doc_id] = {**records.get(doc_id, {}), **record}
            scores[doc_id] += 1 / (rank_constant + rank)
    if query is not None:
        tokens = query_terms(query)
        for record in records.values():
            if "lexicalMatches" in record:
                # A stale local snapshot must not confer keyword confidence on
                # different text returned by the authoritative remote record.
                record["lexicalMatches"] = len(tokens & tokenize(evidence_text(record)))
                record["lexicalCoverage"] = record["lexicalMatches"] / max(1, len(tokens))
                record["lexicalTitleMatch"] = bool(tokens) and tokens <= tokenize(
                    record.get("storyTitle", "")
                )
    return sorted(
        [{**record, "fusionScore": scores[doc_id]} for doc_id, record in records.items()],
        key=lambda r: (r["fusionScore"], r.get("similarity", 0)),
        reverse=True,
    )


def strong_evidence(record, threshold, lexical_coverage=0.6):
    similarity = record.get("similarity", 0)
    return (
        isinstance(similarity, (int, float))
        and math.isfinite(similarity)
        and similarity >= threshold
    ) or (
        (record.get("lexicalMatches", 0) >= 2 or record.get("lexicalTitleMatch", False))
        and record.get("lexicalCoverage", 0) >= lexical_coverage
    )


def select_evidence(ranked, limit, diversity=0.2):
    """MMR-style lexical redundancy penalty; no extra model inference."""
    selected, remaining = [], list(ranked)
    token_sets = {r["id"]: tokenize(evidence_text(r)) for r in ranked}
    maximum = max((r.get("fusionScore", r.get("rerankScore", 0)) for r in ranked), default=1) or 1
    while remaining and len(selected) < limit:

        def score(record):
            tokens = token_sets[record["id"]]
            redundancy = max(
                (
                    len(tokens & token_sets[v["id"]]) / max(1, len(tokens | token_sets[v["id"]]))
                    for v in selected
                ),
                default=0,
            )
            relevance = record.get("fusionScore", record.get("rerankScore", 0)) / maximum
            return relevance - diversity * redundancy

        best = max(remaining, key=score)
        remaining.remove(best)
        # Avoid spending the entire prompt on near-identical source passages.
        if any(token_sets[best["id"]] == token_sets[v["id"]] for v in selected):
            continue
        selected.append(best)
    return selected
