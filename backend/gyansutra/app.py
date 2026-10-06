"""FastAPI application with frontend-compatible routes and response fields."""

import asyncio
import json
import logging
import math
import os
import re
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
from fastapi import BackgroundTasks, FastAPI, Request
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, Response

from .cache import ServiceError, SingleFlight
from .config import ROOT, enabled
from .embedding import LocalScriptureEmbeddings
from .firestore import ScriptureStore, retrieved
from .generation import GenerationService
from .middleware import ApiMiddleware
from .narration import NarrationService
from .rag import CITATION_FIELDS, LANGUAGES, RagService
from .text import SOURCES
from .translation import TARGETS, TranslationService

READ_CACHE = {"Cache-Control": "public, max-age=300, stale-while-revalidate=3600"}
PURANA_CACHE = {"Cache-Control": "public, max-age=3600, stale-while-revalidate=86400"}
SECTION_CACHE = {"Cache-Control": "public, max-age=86400, stale-while-revalidate=604800"}
COUNTS = [47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 35, 27, 20, 24, 28, 78]


def error(message, status=400, **extra):
    return JSONResponse({"error": message, **extra}, status_code=status)


def public(verse):
    return {k: v for k, v in verse.items() if k != "embedding"}


def summary(verse):
    return {
        k: v
        for k, v in verse.items()
        if k not in {"comments", "detailedExplanations", "wordMeanings"}
    }


def positive(value):
    return (
        int(value)
        if isinstance(value, str)
        and re.fullmatch(r"[0-9]+", value)
        and 0 < int(value) <= 9007199254740991
        else None
    )


async def body_object(request):
    try:
        body = await request.json()
    except (ValueError, UnicodeDecodeError):
        return None, error("Request body contains invalid JSON.")
    if not isinstance(body, dict):
        return None, error("Request body must be a JSON object.")
    return body, None


