"""Resumable, local-only Svara synthesis on Apple Silicon. No hosted TTS API."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import time

MODEL = 'mlx-community/svara-tts-v1-8bit'
REVISION = '4531082be5031017247db28b144d0d9390f82273'
VOICES = {'sa-IN': 'Sanskrit', 'en-IN': 'English (Indian)', 'hi-IN': 'Hindi',
          'bn-IN': 'Bengali', 'mr-IN': 'Marathi', 'te-IN': 'Telugu', 'ta-IN': 'Tamil'}


def key(item):
    return json.dumps([item['locale'], item['kind'], item['text']], ensure_ascii=False, separators=(',', ':'))


def validate(items):
    for item in items:
        if item.get('locale') not in VOICES or item.get('kind') not in ('verse', 'translation', 'explanation', 'context'):
            raise ValueError('Unsupported language or narration section')
        if not isinstance(item.get('text'), str) or not 1 <= len(item['text'].strip()) <= 360:
            raise ValueError('Queue texts must contain 1–360 characters; use the app script builder to split text')
        if item.get('rights') not in ('public-domain', 'project-original', 'permission-granted'):
            raise ValueError('Each text needs documented commercial rights before audio export')
        if not item.get('rightsNote'):
            raise ValueError('Missing text provenance / permission note')
    return items


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def write_gallery(directory, manifest):
    cards = []
    for item in manifest.values():
        cards.append(f'<article><h2>{html.escape(item.get("label", item["locale"]))}</h2>'
            f'<p>{html.escape(item["voice"])}</p><p>{html.escape(item["text"])}</p>'
            f'<audio controls preload="none" src="{item["file"]}"></audio></article>')
    (directory / 'listen.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>GyanSutra voice samples</title>'
        '<style>body{font:18px/1.7 system-ui;max-width:850px;margin:40px auto;padding:0 24px;'
        'background:#fffaf3;color:#30251c}article{border-top:1px solid #d4c5b1;padding:20px 0}'
        'audio{width:100%}</style><h1>GyanSutra voice samples</h1>'
        '<p>AI-generated with Svara-TTS on your Mac. Built with Llama. '
        'Listen for pronunciation, missing or repeated words, and a pleasant adult voice. '
        'These samples have not received a fluent-speaker listening review. '
        'The demonstration meanings are original sample prose, not quoted translations.</p>'
        + ''.join(cards) + '</html>')


def load_voice(home):
    from huggingface_hub import snapshot_download
    from mlx_audio.tts.utils import load_model
    snapshot = Path(snapshot_download(MODEL, revision=REVISION, max_workers=2,
        allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', 'README.md', 'LICENSE*']))
    # MLX's generic Orpheus loader defaults to the English Orpheus tokenizer.
    # Point it at Svara's own tokenizer without altering the HF cached snapshot.
    local = home / 'models' / 'svara-tts-v1-8bit'
    local.mkdir(parents=True, exist_ok=True)
    for source in snapshot.iterdir():
        if source.name != 'config.json' and not (local / source.name).exists():
            (local / source.name).symlink_to(source)
    config = json.loads((snapshot / 'config.json').read_text())
    config['tokenizer_name'] = str(local)
    atomic_json(local / 'config.json', config)
    model = load_model(local)
    # MLX Audio 0.5.1 expects this compatibility attribute to be iterable,
    # while Transformers exposes Svara's single end token as an integer.
    eos_token_ids = getattr(model.tokenizer, 'eos_token_ids', None)
    if isinstance(eos_token_ids, int):
        # Transformers intercepts normal assignment because it interprets the
        # attribute name as a token string; an explicit instance value is safe.
        model.tokenizer.__dict__['eos_token_ids'] = [eos_token_ids]
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--limit', type=int, default=0, help='0 processes the full queue; completed clips are skipped')
    parser.add_argument('--gender', choices=['Male', 'Female'], default='Male')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    items = validate(json.loads(args.queue.read_text()))
    if args.limit < 0:
        parser.error('--limit must be nonnegative')
    if args.limit:
        items = items[:args.limit]
    home = Path(os.environ['NARRATION_HOME'])
    args.output.mkdir(parents=True, exist_ok=True)
    import mlx.core as mx
    import numpy as np
    import soundfile as sf
    if not mx.metal.is_available():
        raise RuntimeError('Apple Metal GPU is unavailable; run on your Apple Silicon Mac')
    manifest_path = args.output / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    model = None
    for index, item in enumerate(items):
        voice = f"{VOICES[item['locale']]} ({args.gender})"
        fingerprint = hashlib.sha256(f'{REVISION}:{voice}:{args.seed}:v1:{key(item)}'.encode()).hexdigest()
        target = args.output / f'{fingerprint}.wav'
        if target.exists() and manifest.get(key(item), {}).get('file') == target.name:
            print(f'[{index + 1}/{len(items)}] cached {item.get("label", item["locale"])}', flush=True)
            continue
        if model is None:
            print('Loading Svara on the Apple GPU…', flush=True)
            model = load_voice(home)
        print(f'[{index + 1}/{len(items)}] {voice}: {item["text"]}', flush=True)
        started = time.monotonic()
        mx.random.seed(args.seed)
        chunks = []
        for result in model.generate(text=item['text'], voice=voice, temperature=0.65,
                top_p=0.9, top_k=40, repetition_penalty=1.1, max_tokens=4096):
            if result.token_count >= 4096:
                raise RuntimeError('Generation hit its token limit; split the text before retrying')
            chunks.append(np.asarray(result.audio).reshape(-1))
        if not chunks:
            raise RuntimeError('Model returned no audio')
        audio = np.concatenate(chunks)
        if not np.isfinite(audio).all() or len(audio) < model.sample_rate // 4 or np.max(np.abs(audio)) < 0.001:
            raise RuntimeError('Model returned invalid or silent audio')
        temporary = target.with_suffix('.tmp')
        sf.write(temporary, audio, model.sample_rate, format='WAV', subtype='PCM_16')
        if temporary.stat().st_size > 4 * 1024 * 1024:
            temporary.unlink()
            raise RuntimeError('Audio exceeds app limit; split the text further')
        temporary.replace(target)
        manifest[key(item)] = {**item, 'file': target.name, 'voice': voice, 'model': MODEL,
            'revision': REVISION, 'seconds': round(len(audio) / model.sample_rate, 2),
            'generationSeconds': round(time.monotonic() - started, 2),
            'audioSHA256': hashlib.sha256(target.read_bytes()).hexdigest(), 'listeningReviewed': False}
        atomic_json(manifest_path, manifest)
        write_gallery(args.output, manifest)
        print(f'Saved {target.name}: {manifest[key(item)]["seconds"]}s audio, '
              f'{manifest[key(item)]["generationSeconds"]}s generation', flush=True)
        mx.clear_cache()
    write_gallery(args.output, manifest)
    print(f'Finished. Audio and provenance: {args.output}', flush=True)


if __name__ == '__main__':
    main()
