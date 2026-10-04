# Gyan Sutra

Gyan Sutra is a multilingual scripture-reading platform for the Bhagavad Gita,
Valmiki Ramayana, and Vishnu Purana. It combines a React progressive web app
and Android shell with a Node.js API for retrieval, semantic search, and the
retrieval-grounded Sarathi guide.

## Architecture

```text
frontend/       React + Vite PWA and Capacitor Android project
backend/        Express API, Firestore integration, local embeddings, RAG
docs/           Operational documentation
```

The frontend is deployed to Cloudflare Pages and GitHub Pages. The API is
configured for Render and uses Firestore for the scripture corpus and vector
search. The local `Xenova/gte-small` ONNX model is intentionally versioned so
production deployments do not depend on a model download at startup.

## Prerequisites

- Node.js 22 or newer (`.nvmrc` pins the supported major version)
- A Firestore project in Native mode
- A Google AI Studio API key for Sarathi generation

## Local development

Configure the backend environment, then install each application independently:

```bash
cp backend/.env.example backend/.env
cd backend && npm ci

cd ../frontend && cp .env.example .env && npm ci
```

Run the API and web app in separate terminals:

```bash
cd backend && npm run dev
cd frontend && npm run dev
```

The API defaults to `http://localhost:3001`; Vite serves the frontend on
`http://localhost:5173`.

## Quality checks

```bash
cd backend && npm test

cd frontend
npm test
npm run lint
npm run build
```

GitHub Actions runs these checks for pull requests and pushes to `main`.

## Data ingestion

The production Gita data lives in `backend/data/gita.json`. To populate
Firestore after configuring credentials:

```bash
cd backend
npm run ingest
npm run ingest:vishnu
node scripts/ingest_ramayana.js
```

The Ramayana ingestion source datasets are intentionally ignored under
`backend/data/raw/`; see the ingestion script and data-source documentation
before obtaining or preparing them.

## Android

The Capacitor project is under `frontend/android`. Build and synchronize it
from the frontend directory:

```bash
cd frontend
npm run android:sync
npm run android:open
```

See [frontend/ANDROID.md](frontend/ANDROID.md) for signing, testing, versioning,
and release details.

## Deployment

- **Cloudflare Pages:** build in `frontend/` with `npm run build`; publish
  `frontend/dist`.
- **GitHub Pages:** `.github/workflows/deploy-github-pages.yml` builds the app
  with `VITE_BASE_PATH=/GyanSutra/`.
- **Render:** deploy `backend/` using `backend/render.yaml` and configure the
  variables listed in `backend/.env.example`.

Set `VITE_API_BASE_URL` to the deployed API URL for each frontend deployment.

## License and content sources

The code is licensed under the MIT License. Scripture content and narration
assets have their own attribution and usage notes; see
[backend/narration/README.md](backend/narration/README.md) and
[backend/data/VISHNU_PURANA_SOURCES.md](backend/data/VISHNU_PURANA_SOURCES.md).
