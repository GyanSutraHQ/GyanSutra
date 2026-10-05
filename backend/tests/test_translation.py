import json
from unittest.mock import AsyncMock, Mock

import pytest

from gyansutra.cache import ServiceError
from gyansutra.translation import TranslationOutputParser, TranslationService, source_details
from tests.conftest import VERSE


def test_translation_parser_preserves_sanskrit_words_and_validates_script():
    source = source_details(
        {
            **VERSE,
            "explanationEnglish": "Act without attachment.",
            "comments": "A teaching about duty.",
            "wordMeanings": [{"word": "कर्म", "meaning": "action"}],
        }
    )
    parser = TranslationOutputParser(language="bn", source=source)
    result = parser.parse(
        "```json\n"
        + json.dumps(
            {
                "translation": "কর্মে তোমার অধিকার",
                "explanation": "আসক্তি ছাড়া কাজ",
                "context": "কর্তব্যের শিক্ষা",
                "wordMeanings": [{"word": "changed", "meaning": "কর্ম"}],
            }
        )
        + "\n```"
    )
    assert result["wordMeanings"][0]["word"] == "कर्म"
    with pytest.raises(ServiceError, match="script"):
        parser.parse('{"translation":"Wrong script"}')
    with pytest.raises(ServiceError) as caught:
        parser.parse('{"translation":"কর্মে তোমার অধিকার"}')
    assert caught.value.code == "INCOMPLETE_TRANSLATION_RESPONSE"


async def test_translation_cache_and_stored_content_precedence():
    generation = Mock()
    generation.generate = AsyncMock(
        return_value={
            "answer": '{"translation":"কর্মে তোমার অধিকার","explanation":"","context":"","wordMeanings":[]}'
        }
    )
    service = TranslationService(generation)
    first = await service.translate(VERSE, "bn")
    assert first["status"] == "machine-assisted-unreviewed"
    assert (await service.translate(VERSE, "bn"))["cached"]
    generation.generate.assert_awaited_once()
    stored = await service.translate(
        {**VERSE, "localizedContent": {"bn": {"translation": "সংরক্ষিত অনুবাদ"}}}, "bn"
    )
    assert stored["status"] == "stored-source-translation"
    generation.generate.assert_awaited_once()
    await service.flight.close()
