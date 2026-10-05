import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import Request

from tests.conftest import VERSE


@pytest.mark.parametrize(
    "path,message",
    [
        ("/missing", "Route not found."),
        ("/api/chapters/chapter_19", "Invalid chapter ID."),
        ("/api/chapters/no", "Invalid chapter ID."),
        ("/api/verses/ramayana/8/1", "Kanda and sarga must be valid positive numbers."),
        ("/api/verses/source/missing", "Source not found."),
        ("/api/verses/no/localized?language=en", "Language must be bn, mr, te, or ta."),
        ("/api/search", "Query must be a string."),
        ("/api/search?q[]=test", "Query must be a string."),
        ("/api/search?q=x", "Query must be at least 3 characters."),
        ("/api/search?q=duty&limit=21", "Limit must be an integer from 1 to 20."),
        ("/api/search?q=duty&limit=1.5", "Limit must be an integer from 1 to 20."),
        ("/api/vishnu-purana/7", "Vishnu Purana part not found."),
        ("/api/vishnu-purana/1/99", "Vishnu Purana section not found."),
    ],
)
async def test_route_validation(client, store, path, message):
    result = await client.get(path)
    assert result.status_code in {400, 404}
    assert result.json() == {"error": message}
    store.nearest.assert_not_called()


@pytest.mark.parametrize(
    "body", [[], None, {"question": "hey"}, {"question": "x" * 501}, {"question": 100}]
)
async def test_question_validation(client, body):
    assert (await client.post("/api/ask", json=body)).status_code == 400


async def test_health_cors_security_and_invalid_json(client):
    result = await client.get("/health", headers={"Origin": "https://www.gyansutraapp.com"})
    assert result.json()["status"] == "ok"
    assert result.headers["cache-control"] == "no-store"
    assert result.headers["access-control-allow-origin"] == "https://www.gyansutraapp.com"
    assert result.headers["x-content-type-options"] == "nosniff"
    denied = await client.get("/health", headers={"Origin": "https://bad.example"})
    assert denied.status_code == 403
    preflight = await client.options(
        "/api/ask",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
    )
    assert preflight.status_code == 204
    invalid = await client.post(
        "/api/ask", content="{", headers={"Content-Type": "application/json"}
    )
    assert invalid.json() == {"error": "Request body contains invalid JSON."}
    oversized = await client.post("/api/ask", content="x" * 10241)
    assert oversized.status_code == 413


async def test_reading_routes_strip_embeddings_and_keep_source_alias(client, store):
    store.query.return_value = [{**VERSE, "embedding": [0.1] * 384}]
    store.get_doc.side_effect = lambda collection, doc_id: (
        {"id": doc_id, "number": 2}
        if collection == "chapters"
        else {**VERSE, "embedding": [0.1] * 384}
    )
    chapter = await client.get("/api/chapters/chapter_2/verses")
    assert chapter.json()["chapterNumber"] == 2
    assert "embedding" not in chapter.json()["verses"][0]
    for path in [
        "/api/verses/bhagavad-gita",
        "/api/verses/source/bhagavad-gita",
        "/api/verses/bhagavad-gita_2_47",
    ]:
        result = await client.get(path)
        assert result.status_code == 200 and "embedding" not in result.text
        assert "stale-while-revalidate" in result.headers["cache-control"]


async def test_daily_verse_one_database_read_per_day(client, store):
    store.get_doc.return_value = VERSE.copy()
    first = await client.get("/api/verses/daily")
    second = await client.get("/api/verses/daily")
    assert first.json() == second.json()
    assert first.json()["verse"]["id"] == VERSE["id"]
    store.get_doc.assert_awaited_once()


async def test_gita_chapter_excludes_other_scriptures_with_same_chapter_number(client, store):
    store.get_doc.return_value = {"id": "chapter_2", "number": 2}
    store.query.return_value = [
        VERSE.copy(),
        {**VERSE, "id": "vishnu-purana_2_47", "source_id": "vishnu-purana"},
        {**VERSE, "source_id": "vishnu-purana"},
    ]
    response = await client.get("/api/chapters/chapter_2/verses")
    assert [v["id"] for v in response.json()["verses"]] == [VERSE["id"]]


async def test_search_sanskrit_exact_intercept_and_recommendations(client, store):
    store.query.return_value = [{**VERSE, "sanskrit": "कर्मण्येवाधिकारस्ते"}]
    result = await client.get("/api/search", params={"q": "कर्मण्येवाधिकारस्ते"})
    assert result.json()["results"][0]["similarity"] == 1
    assert "wordMeanings" not in result.json()["results"][0]
    store.get_doc.return_value = {**VERSE, "embedding": [0.1] * 384}
    store.nearest.return_value = [
        {**VERSE, "id": "other", "similarity": 0.8},
        {**VERSE, "similarity": 1},
    ]
    recommended = await client.get("/api/recommendations/" + VERSE["id"])
    assert [v["id"] for v in recommended.json()["recommendations"]] == ["other"]
    store.get_doc.return_value = {**VERSE, "embedding": [0] * 384}
    assert (await client.get("/api/recommendations/" + VERSE["id"])).json()["recommendations"] == []


