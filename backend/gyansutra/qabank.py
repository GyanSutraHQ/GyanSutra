"""Pre-computed Q&A bank service for fast, zero-LLM-cost scripture answers."""

from __future__ import annotations

import asyncio
import gzip
import json
import math
import re
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from .config import ROOT
from .retrieval import query_terms, requested_sources, source_id
from .text import (
    direct_request,
    explicit_references,
    follow_up,
    normalize_question,
    terms,
    tokenize,
)

BANK_PATH = ROOT / "data" / "qa_bank.json.gz"
VECTORS_PATH = ROOT / "data" / "qa_vectors.npz"

KANDA_BY_NAME = {
    "bala": 1,
    "bal": 1,
    "ayodhya": 2,
    "aranya": 3,
    "kishkindha": 4,
    "sundara": 5,
    "sundar": 5,
    "yuddha": 6,
    "lanka": 6,
    "uttara": 7,
    "uttar": 7,
}

KANDA_HI_BY_NAME = {
    "बालकाण्ड": 1,
    "बालकांड": 1,
    "अयोध्याकाण्ड": 2,
    "अयोध्याकांड": 2,
    "अरण्यकाण्ड": 3,
    "अरण्यकांड": 3,
    "किष्किन्धाकाण्ड": 4,
    "किष्किन्धाकांड": 4,
    "सुन्दरकाण्ड": 5,
    "सुन्दरकांड": 5,
    "सुंदरकांड": 5,
    "युद्धकाण्ड": 6,
    "युद्धकांड": 6,
    "उत्तरकाण्ड": 7,
    "उत्तरकांड": 7,
}

BOILERPLATE_TERMS = frozenset(
    """
    about answer apply appear appears addressed book brief bullet canto chapter chapters
    concise daily describe details distinguish does english explain excerpt figure figures
    happen happens hindi ideas importance important inspiration inspire interpretation
    invent kanda kandas key language life list main mean meaning number organize organized
    overview part parts partial plain points practice practiced read remember role sarga
    sargas say says section sections sentences setting shloka shlokas short significance
    significant simple source speak speaker speaking spoken stage story structure summarize
    summary teach teaches teaching tell text three translation two unfold verse verses
    """.split()
)

HINGLISH_MAP = {
    "matlab": "meaning",
    "arth": "meaning",
    "kya": "what",
    "kaise": "how",
    "kyun": "why",
    "kyon": "why",
    "kyo": "why",
    "kaun": "who",
    "kisne": "who",
    "kisko": "who",
    "kab": "when",
    "kahan": "where",
    "kahaan": "where",
    "gussa": "anger",
    "krodh": "anger",
    "chinta": "anxiety",
    "tension": "anxiety",
    "pareshani": "anxiety",
    "darr": "fear",
    "dar": "fear",
    "bhay": "fear",
    "shanti": "peace",
    "sukoon": "peace",
    "dukh": "grief",
    "dukkha": "suffering",
    "gham": "grief",
    "udaasi": "sadness",
    "mann": "mind",
    "dimag": "mind",
    "kartavya": "duty",
    "farz": "duty",
    "ahankar": "ego",
    "ghamand": "ego",
    "maafi": "forgiveness",
    "kshama": "forgiveness",
    "srishti": "creation",
    "mrityu": "death",
    "maut": "death",
    "safalta": "success",
    "haar": "failure",
    "asafalta": "failure",
    "alsi": "laziness",
    "aalas": "laziness",
    "alasya": "laziness",
    "jalan": "jealousy",
    "irshya": "jealousy",
    "paisa": "wealth",
    "dhan": "wealth",
    "saar": "summary",
    "sar": "summary",
    "samjhaiye": "explain",
    "samjhao": "explain",
    "bataya": "teach",
    "kahani": "story",
    "katha": "story",
    "akelepan": "loneliness",
    "akelapan": "loneliness",
    "bhakti": "devotion",
    "vishwas": "faith",
    "shraddha": "faith",
    "prem": "love",
    "pyar": "love",
    "neend": "sleep",
    "karm": "karma",
    "dharm": "dharma",
    "moksh": "liberation",
    "mukti": "liberation",
    "narak": "hell",
    "swarg": "heaven",
    "paap": "sin",
    "punya": "virtue",
    "dhyan": "meditation",
    "ishwar": "god",
    "bhagwan": "god",
    "prabhu": "god",
    "aatma": "soul",
    "atma": "soul",
    "punarjanam": "reincarnation",
    "rishta": "relationship",
    "rishtey": "relationships",
    "parivar": "family",
    "dost": "friendship",
    "dosti": "friendship",
    "bharosa": "trust",
    "dhoka": "betrayal",
    "seva": "service",
    "tyag": "renunciation",
    "sanyas": "renunciation",
    "ahimsa": "nonviolence",
    "satya": "truth",
    "sach": "truth",
    "lobh": "greed",
    "lalach": "greed",
    "moh": "attachment",
    "moha": "attachment",
    "kaam": "desire",
    "vasna": "desire",
    "ichha": "desire",
    "iccha": "desire",
    "buddhi": "wisdom",
    "gyan": "knowledge",
    "vidya": "knowledge",
    "kaal": "time",
    "yug": "yuga",
    "avtar": "avatar",
    "niti": "ethics",
    "mukhya": "key",
    "bindu": "points",
}

