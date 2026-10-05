import asyncio
import json

import numpy as np

from gyansutra.config import ROOT
from gyansutra.embedding import LocalScriptureEmbeddings, embed_text


async def test_local_vectors_match_original_javascript_model(monkeypatch):
    cases = json.loads((ROOT / "tests/fixtures/legacy_embeddings.json").read_text())
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
