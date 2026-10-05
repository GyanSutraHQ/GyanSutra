"""Asynchronous official Firestore client; retain collection/index contracts."""

import json
import math
import os

from google.cloud.firestore_v1 import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector
from google.oauth2 import service_account

from .config import ROOT
from .embedding import DIMENSIONS

FIELDS = "chapterNumber verseNumber book kanda kandaNumber sarga shlokaNumber partNumber partTitle sectionNumber passageNumber storyTitle storySummary sanskrit transliteration translationEnglish translationHindi explanationEnglish comments wordMeanings detailedExplanations tags".split()
TEXT_FIELDS = "sanskrit transliteration translationEnglish translationHindi explanationEnglish comments".split()
ARRAY_FIELDS = "wordMeanings detailedExplanations tags".split()


def retrieved(doc: dict, similarity: float = 1) -> dict:
    result = {key: doc[key] for key in FIELDS if key in doc}
    result.update(id=doc["id"], similarity=similarity)
    for key in TEXT_FIELDS:
        result[key] = doc.get(key) or ""
    for key in ARRAY_FIELDS:
        result[key] = doc.get(key) or []
    return result


class ScriptureStore:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self) -> AsyncClient:
        if self._client is None:
            project = os.getenv("FIREBASE_PROJECT_ID")
            if os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON"):
                info = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT_JSON"])
                credentials = service_account.Credentials.from_service_account_info(info)
                project = project or info.get("project_id")
            elif os.getenv("NODE_ENV") != "production" and os.getenv(
                "FIREBASE_SERVICE_ACCOUNT_PATH"
            ):
                credentials = service_account.Credentials.from_service_account_file(
                    str(ROOT / os.environ["FIREBASE_SERVICE_ACCOUNT_PATH"])
                )
                project = project or credentials.project_id
            else:
                raise RuntimeError(
                    "Firebase credentials not found. Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH."
                )
            self._client = AsyncClient(project=project, credentials=credentials)
        return self._client

    async def get_doc(self, collection: str, doc_id: str) -> dict | None:
        snap = await self.client.collection(collection).document(doc_id).get()
        return {"id": snap.id, **snap.to_dict()} if snap.exists else None

    async def query(self, collection: str, filters=(), order=None, limit=None) -> list[dict]:
        query = self.client.collection(collection)
        for field, op, value in filters:
            query = query.where(filter=FieldFilter(field, op, value))
        if order:
            query = query.order_by(order)
        if limit:
            query = query.limit(limit)
        return [{"id": snap.id, **snap.to_dict()} async for snap in query.stream()]

    async def nearest(self, vector: list[float], top_k: int = 8) -> list[dict]:
        if (
            len(vector) != DIMENSIONS
            or not all(math.isfinite(v) for v in vector)
            or not any(vector)
        ):
            raise ValueError(
                f"Query vector must contain exactly {DIMENSIONS} finite, non-zero values."
            )
        query = (
            self.client.collection("verses")
            .select(FIELDS + ["_distance"])
            .find_nearest(
                vector_field="embedding",
                query_vector=Vector(vector),
                limit=min(max(top_k, 1), 20),
                distance_measure=DistanceMeasure.COSINE,
                distance_result_field="_distance",
            )
        )
        return [
            retrieved(
                {"id": snap.id, **snap.to_dict()},
                max(0, min(1, 1 - snap.to_dict().get("_distance", 1))),
            )
            async for snap in query.stream()
        ]

    async def batch_write(self, collection: str, items: list[dict]) -> None:
        for start in range(0, len(items), 499):
            batch = self.client.batch()
            for item in items[start : start + 499]:
                batch.set(self.client.collection(collection).document(item["id"]), item["data"])
            await batch.commit()

    async def log(self, data: dict) -> None:
        await self.client.collection("qaLog").add(data)

    async def close(self) -> None:
        if self._client is not None:
            api = self._client._firestore_api_internal
            if api is not None:
                await api.transport.close()
            self._client.close()
            self._client = None
