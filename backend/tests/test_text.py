import json

import pytest

from gyansutra.config import ROOT
from gyansutra.text import (
    classify_guardrail,
    direct_request,
    explicit_references,
    follow_up,
    modernize,
    rerank,
    unsupported_references,
)

CASES = json.loads((ROOT / "tests/fixtures/legacy_contract.json").read_text())


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["question"])
def test_legacy_routing_parity(case):
    question = case["question"]
    assert explicit_references(question) == case["references"]
    assert follow_up(question) == case["followUp"]
    assert direct_request(question) == case["direct"]
    assert classify_guardrail(question) == case["guardrail"]
    assert classify_guardrail(question, "hi") == case["guardrailHindi"]


def test_citation_checks_and_modern_english():
    assert unsupported_references("Chapter 18 Verse 66 [S1]", ["bhagavad-gita_2_47"], 1)
    assert unsupported_references("Do your duty [S7]", ["bhagavad-gita_2_47"], 1)
    assert unsupported_references("Do your duty", ["bhagavad-gita_2_47"], 1)
    assert not unsupported_references("Gita 2.47 teaches duty [S1]", ["bhagavad-gita_2_47"], 1)
    assert (
        modernize("Thou art responsible for thy effort; thou shalt act.")
        == "You are responsible for your effort; you shall act."
    )


def test_rerank_deduplicates_and_keeps_exact_reference():
    values = [
        {"id": "a", "similarity": 0.9, "translationEnglish": "duty"},
        {"id": "b", "similarity": 1},
        {"id": "a", "similarity": 0.8},
    ]
    assert [v["id"] for v in rerank(values, "duty")] == ["b", "a"]
