"""Shared source-locked records for ingestion and local lexical retrieval."""

import json
import re

from gyansutra.config import ROOT


def word_meanings(raw, chapter, verse):
    text = re.sub(r"^English Commentary By [^\d]+", "", str(raw or ""), flags=re.I)
    text = re.sub(rf"^\s*{chapter}\.{verse}\.?\s*", "", text)
    text = re.split(r"\.?\s*Commentary\b", text, flags=re.I)[0]
    return [
        {"word": m[1].strip(), "meaning": re.sub(r"[.,;:]$", "", m[2].strip())}
        for entry in text.split("?")
        if (m := re.match(r"^([\u0900-\u097f]+)\s+(.+)$", entry.strip()))
    ]


def chunks(paragraphs, maximum=2400):
    result, current = [], ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > maximum:
            result.append(current)
            current = ""
        if len(paragraph) > maximum:
            if current:
                result.append(current)
                current = ""
            result.extend(paragraph[i : i + maximum] for i in range(0, len(paragraph), maximum))
            continue
        current = current + "\n\n" + paragraph if current else paragraph
    if current:
        result.append(current)
    return result


def gita_records():
    data = json.loads((ROOT / "data/gita.json").read_text())
    for verse in data:
        ch, num = verse["chapter_number"], verse["verse_number"]
        record = {
            "source_id": "bhagavad-gita",
            "chapterNumber": ch,
            "verseNumber": num,
            "sanskrit": verse.get("sanskrit", ""),
            "transliteration": verse.get("transliteration", ""),
            "wordMeanings": word_meanings(verse.get("word_meanings"), ch, num),
            "translationHindi": verse.get("hindi", ""),
            "translationEnglish": verse.get("english", ""),
            "translationSources": {
                "english": {"author": "Swami Sivananda", "type": "translation"},
                "hindi": {"author": "Swami Tejomayananda", "type": "translation"},
            },
            "additionalTranslations": verse.get("additional_translations", []),
            "detailedExplanations": verse.get("detailed_explanations", []),
            "sourceText": "Bhagavad Gita",
            "verificationStatus": "source-compiled",
            "tags": [],
        }
        yield (
            f"bhagavad-gita_{ch}_{num}",
            record,
            f"Chapter {ch}, Verse {num}\n{record['sanskrit']}\n{record['translationEnglish']}\n{record['translationHindi']}",
        )


def vishnu_records():
    corpus = json.loads((ROOT / "data/vishnu-purana.json").read_text())
    for part in corpus["parts"]:
        for section in part["sections"]:
            passages = chunks(section["paragraphs"])
            base = {
                "source_id": corpus["id"],
                "book": "vishnu-purana",
                "partNumber": part["number"],
                "partTitle": part["title"],
                "sectionNumber": section["sectionNumber"],
                "storyTitle": section["title"],
                "storySummary": section["synopsis"],
                "chapterNumber": part["number"],
                "verseNumber": section["sectionNumber"],
                "sanskrit": "",
                "transliteration": "",
                "translationHindi": "",
                "explanationEnglish": section["synopsis"],
                "sourceText": corpus["edition"]["translation"],
                "translationSources": {
                    "english": {
                        "author": "Manmatha Nath Dutt",
                        "publicationYear": 1896,
                        "corpus": "Project Gutenberg eBook #66208",
                        "type": "complete public-domain translation",
                    }
                },
                "sanskritWitness": corpus["edition"]["sanskritWitness"],
                "verificationStatus": "canonical-translation-source-locked",
                "verified": True,
                "tags": [part["theme"].lower(), "vishnu purana"],
                "passageCount": len(passages),
            }
            yield (
                section["id"],
                {
                    **base,
                    "translationEnglish": "\n\n".join(section["paragraphs"]),
                    "footnotes": section["footnotes"],
                    "ragOnly": False,
                },
                None,
            )
            for index, passage in enumerate(passages, 1):
                text = f"Vishnu Purana, Part {part['number']}, Section {section['sectionNumber']}\n{section['title']}\n{section['synopsis']}\n{passage}"
                yield (
                    f"{section['id']}_{index}",
                    {
                        **base,
                        "passageNumber": index,
                        "translationEnglish": passage,
                        "ragOnly": True,
                    },
                    text,
                )


def normalize_sanskrit(value):
    # JavaScript \d is ASCII: preserve the original matching of Devanagari digits.
    return re.sub(r"[\s\u200b\u200c\u200d।॥0-9.,?!\-_;(){}\[\]]", "", value or "").strip()


def ramayana_records(kanda_filter=None):
    raw_path = ROOT / "data/raw/Valmiki_Ramayan_Dataset/data/Valmiki_Ramayan_Shlokas.json"
    data = json.loads(raw_path.read_text())
    index = {}
    itihasa_path = ROOT / "data/raw/itihasa/res/ramayana.json"
    if itihasa_path.exists():
        for chapters in json.loads(itihasa_path.read_text()).values():
            for chapter in chapters:
                for sanskrit, english in zip(chapter.get("sn", []), chapter.get("en", [])):
                    if sanskrit and english and (key := normalize_sanskrit(sanskrit)):
                        index[key] = english
    kandas = {
        name + " Kanda": i
        for i, name in enumerate(
            ["Bala", "Ayodhya", "Aranya", "Kishkindha", "Sundara", "Yuddha", "Uttara"], 1
        )
    }
    for verse in data:
        kanda = kandas.get(verse["kanda"], 0)
        if kanda_filter and kanda != kanda_filter:
            continue
        doc_id = f"valmiki-ramayana_{kanda}_{verse['sarga']}_{verse['shloka']}"
        translated = index.get(normalize_sanskrit(verse.get("shloka_text")))
        record = {
            "id": doc_id,
            "source_id": "valmiki-ramayana",
            "book": "ramayana",
            "kanda": verse["kanda"],
            "kandaNumber": kanda,
            "sarga": verse["sarga"],
            "shlokaNumber": verse["shloka"],
            "sanskrit": verse.get("shloka_text") or "",
            "transliteration": verse.get("transliteration") or "",
            "translationHindi": None,
            "translationEnglish": translated or verse.get("translation") or None,
            "explanationHindi": None,
            "explanationEnglish": verse.get("explanation") or None,
            "comments": verse.get("comments") or None,
            "key_terms": [],
            "source": "AshuVj/Valmiki_Ramayan_Dataset + rahular/itihasa"
            if translated
            else "AshuVj/Valmiki_Ramayan_Dataset",
            "textSource": {
                "title": "Valmiki Ramayana Dataset",
                "corpus": "AshuVj/Valmiki_Ramayan_Dataset",
            },
            "translationSources": {
                "english": {
                    "author": "M. N. Dutt",
                    "corpus": "rahular/itihasa",
                    "type": "translation",
                }
                if translated
                else {"corpus": "AshuVj/Valmiki_Ramayan_Dataset", "type": "supporting translation"}
            },
            "verificationStatus": "source-matched" if translated else "unreviewed",
            "verified": False,
        }
        yield (
            doc_id,
            record,
            " | ".join(
                filter(
                    None,
                    [
                        record["sanskrit"],
                        record["translationEnglish"],
                        record["explanationEnglish"],
                        record["comments"],
                    ],
                )
            ),
        )
