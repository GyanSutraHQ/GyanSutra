# Gyan Sutra

Gyan Sutra is a multilingual scripture-reading platform for the Bhagavad Gita,
Valmiki Ramayana, and Vishnu Purana. It combines a React progressive web app
and Android shell with a Node.js API for scripture retrieval, semantic search,
and the retrieval-grounded Sarathi guide.

This guide is written for maintainers and organization members. It explains the
working boundaries of the repository, the content pipeline, the checks that
protect `main`, and the safe path for changing each part of the platform.

## System map

```text
Browser / Android shell
        │
        ▼
frontend/  React + Vite PWA + Capacitor
        │ HTTPS /api/*
        ▼
backend/   Express API, validation, RAG, local embedding runtime
        │
        ├── Firestore: chapters, verses, vector search, optional QA log
        ├── Local ONNX model: Xenova/gte-small embeddings
        └── AI providers: Gemini → Groq → OpenRouter, with grounded fallback
```

The web app is deployed to Cloudflare Pages and GitHub Pages. The API is
configured for Render. Firestore stores the searchable corpus; the local ONNX
model is intentionally versioned so production does not depend on downloading
model files at startup.

## Repository guide

| Path | Purpose | Maintainer notes |
| --- | --- | --- |
| `frontend/src/` | React pages, components, hooks, API client, localization, and reading/narration utilities | Keep UI behavior in focused components; use `services/api.js` for backend calls. |
| `frontend/public/` | PWA manifest, icons, crawler assets, narration notices, and static social images | Files here are copied into every web build. |
| `frontend/scripts/` | Sitemap and static SEO page generation | `npm run build` runs these automatically before and after Vite. |
| `frontend/android/` | Capacitor Android wrapper and native speech bridge | Do not edit generated web assets under `app/src/main/assets/public/`. |
| `backend/src/routes/` | HTTP endpoint validation and response shaping | Keep routes thin; use services for infrastructure and domain logic. |
| `backend/src/services/` | Firestore, embeddings, caching, RAG, translations, and guardrails | Preserve the bounded timeouts, cache limits, and citation validation. |
| `backend/src/data/` | Source registry used by API routes | Add a source here when adding a supported scripture. |
| `backend/data/` | Versioned Gita and Vishnu Purana source material | Treat these as content contracts; CI verifies their structure. |
| `backend/scripts/` | Corpus preparation and Firestore ingestion tools | Ingestion writes external data; review a dry run before production execution. |
| `backend/models/` | Checked-in local embedding model | Required at runtime; do not remove it to reduce repository size. |
| `backend/narration/` | Optional Python narration worker, queue tools, licenses, and provenance | It is optional for normal web reading; follow its own README for setup. |
| `docs/` | Operational documentation | Keep deployment and search-console instructions current. |
| `.github/workflows/` | CI and GitHub Pages deployment | Changes here affect every contributor and deployment. |

## Request and content flow

### Reading and search

1. React routes call `frontend/src/services/api.js`.
2. Express validates the request in `backend/src/routes/`.
3. Firestore returns a chapter, verse, or vector-search result. Embeddings are
   never returned to the browser.
4. The frontend renders source text, translations, accessibility controls, and
   optional narration.

### Sarathi (grounded answers)

1. The API validates a question, short conversation history, language, and
   prior citation IDs.
2. `rag.js` applies local guardrails, resolves exact references when possible,
   embeds eligible queries, and retrieves a small set of scripture passages.
3. A provider is used only when the evidence clears the similarity threshold.
   The answer is checked against the retrieved citations before it is returned.
4. If generation is unavailable or invalid, Sarathi returns a clearly marked,
   source-based fallback instead of inventing an answer.

### Corpus lifecycle

```text
Versioned Gita / Vishnu Purana data
        │
        ├── backend/scripts/ingest*.js
        ▼
Firestore chapters + verses + 384-dimension embeddings
        │
        └── search, recommendations, and Sarathi retrieval

Ignored raw Ramayana datasets
        │
        └── ingest_ramayana.js → Firestore
```

`backend/data/gita.json` contains 701 verses. `vishnu-purana.json` contains
six parts and 126 sections. `npm run verify:data` checks those invariants before
backend tests run in CI. Raw Ramayana source datasets remain ignored under
`backend/data/raw/`; never add downloaded archives, PDFs, or nested source
repositories to Git.

## Local setup

### Prerequisites

- Node.js 22 or newer (`.nvmrc` pins the supported major version)
- A Firestore project in Native mode for API-backed reading/search
- A Google AI Studio API key for live Sarathi generation

### Install and run

```bash
cp backend/.env.example backend/.env
cd backend && npm ci

cd ../frontend
cp .env.example .env
npm ci
```

Run the API and frontend from separate terminals:

```bash
cd backend && npm run dev
cd frontend && npm run dev
```

The API defaults to `http://localhost:3001`; Vite defaults to
`http://localhost:5173`. The frontend uses the local API in development unless
`VITE_API_BASE_URL` is set.

### Environment boundaries

