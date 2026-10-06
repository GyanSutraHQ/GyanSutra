# Sarathi RAG architecture

Sarathi combines source lookups, local BM25 keywords, Firestore cosine search,
rank fusion, diverse evidence selection, and bounded provider generation.
The API response contract remains compatible with the existing reader.

## Answer path

1. Validate the question, language, recent history, and previous citation IDs.
2. Answer narrow conversational/utility guardrails locally.
3. Resolve explicit scripture references directly. Missing references never
   become unrelated vector matches. A partially missing comparison returns the
   available source text with `answered=false` and `degraded=true`.
4. For topical questions, run native keyword search and dense retrieval in
   parallel. Indian-script queries optionally pass through a cached English
   question translation before embedding. Exact references skip translation.
5. Combine keyword and vector rankings using reciprocal rank fusion (RRF).
   Apply a requested-book constraint, then evidence gates and an MMR-style
   lexical redundancy penalty. Simple cited follow-ups keep their source;
   follow-ups introducing a topic also retrieve additional evidence.
6. Give each selected source a share of the context budget. Include translations,
   source provenance, verification status, and bounded commentary. Generate
   only from this pack, in the requested response language.
7. Reject missing/invalid source markers, unsupported English/Hindi scripture
   references, wrong-script prose, and provider failures. Return the existing
   localized source fallback. Cache successful, non-degraded answers only.

The fusion/diversity steps rank evidence; they do not establish factual truth.
Citation validation checks references and markers, not semantic entailment of
every sentence. Hindi and Marathi share a script, so script checks alone cannot
distinguish them. Independent answer review remains necessary for quality claims.

## Retrieval and source consistency

`gyansutra/corpus.py` supplies the same records to ingestion and the keyword
index. Gita verses and 499 Purana passages provide 1,200 default indexed
passages. Full Purana sections are excluded from keywords because their passage
children already carry the text. Scripture IDs and embedding vectors remain
compatible with the existing database. Duplicate hybrid hits prefer Firestore's
source text and metadata.
Keyword confidence is recalculated against the preferred text after merging, so
a stale local record cannot promote unrelated remote text past the evidence gate.

BM25 uses a Unicode tokenizer that preserves Indic combining marks, an inverted
index, length normalization, and compact integer posting arrays. It runs on one
dedicated CPU thread, with a single shared background index build. No additional
database scan or embedding API is required for keyword retrieval.

Cosine similarity and BM25/fusion scores are kept separate. Vector evidence
must clear `RAG_SIMILARITY_THRESHOLD`. Keyword-only evidence requires at least
two matching content terms (or a complete story-title match) and the configured
query-term coverage. These are tunable heuristics, not confidence probabilities.

Book restrictions currently filter dense candidates after Firestore KNN and
before fusion, while BM25 filters during search. This avoids requiring new
Firestore composite indexes, but a narrow book question can miss relevant
vectors outside the top 20 global hits. A future prefiltered vector migration
should include composite indexes and a broader independently reviewed evaluation.

The checked-in GTE model is English-only and truncates at 512 tokens. Cached
query translation improves access to English evidence for supported Indian
scripts without invalidating existing vectors. It adds one bounded model call
per uncached non-English query, shares the same generation budget, and falls
back to the original query if unavailable or invalid. It does not supply facts
or translate the source corpus. A fully multilingual embedding upgrade requires
re-embedding the entire corpus and validating an index migration; this change
does not perform that migration or fine-tune the answer model.

## Ramayana keywords

Ramayana vector retrieval continues to use Firestore. To add its source-locked
keyword branch, prepare a JSON Lines snapshot from the same local raw datasets
used by ingestion:

```bash
cd backend
uv run python -m scripts.build_lexical_snapshot \
  --output data/raw/rag/ramayana-lexical.jsonl
```

Set `RAG_LEXICAL_SNAPSHOT=data/raw/rag/ramayana-lexical.jsonl`. The builder
refuses to overwrite an existing artifact, writes no database data, and calls
no model. The snapshot retains translation provenance and verification status;
it does not mark unreviewed verses as verified.

The local development snapshot contains 23,291 Ramayana records, bringing the
local index to 24,491 passages. It is under ignored `data/raw/` and is **not
shipped by a Git-based Render deployment**. Production must deliberately bundle
the snapshot and set its path to enable Ramayana keywords. The default Render
configuration keeps the smaller Gita/Purana keyword index plus all-book vectors.
Bundle the matching corpus version, and rebuild snapshots after source changes.

## Budgets and operations

| Setting | Default per API process |
| --- | --- |
| Active retrievals / queued retrievals | 8 / 32 |
| Retrieval queue wait | 3 seconds |
| Each retrieval branch | 8 seconds; dense may additionally use 4 seconds for query translation |
| Active generation calls / queued calls | 4 / 24; shared with query and reader translation |
| Generation queue wait | 10 seconds |
| Model timeout / generation attempts deadline | 10 / 24 seconds |
| Complete answer deadline | 45 seconds |
| Source candidates / final source pack | Up to 20 per branch / 4 passages |
| Source pack characters | 7,000 |

The outer deadline bounds the combined path, even when individual limits add
up to more than 45 seconds. Queue overflow/expiry produces a degraded fallback;
it does not guarantee eventual AI generation for every caller. Cancellation
releases slots. Ten English requests can use four generation slots concurrently;
real completion time still depends on the provider, quota, network, and evidence.
The existing 20-questions-per-15-minutes **per-IP** limit remains, so users sharing
a network also share that rate limit.

Use one API worker per instance. Limits and caches are per process, not a
distributed quota across replicas. The response cache includes corpus/prompt/
retrieval settings and language; contextual conversations do not share response
cache keys. Single-flight work coalesces identical cacheable requests safely.
Logs include retrieval mode, query mode, candidate/evidence counts, branch
failures, provider attempts, queue/stage timings, and answer-generation usage.
Query translation consumes additional provider tokens that are not included in
the final answer's usage counters. Analytics have a two-second timeout.

## Verification and limits

```bash
cd backend
uv run pytest
uv run ruff check gyansutra scripts tests
uv run ruff format --check gyansutra scripts tests
uv run python -m scripts.verify_data
uv run python -m scripts.evaluate_rag --output ../docs/verification/rag-retrieval.json
```

The recorded offline smoke evaluation found the expected passage first for all
eight targeted English/Hindi/Sanskrit queries. It tests keyword retrieval only;
it is neither an unbiased benchmark nor a measurement of final answer quality.
The ten-user test uses simulated provider latency, not production infrastructure.
No live provider benchmark, external database mutation, or deployment was done.

On the local macOS process, the full optional index built in about 2.6 seconds.
JSON Lines loading and compact postings reduced measured peak process RSS from
572.1 MiB to 345.9 MiB. This includes imported runtime libraries but excludes a
loaded embedding inference session and live API traffic; it is not a production
memory guarantee. Validate the complete service on the intended instance before
bundling the full snapshot on a small hosting tier.
An additional local initialization check loaded the real embedding session and
the 24,491-passage index together, peaking at 458.7 MiB without live API traffic.

Design references: [Microsoft's RRF documentation](https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking),
[GTE model limitations](https://huggingface.co/thenlper/gte-small),
and [Firestore vector filtering/index requirements](https://firebase.google.com/docs/firestore/vector-search).
