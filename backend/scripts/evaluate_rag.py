"""Offline lexical recall smoke evaluation; no database or paid provider calls.

This measures one retrieval branch on explicit fixtures, not answer correctness
or production throughput. Add independently reviewed cases as the corpus grows.
"""

import argparse
import json
import statistics
import time
from pathlib import Path

from gyansutra.config import ROOT
from gyansutra.retrieval import LexicalIndex, local_records, requested_sources, strong_evidence


def evaluate(cases, top_k=5, repeats=20, snapshot=None):
    started = time.perf_counter()
    index = LexicalIndex(local_records(snapshot))
    build_ms = (time.perf_counter() - started) * 1000
    results, timings = [], []
    for case in cases:
        for _ in range(repeats):
            started = time.perf_counter()
            values = index.search(case["query"], top_k, requested_sources(case["query"]))
            timings.append((time.perf_counter() - started) * 1000)
        rank = next(
            (
                i
                for i, value in enumerate(values, 1)
                if value["id"] in case.get("relevantIds", [])
                or any(value["id"].startswith(p) for p in case.get("relevantPrefixes", []))
            ),
            None,
        )
        results.append(
            {
                "query": case["query"],
                "firstRelevantRank": rank,
                "retrievedIds": [v["id"] for v in values],
                "strongEvidenceCount": sum(strong_evidence(v, 0.55) for v in values),
            }
        )
    return {
        "scope": "offline keyword retrieval smoke evaluation; not end-to-end answer quality",
        "indexedPassages": len(index.records),
        "cases": len(cases),
        "topK": top_k,
        "recallAtK": sum(r["firstRelevantRank"] is not None for r in results)
        / max(1, len(results)),
        "meanReciprocalRank": sum(
            1 / r["firstRelevantRank"] if r["firstRelevantRank"] else 0 for r in results
        )
        / max(1, len(results)),
        "indexBuildMs": round(build_ms, 2),
        "queryMedianMs": round(statistics.median(timings), 3),
        "queryP95Ms": round(sorted(timings)[int((len(timings) - 1) * 0.95)], 3),
        "results": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / "tests/fixtures/rag_retrieval.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--snapshot", help="Optional backend-relative lexical snapshot")
    parser.add_argument("--top-k", type=int, choices=range(1, 21), default=5)
    args = parser.parse_args()
    report = evaluate(json.loads(args.cases.read_text()), args.top_k, snapshot=args.snapshot)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered)
