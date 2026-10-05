"""Bounded HTTP load test with real database reads; no generated answers or writes."""

import argparse
import asyncio
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import httpx

PROFILES = {
    "reading": [
        "/api/chapters",
        "/api/chapters/chapter_2/verses",
        "/api/verses/bhagavad-gita_2_47",
        "/api/vishnu-purana/1/1",
    ],
    "search": ["/api/search?q=What+does+the+Gita+teach+about+duty&limit=5"],
    "health": ["/health"],
}


def percentile(values, fraction):
    ordered = sorted(values)
    index = (len(ordered) - 1) * fraction
    lower = int(index)
    return round(
        ordered[lower]
        + (ordered[min(lower + 1, len(ordered) - 1)] - ordered[lower]) * (index - lower),
        2,
    )


async def run(args):
    semaphore = asyncio.Semaphore(args.concurrency)
    results = []
    paths = PROFILES[args.profile]
    async with httpx.AsyncClient(
        base_url=args.base_url.rstrip("/"),
        timeout=40,
        limits=httpx.Limits(max_connections=args.concurrency),
    ) as client:
        # Warm each path once; measured requests represent a warm service.
        for path in paths:
            response = await client.get(path)
            response.raise_for_status()

        async def request(index):
            async with semaphore:
                started = perf_counter()
                try:
                    response = await client.get(paths[index % len(paths)])
                    status = str(response.status_code)
                    payload = response.json() if response.status_code == 200 else {}
                    valid = response.status_code == 200 and isinstance(payload, dict)
                    if args.profile == "search":
                        valid = valid and bool(payload.get("results"))
                except (httpx.HTTPError, ValueError):
                    status, valid = "transport_error", False
                results.append(
                    {
                        "latencyMs": (perf_counter() - started) * 1000,
                        "status": status,
                        "valid": valid,
                    }
                )

        started = perf_counter()
        await asyncio.gather(*(request(i) for i in range(args.requests)))
        elapsed = perf_counter() - started
    latencies = [v["latencyMs"] for v in results]
    return {
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "baseUrl": args.base_url,
        "profile": args.profile,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "warmupRequests": len(paths),
        "seconds": round(elapsed, 3),
        "requestsPerSecond": round(len(results) / elapsed, 2),
        "p50Ms": percentile(latencies, 0.5),
        "p95Ms": percentile(latencies, 0.95),
        "maxMs": round(max(latencies), 2),
        "statuses": dict(Counter(v["status"] for v in results)),
        "failures": sum(not v["valid"] for v in results),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--profile", choices=PROFILES, default="reading")
    parser.add_argument("--requests", type=int, default=40)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.requests <= 180 or not 1 <= args.concurrency <= 16:
        parser.error(
            "Use 1–180 requests and 1–16 concurrent clients. Keep production rate limits in mind."
        )
    report = asyncio.run(run(args))
    content = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(content)
    print(content)
    raise SystemExit(0 if not report["failures"] else 1)
