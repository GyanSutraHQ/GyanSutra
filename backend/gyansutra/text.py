"""Deterministic scripture routing, guardrails, reranking and citation checks."""

import json
import math
import unicodedata

import regex as re

from .config import ROOT

POLICY = json.loads((ROOT / "data/ai-policy.json").read_text())
SOURCES = POLICY["sources"]
STOP_WORDS = set(
    "a an and are about does for from how in is it me of on or the to what when where which who why with teach teaches explain please tell give according scripture scriptures can could should would do did this that those these its my your us more follow up और का की के क्या को से है हैं में पर यह वह मुझे बताओ समझाओ".split()
)
KANDAS = {
    name: index + 1
    for index, name in enumerate("bala ayodhya aranya kishkindha sundara yuddha uttara".split())
}


def normalize_question(value) -> str:
    value = unicodedata.normalize("NFKC", str(value or "")).lower()
    value = value.translate(str.maketrans("०१२३४५६७८९", "0123456789"))
    return re.sub(r"\s+", " ", re.sub(r"[\u200b-\u200d\ufeff]", "", value)).strip()


def modernize(value):
    if not isinstance(value, str):
        return value
    for pattern, replacement in POLICY["modernEnglish"]:
        value = re.sub(
            pattern,
            lambda m, r=replacement: r[:1].upper() + r[1:] if m[0][0].isupper() else r,
            value,
            flags=re.I,
        )
    return value


def truncate(value, maximum: int) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= maximum:
        return text
    clipped = text[: max(1, maximum - 1)]
    boundary = max(clipped.rfind(". "), clipped.rfind("। "), clipped.rfind(" "))
    return clipped[: boundary if boundary > maximum * 0.55 else len(clipped)].strip() + "…"


def reference(kind: str, values: tuple) -> dict | None:
    if kind == "gita":
        chapter, verse = values
        if 1 <= chapter <= 18 and verse >= 1:
            return {
                "type": kind,
                "id": f"bhagavad-gita_{chapter}_{verse}",
                "chapterNumber": chapter,
                "verseNumber": verse,
            }
    elif kind == "ramayana":
        kanda, sarga, shloka = values
        if 1 <= kanda <= 7 and sarga >= 1 and shloka >= 1:
            return {
                "type": kind,
                "id": f"valmiki-ramayana_{kanda}_{sarga}_{shloka}",
                "kandaNumber": kanda,
                "sarga": sarga,
                "shlokaNumber": shloka,
            }
    else:
        part, section = values
        if 1 <= part <= 6 and section >= 1:
            return {
                "type": kind,
                "id": f"vishnu-purana_{part}_{section}",
                "partNumber": part,
                "sectionNumber": section,
            }
    return None


def explicit_references(value, maximum=4) -> list[dict]:
    question = normalize_question(value)
    patterns = [
        (
            "vishnu-purana",
            r"(?:vishnu\s*purana|viṣṇu\s*purāṇa|विष्णु\s*पुराण)[^\d]{0,30}(?:part|book|a[mṃ]s[ha]|अंश)\s*(\d)[^\d]{0,20}(?:section|chapter|अध्याय)\s*(\d{1,2})",
        ),
        (
            "gita",
            r"(?:bhagavad\s*gita|gita|bg|भगवद्?\s*गीता|गीता)\s*(?:chapter|अध्याय)?\s*(\d{1,2})\s*[.:/\-]\s*(\d{1,3})",
        ),
        (
            "gita",
            r"(?:chapter|अध्याय)\s*(\d{1,2})(?:\s*,?\s*|\s+and\s+)(?:verse|shloka|श्लोक)\s*(\d{1,3})",
        ),
        (
            "ramayana",
            r"(?:valmiki\s+)?(?:ramayana|रामायण)\s*(\d)\s*[.:/\-]\s*(\d{1,3})\s*[.:/\-]\s*(\d{1,3})",
        ),
        (
            "ramayana",
            r"(?:kanda|काण्ड|कांड)\s*(\d)(?:\s*,?\s*|\s+and\s+)(?:sarga|सर्ग)\s*(\d{1,3})(?:\s*,?\s*|\s+and\s+)(?:shloka|verse|श्लोक)\s*(\d{1,3})",
        ),
    ]
    result = []
    for kind, pattern in patterns:
        match = re.search(pattern, question, re.I)
        if match and (item := reference(kind, tuple(map(int, match.groups())))):
            result.append(item)
            break
    if not result:
        match = re.search(
            r"(bala|ayodhya|aranya|kishkindha|sundara|yuddha|uttara)(?:\s+kanda)?\s*,?\s*sarga\s*(\d{1,3})\s*,?\s*(?:shloka|verse)\s*(\d{1,3})",
            question,
        )
        if match and (
            item := reference("ramayana", (KANDAS[match[1]], int(match[2]), int(match[3])))
        ):
            result.append(item)
    extra = []
    if re.search(r"vishnu\s*purana|viṣṇu\s*purāṇa|विष्णु\s*पुराण", question):
        extra.append(
            (
                "vishnu-purana",
                r"(?:part|book|a[mṃ]s[ha]|अंश)\s*(\d)[^\d]{0,20}(?:section|chapter|अध्याय)\s*(\d{1,2})",
            )
        )
    if re.search(r"bhagavad\s*gita|\bgita\b|\bbg\b|भगवद्?\s*गीता|गीता", question):
        extra.append(("gita", r"(\d{1,2})\s*[.:/\-]\s*(\d{1,3})"))
    if re.search(r"ramayana|रामायण", question):
        extra.append(("ramayana", r"(\d)\s*[.:/\-]\s*(\d{1,3})\s*[.:/\-]\s*(\d{1,3})"))
    seen = {item["id"] for item in result}
    for kind, pattern in extra:
        for match in re.finditer(pattern, question):
            item = reference(kind, tuple(map(int, match.groups())))
            if item and item["id"] not in seen:
                result.append(item)
                seen.add(item["id"])
    return result[:maximum]


