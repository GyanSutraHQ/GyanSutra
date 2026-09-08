# Local narration on an Apple Silicon Mac

GyanSutra now supports **pregenerated narration for both Sanskrit and meanings**.
The selected local engine is [Svara-TTS, MLX 8-bit](https://huggingface.co/mlx-community/svara-tts-v1-8bit),
running on the Mac's Apple GPU. Generate once on the SSD, then bundle the small
audio files with the website and Android app. Render does not run this model;
your Mac does not need to stay online for users to play imported clips.

The previous Rohan / GitaGuru audio source has been removed because its
CC BY-NC-ND licence prohibits commercial use. The app deletes its old
`gyansutra-recitations-v1` cache on reader initialization. No third-party human
recording is currently selected automatically.

## Current setup and coverage

- Machine: MacBook Air M4, 16 GB unified memory.
- External folder: `/Volumes/SP Extreme SSD/GyanSutraAudio`.
- Isolated Python 3.13 environment and MLX Audio dependencies installed there.
- Apple Metal GPU availability verified.
- Model: 3.51 GB of 8-bit weights, plus tokenizer and SNAC decoder. Both model
  files were SHA-256 verified after download. Allow roughly 10 GB for the
  environment, model cache and generated masters.
- `sample-queue.json`: 37 segments covering Gita 1.1 and 2.47, introductions in
  six meaning languages, original meanings for both verses in all six languages,
  and six short voice demonstrations.
- The two evaluation verses display these original AI-assisted meanings, with
  project attribution and an editorial-review-pending note. Other verses retain
  their existing text sources; this change does not clear the whole corpus.
- All 37 evaluation clips were generated: 196.8 seconds of audio in 660.72
  seconds of M4 generation time. The 31 non-demo clips were imported as about
  1.4 MB of AAC for Gita 1.1 and 2.47.
- The complete Sanskrit Gita batch is generated and imported: 1,510 unique
  spoken segments covering all 701 verses, 6,548.45 seconds of audio, and
  36,046.88 seconds of recorded M4 generation time. Lossless masters use about
  307 MB on the SSD; the complete AAC bundle, including the original evaluation
  meanings, uses about 58 MB and contains 1,536 exact spoken segments.
- The checked-in `frontend/src/data/narrationInventory.json` is the authoritative
  list of clips actually imported. An empty inventory means no new audio has
  been shipped yet. Installing software alone does not change the app's voice.
- Generated clips carry `listeningReviewed: false` until a fluent listener has
  checked them. Automated waveform checks cannot certify pronunciation or emotion.

The download server was intermittent during setup. `--download` preserves
completed ranges and verifies the complete model's SHA-256 before installation.
The initial installation and evaluation generation are complete; subsequent
batches reuse the verified model without downloading it again.

## Generate and import audio

Run from the repository root, with the SSD connected. No API key, subscription,
paid cloud GPU or Python worker on Render is needed.

```sh
# Already installed on this Mac; needed when setting up a new environment.
sh backend/narration/install-mac.sh

# Needed only for compact app copies; lossless masters remain on the SSD.
brew install ffmpeg

# Optional robust download on slow / unreliable connections.
sh backend/narration/run-mac.sh --download
sh backend/narration/run-mac.sh --download --decoder

# Generate samples. Repeating this command skips completed matching clips.
sh backend/narration/run-mac.sh \
  --queue backend/narration/sample-queue.json \
  --output '/Volumes/SP Extreme SSD/GyanSutraAudio/samples'

# Open samples/listen.html on the SSD and listen to the actual voices.
# Import completed non-demo clips into the website / Android static assets.
node backend/narration/import-audio.mjs \
  '/Volumes/SP Extreme SSD/GyanSutraAudio/samples' --aac --prune

# Build and copy the updated audio into the Android project.
cd frontend
npm run android:sync
```

Set `NARRATION_HOME` to use another disk location. Keep the environment, model
cache and generated originals together. Don't unplug the SSD during a batch.
Generation uses one model and one clip at a time. Closing the terminal stops
the command; rerun it to resume. No background login service is installed.

The default selects each language's male voice. To compare the female voices,
run with `--gender Female` and a different output folder. `--limit 3` limits
the run to the first three queue entries. Samples are evaluation material;
Svara speech is not a guarantee of authentic chanting, metre or Vedic svaras.

## Expand the library

For the complete Sanskrit Gita queue:

```sh
node backend/narration/prepare-queue.mjs --all-gita \
  --output='/Volumes/SP Extreme SSD/GyanSutraAudio/gita-queue.json'
sh backend/narration/run-mac.sh \
  --queue '/Volumes/SP Extreme SSD/GyanSutraAudio/gita-queue.json' \
  --output '/Volumes/SP Extreme SSD/GyanSutraAudio/gita'
node backend/narration/import-audio.mjs '/Volumes/SP Extreme SSD/GyanSutraAudio/gita' --aac --prune
```

This uses the app's actual `buildNarration` function, so punctuation, pauses and
text segmentation agree with playback. It doesn't silently rewrite scripture.
The full batch is generated and waveform/integrity checked. It is not claimed as
listening-reviewed: a fluent Sanskrit reviewer should still check pronunciation
through `gita/listen.html`. Generation time and audio duration are recorded for
every completed clip.

Other books and meanings use the same JSON queue format:

```json
[
  {
    "text": "Now, the meaning.",
    "locale": "en-IN",
    "kind": "translation",
    "rights": "project-original",
    "rightsNote": "Original GyanSutra section introduction"
  }
]
```

Supported locales: `sa-IN`, `en-IN`, `hi-IN`, `bn-IN`, `mr-IN`, `te-IN`, `ta-IN`.
Use `buildNarration` to export the **exact displayed text** and section headings.
Sections are `verse`, `translation`, `explanation`, `context`; texts are limited
to 360 characters. Add `demoOnly: true` to samples that should not enter the app.
Each queue item must record its text rights and provenance. The script checks
these fields, but they are declarations, not independent legal verification.

**Modern translations need separate rights.** The current Gita dataset includes
translations and commentaries credited to named authors. They are not
automatically public domain because the Sanskrit scripture is ancient.
The sample queue excludes these texts. Obtain applicable permissions or use
original / appropriately public-domain translations before exporting a
commercial meaning-audio library. A TTS model's licence does not clear its input.

## Commercial use and attribution

- [Svara-TTS by Kenpath](https://huggingface.co/kenpath/svara-tts-v1) and its MLX
  conversion are published under Apache 2.0.
- The model derives from Orpheus / Llama 3.2. Preserve the underlying
  [Llama 3.2 licence](licenses/LLAMA-3.2.txt) and comply with its
  [Acceptable Use Policy](https://www.llama.com/llama3_2/use-policy).
  Its commercial terms include an additional licence requirement for entities
  exceeding the specified 700-million-MAU threshold. It is not unconditional MIT.
- [MLX Audio](https://github.com/Blaizzy/mlx-audio) is MIT;
  [SNAC](https://huggingface.co/hubertsiuzdak/snac_24khz) is MIT.
- The app discloses AI narration and links to `/narration-notices.html`, including
  “Built with Llama” attribution. The model weights stay on the SSD, outside Git
  and outside the APK. Keep licence notices with any weights you redistribute.
- Only supplied model voices are used; no person's voice is cloned.

Local generation has no per-character or API charge. Electricity and your
existing hardware are still resources, and public hosting/storage limits remain
those of your hosting provider. No paid service is activated by these scripts.

## Playback behavior

- Saved clips are matched by complete text, locale and section. A changed
  translation cannot accidentally play the old translation's audio.
- Order remains Sanskrit → meaning → optional explanation → context, with pauses.
- Missing clips use the best installed device voice and show that source.
  A named meaning voice overrides saved prose, while saved Sanskrit remains.
- Recent downloaded clips use a bounded cache. Bundled Android audio can be
  read offline. Website offline availability depends on its cache.
- Stop, navigation and language changes cancel playback and pending lookups.
  An audio playback failure stops rather than unexpectedly repeating a verse.
- Import verifies each master WAV's SHA-256, format and size before updating the
  inventory. `--aac` creates 64-kbit/s AAC app copies while retaining lossless
  masters on the SSD; `--prune` removes superseded generated app assets.

## Other engines

The existing `server.py` / `requirements.txt` Indic Parler worker and Node
`/api/narration` route remain optional. They are **not** used by default and have
not been activated by this local workflow. Indic Parler's original Hugging Face
repository requires account access acceptance. Do not assume Render's free
instance can run a multi-GB model.

[Vāgdhenu](https://huggingface.co/prathoshap/vagdhenu) remains a Sanskrit-specific
chanting alternative to evaluate, but its upstream GPU setup isn't a verified
drop-in Apple Silicon installation. Svara was selected for its published native
MLX workflow and coverage of all seven required languages, not a claim that it
is objectively the best voice. Listen and compare before a full-library batch.

## Verification

```sh
python3 -m unittest discover -s backend/narration -p 'test_*.py'
cd frontend
npm run test:narration
npm run lint
npm run build:android
```

These cover sequencing, exact text matching, saved/device fallback, cancellation,
cache migration, bundled-audio handling and basic provenance validation. They do not
replace listening to Sanskrit with someone fluent in its pronunciation.
