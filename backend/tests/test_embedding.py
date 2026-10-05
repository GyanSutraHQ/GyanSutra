import asyncio
import json
import os
import platform
from pathlib import Path

import numpy as np

from gyansutra.config import ROOT
from gyansutra.embedding import LocalScriptureEmbeddings, embed_text


async def test_local_vectors_match_original_javascript_model(monkeypatch):
    # Quantized kernels vary by CPU. CI captures the legacy adapter on the
    # same runner; offline fixtures cover the validated ARM and x86 runtimes.
    fixture = (
        "legacy_embeddings_linux.json"
        if platform.machine() == "x86_64"
        else "legacy_embeddings.json"
    )
    reference = Path(
        os.getenv("LEGACY_EMBEDDING_REFERENCE", str(ROOT / "tests/fixtures" / fixture))
    )
    cases = json.loads(reference.read_text())
    embeddings = LocalScriptureEmbeddings()
    try:
        vectors = await asyncio.gather(
            *(embed_text(embeddings, case["text"], case["inputType"]) for case in cases)
        )
        for case, vector in zip(cases, vectors):
            assert len(vector) == 384
            assert np.isfinite(vector).all()
            np.testing.assert_allclose(vector, case["vector"], atol=2e-5, rtol=2e-4)
            assert np.dot(vector, case["vector"]) > 0.99999
        cached = await embeddings.aembed_query(cases[0]["text"])
        cached[0] = 999
        assert (await embeddings.aembed_query(cases[0]["text"]))[0] != 999
        monkeypatch.setenv("EMBEDDING_QUERY_PREFIX", "query: ")
        prefixed = await embeddings.aembed_query(" duty   and right action ")
        monkeypatch.setenv("EMBEDDING_QUERY_PREFIX", "")
        expected = await embeddings.aembed_query("query: duty and right action")
        np.testing.assert_array_equal(prefixed, expected)
        assert embeddings.status()["ready"]
    finally:
        embeddings.close()
