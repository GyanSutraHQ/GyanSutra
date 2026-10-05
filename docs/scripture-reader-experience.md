# Scripture reader experience

The Bhagavad Gita chapter reader, Valmiki Ramayana sarga reader, and shared full verse card now use a consistent reading layout. Search and citation cards retain their compact presentation.

## Reading and learning

- Plain-language chapter orientation precedes the passage. The Chapter 1 introduction is editorial orientation, not a scripture translation. Ramayana explains the relationship between a kanda and a sarga.
- Readers can choose 100%, 115%, or 130% text size and show or hide Sanskrit. Preferences are stored on the device; unavailable storage does not prevent reading.
- Sanskrit and translation remain separate. Transliteration, comparison translations, word meanings, individual commentaries, and source notes open on demand. Their complete available text remains accessible.
- Published English and Hindi translations take precedence over the project's AI-assisted meanings. Original source wording is retained rather than automatically replacing archaic English. Existing AI-assisted meanings remain accessible with an explicit pending-review label.
- Assistant requests include a bounded source excerpt and the current verse ID. They stay within the existing backend's 500-character question limit and use the existing RAG and guardrails.
- One listening panel offers section selection, speed, voice selection, playback state, and Stop. It never starts automatically. Closing the panel or changing passage unmounts the player and stops its session. The recording index loads only when playback starts; existing exact-text matching and fallback rules remain in force.

## Navigation and accessibility

- Verse and sarga locations are reflected in query parameters, allowing bookmarks and copied URLs to open the passage directly. Changing verses within a chapter does not refetch its contents.
- Previous from the first shloka goes to the last available shloka of the previous sarga. Ramayana also offers direct shloka selection.
- Stale API results cannot replace a later request. Failed chapter/sarga fetches expose a localized retry action.
- Navigation stays within reach and sits above the mobile app's bottom menu. Interactive targets are at least 44 pixels; controls have visible focus states and explicit labels. Translation and Sanskrit carry appropriate language attributes.
- Arrow shortcuts operate inside the reader and leave form controls, links, disclosures, editable content, and dialogs alone. Reader navigation uses native buttons without page-turn delays; progress transitions honor reduced-motion preferences.

## Sources and review status

The source datasets were not replaced or silently corrected as part of this presentation change. Attribution and pending editorial-review statements remain available. Ramayana's pending review is visible beside the text, not only inside a closed source disclosure. Unmatched dataset material is labeled “Supporting text · unreviewed”; its publication provenance is unresolved. The upstream dataset includes a Gemini script for filling missing Uttara Kanda translations and explanations, without per-record generation metadata.

The [automated source audit](scripture-source-audit.json) checks every local Gita record and all 23,291 ingested Ramayana records. Ramayana has 2,491 Sanskrit/English source matches and 20,800 fallback records; 14 normalized Sanskrit matches have multiple English witnesses. Gita has 698 exact Hindi matches out of 701, but English wording differs from the pinned upstream dataset for most verses, including possible transcription defects and edition differences. These findings form an editorial review queue; normalization matches are not scholarly validation. No record was marked verified by this audit.

Reproduce the audit with `cd backend && .venv/bin/python -m scripts.audit_scripture_sources --output ../docs/scripture-source-audit.json`. It requires the git-ignored raw datasets used by ingestion and `gita-verse.json`, `gita-translation.json`, and `gita-commentary.json` under `backend/data/raw/source-audit`, downloaded from [gita/gita](https://github.com/gita/gita/tree/c6fce39595445768876ddbb8d1268a9c935e1d2b/data) at the pinned revision in the script. The report fingerprints its input files with SHA-256.

Readers can compare editions using [IIT Kanpur's Gita Supersite](https://www.gitasupersite.iitk.ac.in/) and the [Valmiki Ramayana reference site](https://www.valmikiramayan.net/). These are comparison references, not a claim that the app's entire corpus was independently checked against those editions. Human editorial verification of the complete corpus remains outstanding.

## Verification

Run from `frontend`:

```sh
npm run lint
npm test
npm run build
```

Reader regression checks cover source wording and attribution, separate AI meanings, preserved commentary, language attributes, Sanskrit visibility and text sizing, compact cards, Ramayana references, bounded assistant prompts, invalid URL/preferences recovery, and shortcut isolation. The existing narration tests cover playback ownership, cancellation, offline recordings, exact-text matching, and fallback behavior.

Verification on 2026-10-05: 45 frontend tests, 74 backend tests, frontend lint, Python lint/format, and a production build generating 142 indexable pages passed. Chrome on this Mac was used to inspect light and dark desktop readers and 390px/320px responsive layouts with 130% text and Sanskrit hidden. Preferences persisted across passages and between scripture readers. Previous from Ramayana 1.2.1 opened 1.1.100. English playback entered “Reading aloud” with a device voice and returned to Ready; audible quality requires the user's confirmation. The local API proxy received a 403 for neural narration, so this observation demonstrates device fallback, not live neural audio.

The browser check discovered that the deployed chapter API returned 133 Vishnu Purana records alongside 47 Gita verses. The reader now excludes other scriptures and deduplicates/sorts canonical Gita records; the Python endpoint also filters its results. The reader displayed the correct 47-verse count against the existing deployed API. This frontend compatibility fix takes effect on frontend deployment even before the Python API is released.

Screen-reader certification, full human editorial review, and pronunciation review are not claimed. The source-audit report records the unresolved editorial work explicitly. Frontend deployment uses the existing main-branch Cloudflare Pages and GitHub Pages workflows; Python/Render deployment remains a separate service operation.

## Release verification

Commit `75a2435` was pushed to `main`. [Maintainer CI](https://github.com/GyanSutraHQ/GyanSutra/actions/runs/37322895384) passed both backend and frontend jobs; [GitHub Pages deployment](https://github.com/GyanSutraHQ/GyanSutra/actions/runs/37322895484) and the Cloudflare Pages check succeeded. The custom domain served the new `index-legacy-9JF-l0ak.js` bundle. Chrome subsequently loaded the deployed Chapter 10 reader at verse 31, showing the new reading controls, source disclosure, and correct 42-verse count. A transient Chrome network failure preceded the successful observation. The Chapter 1 reader bundle served by the custom domain also matches the locally tested build byte-for-byte.

Audible playback quality remains unconfirmed by the user; entering a playback state alone does not establish audible output. Corpus-wide human editorial verification remains pending, with concrete discrepancies preserved in the audit report. These are the outstanding review items, rather than completed certifications.