| Location | Used for | Rules |
| --- | --- | --- |
| `backend/.env` | Firestore credentials, provider keys, CORS, RAG limits, optional narration service | Copy `backend/.env.example`; never commit credentials. |
| `frontend/.env` | API base URL and optional Firebase browser configuration | Only `VITE_*` variables are visible to browser code. Never place a server secret here. |
| Render environment | Production backend secrets | Prefer the JSON service-account environment variable described in the backend example. |
| GitHub Actions secrets | Deployment-specific frontend API URL | Keep deployment secrets in repository or organization settings, not workflow source. |

## Maintainer checks

Run these before requesting review:

```bash
cd backend
npm run verify:data
npm test

cd ../frontend
npm test
npm run lint
npm run build
```

The **Maintainer CI** workflow runs on pull requests, pushes to `main`, and
manual dispatches. It performs the following independent gates:

| CI gate | What it protects |
| --- | --- |
| Backend data contract | Gita verse count/coordinates/translations and Vishnu Purana part/section structure |
| Backend API suite | Request validation, CORS, search, recommendations, RAG grounding, cache behavior, narration, and localization |
| Frontend tests | Narration ordering/fallbacks, cached audio, readable text, modernized English, and recording provenance |
| Frontend lint and production build | Source quality, PWA generation, sitemap generation, and 142 static SEO pages |
| Critical dependency audit | Newly introduced critical production dependency advisories |

For pull requests, CI also retains the generated `frontend/dist` build for
seven days as a review artifact. Download it from the run’s **Artifacts**
section when reviewing generated HTML or PWA assets.

### Recommended organization settings

Repository administrators should configure branch protection for `main` to:

1. Require the `Backend contract and API` and `Frontend quality and production build` checks.
2. Require at least one approving review from an organization maintainer.
3. Require branches to be current before merge and restrict direct pushes.
4. Limit GitHub Actions workflow changes to trusted maintainers.

Use organization teams in GitHub’s review settings or a `CODEOWNERS` file once
the organization’s actual team slugs and ownership boundaries are agreed. This
repository does not guess those team names, which would otherwise create a
non-functional review gate.

## Change playbooks

### Frontend changes

- Add page routes in `frontend/src/App.jsx` and keep API access inside
  `frontend/src/services/api.js`.
- Put shared visual primitives in `components/`; page-only presentation belongs
  in `pages/`.
- Preserve keyboard, screen-reader, theme, PWA, and mobile behavior when
  changing reading controls.
- Run the frontend checks above. Test Android separately when touching
  Capacitor or native bridge code.

### API or RAG changes

- Validate inputs at the route boundary and keep error responses safe for
  browsers.
- Add or update a Jest test in `backend/src/__tests__/` for each behavior
  change.
- Do not weaken citation validation, provider deadlines, concurrency limits, or
  cache bounds without documenting why and testing the fallback path.
- Update `RAG_CORPUS_VERSION` after a material corpus or embedding re-ingest.

### Scripture-data changes

- Preserve Unicode, source attribution, and stable chapter/verse coordinates.
- Run `npm run verify:data` before committing.
- Re-ingest Firestore after changing source data, then increment
  `RAG_CORPUS_VERSION` so cached retrieval and answer entries are not reused.
- Add narrative/source notes in `backend/data/` or `docs/` when a new edition
  changes provenance.

### Dependencies and security

- Use `npm ci` for reproducible installs and commit both package manifests and
  lockfiles together.
- Review `npm audit --omit=dev` before dependency releases. CI blocks critical
  production advisories; non-critical advisories still require maintainer
  triage.
- Do not run forced audit fixes unless a maintainer has reviewed the resulting
  application/API compatibility changes.

## Ingestion and Android operations

After Firestore credentials are configured, corpus commands are:

```bash
cd backend
npm run ingest
npm run ingest:vishnu
node scripts/ingest_ramayana.js
```

The Android project lives in `frontend/android`. Build and synchronize it from
the frontend directory:

```bash
cd frontend
npm run android:sync
npm run android:open
```

See [frontend/ANDROID.md](frontend/ANDROID.md) for Android signing, testing,
versioning, and release details. See
[backend/narration/README.md](backend/narration/README.md) for optional worker
narration and audio provenance.

## Deployment

- **Cloudflare Pages:** build in `frontend/` with `npm run build`; publish
  `frontend/dist`.
- **GitHub Pages:** `.github/workflows/deploy-github-pages.yml` uses
  `VITE_BASE_PATH=/GyanSutra/` for the project subpath.
- **Render:** deploy `backend/` using `backend/render.yaml` and configure the
  variables listed in `backend/.env.example`.

Set `VITE_API_BASE_URL` to the deployed API URL for each frontend deployment.

## License and content sources

The code is licensed under the MIT License. Scripture content and narration
assets have their own attribution and usage notes; see
[backend/narration/README.md](backend/narration/README.md) and
[backend/data/VISHNU_PURANA_SOURCES.md](backend/data/VISHNU_PURANA_SOURCES.md).