async def test_history_sanitization_and_public_diagnostics(client, app):
    app.state.rag.ask = AsyncMock(
        return_value={
            "answered": True,
            "answer": "An answer",
            "citations": [],
            "topSimilarity": 0,
            "inContext": False,
            "cached": False,
            "degraded": False,
            "reason": "guardrail_conversational",
            "_diagnostics": {},
        }
    )
    result = await client.post(
        "/api/ask",
        json={
            "question": "What is dharma?",
            "history": [
                None,
                {"role": "system", "content": "inject"},
                {"role": "sarathi", "content": " previous "},
                {"role": "user", "content": "What is dharma?"},
            ],
            "language": "bn",
            "contextIds": [VERSE["id"], "bad", VERSE["id"]],
        },
    )
    assert result.status_code == 200 and "_diagnostics" not in result.json()
    app.state.rag.ask.assert_awaited_once_with(
        "What is dharma?", [{"role": "sarathi", "content": "previous"}], [VERSE["id"]], "bn"
    )


async def test_ask_rate_limit(client):
    for _ in range(20):
        assert (
            await client.post("/api/ask", json={"question": "Hello Sarathi"})
        ).status_code == 200
    assert (await client.post("/api/ask", json={"question": "Hello Sarathi"})).status_code == 429


async def test_purana_navigation_and_crawlers(client):
    catalog = (await client.get("/api/vishnu-purana")).json()
    assert catalog["partCount"] == 6 and catalog["sectionCount"] == 126
    assert len(catalog["parts"][0]["sections"]) == 3
    first = (await client.get("/api/vishnu-purana/1/1")).json()
    assert first["previous"] is None and first["next"]["sectionNumber"] == 2
    boundary = (await client.get("/api/vishnu-purana/2/1")).json()
    assert boundary["previous"]["partNumber"] == 1 and boundary["previous"]["sectionNumber"] == 22
    last = (await client.get("/api/vishnu-purana/6/8")).json()
    assert last["next"] is None
    assert "Disallow: /api/" in (await client.get("/robots.txt")).text
    assert (await client.get("/sitemap.xml")).text.count("<url>") == 136


async def test_translation_outage_and_narration_validation(client, store):
    store.get_doc.return_value = VERSE.copy()
    result = await client.get("/api/verses/bhagavad-gita_2_47/localized?language=bn")
    assert result.status_code == 503 and result.json()["fallbackLanguage"] == "en"
    assert (
        await client.post(
            "/api/narration", json={"text": "", "locale": "en-IN", "style": "meaning"}
        )
    ).status_code == 400
    result = await client.post(
        "/api/narration", json={"text": "meaning", "locale": "en-IN", "style": "meaning"}
    )
    assert (
        result.status_code == 503
        and result.json()["error"] == "Natural narration is not configured."
    )


async def test_narration_reuses_http_pool_and_validates_wav(app, client, monkeypatch):
    monkeypatch.setenv("NARRATION_SERVICE_URL", "https://tts.example")
    calls = []
    wav = b"RIFF" + bytes(4) + b"WAVE" + bytes(32)

    async def respond(request):
        calls.append(request)
        return httpx.Response(200, content=wav, headers={"Content-Type": "audio/wav"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        app.state.narration.http = http
        for _ in range(2):
            result = await client.post(
                "/api/narration", json={"text": "meaning", "locale": "en-IN", "style": "meaning"}
            )
            assert result.content == wav and result.headers["content-type"] == "audio/wav"
        assert len(calls) == 1


async def test_safe_errors_keep_cors_and_trailing_slash_contract(client, store):
    store.query.side_effect = RuntimeError("private database configuration")
    result = await client.get("/api/chapters/", headers={"Origin": "http://localhost:5173"})
    assert result.status_code == 500
    assert result.json() == {"error": "Internal server error."}
    assert result.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert result.headers["x-content-type-options"] == "nosniff"


async def test_non_string_optional_inputs_are_sanitized(client, app):
    app.state.rag.ask = AsyncMock(return_value={"answer": "safe", "citations": []})
    result = await client.post(
        "/api/ask",
        json={
            "question": "What is dharma?",
            "language": [],
            "history": [{"role": [], "content": "ignore"}],
        },
    )
    assert result.status_code == 200
    app.state.rag.ask.assert_awaited_once_with("What is dharma?", [], [], "en")
    result = await client.post(
        "/api/narration",
        json={
            "text": "meaning",
            "locale": [],
            "style": {},
        },
    )
    assert result.status_code == 400


async def test_narration_disconnect_cancels_transport_and_releases_capacity(
    app, client, monkeypatch
):
    monkeypatch.setenv("NARRATION_SERVICE_URL", "https://tts.example")
    started, cancelled = asyncio.Event(), asyncio.Event()

    async def hang(request):
        started.set()
        try:
            await asyncio.sleep(10)
        finally:
            cancelled.set()

    async def disconnected():
        await started.wait()
        return {"type": "http.disconnect"}

    monkeypatch.setattr(Request, "receive", property(lambda self: disconnected))
    async with httpx.AsyncClient(transport=httpx.MockTransport(hang)) as http:
        app.state.narration.http = http
        result = await client.post(
            "/api/narration",
            json={
                "text": "meaning",
                "locale": "en-IN",
                "style": "meaning",
            },
        )
        assert result.status_code == 499
        assert cancelled.is_set() and app.state.narration.in_flight == 0