def create_app(store=None, embeddings=None, generation=None, http_client=None):
    store = store or ScriptureStore()
    embeddings = embeddings or LocalScriptureEmbeddings()
    http = http_client or httpx.AsyncClient(
        limits=httpx.Limits(max_connections=30, max_keepalive_connections=10), timeout=30
    )
    generation = generation or GenerationService(http)
    rag = RagService(store, embeddings, generation)
    translation, narration = TranslationService(generation), NarrationService(http)
    corpus = json.loads((ROOT / "data/vishnu-purana.json").read_text())
    metadata = {k: v for k, v in corpus.items() if k != "parts"}
    daily = {}
    daily_flight = SingleFlight()
    started = time.monotonic()

    @asynccontextmanager
    async def lifespan(app):
        prewarm = None
        if enabled("EMBEDDING_PREWARM") and os.getenv("NODE_ENV") != "test":

            async def warm():
                async def stage(service, label):
                    try:
                        await service.prewarm()
                    except Exception:
                        logging.exception("%s background prewarm failed", label)

                jobs = [stage(embeddings, "Embedding")]
                if rag.lexical:
                    jobs.append(stage(rag.lexical, "Keyword index"))
                await asyncio.gather(*jobs)

            prewarm = asyncio.create_task(warm())
        try:
            yield
        finally:
            if prewarm:
                prewarm.cancel()
                await asyncio.gather(prewarm, return_exceptions=True)
            await rag.close()
            await translation.flight.close()
            await daily_flight.close()
            await store.close()
            generation.close()
            await http.aclose()
            embeddings.close()

    app = FastAPI(
        title="Gyan Sutra API", version="2.0.0", lifespan=lifespan, redirect_slashes=False
    )
    app.state.rag, app.state.store = rag, store
    app.state.translation, app.state.narration = translation, narration
    app.add_middleware(ApiMiddleware)

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return error(
            "Route not found." if exc.status_code == 404 else str(exc.detail), exc.status_code
        )

    @app.exception_handler(Exception)
    async def unhandled(request, exc):
        logging.error("API request failed", exc_info=exc)
        return error("Internal server error.", 500)

    @app.get("/health")
    async def health():
        return JSONResponse(
            {
                "status": "ok",
                "timestamp": datetime.now(timezone.utc)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z"),
                "uptimeSeconds": int(time.monotonic() - started),
            },
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/api/sources")
    async def sources():
        return SOURCES

    @app.get("/api/chapters")
    async def chapters():
        return {"chapters": await store.query("chapters", order="number")}

    def valid_chapter(doc_id):
        match = re.fullmatch(r"chapter_([0-9]{1,2})", doc_id)
        return bool(match and 1 <= int(match[1]) <= 18)

    @app.get("/api/chapters/{doc_id}")
    async def chapter(doc_id: str):
        if not valid_chapter(doc_id):
            return error("Invalid chapter ID.")
        value = await store.get_doc("chapters", doc_id)
        return value or error("Chapter not found.", 404)

    @app.get("/api/chapters/{doc_id}/verses")
    async def chapter_verses(doc_id: str):
        if not valid_chapter(doc_id):
            return error("Invalid chapter ID.")
        value = await store.get_doc("chapters", doc_id)
        if not value:
            return error("Chapter not found.", 404)
        verses = await store.query(
            "verses", [("chapterNumber", "==", value["number"])], order="verseNumber"
        )
        prefix = f"bhagavad-gita_{value['number']}_"
        verses = [
            v
            for v in verses
            if v.get("id", "").startswith(prefix)
            and v.get("source_id", "bhagavad-gita") == "bhagavad-gita"
        ]
        return {"chapterNumber": value["number"], "verses": [public(v) for v in verses]}

    @app.get("/api/verses/daily")
    async def daily_verse():
        day = int(time.time() // 86400)

        async def load():
            offset = day % sum(COUNTS)
            chapter_number = 1
            for chapter_number, count in enumerate(COUNTS, 1):
                if offset < count:
                    break
                offset -= count
            value = await store.get_doc("verses", f"bhagavad-gita_{chapter_number}_{offset + 1}")
            if value:
                keys = set(CITATION_FIELDS) - {
                    "similarity",
                    "partNumber",
                    "partTitle",
                    "sectionNumber",
                    "passageNumber",
                    "storyTitle",
                }
                daily.clear()
                daily.update(
                    day=day,
                    verse={
                        k: v
                        for k, v in retrieved(value).items()
                        if k in keys or k == "explanationEnglish"
                    },
                )
            return value

        if daily.get("day") != day:
            if not await daily_flight.run(str(day), load):
                return error("Internal server error.", 503)
        return JSONResponse({"verse": daily["verse"]}, headers=READ_CACHE)

    @app.get("/api/verses/ramayana/{kanda}/{sarga}")
    async def ramayana(kanda: str, sarga: str):
        if not positive(kanda) or not positive(sarga) or int(kanda) > 7:
            return error("Kanda and sarga must be valid positive numbers.")
        verses = await store.query(
            "verses",
            [
                ("book", "==", "ramayana"),
                ("kandaNumber", "==", int(kanda)),
                ("sarga", "==", int(sarga)),
            ],
        )
        return {"verses": sorted((public(v) for v in verses), key=lambda v: v["shlokaNumber"])}

    async def source_verses(source_id):
        if source_id not in {v["id"] for v in SOURCES}:
            return error("Source not found.", 404)
        verses = await store.query("verses", [("source_id", "==", source_id)])
        verses = sorted(
            (public(v) for v in verses),
            key=lambda v: (v.get("chapterNumber", 0), v.get("verseNumber", 0)),
        )
        return JSONResponse({"verses": verses}, headers=READ_CACHE)

    @app.get("/api/verses/source/{source_id}")
    async def source_route(source_id: str):
        return await source_verses(source_id)

    @app.get("/api/verses/{doc_id}/localized")
    async def localized(doc_id: str, request: Request):
        language = request.query_params.get("language", "").strip().lower()
        if len(doc_id) > 256:
            return error("Invalid verse ID.")
        if language not in TARGETS:
            return error("Language must be bn, mr, te, or ta.")
        verse = await store.get_doc("verses", doc_id)
        if not verse:
            return error("Verse not found.", 404)
        try:
            return JSONResponse(
                {"content": await translation.translate(verse, language)}, headers=SECTION_CACHE
            )
        except Exception:
            return error(
                "The requested translation is temporarily unavailable.",
                503,
                fallbackLanguage="en" if verse.get("translationEnglish") else "hi",
            )

    @app.get("/api/verses/{doc_id}")
    async def verse(doc_id: str):
        if doc_id in {v["id"] for v in SOURCES}:
            return await source_verses(doc_id)
        if len(doc_id) > 256:
            return error("Invalid verse ID.")
        value = await store.get_doc("verses", doc_id)
        return (
            JSONResponse(public(value), headers=READ_CACHE)
            if value
            else error("Verse not found.", 404)
        )

    @app.get("/api/search")
    async def search(request: Request):
        values = request.query_params.getlist("q")
        if len(values) != 1 or any(k.startswith("q[") for k in request.query_params):
            return error("Query must be a string.")
        query = values[0].strip()
        if len(query) < 3:
            return error("Query must be at least 3 characters.")
        if len(query) > 500:
            return error("Query is too long (max 500 characters).")
        limit = request.query_params.get("limit")
        if limit is not None and (
            not positive(limit)
            or int(limit) > 20
            or len(request.query_params.getlist("limit")) != 1
        ):
            return error("Limit must be an integer from 1 to 20.")
        limit = int(limit or "10")
        vector = await embeddings.aembed_query(query)
        results = await store.nearest(vector, min(limit * 2, 20))
        gita = re.search(r"chapter\s+(\d+)(?:\s*,?\s*|\s+and\s+)verse\s+(\d+)", query, re.I)
        ram = re.search(
            r"kanda\s+(\d+)(?:\s*,?\s*|\s+and\s+)sarga\s+(\d+)(?:\s*,?\s*|\s+and\s+)(?:shloka|verse)\s+(\d+)",
            query,
            re.I,
        )
        for book, match in [("bhagavad-gita", gita), ("valmiki-ramayana", ram)]:
            if match:
                value = await store.get_doc(
                    "verses", book + "_" + "_".join(str(int(n)) for n in match.groups())
                )
                if value:
                    results = [retrieved(value)] + [v for v in results if v["id"] != value["id"]]
        devanagari = bool(re.search(r"[\u0900-\u097f]", query))
        if devanagari:
            exact = await store.query("verses", [("sanskrit", "==", query)], limit=1)
            if exact:
                results = [retrieved(exact[0])] + [v for v in results if v["id"] != exact[0]["id"]]
        values = [
            summary(v) for v in results if v.get("similarity", 0) >= (0.35 if devanagari else 0.55)
        ][:limit]
        return {"query": query, "total": len(values), "results": values}

    @app.post("/api/ask")
    async def ask(request: Request, tasks: BackgroundTasks):
        body, invalid = await body_object(request)
        if invalid:
            return invalid
        question = body.get("question")
        if not isinstance(question, str) or len(question.strip()) < 5:
            return error("Please provide a question (at least 5 characters).")
        question = question.strip()
        if len(question) > 500:
            return error("Question is too long (max 500 characters).")
        raw_history = body.get("history") if isinstance(body.get("history"), list) else []
        history = [
            {"role": m["role"], "content": m["content"].strip()[:1000]}
            for m in raw_history
            if isinstance(m, dict)
            and m.get("role") in ("user", "sarathi")
            and isinstance(m.get("content"), str)
            and m["content"].strip()
        ]
        if history and history[-1] == {"role": "user", "content": question}:
            history.pop()
        raw_ids = body.get("contextIds") if isinstance(body.get("contextIds"), list) else []
        ids = list(
            dict.fromkeys(
                v.strip()
                for v in raw_ids
                if isinstance(v, str)
                and re.fullmatch(r"(?:bhagavad-gita|valmiki-ramayana)_\d+_\d+(?:_\d+)?", v.strip())
            )
        )[:4]
        language = body.get("language")
        language = language if isinstance(language, str) and language in LANGUAGES else "en"
        result = await rag.ask(question, history[-4:], ids, language)
        tasks.add_task(rag.log, question, result)
        return JSONResponse(
            {k: v for k, v in result.items() if k != "_diagnostics"},
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/api/recommendations/{doc_id}")
    async def recommendations(doc_id: str, request: Request):
        kind = "story" if request.query_params.get("type") == "story" else "verse"
        if len(doc_id) > 256:
            return error("Invalid content ID.")
        source = await store.get_doc("stories" if kind == "story" else "verses", doc_id)
        if not source:
            return error(f"{kind} not found.", 404)
        raw = source.get("embedding")
        if hasattr(raw, "to_map"):
            raw = raw.to_map().get("value")
        if isinstance(raw, dict):
            raw = [
                v.get("doubleValue", v.get("integerValue"))
                for v in raw.get("arrayValue", {}).get("values", [])
            ]
        try:
            vector = [float(v) for v in raw]
            valid = len(vector) == 384 and all(math.isfinite(v) for v in vector) and any(vector)
        except (TypeError, ValueError):
            valid = False
        values = await store.nearest(vector, 11) if valid else []
        return {
            "contentId": doc_id,
            "recommendations": [
                summary(v) for v in values if v["id"] != doc_id and v["similarity"] >= 0.6
            ][:6],
        }

    @app.post("/api/narration")
    async def audio(request: Request):
        body, invalid = await body_object(request)
        if invalid:
            return invalid
        text, locale, style = body.get("text"), body.get("locale"), body.get("style")
        if (
            not isinstance(text, str)
            or not text.strip()
            or len(text) > 360
            or locale not in ("sa-IN", "en-IN", "hi-IN", "bn-IN", "mr-IN", "te-IN", "ta-IN")
            or style not in ("recitation", "meaning")
        ):
            return error("Provide up to 360 characters, a supported locale, and a narration style.")
        try:
            # Match the previous proxy's abort-on-disconnect behavior.
            async def disconnected():
                while True:
                    message = await request.receive()
                    if message["type"] == "http.disconnect":
                        return

            job = asyncio.create_task(narration.audio(text, locale, style))
            watcher = asyncio.create_task(disconnected())
            try:
                done, _ = await asyncio.wait((job, watcher), return_when=asyncio.FIRST_COMPLETED)
                if watcher in done and job not in done:
                    return Response(status_code=499)
                value = await job
            finally:
                job.cancel()
                watcher.cancel()
                await asyncio.gather(job, watcher, return_exceptions=True)
            return Response(
                value, media_type="audio/wav", headers={"Cache-Control": "private, max-age=86400"}
            )
        except ServiceError as exc:
            return error(str(exc), 503)

    def section_summary(section):
        return {k: v for k, v in section.items() if k not in {"paragraphs", "footnotes"}}

    @app.get("/api/vishnu-purana")
    async def purana():
        parts = [
            {
                **{k: v for k, v in p.items() if k != "sections"},
                "sections": [section_summary(s) for s in p["sections"][:3]],
            }
            for p in corpus["parts"]
        ]
        return JSONResponse({**metadata, "parts": parts}, headers=PURANA_CACHE)

    def find_part(value):
        try:
            return next((p for p in corpus["parts"] if p["number"] == float(value)), None)
        except ValueError:
            return None

    @app.get("/api/vishnu-purana/{part_number}")
    async def part(part_number: str):
        value = find_part(part_number)
        if not value:
            return error("Vishnu Purana part not found.", 404)
        return JSONResponse(
            {
                **metadata,
                "part": {**value, "sections": [section_summary(s) for s in value["sections"]]},
            },
            headers=PURANA_CACHE,
        )

    @app.get("/api/vishnu-purana/{part_number}/{section_number}")
    async def section(part_number: str, section_number: str):
        value = find_part(part_number)
        try:
            section_value = (
                next(
                    (s for s in value["sections"] if s["sectionNumber"] == float(section_number)),
                    None,
                )
                if value
                else None
            )
        except ValueError:
            section_value = None
        if not section_value:
            return error("Vishnu Purana section not found.", 404)
        p, s = value["number"], section_value["sectionNumber"]
        previous = (
            value["sections"][s - 2]
            if s > 1
            else corpus["parts"][p - 2]["sections"][-1]
            if p > 1
            else None
        )
        following = (
            value["sections"][s]
            if s < len(value["sections"])
            else corpus["parts"][p]["sections"][0]
            if p < len(corpus["parts"])
            else None
        )
        return JSONResponse(
            {
                **metadata,
                "part": {
                    k: value[k] for k in ("number", "roman", "title", "theme", "sectionCount")
                },
                "section": section_value,
                "previous": section_summary(previous) if previous else None,
                "next": section_summary(following) if following else None,
            },
            headers=SECTION_CACHE,
        )

    @app.get("/robots.txt")
    async def robots():
        return Response(
            "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /login/\nDisallow: /api/\nDisallow: /user/settings/\n\nSitemap: https://gyansutraapp.com/sitemap.xml",
            media_type="text/plain",
        )

    @app.get("/sitemap.xml")
    async def sitemap():
        today = datetime.now(timezone.utc).date().isoformat()
        paths = [
            (p, ".8", "monthly") for p in ["/", "/bhagavad-gita", "/ramayana", "/vishnu-purana"]
        ]
        for p, count in enumerate([22, 16, 18, 24, 38, 8], 1):
            paths.append((f"/vishnu-purana/{p}", ".9", "monthly"))
            paths.extend((f"/vishnu-purana/{p}/{s}", ".7", "yearly") for s in range(1, count + 1))
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += (
            "".join(
                f"  <url>\n    <loc>https://gyansutraapp.com{path}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>{frequency}</changefreq>\n    <priority>0{priority}</priority>\n  </url>\n"
                for path, priority, frequency in paths
            )
            + "</urlset>"
        )
        return Response(xml, media_type="application/xml")

    return app


app = create_app()