HINGLISH_NOISE = frozenset(
    """
    anusar anusaar aur baare bare bata bataiye batao batayein bhi hai hain hota
    hote hoti iska iske iski ka kar karein karen karna karo ke ki ko mein saral
    samjha shabdon tha thi toh unke ya
    """.split()
)

# Canonical Sanskrit terms that already appear directly in English scripture discussions.
_CORPUS_SANSKRIT = frozenset(
    "bhakti dhyan ahimsa satya seva tyag sanyas gyan buddhi atma aatma prabhu shanti yug prem"
    .split()
)
_HINGLISH_TRIGGER = (frozenset(HINGLISH_MAP) | HINGLISH_NOISE) - _CORPUS_SANSKRIT


def _translate_hinglish_text(question: str, *, include_corpus_terms: bool = False) -> tuple[str, bool]:
    """Translate Romanized Hindi words into English equivalents for dense and lexical matching."""
    raw = re.findall(r"[a-z0-9]+", normalize_question(question))
    if not any(tok in _HINGLISH_TRIGGER for tok in raw):
        return question, False
    out: list[str] = []
    for tok in raw:
        if tok in HINGLISH_NOISE:
            continue
        mapped = HINGLISH_MAP.get(tok)
        if mapped:
            if include_corpus_terms and tok in _CORPUS_SANSKRIT:
                out.append(tok)
            out.append(mapped)
        else:
            out.append(tok)
    return (" ".join(out) or question), True


def detect_aspect(question: str) -> str:
    """Classify user query intent (`what`, `why`, `how`, `when`, `where`, `who`, `summary`, `points`)."""
    text = normalize_question(question).lower()
    if re.search(
        r"\bbullet\s*points?\b|\bkey\s*(?:points?|ideas?|takeaways?|lessons?|highlights?)\b"
        r"|\bmain\s*(?:points?|ideas?|takeaways?)\b|\btakeaways?\b|मुख्य\s*बिंदु|\bmukhya\s*bindu\b",
        text,
    ):
        return "points"
    if re.search(
        r"\bsummar(?:y|ize)\b|\bplain\b.*\bsimple\s*language\b|\bsimple\s*language\b"
        r"|\bexplain\s+simply\b|\bin\s+short\b|\btl;?dr\b|\bsa+ra+nsh\b|\bsaa?r\b|सारांश|सरल\s*शब्दों",
        text,
    ):
        return "summary"
    if re.search(r"\bhow come\b|\bwhy\b|\bkyu?n\b|\bkyon\b|\bkyo\b|क्यों", text):
        return "why"
    if re.search(r"\bwhen\b|\bkab\b|कब", text):
        return "when"
    if re.search(r"\bwhere\b|\bkaha+n\b|कहाँ|कहां", text):
        return "where"
    if re.search(r"\bwho\b|\bwhom\b|\bwhose\b|\bkaun\b|\bkisn?e\b|\bkisko\b|कौन|किसने|किसको", text):
        return "who"
    if re.search(r"\bhow\b|\bkaise\b|कैसे", text):
        return "how"
    return "what"


