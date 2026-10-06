# Python backend and LangChain architecture

The backend uses Python 3.12, FastAPI, Uvicorn, and Python LangChain.
The frontend keeps the existing API paths, fields, error messages, cache
headers, scripture coordinates, guardrails, and RAG behavior.

## Components

The current hybrid retrieval and capacity design is documented in
[Sarathi RAG architecture](sarathi-rag.md); that page supersedes the original
vector-only retrieval details below.

| Module under `backend/gyansutra/` | Responsibility |
| --- | --- |
| `app.py`, `middleware.py` | Routes, validation, CORS, security headers, body bounds, rate limits, health, and crawlers. |
| `firestore.py` | Official asynchronous Firestore client, direct lookup, native cosine KNN, batch ingestion, and optional QA logs. |
| `embedding.py` | LangChain `Embeddings` with committed quantized ONNX model and Rust tokenizer. |
| `generation.py` | `ChatPromptTemplate` → `ChatOpenAI` and `StrOutputParser`, shared HTTP transport, provider fallback, deadlines, and capacity budgets. |
| `rag.py` | LangChain `BaseRetriever`/`Document`, exact references, follow-ups, reranking, evidence thresholds, source packs, citations, and extractive fallback. |
| `text.py` | Reference parsing, deterministic guardrails, and modern English rules; original multilingual policy lives in `backend/data/ai-policy.json`. |
| `translation.py` | Source-only translation with `BaseOutputParser`, script/completeness checks, stored-content precedence, provenance, and unreviewed labels. |
| `cache.py`, `narration.py` | Bounded caches, cancellation-safe single-flight requests, and the existing optional WAV narration proxy. |

## Provider APIs

LangChain uses the providers' OpenAI-compatible **Chat Completions** APIs.
`langchain-openai` is the compatible transport adapter; no OpenAI key is required.

| Provider | Key | Endpoint | Default models |
| --- | --- | --- | --- |
| Gemini | `GEMINI_API_KEY` | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-3.8-flash`, `gemini-3.1-flash-lite` |
| xAI Grok | `XAI_API_KEY` (`GROK_API_KEY` alias) | `https://api.x.ai/v1` | `grok-4.7` |
| OpenRouter | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1` | `openrouter/free` |

Model lists and provider order remain configurable in `.env.example`.
Gemini defaults to low reasoning effort and omits temperature. Grok and
OpenRouter retain temperature 0.1. Requests preserve `max_tokens`, output
budgets, and OpenRouter attribution headers. LangChain and SDK retries are
disabled; application interleaving, terminal errors, circuit breakers,
concurrency limits, and deadlines control every attempt. Timeout cancellation
reaches HTTP and releases capacity.

## Behavioral compatibility

Guardrails run before retrieval. Exact references and cited follow-ups use
direct Firestore lookup; missing explicit references cannot be replaced by
semantic matches. Semantic retrieval preserves reranking, evidence thresholds,
bounded context, history limits, citations, and fallback reason codes.
Invalid, empty, truncated, or unavailable generation returns the marked
source fallback. Degraded answers are not cached. Scripture data and
provenance are unchanged.

Embeddings retain the model, query/passage prefixes, whitespace normalization,
512-token slicing, mean pooling, normalization, quantization, and 384 dimensions.
Tests compare against captured JavaScript vectors for English, Sanskrit,
query/passages, and long text. CI additionally compares against the preserved
JavaScript adapter on the same CPU because quantized kernels vary across
architectures. Node is installed only for this migration test reference;
the Python deployment has no Node dependency. No vector re-ingestion or index migration is
required solely for this conversion.

## Performance and deployment

Firestore and provider calls use asynchronous I/O. Provider and narration calls
share a bounded HTTP pool. CPU embedding inference runs on a dedicated thread
with bounded ONNX threads, leaving the request event loop free. Models load
lazily, with optional background prewarming. TTL/LRU caches and single-flight
requests preserve memory and concurrency bounds.

Run one API worker per instance. Limits, circuits, narration capacity, and caches
are per process, matching the previous deployment. More workers duplicate models
and budgets; shared limits require a separate scaling review. Throughput gains
require load testing against deployed services.

Render installs hashed production dependencies from `requirements.txt` and
starts `python -m gyansutra`. CI installs `uv.lock`, checks corpus/tests/lint,
verifies the requirements export, and audits production dependencies.
`NODE_ENV` remains accepted for existing environment compatibility.
The optional Python Parler/Svara TTS worker retains its specialized runtime and
separate requirements. Narration queue/import tools live in `frontend/scripts/`
to reuse frontend text segmentation.

## Development and verification

From `backend/`:

```bash
uv sync --frozen
uv run uvicorn gyansutra.app:app --reload --port 3001
uv run pytest
uv run python -m scripts.verify_data
uv run ruff check gyansutra scripts tests
uv run ruff format --check gyansutra scripts tests
```

Tests use ASGI requests, mocked Firestore, real LangChain chains with mocked HTTP,
and the actual local ONNX model. They cover API contracts, guardrails, provider
payloads/fallback, timeout cancellation, caches, citations, localization,
narration, ingestion records, and vector compatibility. Live provider calls
and production database writes are not part of this verification.

References: [FastAPI async tests](https://fastapi.tiangolo.com/advanced/async-tests/),
[LangChain ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai),
[Google compatibility API](https://ai.google.dev/gemini-api/docs/openai),
[xAI API](https://docs.x.ai/docs/api-reference).

## Live verification and measured performance

See [migration verification](python-migration-verification.md) for recorded live
checks, the Node/Python load comparison, and deployment status. Re-run checks from
`backend/` with real local credentials:

```bash
uv run python -m scripts.live_check --output /tmp/gyansutra-live-check.json
uv run python -m scripts.load_test --base-url http://127.0.0.1:3001 \
  --profile reading --requests 40 --concurrency 8 --output /tmp/gyansutra-load.json
```

Live provider checks consume model quota. Database and load checks only read;
they do not ingest data or write QA logs. Missing provider credentials are marked
blocked and return a nonzero exit status. `--skip-firestore` isolates provider
checks when diagnosing database connectivity. The default native gRPC DNS
resolver is configurable through `GRPC_DNS_RESOLVER`.
