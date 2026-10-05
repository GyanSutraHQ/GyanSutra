"""Live, bounded provider and Firestore verification; never prints credentials."""

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import httpx

from gyansutra.config import ROOT
from gyansutra.embedding import LocalScriptureEmbeddings
from gyansutra.firestore import ScriptureStore
from gyansutra.generation import GenerationService
from gyansutra.rag import RagService


async def verify(providers, check_firestore=True):
    report = {"checkedAt": datetime.now(timezone.utc).isoformat(), "checks": []}
    store, embeddings = ScriptureStore(), LocalScriptureEmbeddings()
    source = next(
        v
        for v in json.loads((ROOT / "data/gita.json").read_text())
        if v["chapter_number"] == 2 and v["verse_number"] == 47
    )

    class VersionedSource:
        async def get_doc(self, collection, doc_id):
            if doc_id == "bhagavad-gita_2_47":
                return {
                    "id": doc_id,
                    "chapterNumber": 2,
                    "verseNumber": 47,
                    "sanskrit": source["sanskrit"],
                    "transliteration": source.get("transliteration", ""),
                    "translationEnglish": source["english"],
                    "translationHindi": source["hindi"],
                }

    async with httpx.AsyncClient(timeout=30) as http:
        try:
            if check_firestore:
                started = perf_counter()
                try:
                    verse = await asyncio.wait_for(
                        store.get_doc("verses", "bhagavad-gita_2_47"), 30
                    )
                    assert verse and verse.get("sanskrit") and verse.get("translationEnglish")
                    vector = await embeddings.aembed_query("What does the Gita teach about duty?")
                    candidates = await asyncio.wait_for(store.nearest(vector, 8), 30)
                    assert candidates and all(v.get("id") for v in candidates)
                    report["checks"].append(
                        {
                            "check": "firestore_and_vector_search",
                            "status": "passed",
                            "elapsedMs": round((perf_counter() - started) * 1000),
                            "candidates": len(candidates),
                            "topSimilarity": max(v["similarity"] for v in candidates),
                        }
                    )
                except Exception as exc:
                    report["checks"].append(
                        {
                            "check": "firestore_and_vector_search",
                            "status": "failed",
                            "errorType": type(exc).__name__,
                        }
                    )
            for provider in providers:
                service = GenerationService(http)
                service.order = [provider]
                # Provider connectivity is independent of Firestore connectivity.
                # This is a real generation call grounded in versioned source text.
                rag = RagService(VersionedSource(), embeddings, service)
                started = perf_counter()
                try:
                    if not service.attempts():
                        report["checks"].append(
                            {
                                "check": provider,
                                "source": "versioned_gita_2_47",
                                "status": "blocked",
                                "reason": "missing_credentials",
                            }
                        )
                        continue
                    result = await rag.ask("Explain Bhagavad Gita 2.47 in plain English.")
                    diagnostics = result.get("_diagnostics", {})
                    passed = result["reason"] == "generated" and bool(result["citations"])
                    report["checks"].append(
                        {
                            "check": provider,
                            "status": "passed" if passed else "failed",
                            "reason": result["reason"],
                            "elapsedMs": round((perf_counter() - started) * 1000),
                            "model": diagnostics.get("model"),
                            "usage": diagnostics.get("usage"),
                            "attempts": diagnostics.get("generationAttempts"),
                            "citationIds": [v["id"] for v in result["citations"]],
                        }
                    )
                finally:
                    await rag.close()
                    service.close()
        finally:
            await store.close()
            embeddings.close()
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=["gemini", "grok", "openrouter"],
        default=["gemini", "grok"],
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--skip-firestore", action="store_true", help="Run provider checks independently."
    )
    args = parser.parse_args()
    report = asyncio.run(verify(args.providers, not args.skip_firestore))
    content = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(content)
    print(content)
    raise SystemExit(0 if all(v["status"] == "passed" for v in report["checks"]) else 1)
