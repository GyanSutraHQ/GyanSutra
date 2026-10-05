"""Reproducible corpus-wide provenance checks; not a scholarly certification.

Pinned upstream files belong in git-ignored data/raw/source-audit. This command
reads scripture and emits a report; it never alters scripture or Firestore.
"""

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from gyansutra.config import ROOT
from scripts.ingest import normalize_sanskrit, ramayana_records

GITA_REVISION = "c6fce39595445768876ddbb8d1268a9c935e1d2b"


def read(path):
    return json.loads(path.read_text())


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prose(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def words(text):
    text = re.sub(r"^[\s।॥|]*(?:[0-9०-९]+[.।:-])+[0-9०-९]+[\s।॥|.]*", "", str(text or ""))
    return re.sub(r"[\W_]+", "", text.casefold())


def audit_gita(raw):
    local = read(ROOT / "data/gita.json")
    upstream = read(raw / "gita-verse.json")
    coordinates = {row["id"]: (row["chapter_number"], row["verse_number"]) for row in upstream}
    translations, commentaries = defaultdict(set), defaultdict(set)
    word_translations, word_commentaries = defaultdict(set), defaultdict(set)
    for name, index in [("translation", translations), ("commentary", commentaries)]:
        for row in read(raw / f"gita-{name}.json"):
            if row["verse_id"] in coordinates:
                index[coordinates[row["verse_id"]]].add(
                    (row.get("authorName"), row.get("lang"), prose(row.get("description")))
                )
                word_index = word_translations if name == "translation" else word_commentaries
                word_index[coordinates[row["verse_id"]]].add(
                    (row.get("authorName"), row.get("lang"), words(row.get("description")))
                )
    checks = Counter()
    issues = []
    for row in local:
        coord = row["chapter_number"], row["verse_number"]
        checks["records"] += 1
        if coord not in coordinates.values():
            issues.append({"coordinate": coord, "field": "coordinate"})
        for field, author, language in [
            ("english", "Swami Sivananda", "english"),
            ("hindi", "Swami Tejomayananda", "hindi"),
        ]:
            matched = (author, language, prose(row[field])) in translations[coord]
            checks[f"{field}Matched"] += matched
            word_matched = (author, language, words(row[field])) in word_translations[coord]
            checks[f"{field}NormalizedTextMatched"] += word_matched
            if not word_matched:
                issues.append({"coordinate": coord, "field": field})
        for field, index, text_field in [
            ("additional_translations", translations, "translation"),
            ("detailed_explanations", commentaries, "explanation"),
        ]:
            for item in row.get(field, []):
                checks[field + "Checked"] += 1
                matched = (
                    item.get("author"),
                    item.get("language"),
                    prose(item[text_field]),
                ) in index[coord]
                checks[field + "Matched"] += matched
                word_index = (
                    word_translations if field == "additional_translations" else word_commentaries
                )
                word_matched = (
                    item.get("author"),
                    item.get("language"),
                    words(item[text_field]),
                ) in word_index[coord]
                checks[field + "NormalizedTextMatched"] += word_matched
                if not word_matched:
                    issues.append(
                        {"coordinate": coord, "field": field, "author": item.get("author")}
                    )
    return {
        "upstreamRevision": GITA_REVISION,
        "localSha256": fingerprint(ROOT / "data/gita.json"),
        "upstreamSha256": {
            name: fingerprint(raw / f"gita-{name}.json")
            for name in ("verse", "translation", "commentary")
        },
        "checks": dict(checks),
        "issues": issues,
        "scope": "Both whitespace-normalized exact wording and normalized letters and digits (ignoring leading verse references, punctuation, case and spacing) are checked. Neither is a critical-edition comparison of Sanskrit.",
    }


def audit_ramayana():
    path = ROOT / "data/raw/Valmiki_Ramayan_Dataset/data/Valmiki_Ramayan_Shlokas.json"
    itihasa = ROOT / "data/raw/itihasa/res/ramayana.json"
    raw = read(path)
    witnesses = defaultdict(set)
    unpaired = 0
    for chapters in read(itihasa).values():
        for chapter in chapters:
            sn, en = chapter.get("sn", []), chapter.get("en", [])
            unpaired += abs(len(sn) - len(en))
            for sanskrit, english in zip(sn, en):
                if sanskrit and english:
                    witnesses[normalize_sanskrit(sanskrit)].add(english)
    coordinates = Counter((row["kanda"], int(row["sarga"]), int(row["shloka"])) for row in raw)
    checks = Counter()
    by_kanda = defaultdict(Counter)
    for _, row, _ in ramayana_records():
        checks["records"] += 1
        by_kanda[row["kanda"]]["records"] += 1
        matches = witnesses.get(normalize_sanskrit(row["sanskrit"]), set())
        matched = bool(matches) and row["translationEnglish"] in matches
        key = "publishedSourceMatched" if matched else "unreviewedFallback"
        checks[key] += 1
        by_kanda[row["kanda"]][key] += 1
        if len(matches) > 1:
            checks["ambiguousNormalizedWitness"] += 1
        checks["missingSanskrit"] += not bool(row["sanskrit"].strip())
        checks["missingTranslation"] += not bool(row["translationEnglish"])
    return {
        "datasetSha256": fingerprint(path),
        "itihasaSha256": fingerprint(itihasa),
        "checks": dict(checks),
        "byKanda": {name: dict(counts) for name, counts in by_kanda.items()},
        "duplicateCoordinates": [list(coord) for coord, count in coordinates.items() if count > 1],
        "unpairedItihasaRows": unpaired,
        "scope": "Exact normalized Sanskrit-to-English source matching as used by ingestion, not proof of editorial accuracy or alignment across editions.",
        "fallbackProvenance": "The dataset includes a Gemini script for filling missing Uttara Kanda translations and explanations. Per-record generation metadata is absent; fallback text must not be represented as a verified published translation.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = {
        "auditType": "automated-source-provenance",
        "humanEditorialReview": "pending",
        "gita": audit_gita(ROOT / "data/raw/source-audit"),
        "ramayana": audit_ramayana(),
    }
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({name: report[name]["checks"] for name in ("gita", "ramayana")}))


if __name__ == "__main__":
    main()
