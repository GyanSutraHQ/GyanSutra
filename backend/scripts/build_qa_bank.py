"""Build the pre-computed 20,000+ 5W1H question bank and cluster embeddings.

Generates structured Q&A clusters across:
- Curated spiritual & life topics (`scripts.qa_topics.CURATED_TOPICS`)
- All 18 Bhagavad Gita chapters & 701 verses
- All 7 Valmiki Ramayana kandas & 648 sargas
- All 6 Vishnu Purana parts & 126 sections

Outputs:
- ``backend/data/qa_bank.json.gz``: deduplicated citation records + clusters + Q&A pairs
- ``backend/data/qa_vectors.npz``: L2-normalized float16 cluster embedding matrix

Usage:
    cd backend && .venv/bin/python -m scripts.build_qa_bank
    cd backend && .venv/bin/python -m scripts.build_qa_bank --sync-firestore
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import time
from collections import defaultdict

import numpy as np

from gyansutra.config import ROOT
from gyansutra.corpus import gita_records, ramayana_records, vishnu_records
from gyansutra.embedding import LocalScriptureEmbeddings
from gyansutra.text import clean_commentary, modernize, repair_ocr_text, truncate

DATA_DIR = ROOT / "data"
OUTPUT_BANK = DATA_DIR / "qa_bank.json.gz"
OUTPUT_VECTORS = DATA_DIR / "qa_vectors.npz"
POLICY_PATH = DATA_DIR / "ai-policy.json"
VISHNU_PATH = DATA_DIR / "vishnu-purana.json"

RECORD_FIELDS = (
    "id",
    "source_id",
    "sourceText",
    "translationSources",
    "verificationStatus",
    "verified",
    "chapterNumber",
    "verseNumber",
    "book",
    "kanda",
    "kandaNumber",
    "sarga",
    "shlokaNumber",
    "partNumber",
    "partTitle",
    "sectionNumber",
    "passageNumber",
    "storyTitle",
    "sanskrit",
    "transliteration",
    "translationEnglish",
    "translationHindi",
    "explanationEnglish",
    "tags",
)

KANDA_HINDI = {
    1: "बालकाण्ड",
    2: "अयोध्याकाण्ड",
    3: "अरण्यकाण्ड",
    4: "किष्किन्धाकाण्ड",
    5: "सुन्दरकाण्ड",
    6: "युद्धकाण्ड",
    7: "उत्तरकाण्ड",
}

PART_HINDI = {
    1: "प्रथम अंश",
    2: "द्वितीय अंश",
    3: "तृतीय अंश",
    4: "चतुर्थ अंश",
    5: "पंचम अंश",
    6: "षष्ठ अंश",
}

KANDA_TIMELINE = {
    1: "early in the Ramayana during Rama's childhood, education under Sage Vishwamitra, and marriage to Sita in Mithila",
    2: "in Ayodhya before and at the start of the fourteen-year forest exile following Kaikeyi's boons",
    3: "during the forest exile in Dandakaranya and Panchavati leading up to Sita's abduction by Ravana",
    4: "during Rama's alliance with Sugriva and Hanuman in Kishkindha while organizing the search for Sita",
    5: "during Hanuman's leap across the ocean to Lanka, discovery of Sita in Ashoka Vatika, and return to Rama",
    6: "during the campaign to Lanka, the building of the bridge, the great war against Ravana, and Rama's coronation",
    7: "in the final kanda after Rama's return to Ayodhya, covering later reigns, sage discourses, and Lava-Kusha",
}

CHAPTER_THEMES = {
    1: "Arjuna's moral crisis and grief on seeing relatives arrayed for war at Kurukshetra",
    2: "Sankhya wisdom of the immortal Self (Atman), equanimity, and the foundations of Karma Yoga",
    3: "selfless action (Karma Yoga), fulfilling duty without selfish attachment, and overcoming desire",
    4: "transcendental knowledge (Jnana Yoga), divine incarnation whenever dharma declines, and offering action as sacrifice",
    5: "harmony between renunciation of results and devoted selfless action with inner equanimity",
    6: "disciplined meditation (Dhyana Yoga), steadying the restless mind, and seeing the Self in all beings",
    7: "knowledge and realization of the Divine across cosmic nature, devotion, and four types of seekers",
    8: "the imperishable Brahman, remembrance of the Divine at the time of departure, and the path beyond rebirth",
    9: "sovereign royal wisdom, all-pervading grace, and direct loving devotion offered with a pure heart",
    10: "cosmic splendors (Vibhuti Yoga) recognizing the Divine as the excellence in all beings and phenomena",
    11: "the awesome cosmic vision (Vishvarupa) uniting creation, preservation, and time before Arjuna",
    12: "loving devotion (Bhakti Yoga) and the compassionate qualities dear to the Divine",
    13: "the distinction between the perishable body-field (Kshetra) and the witnessing knower (Kshetrajna)",
    14: "the three gunas of nature—sattva, rajas, and tamas—and rising beyond their bondage",
    15: "the cosmic Ashvattha tree and the Supreme Person (Purushottama) beyond mutable and immutable existence",
    16: "cultivating divine virtues like fearlessness and compassion while shedding destructive traits of greed and anger",
    17: "threefold expressions of faith, food, austerity, and charity shaped by sattva, rajas, and tamas",
    18: "liberation through duty offered to the Divine, synthesizing knowledge, work, and surrender",
}


def _clean_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\xa0", " ")).strip()


def _strip_verse_prefix(value: str) -> str:
    text = _clean_whitespace(value)
    text = re.sub(r"^(?:।।\s*)?\d+\.\d+\s*(?:।।)?\s*", "", text)
    return text.strip()


def _clean_english(value: str, fallback: str = "") -> str:
    text = _strip_verse_prefix(value)
    if re.search(r"[\u0900-\u097F]", text) and "," in text and ":" in text:
        # Word-by-word Sanskrit gloss string; avoid using as clean prose if fallback exists.
        text = ""
    if not text and fallback:
        text = _strip_verse_prefix(fallback)
    text = re.sub(r"\[\d+\]", "", text)
    return _clean_whitespace(repair_ocr_text(modernize(text)))


def _clean_hindi(value: str) -> str:
    text = _strip_verse_prefix(value)
    text = re.sub(r"^व्याख्या\s*[-–—]+\s*", "", text)
    text = re.sub(r"''([^']+)''", r"\1", text)
    return _clean_whitespace(text)


def _sentence_clip(text: str, maximum: int = 360) -> str:
    text = _clean_whitespace(text)
    if len(text) <= maximum:
        return text
    clipped = text[:maximum]
    for sep in (". ", "! ", "? ", "। "):
        idx = clipped.rfind(sep)
        if idx >= maximum // 2:
            return clipped[: idx + 1].strip()
    idx = clipped.rfind(" ")
    if idx > 0:
        return clipped[:idx].rstrip(" ,;:-") + "..."
    return truncate(text, maximum)


def _pick_gita_commentary(payload: dict) -> tuple[str, str]:
    """Return best cleaned (english_explanation, hindi_explanation) for a Gita verse."""
    en_commentary = ""
    hi_commentary = ""
    for item in payload.get("detailedExplanations") or []:
        if not isinstance(item, dict):
            continue
        author = str(item.get("author") or "").lower()
        lang = str(item.get("language") or "").lower()
        raw = str(item.get("explanation") or "")
        if not raw:
            continue
        if lang == "english" and not en_commentary:
            cleaned = clean_commentary(raw)
            if cleaned and "no commentary" not in cleaned.lower():
                en_commentary = cleaned
        elif lang == "hindi":
            if "chinmayananda" in author or not hi_commentary:
                cleaned_hi = _clean_hindi(raw)
                if cleaned_hi:
                    hi_commentary = cleaned_hi

    if not en_commentary:
        # Fallback to another clean English translation when Sivananda has No Commentary.
        for item in payload.get("additionalTranslations") or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("language") or "").lower() == "english":
                alt = _clean_english(str(item.get("translation") or ""))
                if alt and len(alt) > 25:
                    en_commentary = alt
                    break

    return _sentence_clip(en_commentary, 420), _sentence_clip(hi_commentary, 320)


def _pick_gita_speaker(payload: dict, previous_speaker: str) -> tuple[str, str]:
    """Infer speaker and listener for a Gita verse, carrying context across consecutive verses."""
    sanskrit = payload.get("sanskrit") or ""
    translation = (payload.get("translationEnglish") or "").lower()

    if (
        "श्रीभगवानुवाच" in sanskrit
        or "blessed lord said" in translation
        or "supreme personality" in translation
    ):
        return "Lord Krishna", "Arjuna"
    if "अर्जुन उवाच" in sanskrit or "arjuna said" in translation:
        return "Arjuna", "Lord Krishna"
    if "सञ्जय उवाच" in sanskrit or "संजय उवाच" in sanskrit or "sanjaya said" in translation:
        return "Sanjaya", "King Dhritarashtra"
    if "धृतराष्ट्र उवाच" in sanskrit or "dhritarashtra said" in translation:
        return "King Dhritarashtra", "Sanjaya"

    listeners = {
        "Lord Krishna": "Arjuna",
        "Arjuna": "Lord Krishna",
        "Sanjaya": "King Dhritarashtra",
        "King Dhritarashtra": "Sanjaya",
    }
    return previous_speaker, listeners.get(previous_speaker, "Arjuna")


def _compact_record(doc_id: str, payload: dict) -> dict:
    """Extract lightweight citation record fields matching rag.py CITATION_FIELDS."""
    record = {"id": doc_id}
    for field in RECORD_FIELDS:
        if field == "id":
            continue
        val = payload.get(field)
        if val is not None and val != "" and val != []:
            record[field] = val
    # Ensure clean English summary for Ramayana records whose raw translationEnglish is a gloss dump.
    if record.get("source_id") == "valmiki-ramayana":
        clean_prose = _clean_english(
            str(record.get("explanationEnglish") or ""),
            fallback="",
        )
        if clean_prose and (
            not record.get("translationEnglish")
            or re.search(r"[\u0900-\u097F].*:", str(record.get("translationEnglish")))
        ):
            record["translationEnglish"] = clean_prose
    return record


def _build_gita_data(records_by_id: dict[str, dict]):
    """Build 701 Gita verse clusters + 18 Gita chapter clusters."""
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    chapter_meta = {int(c["number"]): c for c in policy.get("chapters", [])}
    verses_by_chapter: dict[int, list[tuple[str, dict]]] = defaultdict(list)

    clusters = []
    current_chapter = 0
    speaker = "Sanjaya"

    for doc_id, payload, _ in gita_records():
        ch = int(payload.get("chapterNumber") or 0)
        vs = int(payload.get("verseNumber") or 0)
        if not ch or not vs:
            continue
        if ch != current_chapter:
            current_chapter = ch
            speaker = "King Dhritarashtra" if ch == 1 else "Lord Krishna"

        records_by_id[doc_id] = _compact_record(doc_id, payload)
        verses_by_chapter[ch].append((doc_id, payload))

        speaker, listener = _pick_gita_speaker(payload, speaker)
        speaker_hi = {
            "Lord Krishna": "श्रीकृष्ण",
            "Arjuna": "अर्जुन",
            "Sanjaya": "संजय",
            "King Dhritarashtra": "राजा धृतराष्ट्र",
        }[speaker]
        listener_hi = {
            "Arjuna": "अर्जुन",
            "Lord Krishna": "श्रीकृष्ण",
            "King Dhritarashtra": "राजा धृतराष्ट्र",
            "Sanjaya": "संजय",
        }[listener]

        ch_info = chapter_meta.get(ch, {})
        ch_title_en = ch_info.get("titleEnglish") or f"Chapter {ch}"
        ch_title_sk = ch_info.get("titleSanskrit") or ""
        ch_title_hi = ch_info.get("titleHindi") or ch_title_en

        verse_en = _clean_english(payload.get("translationEnglish") or "")
        en_comm, hi_comm = _pick_gita_commentary(payload)
        verse_hi = _clean_hindi(payload.get("translationHindi") or "")
        tags = [str(t).strip() for t in (payload.get("tags") or []) if str(t).strip()]
        theme = CHAPTER_THEMES.get(ch, ch_title_en)

        what_ans = (
            f'In Bhagavad Gita {ch}.{vs} ({ch_title_en}), {speaker} states: "{verse_en}" [S1].'
        )
        if en_comm and en_comm.lower() != verse_en.lower():
            what_ans += f" {en_comm} [S1]."

        why_ans = f"Bhagavad Gita {ch}.{vs} is spoken during {theme.lower()} [S1]. " + (
            f"Commentators note: {en_comm} [S1]."
            if en_comm
            else f"It clarifies why {speaker} guides {listener} through this moment of dharma and inner clarity [S1]."
        )

        how_ans = (
            f'Practicing Bhagavad Gita {ch}.{vs} means applying its core insight—"{_sentence_clip(verse_en, 210)}"—in daily choices [S1]. '
            + (
                f"In commentary: {en_comm} [S1]."
                if en_comm
                else f"Reflect on this teaching from Chapter {ch} ({ch_title_en}) when acting with clarity, restraint, and purpose [S1]."
            )
        )

        when_ans = (
            f"Bhagavad Gita {ch}.{vs} was spoken at the start of the Mahabharata war on the battlefield of Kurukshetra, during Chapter {ch} ({ch_title_en}) [S1]. "
            f"In everyday life, it is especially valuable to recall when facing situations connected to {theme.lower()} [S1]."
        )

        where_ans = (
            f'Bhagavad Gita {ch}.{vs} appears in Chapter {ch}, titled "{ch_title_en}" ({ch_title_sk}) [S1]. '
            f"The setting is the sacred battlefield of Kurukshetra, where {speaker} addresses {listener} [S1]."
        )

        who_ans = (
            f"In Bhagavad Gita {ch}.{vs}, {speaker} is speaking to {listener} during Chapter {ch} ({ch_title_en}) [S1]. "
            f'Here, {speaker} conveys this message: "{_sentence_clip(verse_en, 200)}" [S1].'
        )

        hi_ans = f'भगवद्गीता अध्याय {ch} ({ch_title_hi}) के श्लोक {vs} में {speaker_hi} {listener_hi} से कहते हैं: "{verse_hi}" [S1]।'
        if hi_comm:
            hi_ans += f" {hi_comm} [S1]।"

        speaker_short = speaker.replace("Lord ", "").replace("King ", "")
        questions = [
            {"q": f"What does Bhagavad Gita {ch}.{vs} say?", "aspect": "what"},
            {
                "q": f"What is the meaning of Bhagavad Gita chapter {ch} verse {vs}?",
                "aspect": "what",
            },
            {"q": f"What does Gita {ch}.{vs} teach?", "aspect": "what"},
            {"q": f"Why is Bhagavad Gita {ch}.{vs} significant?", "aspect": "why"},
            {
                "q": f"Why does {speaker_short} teach this in Bhagavad Gita {ch}.{vs}?",
                "aspect": "why",
            },
            {"q": f"How can I apply Bhagavad Gita {ch}.{vs} in daily life?", "aspect": "how"},
            {"q": f"How is the teaching of Gita {ch}.{vs} practiced?", "aspect": "how"},
            {"q": f"When was Bhagavad Gita {ch}.{vs} spoken?", "aspect": "when"},
            {"q": f"When in life should I remember Bhagavad Gita {ch}.{vs}?", "aspect": "when"},
            {
                "q": f"Where does Bhagavad Gita {ch}.{vs} appear in the scripture?",
                "aspect": "where",
            },
            {
                "q": f"Where is the setting of Bhagavad Gita chapter {ch} verse {vs}?",
                "aspect": "where",
            },
            {"q": f"Who is speaking in Bhagavad Gita {ch}.{vs}?", "aspect": "who"},
            {"q": f"Who is addressed in Bhagavad Gita {ch}.{vs}?", "aspect": "who"},
            {"q": f"Explain Bhagavad Gita {ch}.{vs} simply", "aspect": "summary"},
            {"q": f"Summarize Bhagavad Gita {ch}.{vs}", "aspect": "summary"},
            {"q": f"What are the key points of Bhagavad Gita {ch}.{vs}?", "aspect": "points"},
            {"q": f"Gita {ch}.{vs} ka matlab kya hai?", "aspect": "summary"},
            {"q": f"Gita {ch}.{vs} saral shabdon mein samjhaiye", "aspect": "summary"},
            {"q": f"भगवद्गीता अध्याय {ch} श्लोक {vs} का क्या अर्थ है?", "aspect": "hi"},
            {"q": f"गीता {ch}.{vs} में क्या उपदेश दिया गया है?", "aspect": "hi"},
        ]

        embed_text = (
            f"Bhagavad Gita Chapter {ch} Verse {vs} Gita {ch}.{vs} {ch_title_en} {ch_title_sk}. "
            f"Speaker: {speaker} to {listener}. {' '.join(tags)} "
            f"{_sentence_clip(verse_en, 240)} {_sentence_clip(en_comm, 220)}"
        )

        clusters.append(
            {
                "id": f"gita_verse_{ch}_{vs}",
                "type": "gita_verse",
                "sourceId": "bhagavad-gita",
                "title": f"Bhagavad Gita {ch}.{vs}: {ch_title_en}",
                "keywords": " ".join(
                    [
                        "bhagavad",
                        "gita",
                        f"chapter {ch}",
                        f"verse {vs}",
                        f"{ch}.{vs}",
                        f"{ch}:{vs}",
                        ch_title_en.lower(),
                        speaker_short.lower(),
                        listener.lower(),
                        *(t.lower() for t in tags),
                    ]
                ),
                "citationIds": [doc_id],
                "questions": questions,
                "answers": {
                    "en": {
                        "default": what_ans,
                        "what": what_ans,
                        "why": why_ans,
                        "how": how_ans,
                        "when": when_ans,
                        "where": where_ans,
                        "who": who_ans,
                    },
                    "hi": {"default": hi_ans},
                },
                "_embed": embed_text,
            }
        )

    # Now build 18 Gita chapter clusters.
    famous_verses = {
        1: 47,
        2: 47,
        3: 19,
        4: 7,
        5: 10,
        6: 5,
        7: 7,
        8: 5,
        9: 22,
        10: 20,
        11: 32,
        12: 13,
        13: 2,
        14: 26,
        15: 7,
        16: 1,
        17: 3,
        18: 66,
    }
    for ch in range(1, 19):
        ch_info = chapter_meta.get(ch, {})
        ch_title_en = ch_info.get("titleEnglish") or f"Chapter {ch}"
        ch_title_sk = ch_info.get("titleSanskrit") or ""
        ch_title_hi = ch_info.get("titleHindi") or ch_title_en
        vcount = int(ch_info.get("verseCount") or len(verses_by_chapter[ch]))
        theme = CHAPTER_THEMES.get(ch, ch_title_en)

        ch_verses = verses_by_chapter[ch]
        first_id, first_payload = ch_verses[0]
        key_vs = famous_verses.get(ch, 1)
        key_pair = next(
            (pair for pair in ch_verses if int(pair[1].get("verseNumber") or 0) == key_vs),
            ch_verses[-1],
        )
        key_id, key_payload = key_pair
        cids = [first_id] if key_id == first_id else [first_id, key_id]
        s2_marker = "[S2]" if len(cids) > 1 else "[S1]"

        first_en = _sentence_clip(
            _clean_english(first_payload.get("translationEnglish") or ""), 200
        )
        key_en = _sentence_clip(_clean_english(key_payload.get("translationEnglish") or ""), 220)
        key_hi = _sentence_clip(_clean_hindi(key_payload.get("translationHindi") or ""), 220)

        what_ans = (
            f'Bhagavad Gita Chapter {ch}, "{ch_title_en}" ({ch_title_sk}), contains {vcount} verses and focuses on {theme} [S1]. '
            f'It opens with {first_en} [S1] and highlights teachings such as: "{key_en}" {s2_marker}.'
        )
        why_ans = (
            f"Chapter {ch} ({ch_title_en}) matters in the Bhagavad Gita because it develops {theme} [S1]. "
            f'A central insight of this chapter is captured in {ch}.{key_vs}: "{key_en}" {s2_marker}.'
        )
        how_ans = (
            f"You can apply the message of Gita Chapter {ch} ({ch_title_en}) by reflecting on {theme} in daily decisions [S1]. "
            f'In particular, put its core principle into practice: "{key_en}" {s2_marker}.'
        )
        when_ans = (
            f"Chapter {ch} is taught on the battlefield of Kurukshetra just before the Mahabharata war begins, as Krishna addresses Arjuna's confusion ({vcount} verses) [S1]. "
            f"Turn to this chapter whenever you face dilemmas connected to {theme} {s2_marker}."
        )
        where_ans = (
            f"Bhagavad Gita Chapter {ch} ({ch_title_en}) is part of the Bhishma Parva of the Mahabharata, set on the sacred field of Kurukshetra [S1]. "
            f"Within the Gita's 18 chapters, it spans {vcount} verses exploring {theme} {s2_marker}."
        )
        who_ans = (
            f"Chapter {ch} ({ch_title_en}) centers on the dialogue between Lord Krishna and Arjuna, narrated by Sanjaya to King Dhritarashtra [S1]. "
            f"Across its {vcount} verses, their exchange reveals {theme} {s2_marker}."
        )
        hi_ans = (
            f'भगवद्गीता अध्याय {ch} ({ch_title_hi}) में {vcount} श्लोक हैं और इसका मुख्य विषय "{theme}" है [S1]। '
            f'इस अध्याय का प्रमुख संदेश: "{key_hi}" {s2_marker}।'
        )

        questions = [
            {"q": f"What is Bhagavad Gita chapter {ch} about?", "aspect": "what"},
            {"q": f"What does chapter {ch} of the Bhagavad Gita teach?", "aspect": "what"},
            {"q": f"What is the summary of Gita chapter {ch} ({ch_title_en})?", "aspect": "what"},
            {"q": f"Why is Bhagavad Gita chapter {ch} important?", "aspect": "why"},
            {"q": f"Why did Krishna teach Gita chapter {ch}?", "aspect": "why"},
            {"q": f"How can I apply Bhagavad Gita chapter {ch} in life?", "aspect": "how"},
            {"q": f"How does Gita chapter {ch} guide a seeker?", "aspect": "how"},
            {"q": f"When is Bhagavad Gita chapter {ch} spoken?", "aspect": "when"},
            {"q": f"When should someone read Gita chapter {ch}?", "aspect": "when"},
            {"q": f"Where is Bhagavad Gita chapter {ch} set?", "aspect": "where"},
            {"q": f"Where does chapter {ch} fit in the Bhagavad Gita?", "aspect": "where"},
            {"q": f"Who speaks in Bhagavad Gita chapter {ch}?", "aspect": "who"},
            {"q": f"Who are the main figures in Gita chapter {ch}?", "aspect": "who"},
            {"q": f"Summarize Bhagavad Gita chapter {ch} simply", "aspect": "summary"},
            {"q": f"What are the key points of Bhagavad Gita chapter {ch}?", "aspect": "points"},
            {"q": f"What are the main takeaways from Gita chapter {ch}?", "aspect": "points"},
            {"q": f"Gita chapter {ch} ka saar kya hai?", "aspect": "summary"},
            {"q": f"Gita adhyay {ch} mein kya bataya gaya hai?", "aspect": "what"},
            {"q": f"भगवद्गीता अध्याय {ch} का क्या सार है?", "aspect": "hi"},
        ]

        clusters.append(
            {
                "id": f"gita_chapter_{ch}",
                "type": "gita_chapter",
                "sourceId": "bhagavad-gita",
                "title": f"Bhagavad Gita Chapter {ch}: {ch_title_en}",
                "keywords": f"bhagavad gita chapter {ch} summary overview {ch_title_en.lower()} {theme.lower()}",
                "citationIds": cids,
                "questions": questions,
                "answers": {
                    "en": {
                        "default": what_ans,
                        "what": what_ans,
                        "why": why_ans,
                        "how": how_ans,
                        "when": when_ans,
                        "where": where_ans,
                        "who": who_ans,
                    },
                    "hi": {"default": hi_ans},
                },
                "_embed": f"Bhagavad Gita Chapter {ch} {ch_title_en} {ch_title_sk} summary overview {theme} {key_en}",
            }
        )

    return clusters


def _build_ramayana_data(records_by_id: dict[str, dict], needed_cids: set[str] | None = None):
    """Build 648 Valmiki Ramayana sarga clusters + 7 kanda clusters."""
    sarga_groups: dict[tuple[int, int], list[tuple[str, dict]]] = defaultdict(list)
    kanda_names: dict[int, str] = {}
    needed = needed_cids or set()

    for doc_id, payload, _ in ramayana_records():
        knum = int(payload.get("kandaNumber") or 0)
        snum = int(payload.get("sarga") or 0)
        kname = _clean_whitespace(str(payload.get("kanda") or f"Kanda {knum}"))
        if doc_id in needed:
            records_by_id[doc_id] = _compact_record(doc_id, payload)
        if not knum or not snum:
            continue
        kanda_names[knum] = kname
        sarga_groups[(knum, snum)].append((doc_id, payload))

    clusters = []
    kanda_sargas: dict[int, list[tuple[int, str, str, str]]] = defaultdict(list)

    for knum, snum in sorted(sarga_groups.keys()):
        items = sorted(
            sarga_groups[(knum, snum)], key=lambda pair: int(pair[1].get("shlokaNumber") or 0)
        )
        kname = kanda_names.get(knum, f"Kanda {knum}")
        kname_hi = KANDA_HINDI.get(knum, kname)

        comment = ""
        first_doc_id, first_payload = items[0]
        best_doc_id, best_payload = first_doc_id, first_payload
        explanations = []
        for doc_id, payload in items:
            raw_comment = _clean_whitespace(str(payload.get("comments") or ""))
            if raw_comment and not comment:
                comment = modernize(raw_comment.replace("--", "; "))
            exp = _clean_english(str(payload.get("explanationEnglish") or ""))
            if exp:
                if best_doc_id == first_doc_id and len(explanations) == 0:
                    best_doc_id, best_payload = doc_id, payload
                if len(explanations) < 2 and exp not in explanations:
                    explanations.append(exp)

        # Store up to 2 compact citation records per sarga (not all 23,291 shlokas).
        records_by_id[first_doc_id] = _compact_record(first_doc_id, first_payload)
        cids = [first_doc_id]
        if best_doc_id != first_doc_id:
            records_by_id[best_doc_id] = _compact_record(best_doc_id, best_payload)
            cids.append(best_doc_id)

        summary = _sentence_clip(comment or " ".join(explanations), 360)
        opening = _sentence_clip(" ".join(explanations), 320)
        timeline = KANDA_TIMELINE.get(knum, f"during {kname} of the Valmiki Ramayana")
        s2_marker = "[S2]" if len(cids) > 1 else "[S1]"
        shloka_count = len(items)

        kanda_sargas[knum].append((snum, first_doc_id, summary, opening))

        what_ans = (
            f"In Valmiki Ramayana, {kname}, Sarga {snum} ({shloka_count} shlokas), {summary} [S1]."
        )
        if opening and opening.lower() not in summary.lower():
            what_ans += f' The opening lines relate: "{_sentence_clip(opening, 220)}" {s2_marker}.'

        why_ans = (
            f"{kname}, Sarga {snum} is an integral episode {timeline} [S1]. "
            f"It matters because it reveals how dharma, resolve, and character shape this turning point: {_sentence_clip(summary, 240)} {s2_marker}."
        )
        how_ans = (
            f"Sarga {snum} of {kname} unfolds across {shloka_count} shlokas: {_sentence_clip(summary, 240)} [S1]. "
            f"From this episode, seekers draw steadiness, moral courage, and loyalty under testing circumstances {s2_marker}."
        )
        when_ans = (
            f"Valmiki Ramayana {kname}, Sarga {snum} takes place {timeline} [S1]. "
            f"At this stage of the narrative, {_sentence_clip(summary, 210)} [S1]."
        )
        where_ans = (
            f"This episode is recorded in Sarga {snum} of {kname} in Sage Valmiki's Ramayana ({shloka_count} shlokas) [S1]. "
            f"Context of the scene: {_sentence_clip(summary, 230)} {s2_marker}."
        )
        who_ans = f"In {kname}, Sarga {snum} of the Valmiki Ramayana, the scene focuses on the figures involved in this episode: {_sentence_clip(summary, 250)} [S1]."
        hi_ans = f"वाल्मीकि रामायण के {kname_hi} (सर्ग {snum}, {shloka_count} श्लोक) का सार यह है: {_sentence_clip(summary, 240)} [S1]।"

        questions = [
            {"q": f"What happens in Valmiki Ramayana {kname} Sarga {snum}?", "aspect": "what"},
            {"q": f"What is the story of Ramayana {kname} chapter {snum}?", "aspect": "what"},
            {"q": f"What does Ramayana {kname} Sarga {snum} describe?", "aspect": "what"},
            {"q": f"Why is Ramayana {kname} Sarga {snum} important?", "aspect": "why"},
            {"q": f"Why does the episode in {kname} Sarga {snum} take place?", "aspect": "why"},
            {"q": f"How does Ramayana {kname} Sarga {snum} unfold?", "aspect": "how"},
            {"q": f"How do the events of {kname} Sarga {snum} guide readers?", "aspect": "how"},
            {"q": f"When does Ramayana {kname} Sarga {snum} occur?", "aspect": "when"},
            {"q": f"Where is {kname} Sarga {snum} in Valmiki Ramayana?", "aspect": "where"},
            {"q": f"Who appears in Ramayana {kname} Sarga {snum}?", "aspect": "who"},
            {"q": f"Who are the central figures in {kname} Sarga {snum}?", "aspect": "who"},
            {"q": f"Explain Ramayana {kname} Sarga {snum} simply", "aspect": "summary"},
            {"q": f"Summarize {kname} Sarga {snum} of Valmiki Ramayana", "aspect": "summary"},
            {"q": f"What are the key points of Ramayana {kname} Sarga {snum}?", "aspect": "points"},
            {"q": f"{kname} Sarga {snum} mein kya hota hai?", "aspect": "what"},
            {"q": f"Ramayana {kname} Sarga {snum} ki kahani kya hai?", "aspect": "summary"},
            {"q": f"वाल्मीकि रामायण {kname_hi} सर्ग {snum} की क्या कथा है?", "aspect": "hi"},
            {"q": f"रामायण {kname_hi} सर्ग {snum} में क्या वर्णन है?", "aspect": "hi"},
        ]

        embed_text = (
            f"Valmiki Ramayana {kname} Kanda {knum} Sarga {snum} Canto {snum}. {summary} {opening}"
        )

        clusters.append(
            {
                "id": f"ramayana_sarga_{knum}_{snum}",
                "type": "ramayana_sarga",
                "sourceId": "valmiki-ramayana",
                "title": f"Valmiki Ramayana — {kname}, Sarga {snum}",
                "keywords": f"valmiki ramayana {kname.lower()} kanda {knum} sarga {snum} canto {snum} {kname_hi}",
                "citationIds": cids,
                "questions": questions,
                "answers": {
                    "en": {
                        "default": what_ans,
                        "what": what_ans,
                        "why": why_ans,
                        "how": how_ans,
                        "when": when_ans,
                        "where": where_ans,
                        "who": who_ans,
                    },
                    "hi": {"default": hi_ans},
                },
                "_embed": embed_text,
            }
        )

    # Build 7 Ramayana Kanda overview clusters.
    for knum in sorted(kanda_sargas.keys()):
        kname = kanda_names[knum]
        kname_hi = KANDA_HINDI.get(knum, kname)
        sargas = kanda_sargas[knum]
        first_sarga = sargas[0]
        mid_sarga = sargas[len(sargas) // 2]
        cids = (
            [first_sarga[1]] if mid_sarga[1] == first_sarga[1] else [first_sarga[1], mid_sarga[1]]
        )
        s2_marker = "[S2]" if len(cids) > 1 else "[S1]"
        timeline = KANDA_TIMELINE.get(knum, f"in {kname}")
        scount = len(sargas)

        what_ans = (
            f"{kname} is Book {knum} of the Valmiki Ramayana and spans {scount} sargas, taking place {timeline} [S1]. "
            f"It opens with {_sentence_clip(first_sarga[2], 190)} [S1] and develops through episodes such as {_sentence_clip(mid_sarga[2], 180)} {s2_marker}."
        )
        why_ans = (
            f"{kname} is essential to the Valmiki Ramayana because its {scount} sargas trace events {timeline} [S1]. "
            f"Key episodes highlight dharmic duty, perseverance, and devotion under trial {s2_marker}."
        )
        how_ans = f"Across {scount} sargas, {kname} progresses from {_sentence_clip(first_sarga[2], 170)} [S1] toward major turning points {timeline} {s2_marker}."
        when_ans = f"{kname} is the {knum}th book of Valmiki's seven-kanda epic, chronicling events {timeline} [S1]."
        where_ans = f"{kname} forms Book {knum} ({scount} sargas) of the Valmiki Ramayana [S1]. Key settings and events include {_sentence_clip(first_sarga[2], 200)} [S1]."
        who_ans = f"In {kname}, Sage Valmiki narrates pivotal episodes {timeline}, opening with {_sentence_clip(first_sarga[2], 200)} [S1]."
        hi_ans = (
            f"{kname_hi} वाल्मीकि रामायण का {knum}वाँ काण्ड है, जिसमें {scount} सर्ग हैं [S1]। "
            f"इसका आरम्भ इस प्रसंग से होता है: {_sentence_clip(first_sarga[2], 200)} [S1]।"
        )

        questions = [
            {"q": f"What happens in {kname} of the Valmiki Ramayana?", "aspect": "what"},
            {"q": f"What is {kname} about?", "aspect": "what"},
            {"q": f"What is the summary of Ramayana {kname}?", "aspect": "what"},
            {"q": f"Why is {kname} important in the Ramayana?", "aspect": "why"},
            {"q": f"Why is this book called {kname}?", "aspect": "why"},
            {"q": f"How does {kname} unfold in Valmiki Ramayana?", "aspect": "how"},
            {"q": f"How many sargas are in {kname}?", "aspect": "what"},
            {"q": f"When does {kname} take place in the Ramayana?", "aspect": "when"},
            {"q": f"When should I read {kname}?", "aspect": "when"},
            {"q": f"Where do the events of {kname} take place?", "aspect": "where"},
            {"q": f"Where is {kname} in the Ramayana?", "aspect": "where"},
            {"q": f"Who are the key characters in {kname}?", "aspect": "who"},
            {"q": f"Who speaks or leads in {kname}?", "aspect": "who"},
            {"q": f"Summarize {kname} of Valmiki Ramayana in simple words", "aspect": "summary"},
            {"q": f"What are the key points of {kname}?", "aspect": "points"},
            {"q": f"What are the main events in Ramayana {kname}?", "aspect": "points"},
            {"q": f"{kname} mein kya hota hai?", "aspect": "what"},
            {"q": f"{kname} ki mukhya katha kya hai?", "aspect": "summary"},
            {"q": f"वाल्मीकि रामायण के {kname_hi} में क्या कथा है?", "aspect": "hi"},
        ]

        clusters.append(
            {
                "id": f"ramayana_kanda_{knum}",
                "type": "ramayana_kanda",
                "sourceId": "valmiki-ramayana",
                "title": f"Valmiki Ramayana — {kname}",
                "keywords": f"valmiki ramayana {kname.lower()} kanda {knum} summary {kname_hi}",
                "citationIds": cids,
                "questions": questions,
                "answers": {
                    "en": {
                        "default": what_ans,
                        "what": what_ans,
                        "why": why_ans,
                        "how": how_ans,
                        "when": when_ans,
                        "where": where_ans,
                        "who": who_ans,
                    },
                    "hi": {"default": hi_ans},
                },
                "_embed": f"Valmiki Ramayana {kname} Book {knum} overview summary {scount} sargas {timeline} {first_sarga[2]}",
            }
        )

    return clusters


def _build_vishnu_data(records_by_id: dict[str, dict]):
    """Build 126 Vishnu Purana section clusters + 6 part clusters."""
    vp_raw = json.loads(VISHNU_PATH.read_text(encoding="utf-8"))
    vp_first_records: dict[tuple[int, int], tuple[str, dict]] = {}
    for doc_id, payload, _ in vishnu_records():
        records_by_id[doc_id] = _compact_record(doc_id, payload)
        pnum = int(payload.get("partNumber") or 0)
        snum = int(payload.get("sectionNumber") or 0)
        pno = int(payload.get("passageNumber") or 0)
        if pnum and snum and (pno == 1 or (pnum, snum) not in vp_first_records):
            vp_first_records[(pnum, snum)] = (doc_id, payload)

    clusters = []
    for part in vp_raw.get("parts") or []:
        pnum = int(part.get("number") or 0)
        ptitle = _clean_whitespace(str(part.get("title") or f"Part {pnum}"))
        ptheme = _clean_whitespace(str(part.get("theme") or ptitle))
        p_hi = PART_HINDI.get(pnum, f"अंश {pnum}")
        sections = part.get("sections") or []
        scount = len(sections)

        part_cids = []
        section_titles = []

        for sec in sections:
            snum = int(sec.get("sectionNumber") or 0)
            stitle = _clean_whitespace(str(sec.get("title") or f"Section {snum}"))
            synopsis = _clean_english(str(sec.get("synopsis") or ""))
            paras = sec.get("paragraphs") or []
            para1 = _clean_english(str(paras[0])) if paras else ""

            pair = vp_first_records.get((pnum, snum))
            if not pair:
                continue
            doc_id, _ = pair
            section_titles.append(stitle)
            if len(part_cids) < 2:
                part_cids.append(doc_id)

            summary = _sentence_clip(synopsis or para1, 360)
            excerpt = _sentence_clip(para1, 240)

            what_ans = f'In Vishnu Purana, Part {pnum} ({ptitle}), Section {snum} ("{stitle}"), {summary} [S1].'
            if excerpt and excerpt.lower() not in summary.lower():
                what_ans += f' Opening text: "{excerpt}" [S1].'

            why_ans = (
                f'Section {snum} ("{stitle}") contributes to Part {pnum}\'s overarching focus on {ptheme.lower()} [S1]. '
                f"In this section, Sage Parashara clarifies: {_sentence_clip(summary, 240)} [S1]."
            )
            how_ans = f'The Vishnu Purana presents "{stitle}" (Part {pnum}, Section {snum}) as a dialogue in which Maitreya questions Sage Parashara: {_sentence_clip(summary, 240)} [S1].'
            when_ans = (
                f'Vishnu Purana Part {pnum}, Section {snum} ("{stitle}") appears within the {pnum}th Part ({ptitle}), structured around {ptheme.lower()} [S1]. '
                f"Read this section when exploring {_sentence_clip(summary, 180)} [S1]."
            )
            where_ans = f'This teaching is located in Vishnu Purana, Part {pnum} ({ptitle}), Section {snum}, titled "{stitle}" [S1].'
            who_ans = (
                f'Like the rest of the Vishnu Purana, Part {pnum}, Section {snum} ("{stitle}") is narrated by Sage Parashara to his disciple Maitreya [S1]. '
                f"The discourse centers on: {_sentence_clip(summary, 220)} [S1]."
            )
            hi_ans = f'विष्णु पुराण के {p_hi} ({ptitle}), अध्याय {snum} ("{stitle}") में महर्षि पराशर मैत्रेय को यह वर्णन सुनाते हैं: {_sentence_clip(summary, 240)} [S1]।'

            questions = [
                {"q": f"What is Vishnu Purana Part {pnum} Section {snum} about?", "aspect": "what"},
                {"q": f"What does Vishnu Purana {pnum}.{snum} ({stitle}) teach?", "aspect": "what"},
                {"q": f'What is the story of "{stitle}" in Vishnu Purana?', "aspect": "what"},
                {
                    "q": f"Why is Vishnu Purana Part {pnum} Section {snum} important?",
                    "aspect": "why",
                },
                {
                    "q": f"Why does Sage Parashara explain {stitle} in Vishnu Purana {pnum}.{snum}?",
                    "aspect": "why",
                },
                {"q": f"How does Vishnu Purana describe {stitle}?", "aspect": "how"},
                {"q": f"How is Vishnu Purana Part {pnum} Section {snum} framed?", "aspect": "how"},
                {
                    "q": f"When does the topic of {stitle} appear in Vishnu Purana?",
                    "aspect": "when",
                },
                {
                    "q": f"Where is the story of {stitle} found in the Vishnu Purana?",
                    "aspect": "where",
                },
                {
                    "q": f"Where does Vishnu Purana Part {pnum} Section {snum} fit in the text?",
                    "aspect": "where",
                },
                {"q": f"Who speaks in Vishnu Purana Part {pnum} Section {snum}?", "aspect": "who"},
                {"q": f"Who asks questions in Vishnu Purana {pnum}.{snum}?", "aspect": "who"},
                {
                    "q": f"Explain Vishnu Purana Part {pnum} Section {snum} simply",
                    "aspect": "summary",
                },
                {"q": f"Summarize Vishnu Purana Part {pnum} Section {snum}", "aspect": "summary"},
                {
                    "q": f"What are the key points of Vishnu Purana {pnum}.{snum}?",
                    "aspect": "points",
                },
                {
                    "q": f"Vishnu Purana Part {pnum} Section {snum} mein kya bataya gaya hai?",
                    "aspect": "what",
                },
                {"q": f"Vishnu Purana {pnum}.{snum} ka matlab kya hai?", "aspect": "summary"},
                {"q": f"विष्णु पुराण {p_hi} अध्याय {snum} में क्या वर्णन है?", "aspect": "hi"},
                {"q": f"विष्णु पुराण भाग {pnum} खंड {snum} ({stitle}) किस बारे में है?", "aspect": "hi"},
            ]

            clusters.append(
                {
                    "id": f"vishnu_section_{pnum}_{snum}",
                    "type": "vishnu_section",
                    "sourceId": "vishnu-purana",
                    "title": f"Vishnu Purana Part {pnum}, Section {snum}: {stitle}",
                    "keywords": f"vishnu purana part {pnum} section {snum} {pnum}.{snum} {ptitle.lower()} {stitle.lower()}",
                    "citationIds": [doc_id],
                    "questions": questions,
                    "answers": {
                        "en": {
                            "default": what_ans,
                            "what": what_ans,
                            "why": why_ans,
                            "how": how_ans,
                            "when": when_ans,
                            "where": where_ans,
                            "who": who_ans,
                        },
                        "hi": {"default": hi_ans},
                    },
                    "_embed": f"Vishnu Purana Part {pnum} Section {snum} {ptitle} {stitle} {summary}",
                }
            )

        if part_cids:
            sample_topics = ", ".join(section_titles[:4])
            s2_marker = "[S2]" if len(part_cids) > 1 else "[S1]"
            what_ans = (
                f'Vishnu Purana Part {pnum}, titled "{ptitle}", contains {scount} sections focused on {ptheme.lower()} [S1]. '
                f"Its sections include {sample_topics} {s2_marker}."
            )
            why_ans = f"Part {pnum} ({ptitle}) is crucial because its {scount} sections explain {ptheme.lower()} in the cosmic narrative of the Vishnu Purana [S1]."
            how_ans = f"Part {pnum} progresses through {scount} dialogue sections between Maitreya and Sage Parashara, beginning with {sample_topics} [S1]."
            when_ans = f"Part {pnum} ({ptitle}) forms the {pnum}th of the six books (Amshas) of the Vishnu Purana, detailing {ptheme.lower()} [S1]."
            where_ans = f"Part {pnum} ({ptitle}) spans {scount} sections within the six-part structure of the Vishnu Purana [S1]."
            who_ans = f"Throughout Part {pnum} ({ptitle}), Sage Parashara answers Maitreya's questions across {scount} sections on {ptheme.lower()} [S1]."
            hi_ans = (
                f"विष्णु पुराण के {p_hi} ({ptitle}) में {scount} अध्याय हैं, जिनका मुख्य विषय {ptheme} है [S1]।"
            )

            questions = [
                {"q": f"What is Vishnu Purana Part {pnum} about?", "aspect": "what"},
                {
                    "q": f"What does Part {pnum} ({ptitle}) of the Vishnu Purana cover?",
                    "aspect": "what",
                },
                {"q": f"What is the summary of Vishnu Purana Part {pnum}?", "aspect": "what"},
                {"q": f"Why is Vishnu Purana Part {pnum} significant?", "aspect": "why"},
                {
                    "q": f"Why does Sage Parashara teach Part {pnum} of Vishnu Purana?",
                    "aspect": "why",
                },
                {"q": f"How is Vishnu Purana Part {pnum} organized?", "aspect": "how"},
                {"q": f"How many sections are in Vishnu Purana Part {pnum}?", "aspect": "what"},
                {"q": f"When is Vishnu Purana Part {pnum} studied in the text?", "aspect": "when"},
                {"q": f"When does Part {pnum} appear in the Vishnu Purana?", "aspect": "when"},
                {
                    "q": f"Where do the teachings of Part {pnum} fit in Vishnu Purana?",
                    "aspect": "where",
                },
                {"q": f"Where does Part {pnum} ({ptitle}) appear?", "aspect": "where"},
                {"q": f"Who narrates Vishnu Purana Part {pnum}?", "aspect": "who"},
                {"q": f"Who is listening in Vishnu Purana Part {pnum}?", "aspect": "who"},
                {"q": f"Summarize Vishnu Purana Part {pnum} simply", "aspect": "summary"},
                {"q": f"What are the key points of Vishnu Purana Part {pnum}?", "aspect": "points"},
                {"q": f"Vishnu Purana Part {pnum} mein kya hai?", "aspect": "what"},
                {"q": f"Vishnu Purana Ansh {pnum} ka saar kya hai?", "aspect": "summary"},
                {"q": f"विष्णु पुराण {p_hi} का क्या सार है?", "aspect": "hi"},
            ]

            clusters.append(
                {
                    "id": f"vishnu_part_{pnum}",
                    "type": "vishnu_part",
                    "sourceId": "vishnu-purana",
                    "title": f"Vishnu Purana Part {pnum}: {ptitle}",
                    "keywords": f"vishnu purana part {pnum} {ptitle.lower()} {ptheme.lower()} {p_hi}",
                    "citationIds": part_cids,
                    "questions": questions,
                    "answers": {
                        "en": {
                            "default": what_ans,
                            "what": what_ans,
                            "why": why_ans,
                            "how": how_ans,
                            "when": when_ans,
                            "where": where_ans,
                            "who": who_ans,
                        },
                        "hi": {"default": hi_ans},
                    },
                    "_embed": f"Vishnu Purana Part {pnum} {ptitle} {ptheme} {sample_topics}",
                }
            )

    return clusters


def _attach_summary_and_points(cluster: dict) -> None:
    """Ensure every cluster exposes plain 'summary' and bulleted 'points' answers + questions."""
    answers_en = cluster.setdefault("answers", {}).setdefault("en", {})
    what_txt = _clean_whitespace(answers_en.get("what") or answers_en.get("default") or "")
    why_txt = _clean_whitespace(answers_en.get("why") or what_txt)
    how_txt = _clean_whitespace(answers_en.get("how") or what_txt)
    cids = cluster.get("citationIds") or []
    marker = "[S1]" if cids else ""

    if not answers_en.get("summary"):
        core = _sentence_clip(what_txt, 250)
        if marker and "[S" not in core:
            core = core.rstrip(".") + f" {marker}."
        if how_txt and how_txt.lower() != what_txt.lower() and len(core) < 240:
            app = _sentence_clip(how_txt, 170)
            if marker and "[S" not in app:
                app = app.rstrip(".") + f" {marker}."
            answers_en["summary"] = f"{core} {app}".strip()
        else:
            answers_en["summary"] = core

    if not answers_en.get("points"):
        p1 = _sentence_clip(what_txt, 175)
        p2 = _sentence_clip(why_txt, 175)
        p3 = _sentence_clip(how_txt, 175)
        bullets = []
        for label, body in (("Core idea", p1), ("Why it matters", p2), ("Takeaway", p3)):
            if marker and "[S" not in body:
                body = body.rstrip(".") + f" {marker}."
            bullets.append(f"- **{label}**: {body}")
        answers_en["points"] = "\n".join(bullets)

    if cluster.get("type") == "topic":
        title_l = cluster["title"].lower()
        existing = {q["q"].lower() for q in cluster.get("questions") or []}
        extras = [
            (f"Summarize {title_l}", "summary"),
            (f"Explain {title_l} in simple words", "summary"),
            (f"What are the key points about {title_l}?", "points"),
        ]
        for q_text, aspect in extras:
            if q_text.lower() not in existing:
                cluster["questions"].append({"q": q_text, "aspect": aspect})


def _build_curated_clusters(records_by_id: dict[str, dict]):
    """Load curated 5W1H spiritual/life topics and attach citation metadata."""
    from scripts.qa_topics import CURATED_TOPICS

    clusters = []
    for topic in CURATED_TOPICS:
        cids = list(topic.get("citationIds") or [])
        missing = [cid for cid in cids if cid not in records_by_id]
        if missing:
            raise ValueError(
                f"Curated topic {topic['id']} references unknown citationIds: {missing}"
            )

        q_sample = " ".join(item["q"] for item in topic["questions"][:6])
        embed_text = f"{topic['title']} {topic['keywords']} {q_sample}"
        clusters.append(
            {
                "id": topic["id"],
                "type": topic.get("type", "topic"),
                "sourceId": topic.get("sourceId", "all"),
                "title": topic["title"],
                "keywords": topic["keywords"],
                "citationIds": cids,
                "questions": topic["questions"],
                "answers": topic["answers"],
                "_embed": embed_text,
            }
        )
    return clusters


def _embed_clusters(embed_texts: list[str], batch_size: int = 128) -> np.ndarray:
    """Compute normalized float16 vectors for every cluster using LocalScriptureEmbeddings."""
    embeddings = LocalScriptureEmbeddings()
    embeddings.load()
    vectors: list[list[float]] = []
    try:
        for start in range(0, len(embed_texts), batch_size):
            batch = embed_texts[start : start + batch_size]
            batch_vecs = embeddings.embed_documents(batch)
            vectors.extend(batch_vecs)
            if (start // batch_size) % 4 == 0:
                print(
                    f"  Embedded {min(start + batch_size, len(embed_texts))}/{len(embed_texts)} clusters..."
                )
    finally:
        embeddings.close()

    arr = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    arr = arr / norms
    return arr.astype(np.float16)


def _sync_firestore(clusters: list[dict], records: dict[str, dict], vectors: np.ndarray) -> None:
    """Optional upload of Q&A bank clusters to Firestore `qaBank` collection."""
    from gyansutra.firestore import ScriptureStore

    store = ScriptureStore()
    if not store.available or store.db is None:
        raise RuntimeError("Firestore is not configured; cannot run --sync-firestore.")

    collection = os.getenv("FIRESTORE_QABANK_COLLECTION", "qaBank")
    batch = store.db.batch()
    pending = 0
    written = 0

    for idx, cluster in enumerate(clusters):
        doc_ref = store.db.collection(collection).document(cluster["id"])
        payload = {
            **cluster,
            "citations": [records[cid] for cid in cluster["citationIds"] if cid in records],
            "embedding": vectors[idx].astype(np.float32).tolist(),
        }
        batch.set(doc_ref, payload, merge=True)
        pending += 1
        written += 1
        if pending >= 250:
            batch.commit()
            batch = store.db.batch()
            pending = 0

    if pending:
        batch.commit()
    print(f"Synced {written} Q&A clusters to Firestore collection '{collection}'.")


def build_bank(sync_firestore: bool = False) -> dict:
    """Build the entire Q&A bank, write compressed artifacts, and return summary metrics."""
    started = time.perf_counter()
    records_by_id: dict[str, dict] = {}

    from scripts.qa_topics import CURATED_TOPICS

    needed_cids = {cid for topic in CURATED_TOPICS for cid in (topic.get("citationIds") or [])}

    print("1/5 Building Bhagavad Gita verse & chapter clusters...")
    gita_clusters = _build_gita_data(records_by_id)

    print("2/5 Building Valmiki Ramayana sarga & kanda clusters...")
    ramayana_clusters = _build_ramayana_data(records_by_id, needed_cids=needed_cids)

    print("3/5 Building Vishnu Purana section & part clusters...")
    vishnu_clusters = _build_vishnu_data(records_by_id)

    print("4/5 Attaching curated 5W1H topic clusters...")
    curated_clusters = _build_curated_clusters(records_by_id)

    # Order curated topics + macro chapters/kandas/parts before verse/sarga clusters so ties favor richer answers.
    all_clusters = []
    seen_ids = set()
    for group in (curated_clusters, gita_clusters, ramayana_clusters, vishnu_clusters):
        for cluster in group:
            cid = cluster["id"]
            if cid in seen_ids:
                raise ValueError(f"Duplicate cluster ID generated: {cid}")
            seen_ids.add(cid)
            _attach_summary_and_points(cluster)
            all_clusters.append(cluster)

    embed_texts = [c.pop("_embed") for c in all_clusters]
    print(f"5/5 Computing 384-dim Xenova/gte-small embeddings for {len(all_clusters)} clusters...")
    vectors = _embed_clusters(embed_texts)

    total_questions = sum(len(c["questions"]) for c in all_clusters)
    aspect_counts: dict[str, int] = defaultdict(int)
    for c in all_clusters:
        for q in c["questions"]:
            aspect_counts[q["aspect"]] += 1

    payload = {
        "version": 1,
        "model": os.getenv("EMBEDDING_MODEL_ID", "Xenova/gte-small"),
        "dimensions": int(vectors.shape[1]),
        "clusterCount": len(all_clusters),
        "questionCount": total_questions,
        "records": records_by_id,
        "clusters": all_clusters,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUTPUT_BANK, "wt", encoding="utf-8", compresslevel=6) as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    np.savez_compressed(OUTPUT_VECTORS, vectors=vectors)

    if sync_firestore:
        _sync_firestore(all_clusters, records_by_id, vectors)

    elapsed = time.perf_counter() - started
    bank_size = OUTPUT_BANK.stat().st_size
    vec_size = OUTPUT_VECTORS.stat().st_size

    stats = {
        "clusters": len(all_clusters),
        "questions": total_questions,
        "records": len(records_by_id),
        "aspects": dict(aspect_counts),
        "bankBytes": bank_size,
        "vectorBytes": vec_size,
        "elapsedSec": round(elapsed, 2),
    }
    print(f"Done in {stats['elapsedSec']}s: {json.dumps(stats, ensure_ascii=False)}")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Sarathi AI 20,000+ pre-computed Q&A bank")
    parser.add_argument(
        "--sync-firestore",
        action="store_true",
        help="Also upload built Q&A clusters to Firestore qaBank collection",
    )
    args = parser.parse_args()
    build_bank(sync_firestore=args.sync_firestore)


if __name__ == "__main__":
    main()