def follow_up(value) -> bool:
    question = normalize_question(value)
    return len(question.split()) <= 18 and bool(
        re.search(
            r"\b(it|that|this|those|them|first|second|former|latter|above|more|why|how|what about)\b|यह|इस|उस|वह|इन|उन|पहले|दूसरे|और समझा|क्यों|कैसे",
            question,
        )
    )


def retrieval_query(question, history) -> str:
    if follow_up(question):
        previous = next(
            (
                m
                for m in reversed(history)
                if m.get("role") == "user" and isinstance(m.get("content"), str)
            ),
            None,
        )
        if previous:
            return f"{previous['content'][:350]}\nFollow-up: {question}"
    return question


def direct_request(question) -> bool:
    return bool(
        explicit_references(question)
        and re.search(
            r"\b(show|quote|display|read|text|translation|original verse)\b|दिखा|पढ़|मूल श्लोक|अनुवाद",
            question,
            re.I,
        )
    )


def context_ids(values) -> list[str]:
    if not isinstance(values, list):
        return []
    return list(
        dict.fromkeys(
            v.strip()
            for v in values
            if isinstance(v, str)
            and re.fullmatch(
                r"(?:bhagavad-gita_\d+_\d+|valmiki-ramayana_\d+_\d+_\d+|vishnu-purana_\d+_\d+(?:_\d+)?)",
                v.strip(),
            )
        )
    )[:4]


def classify_guardrail(question, language="en") -> dict | None:
    value = re.sub(
        r"^(?:(?:question|user|q)\s*[.:)\]\-]*\s*)+", "", normalize_question(question), flags=re.I
    ).strip()
    copy = POLICY["guardrailCopy"].get(language, POLICY["guardrailCopy"]["en"])
    suffix = r"(?:[,:]?\s+(?:sarathi|saarthi))?[!?.]*"
    patterns = {
        "greeting": r"(?:hi|hello|hey|namaste|namaskar|good (?:morning|afternoon|evening))(?:\s+(?:sarathi|saarthi))?[!?.]*",
        "identity": r"(?:who|what) (?:are|is) (?:you|sarathi|saarthi)" + suffix,
        "capabilities": r"(?:tell me about yourself|introduce yourself|what can you do)" + suffix,
        "wellbeing": r"(?:how are you|how(?:'s| is) it going|are you (?:okay|well))(?:\s+(?:sarathi|saarthi))?[!?.]*",
        "thanks": r"(?:thanks|thank you|thankyou|dhanyavad|shukriya)(?:\s+(?:sarathi|saarthi))?[!?.]*",
    }
    for key, pattern in patterns.items():
        if re.fullmatch(pattern, value, re.I):
            return {"type": "conversational", "answer": copy[key]}
    utility = [
        r"\b(?:what|which) (?:day|date) (?:is it|is today|is today\'?s)\b",
        r"\b(?:what(?:'s| is) )?(?:today\'?s|current) (?:day|date|time)\b",
        r"\b(?:weather|temperature|forecast)\b",
        r"\b(?:what is|define|tell me about) python\b",
        r"\b(?:what is|define|tell me about) (?:javascript|java|programming|coding|an algorithm)\b",
        r"\b(?:write|debug|fix) (?:a |the )?(?:python|javascript|java|code|program)\b",
    ]
    if any(re.search(p, value, re.I) for p in utility):
        return {"type": "out_of_scope", "answer": copy["outOfScope"]}
    return None


def terms(value) -> list[str]:
    return [
        t
        for t in re.findall(r"[\p{L}\p{N}][\p{L}\p{M}\p{N}]*", normalize_question(value))
        if len(t) > 1 and t not in STOP_WORDS
    ]


def tokenize(value) -> set[str]:
    return set(terms(value))


