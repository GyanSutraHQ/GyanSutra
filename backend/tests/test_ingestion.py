from scripts.ingest import chunks, gita_records, vishnu_records, word_meanings
from scripts.verify_data import verify


def test_corpus_and_ingestion_contracts():
    verify()
    verses = list(gita_records())
    assert len(verses) == 701 and verses[0][0] == "bhagavad-gita_1_1"
    assert verses[0][1]["translationSources"]["english"]["author"] == "Swami Sivananda"
    records = list(vishnu_records())
    sections = [v for v in records if not v[1]["ragOnly"]]
    assert len(sections) == 126
    assert all(v[2] is None for v in sections)
    assert all(len(v[1]["translationEnglish"]) <= 2400 for v in records if v[1]["ragOnly"])
    assert "Commentary" not in str(
        word_meanings("2.47 कर्म action? फल fruit. Commentary hidden prose", 2, 47)
    )
    assert chunks(["a" * 2500]) == ["a" * 2400, "a" * 100]
