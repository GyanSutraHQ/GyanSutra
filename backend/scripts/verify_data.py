"""Verify the versioned corpus without network access or credentials."""

import json

from gyansutra.config import ROOT


def verify():
    gita = json.loads((ROOT / "data/gita.json").read_text())
    assert isinstance(gita, list) and len(gita) == 701, "Expected 701 Gita verses."
    coordinates = set()
    for verse in gita:
        chapter, number = verse["chapter_number"], verse["verse_number"]
        assert type(chapter) is int and 1 <= chapter <= 18
        assert type(number) is int and number >= 1
        assert (chapter, number) not in coordinates, "Duplicate verse."
        coordinates.add((chapter, number))
        for key in ("sanskrit", "english", "hindi"):
            assert isinstance(verse.get(key), str) and verse[key].strip(), (
                f"Missing {key}: {chapter}.{number}"
            )
    assert len({c for c, _ in coordinates}) == 18
    corpus = json.loads((ROOT / "data/vishnu-purana.json").read_text())
    assert corpus["partCount"] == len(corpus["parts"]) == 6
    sections = 0
    for part_number, part in enumerate(corpus["parts"], 1):
        assert part["number"] == part_number
        assert part["sectionCount"] == len(part["sections"])
        for section_number, section in enumerate(part["sections"], 1):
            assert isinstance(section.get("title"), str) and section["title"].strip()
            assert section["sectionNumber"] == section_number
            assert section["id"] == f"vishnu-purana_{part_number}_{section_number}"
            assert isinstance(section["paragraphs"], list) and section["paragraphs"]
            assert all(isinstance(p, str) and p.strip() for p in section["paragraphs"])
            sections += 1
    assert sections == corpus["sectionCount"] == 126
    print("Scripture data contract passed: 701 Gita verses and 126 Vishnu Purana sections.")


if __name__ == "__main__":
    verify()