def rerank(candidates, question) -> list[dict]:
    tokens = tokenize(question)
    seen = set()
    ranked = []
    for verse in candidates:
        if not verse.get("id") or verse["id"] in seen:
            continue
        seen.add(verse["id"])
        text = " ".join(
            str(verse.get(k) or "")
            for k in "translationEnglish translationHindi transliteration explanationEnglish comments storyTitle storySummary".split()
        )
        text += " " + " ".join(verse.get("tags") or [])
        text += " " + " ".join(
            item.get("explanation", "") for item in (verse.get("detailedExplanations") or [])[:3]
        )
        lexical = len(tokens & tokenize(text)) / len(tokens) if tokens else 0
        semantic = verse.get("similarity", 0)
        semantic = semantic if isinstance(semantic, (int, float)) and math.isfinite(semantic) else 0
        ranked.append(
            {**verse, "rerankScore": 1 if semantic >= 0.999 else semantic * 0.88 + lexical * 0.12}
        )
    return sorted(ranked, key=lambda v: v["rerankScore"], reverse=True)


def verse_reference(verse) -> str:
    if verse.get("book") == "vishnu-purana" or verse.get("partNumber"):
        passage = f", Passage {verse['passageNumber']}" if verse.get("passageNumber") else ""
        return f"Vishnu Purana, Part {verse.get('partNumber')}, Section {verse.get('sectionNumber')}{passage}"
    if verse.get("book") == "ramayana" or verse.get("kanda") or verse.get("kandaNumber"):
        kanda = verse.get("kanda") or f"Kanda {verse.get('kandaNumber')}"
        return f"Valmiki Ramayana, {kanda}, Sarga {verse.get('sarga')}, Shloka {verse.get('shlokaNumber')}"
    return f"Bhagavad Gita, Chapter {verse.get('chapterNumber')}, Verse {verse.get('verseNumber')}"


def response_script_matches(answer, language):
    script = {
        "hi": "Devanagari",
        "mr": "Devanagari",
        "bn": "Bengali",
        "te": "Telugu",
        "ta": "Tamil",
    }.get(language)
    if not script:
        return True
    # This catches wrong-script output; it cannot distinguish Hindi from Marathi.
    prose = re.sub(r"\[S\d+\]", "", str(answer), flags=re.I)
    letters = re.findall(r"\p{L}", prose)
    target = sum(bool(re.fullmatch(r"\p{" + script + "}", letter)) for letter in letters)
    return bool(letters) and target >= len(letters) * 0.25


def unsupported_references(answer, allowed_ids, source_count) -> list[str]:
    text = str(answer or "").translate(str.maketrans("०१२३४५६७८९", "0123456789"))
    unsupported = []
    valid = 0
    for match in re.finditer(r"\[S(\d+)\]", text, re.I):
        if not 1 <= int(match[1]) <= source_count:
            unsupported.append(match[0])
        else:
            valid += 1
    if source_count and not valid:
        unsupported.append("missing source marker")
    for marker in re.findall(r"\[S[^\]\n]{0,30}\]", text, re.I):
        if not re.fullmatch(r"\[S\d+\]", marker, re.I):
            unsupported.append(marker)
    # Reuse multilingual routing rules so Hindi references cannot bypass validation.
    for ref in explicit_references(text, maximum=100):
        doc_id = ref["id"]
        if doc_id not in allowed_ids and not (
            ref["type"] == "vishnu-purana" and any(v.startswith(doc_id + "_") for v in allowed_ids)
        ):
            unsupported.append(doc_id)
    patterns = [
        (
            "bhagavad-gita",
            r"(?:bhagavad\s*gita|gita)\s*(?:chapter\s*)?(\d{1,2})\s*[,.:\-]?\s*(?:verse\s*)?(\d{1,3})",
        ),
        ("bhagavad-gita", r"chapter\s*(\d{1,2})\s*[,.:\-]?\s*verse\s*(\d{1,3})"),
        (
            "valmiki-ramayana",
            r"(?:valmiki\s+)?ramayana[^\n]{0,50}?(?:kanda\s*)?(\d)[,.:\-\s]+(?:sarga\s*)?(\d{1,3})[,.:\-\s]+(?:shloka|verse)\s*(\d{1,3})",
        ),
        (
            "vishnu-purana",
            r"vishnu\s*purana[^\n]{0,40}?(?:part|book)\s*(\d)[^\d]{0,20}(?:section|chapter)\s*(\d{1,2})",
        ),
    ]
    for book, pattern in patterns:
        for match in re.finditer(pattern, text, re.I):
            doc_id = book + "_" + "_".join(str(int(v)) for v in match.groups())
            allowed = doc_id in allowed_ids or (
                book == "vishnu-purana" and any(v.startswith(doc_id + "_") for v in allowed_ids)
            )
            if not allowed:
                unsupported.append(match[0])
    return list(dict.fromkeys(unsupported))