def _bank_tokens(value: str) -> set[str]:
    """Extract normalized English + Hinglish-expanded + Devanagari lexical tokens."""
    tokens = set(tokenize(value))
    raw_en = re.findall(r"[a-z0-9]+", normalize_question(value))
    hinglish_words = [HINGLISH_MAP[tok] for tok in raw_en if tok in HINGLISH_MAP]
    if hinglish_words:
        tokens.update(tokenize(" ".join(hinglish_words)))
    for match in re.findall(r"[\u0900-\u097F]{2,}", normalize_question(value)):
        tokens.add(match)
    return tokens


def _query_lex_tokens(question: str) -> set[str]:
    """Extract normalized topical tokens for BM25 lookup and alien-term rejection."""
    mapped, is_hinglish = _translate_hinglish_text(question, include_corpus_terms=True)
    source_text = mapped if is_hinglish else question
    q_tokens = _bank_tokens(source_text)
    if _has_devanagari(question):
        q_tokens |= {t for t in _bank_tokens(question) if _has_devanagari(t)}
    allowed = set(query_terms(source_text)) | {t for t in q_tokens if _has_devanagari(t)}
    return {t for t in q_tokens if t not in BOILERPLATE_TERMS} & allowed


def _strip_assistant_boilerplate(question: str) -> tuple[str, bool]:
    """Strip ReadingAssistant instructions/excerpt suffix while flagging assistant prompts."""
    lower = question.lower()
    is_assistant = (
        "distinguish interpretation from translation" in lower
        or "partial source excerpt" in lower
    )
    if not is_assistant:
        return question, False
    head = re.split(
        r"(?:\bpartial source excerpt\b|distinguish interpretation from translation|\banswer in\b)",
        question,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip(" .:\n")
    return (head or question), True


def _has_devanagari(value: str) -> bool:
    return bool(re.search(r"[\u0900-\u097F]", value or ""))


def _macro_cluster_id(question: str) -> str | None:
    """Resolve chapter-, sarga-, kanda-, or part-level explicit references."""
    text = normalize_question(question)

    # 1. Ramayana Sarga (named Kanda or numbered Kanda + Sarga/Chapter)
    sarga_named = re.search(
        r"\b(bala|bal|ayodhya|aranya|kishkindha|sundara|sundar|yuddha|lanka|uttara|uttar)\s*(?:kanda|kand)?\s*,?\s*(?:sarga|chapter|canto)\s*(\d{1,3})\b",
        text,
    )
    if sarga_named and not re.search(r"\b(?:shloka|verse)\s*\d+\b", text):
        knum = KANDA_BY_NAME[sarga_named[1]]
        snum = int(sarga_named[2])
        if snum >= 1:
            return f"ramayana_sarga_{knum}_{snum}"

    sarga_num = re.search(
        r"\bkanda\s*(\d)\s*,?\s*(?:sarga|chapter|canto)\s*(\d{1,3})\b",
        text,
    )
    if sarga_num and not re.search(r"\b(?:shloka|verse)\s*\d+\b", text):
        knum, snum = int(sarga_num[1]), int(sarga_num[2])
        if 1 <= knum <= 7 and snum >= 1:
            return f"ramayana_sarga_{knum}_{snum}"

    # 2. Bhagavad Gita Chapter (without verse number)
    if not re.search(r"\b(?:verse|shloka)\s*\d+\b|\d+\s*[.:/\-]\s*\d+", text):
        gita_ch = re.search(
            r"(?:bhagavad\s*gita|\bgita\b|\bbg\b|भगवद्?\s*गीता|गीता)\s*(?:chapter|अध्याय)\s*(\d{1,2})\b",
            text,
        ) or re.search(
            r"(?:chapter|अध्याय)\s*(\d{1,2})\s*(?:of\s+)?(?:the\s+)?(?:bhagavad\s*gita|\bgita\b)",
            text,
        )
        if gita_ch:
            ch = int(gita_ch[1])
            if 1 <= ch <= 18:
                return f"gita_chapter_{ch}"

    # 3. Vishnu Purana Part (without section number)
    if not re.search(r"\b(?:section|chapter)\s*\d+\b|अध्याय\s*\d+", text):
        vp_part = re.search(
            r"(?:vishnu\s*purana|viṣṇu\s*purāṇa|विष्णु\s*पुराण)\s*,?\s*(?:part|book|a[mṃ]s[ha]|अंश)\s*(\d)\b",
            text,
        )
        if vp_part:
            part = int(vp_part[1])
            if 1 <= part <= 6:
                return f"vishnu_part_{part}"

    # 4. Ramayana Kanda overview (named Kanda without sarga)
    kanda_match = re.search(
        r"\b(bala|bal|ayodhya|aranya|kishkindha|sundara|sundar|yuddha|uttara|uttar)\s+kanda\b",
        text,
    )
    if kanda_match and not re.search(r"\b(?:sarga|chapter|canto|shloka|verse)\s*\d+\b", text):
        return f"ramayana_kanda_{KANDA_BY_NAME[kanda_match[1]]}"

    for hi_name, knum in KANDA_HI_BY_NAME.items():
        if hi_name in text and not re.search(r"सर्ग\s*\d+", text):
            return f"ramayana_kanda_{knum}"

    return None


class QABankService:
    """In-memory hybrid lookup over 20,000+ pre-computed scripture Q&A pairs."""

    def __init__(self, bank_path=BANK_PATH, vectors_path=VECTORS_PATH):
        self.bank_path = bank_path
        self.vectors_path = vectors_path
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._lock = threading.Lock()
        self._load_future = None

        self.ready = False
        self.clusters: list[dict] = []
        self.records: dict[str, dict] = {}
        self.vectors: np.ndarray | None = None
        self.exact_map: dict[str, tuple[int, str]] = {}
        self.cluster_by_id: dict[str, int] = {}
        self.citation_to_cluster: dict[str, int] = {}
        self.postings: dict[str, list[tuple[int, float]]] = {}
        self.cluster_tokens: list[set[str]] = []

    def available(self) -> bool:
        return self.bank_path.exists() and self.vectors_path.exists()

    def load_sync(self) -> None:
        with self._lock:
            if self.ready:
                return
            if not self.available():
                self.ready = True
                return

            with gzip.open(self.bank_path, "rt", encoding="utf-8") as fh:
                data = json.load(fh)
            with np.load(self.vectors_path) as vec_data:
                vectors = np.asarray(vec_data["vectors"], dtype=np.float32)

            clusters = data.get("clusters") or []
            records = data.get("records") or {}

            exact_map: dict[str, tuple[int, str]] = {}
            cluster_by_id: dict[str, int] = {}
            citation_to_cluster: dict[str, int] = {}
            doc_freq: dict[str, int] = defaultdict(int)
            doc_tfs: list[Counter[str]] = []
            doc_lengths: list[int] = []
            cluster_tokens: list[set[str]] = []

            for idx, cluster in enumerate(clusters):
                cluster_by_id[cluster["id"]] = idx
                for cid in cluster.get("citationIds") or []:
                    # First cluster referencing a citation wins unless a verse-level cluster overrides it.
                    if cid not in citation_to_cluster or cluster.get("type") in (
                        "gita_verse",
                        "ramayana_sarga",
                        "vishnu_section",
                    ):
                        citation_to_cluster[cid] = idx

                q_texts = []
                for q_item in cluster.get("questions") or []:
                    q_text = q_item["q"]
                    norm = normalize_question(q_text)
                    if norm and norm not in exact_map:
                        exact_map[norm] = (idx, q_item.get("aspect") or "what")
                    q_texts.append(q_text)

                en_what = (cluster.get("answers") or {}).get("en", {}).get("what", "")
                hi_def = (cluster.get("answers") or {}).get("hi", {}).get("default", "")
                searchable = " ".join(
                    [
                        cluster.get("title", ""),
                        cluster.get("keywords", ""),
                        en_what,
                        hi_def,
                        *q_texts[:6],
                    ]
                )
                tokens = _bank_tokens(searchable)
                cluster_tokens.append(tokens)

                tf = Counter(terms(searchable) + re.findall(r"[\u0900-\u097F]{2,}", searchable))
                doc_tfs.append(tf)
                doc_lengths.append(max(1, sum(tf.values())))
                for term in tf:
                    doc_freq[term] += 1

            total_docs = max(1, len(clusters))
            avg_dl = sum(doc_lengths) / total_docs
            k1, b = 1.2, 0.65
            postings: dict[str, list[tuple[int, float]]] = defaultdict(list)

            for idx, tf in enumerate(doc_tfs):
                dl = doc_lengths[idx]
                norm_dl = 1 - b + b * (dl / max(1.0, avg_dl))
                for term, count in tf.items():
                    idf = math.log(1 + (total_docs - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
                    score = idf * (count * (k1 + 1)) / (count + k1 * norm_dl)
                    postings[term].append((idx, score))

            self.clusters = clusters
            self.records = records
            self.vectors = vectors
            self.exact_map = exact_map
            self.cluster_by_id = cluster_by_id
            self.citation_to_cluster = citation_to_cluster
            self.postings = dict(postings)
            self.cluster_tokens = cluster_tokens
            self.ready = True

    async def prewarm(self) -> None:
        if self.ready:
            return
        if self._load_future is None:
            loop = asyncio.get_running_loop()
            self._load_future = asyncio.ensure_future(loop.run_in_executor(self._executor, self.load_sync))
        await asyncio.shield(self._load_future)

    async def close(self) -> None:
        if self._load_future is not None:
            await asyncio.gather(self._load_future, return_exceptions=True)
        self._executor.shutdown(wait=True, cancel_futures=True)

    def _record_source(self, cid: str) -> str:
        rec = self.records.get(cid)
        return source_id(rec) if rec else ""

    def _source_allowed(self, cluster: dict, sources: set[str]) -> bool:
        if not sources:
            return True
        cids = cluster.get("citationIds") or []
        return bool(cids) and all(self._record_source(cid) in sources for cid in cids)

    def _format_hit(self, idx: int, aspect: str, language: str, question: str, score: float) -> dict:
        cluster = self.clusters[idx]
        answers = cluster.get("answers") or {}
        use_hindi = language == "hi" or (aspect == "hi") or _has_devanagari(question)
        if use_hindi and (answers.get("hi") or {}).get("default"):
            answer = answers["hi"]["default"]
        else:
            en_answers = answers.get("en") or {}
            answer = en_answers.get(aspect) or en_answers.get("default") or ""

        citations = []
        for cid in cluster.get("citationIds") or []:
            rec = self.records.get(cid)
            if rec:
                citations.append({**rec, "similarity": round(float(score), 4)})

        return {
            "matched": True,
            "clusterId": cluster["id"],
            "aspect": aspect,
            "score": float(score),
            "answer": answer,
            "citations": citations,
        }

    def _lexical_candidates(self, question: str, sources: set[str], limit: int = 32):
        content_tokens = _query_lex_tokens(question)
        q_tokens = _bank_tokens(question)
        if not content_tokens and not q_tokens:
            return [], set()

        scores: dict[int, float] = defaultdict(float)
        for token in content_tokens or q_tokens:
            for idx, weight in self.postings.get(token, ()):
                scores[idx] += weight

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        filtered = []
        for idx, bm25 in ranked:
            cluster = self.clusters[idx]
            if not self._source_allowed(cluster, sources):
                continue
            overlap = len(content_tokens & self.cluster_tokens[idx])
            if content_tokens and overlap == 0:
                continue
            filtered.append((idx, bm25, overlap))
            if len(filtered) >= limit:
                break
        return filtered, content_tokens

    def _extra_unknown_terms(self, question: str, cluster_idx: int) -> bool:
        """True if an explicit-reference query introduces significant out-of-cluster topical words."""
        content = {t for t in _query_lex_tokens(question) if not t.isdigit()}
        if not content:
            return False
        cluster = self.clusters[cluster_idx]
        corpus_text = " ".join(
            [
                cluster.get("title", ""),
                cluster.get("keywords", ""),
                " ".join(
                    str(self.records[cid].get("translationEnglish") or "")
                    + " "
                    + str(self.records[cid].get("explanationEnglish") or "")
                    for cid in (cluster.get("citationIds") or [])
                    if cid in self.records
                ),
            ]
        )
        corpus_tokens = _bank_tokens(corpus_text)
        unknown = content - corpus_tokens
        return len(unknown) >= 2

    async def match(
        self,
        question: str,
        embeddings=None,
        language: str = "en",
        context_ids: list[str] | None = None,
        history: list | None = None,
    ) -> dict | None:
        if language not in ("en", "hi"):
            return None
        if history:
            return None
        if direct_request(question):
            return None

        match_q, is_assistant = _strip_assistant_boilerplate(question)
        refs = explicit_references(match_q, maximum=4)
        if len(refs) > 1:
            return None

        await self.prewarm()
        if not self.clusters or self.vectors is None:
            return None

        aspect = detect_aspect(match_q)
        sources = requested_sources(match_q)
        norm_q = normalize_question(match_q)

        # 1. Exact question match
        if norm_q in self.exact_map:
            idx, q_aspect = self.exact_map[norm_q]
            cluster = self.clusters[idx]
            if self._source_allowed(cluster, sources):
                chosen_aspect = aspect if q_aspect == "hi" and aspect != "what" else q_aspect
                if chosen_aspect == "hi":
                    chosen_aspect = aspect
                return self._format_hit(idx, chosen_aspect, language, match_q, 1.0)

        # 2. Single explicit verse / section / shloka reference
        if len(refs) == 1:
            ref = refs[0]
            ref_id = ref["id"]
            target_idx = None
            if ref["type"] == "gita":
                target_idx = self.cluster_by_id.get(
                    f"gita_verse_{ref['chapterNumber']}_{ref['verseNumber']}"
                )
            elif ref["type"] == "vishnu-purana":
                target_idx = self.cluster_by_id.get(
                    f"vishnu_section_{ref['partNumber']}_{ref['sectionNumber']}"
                )
            elif ref["type"] == "ramayana":
                target_idx = self.citation_to_cluster.get(ref_id)

            if target_idx is not None and (
                is_assistant or not self._extra_unknown_terms(match_q, target_idx)
            ):
                return self._format_hit(target_idx, aspect, language, match_q, 0.99)

        # 3. Single macro reference (Gita chapter, Ramayana kanda/sarga, VP part)
        if not refs:
            macro_id = _macro_cluster_id(match_q)
            if macro_id and macro_id in self.cluster_by_id:
                idx = self.cluster_by_id[macro_id]
                if is_assistant or not self._extra_unknown_terms(match_q, idx):
                    return self._format_hit(idx, aspect, language, match_q, 0.98)

        # 4. Follow-up / reading-page context resolution
        if not refs and context_ids and len(context_ids) >= 1:
            ctx_id = context_ids[0]
            if ctx_id in self.citation_to_cluster and (
                is_assistant
                or follow_up(match_q)
                or len(_query_lex_tokens(match_q)) <= 3
            ):
                idx = self.citation_to_cluster[ctx_id]
                if is_assistant or not self._extra_unknown_terms(match_q, idx):
                    return self._format_hit(idx, aspect, language, match_q, 0.95)

        # 5. Hybrid Lexical BM25 + Dense Cosine Similarity
        lex_candidates, content_tokens = self._lexical_candidates(match_q, sources)
        if not lex_candidates or not content_tokens:
            return None

        candidate_indices = [item[0] for item in lex_candidates]
        dense_scores: dict[int, float] = {}
        if embeddings is not None and len(self.vectors):
            semantic_q, _ = _translate_hinglish_text(match_q, include_corpus_terms=False)
            q_vec = np.asarray(await embeddings.aembed_query(semantic_q), dtype=np.float32)
            q_norm = float(np.linalg.norm(q_vec))
            if q_norm > 0:
                q_vec = q_vec / q_norm
            sub_vecs = self.vectors[candidate_indices]
            sims = sub_vecs @ q_vec
            for pos, idx in enumerate(candidate_indices):
                dense_scores[idx] = float(sims[pos])

        best = None
        best_combined = -1.0
        n_terms = max(1, len(content_tokens))

        for idx, bm25, overlap in lex_candidates:
            cluster = self.clusters[idx]
            ctype = cluster.get("type", "")
            coverage = overlap / n_terms
            dense = dense_scores.get(idx, 0.0)
            is_macro_or_topic = ctype in (
                "topic",
                "gita_chapter",
                "ramayana_kanda",
                "vishnu_part",
            )

            if dense_scores:
                if is_macro_or_topic:
                    accepted = (dense >= 0.78 and overlap >= 1) or (
                        dense >= 0.72 and (overlap >= 2 or coverage >= 0.5)
                    )
                else:
                    accepted = dense >= 0.78 and (overlap >= 2 or coverage >= 0.8) and coverage >= 0.5
            else:
                accepted = is_macro_or_topic and overlap >= 2 and coverage >= 0.6

            if not accepted:
                continue

            combined = (dense if dense_scores else 0.75) + min(bm25, 12.0) * 0.015 + coverage * 0.05
            if combined > best_combined:
                best_combined = combined
                best = (idx, dense if dense_scores else min(0.95, 0.7 + coverage * 0.25))

        if best is None:
            return None
        return self._format_hit(best[0], aspect, language, question, best[1])
