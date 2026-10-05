# Python migration verification

Verified on 5 October 2026. Backend code uses FastAPI, Python LangChain, the
official async Firestore client, and the committed quantized ONNX model.

## Live checks

| Check | Result |
| --- | --- |
| Firestore direct read of Gita 2.47 | Passed using the configured service account. |
| Native Firestore cosine vector search | Passed; eight results, top similarity 0.8540. |
| Gemini generation and citation validation | Passed with `gemini-3.1-flash-lite`; answer cited the supplied Gita 2.47 source. |
| Primary-to-backup model fallback | Passed; `gemini-3.8-flash` returned HTTP 503 and the configured backup answered. Primary-model availability is not confirmed. |
| Grok live request | Blocked: no `XAI_API_KEY` or `GROK_API_KEY` is available locally. Mocked transport tests verify endpoint and request compatibility. |
| Current production health | Existing Node API at `https://gyansutra-backend-0yo7.onrender.com/health` returned HTTP 200. |
| Current production reading load | All 16 measured requests passed at four clients; 3.09 requests/s and p95 3,213 ms. This measures the existing Node deployment. |
| Python production deployment | Pending Render credentials/access; the existing Node runtime must be switched before deploying Python source. |

The Gemini check used real HTTP generation grounded in the versioned Gita
2.47 text. Firestore connectivity was checked independently. No scripture data
was changed and the verification script did not write QA logs. An initial local
gRPC timeout was isolated to DNS resolution: HTTPS access and the native resolver
worked. The runtime now defaults to the native system DNS resolver, with an
environment override. Shutdown explicitly awaits closure of Firestore's gRPC
transport as well as the HTTP clients.

## Load comparison

The preserved Node implementation and the Python implementation ran sequentially
on the same Mac against the same live Firestore project. Each used a single
process, the same model/cache settings, and fresh per-process rate limits. Models
and routes were warmed before measurement. No model generation was included in
the load test. Responses were checked for HTTP success and search results.

| Workload | Clients | Requests per backend | Node requests/s | Python requests/s | Node p95 | Python p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Reading | 1 | 24 | 0.61 | 0.82 | 5,184 ms | 3,368 ms |
| Reading | 8 | 40 | 1.37 | 3.54 | 19,724 ms | 4,859 ms |
| Search | 1 | 12 | 0.97 | 0.94 | 1,225 ms | 1,245 ms |
| Search | 8 | 24 | 4.98 | 4.98 | 2,643 ms | 2,117 ms |

All 200 measured requests succeeded; warm-up requests also succeeded. Reading
cycled through chapter listing, chapter 2 verses, Gita 2.47, and Vishnu Purana
1.1. Search repeated a duty question with a five-result limit, so these search
figures include a warm embedding cache. They do not measure uncached embedding
throughput. Eight-client reading throughput was about 2.6 times the baseline in
this run; search throughput was effectively unchanged.

This is a short local comparison, not a sustained capacity test. Network and
Firestore variability affect the results, and the sequential order is a source
of bias. These numbers are not production latency targets or evidence of faster
LLM generation. Repeat the same bounded profiles against the Python deployment
after the runtime switch. Keep the existing per-IP limits intact and allow their
15-minute window to reset between larger test runs.

Sanitized raw results are preserved in
[verification results](verification/python-migration.json).

## Deployment completion

1. Make Render management credentials available through `RENDER_API_KEY` or an
   approved authenticated dashboard session. Keep keys out of Git and chat.
2. Target the existing service behind the frontend API URL. Preserve its
   Firestore/provider secrets, region, plan, and domain. Change its runtime to
   Python, root directory to `backend`, build command to
   `pip install -r requirements.txt`, and start command to `python -m gyansutra`.
   Use Python 3.12.15 and the configuration in `backend/render.yaml`.
3. Deploy the tested migration commit, verify `/health`, reading, semantic
   search, CORS, guardrails, and one grounded generated answer, then run the
   bounded load profiles against the deployed API.
4. Run the Grok live check once an xAI key is available. Do not label this check
   passed based only on mocked tests.

Render supports changing an existing runtime through its API or Blueprint sync:
[Render runtime changes](https://render.com/changelog/change-an-existing-services-runtime-via-api-or-blueprint).
