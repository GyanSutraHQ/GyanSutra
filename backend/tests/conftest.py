import os
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from gyansutra.app import create_app
from gyansutra.embedding import LocalScriptureEmbeddings
from gyansutra.generation import GenerationService

VERSE = {
    "id": "bhagavad-gita_2_47",
    "chapterNumber": 2,
    "verseNumber": 47,
    "sanskrit": "कर्मण्येवाधिकारस्ते",
    "transliteration": "karmaṇy evādhikāras te",
    "translationEnglish": "You have a right to action, but not to its fruits.",
    "translationHindi": "तुम्हारा अधिकार कर्म में है, फल में नहीं।",
    "similarity": 0.91,
    "wordMeanings": [],
    "detailedExplanations": [],
    "tags": ["duty"],
    "source_id": "bhagavad-gita",
}


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    for key in list(os.environ):
        if key.startswith(
            ("RAG_", "GEMINI_", "GROK_", "XAI_", "OPENROUTER_", "EMBEDDING_", "NARRATION_")
        ):
            monkeypatch.delenv(key)
    monkeypatch.setenv("NODE_ENV", "test")
    monkeypatch.setenv("EMBEDDING_MODEL_ID", "Xenova/gte-small")


@pytest.fixture
def store():
    value = Mock()
    value.get_doc = AsyncMock(return_value=None)
    value.query = AsyncMock(return_value=[])
    value.nearest = AsyncMock(return_value=[VERSE.copy()])
    value.log = AsyncMock()
    value.close = AsyncMock()
    return value


@pytest.fixture
def embeddings():
    value = Mock(spec=LocalScriptureEmbeddings)
    value.aembed_query = AsyncMock(return_value=[0.01] * 384)
    value.prewarm = AsyncMock()
    return value


@pytest.fixture
async def app(store, embeddings):
    http = httpx.AsyncClient()
    value = create_app(store=store, embeddings=embeddings, http_client=http)
    async with value.router.lifespan_context(value):
        yield value


@pytest.fixture
async def client(app):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as value:
        yield value


@pytest.fixture
async def provider(monkeypatch):
    calls = []
    responses = []

    async def handle(request):
        calls.append(request)
        if responses:
            value = responses.pop(0)
            if isinstance(value, Exception):
                raise value
            return value
        return httpx.Response(
            200,
            json={
                "id": "chat-1",
                "object": "chat.completion",
                "model": "test-model",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": "Act with care and attention. [S1]",
                        },
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
        services = []

        def factory():
            service = GenerationService(http)
            services.append(service)
            return service

        try:
            yield factory, calls, responses
        finally:
            for service in services:
                service.close()
