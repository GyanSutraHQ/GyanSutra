"""LangChain embeddings from the committed quantized GTE ONNX model."""

import asyncio
import hashlib
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import onnxruntime as ort
from langchain_core.embeddings import Embeddings
from tokenizers import Tokenizer

from .cache import TTLCache
from .config import ROOT, integer

ort.disable_telemetry_events()

MODEL = os.getenv("EMBEDDING_MODEL_ID", "Xenova/gte-small").strip()
DIMENSIONS = integer("EMBEDDING_DIMENSIONS", 384, 1, 2048)


class LocalScriptureEmbeddings(Embeddings):
    def __init__(self) -> None:
        self.cache = TTLCache(
            integer("EMBEDDING_CACHE_MAX_ENTRIES", 500, 1, 5000),
            integer("EMBEDDING_CACHE_TTL_SECONDS", 86400, 1, 604800),
        )
        self._lock = threading.Lock()
        self._session = None
        self._tokenizer = None
        self._loading = False
        self._maximum_length = 512
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="embedding")

    def load(self) -> None:
        if self._session is not None:
            return
        path = (ROOT / "models" / MODEL).resolve()
        if not path.is_relative_to((ROOT / "models").resolve()):
            raise ValueError("Embedding model must be inside backend/models.")
        self._loading = True
        try:
            tokenizer = Tokenizer.from_file(str(path / "tokenizer.json"))
            # The serialized tokenizer contains fixed padding. Transformers.js
            # overrides it to the current single-input length. Keep that behavior:
            # padded inputs change dynamic quantization even with a masked mean.
            tokenizer.no_padding()
            config = json.loads((path / "tokenizer_config.json").read_text())
            # Transformers.js truncates after adding special tokens rather than
            # reserving a trailing SEP token. Preserve long-passage vectors too.
            tokenizer.no_truncation()
            self._maximum_length = config.get("model_max_length", 512)
            options = ort.SessionOptions()
            options.intra_op_num_threads = integer("EMBEDDING_THREADS", 2, 1, 32)
            options.inter_op_num_threads = 1
            session = ort.InferenceSession(
                str(path / "onnx/model_quantized.onnx"),
                sess_options=options,
                providers=["CPUExecutionProvider"],
            )
            self._tokenizer, self._session = tokenizer, session
        finally:
            self._loading = False

    def _embed(self, text: str, kind: str) -> list[float]:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text must be a valid, non-empty string.")
        if kind not in {"query", "passage"}:
            raise ValueError("Embedding inputType must be either query or passage.")
        prefix = os.getenv(f"EMBEDDING_{'QUERY' if kind == 'query' else 'PASSAGE'}_PREFIX", "")
        prepared = prefix + " ".join(text.split())
        key = hashlib.sha256(f"{MODEL}\0{kind}\0{prepared}".encode()).hexdigest()
        with self._lock:
            if key in self.cache:
                return self.cache[key].copy()
            self.load()
            encoding = self._tokenizer.encode(prepared)
            inputs = {
                "input_ids": np.array([encoding.ids[: self._maximum_length]], dtype=np.int64),
                "attention_mask": np.array(
                    [encoding.attention_mask[: self._maximum_length]], dtype=np.int64
                ),
                "token_type_ids": np.array(
                    [encoding.type_ids[: self._maximum_length]], dtype=np.int64
                ),
            }
            feeds = {item.name: inputs[item.name] for item in self._session.get_inputs()}
            output = self._session.run(None, feeds)[0]
            # Match Transformers.js float32 masked mean pooling and L2 normalization.
            mask = inputs["attention_mask"][..., None].astype(np.float32)
            pooled = (output * mask).sum(axis=1) / mask.sum(axis=1)
            pooled /= np.linalg.norm(pooled, axis=1, keepdims=True)
            vector = pooled[0].tolist()
            if len(vector) != DIMENSIONS or not all(np.isfinite(vector)):
                raise ValueError(f"Embedding model returned an invalid {len(vector)}-value vector.")
            self.cache[key] = vector
            return vector.copy()

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text, "query")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text, "passage") for text in texts]

    async def aembed_query(self, text: str) -> list[float]:
        return await asyncio.get_running_loop().run_in_executor(
            self._executor, self.embed_query, text
        )

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.get_running_loop().run_in_executor(
            self._executor, self.embed_documents, texts
        )

    async def prewarm(self) -> None:
        await asyncio.get_running_loop().run_in_executor(self._executor, self._prewarm)

    def _prewarm(self) -> None:
        with self._lock:
            self.load()

    def status(self) -> dict:
        return {
            "model": MODEL,
            "dimensions": DIMENSIONS,
            "ready": self._session is not None,
            "loading": self._loading,
            "cachedEmbeddings": len(self.cache),
        }

    def close(self) -> None:
        self._executor.shutdown(wait=True, cancel_futures=True)


async def embed_text(
    embeddings: LocalScriptureEmbeddings, text: str, input_type="query"
) -> list[float]:
    if input_type == "query":
        return await embeddings.aembed_query(text)
    if input_type == "passage":
        return (await embeddings.aembed_documents([text]))[0]
    raise ValueError("Embedding inputType must be either query or passage.")
