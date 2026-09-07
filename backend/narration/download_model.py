"""Download the pinned Svara model in resumable ranges on slow connections."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import os
from pathlib import Path
import subprocess
import sys

from generate_mac import MODEL, REVISION

SIZE = 3507409069
SHA256 = '0a3ce5a39ac42a71b40e9e422225cd1a0d8f7d4c852dd49088953da9c2b28b39'
CHUNK = 16 * 1024 * 1024


def main():
    model, revision, size, checksum = MODEL, REVISION, SIZE, SHA256
    if '--decoder' in sys.argv:
        model, revision = 'mlx-community/snac_24khz', '556af1cd3b1c5f2d294f6aa9bb886245d7b716ac'
        size, checksum = 79404951, 'e61ae2f638f56ee07a37592cd5a6a9e7d642560ddc78a76ee4a7f96d6922f1be'
    home = Path(os.environ['NARRATION_HOME'])
    repo = home / 'huggingface/hub' / ('models--' + model.replace('/', '--'))
    blobs = repo / 'blobs'
    parts = home / ('decoder-parts' if '--decoder' in sys.argv else 'download-parts')
    parts.mkdir(parents=True, exist_ok=True)
    blobs.mkdir(parents=True, exist_ok=True)
    target = blobs / checksum
    if target.exists():
        print('Model already downloaded', flush=True)
        return
    # A stopped HF download is a contiguous prefix. Preserve its complete ranges.
    partials = list(blobs.glob(f'{checksum}.*.incomplete'))
    if partials:
        prefix = max(partials, key=lambda p: p.stat().st_size)
        with prefix.open('rb') as source:
            for start in range(0, prefix.stat().st_size // CHUNK * CHUNK, CHUNK):
                part = parts / f'{start}.part'
                if not part.exists():
                    part.write_bytes(source.read(CHUNK))
                else:
                    source.seek(CHUNK, 1)

    def download(start):
        end = min(start + CHUNK, size) - 1
        part = parts / f'{start}.part'
        expected = end - start + 1
        if part.exists() and part.stat().st_size == expected:
            return expected
        temporary = part.with_suffix('.tmp')
        if temporary.exists() and temporary.stat().st_size > expected:
            temporary.unlink()
        url = f'https://huggingface.co/{model}/resolve/{revision}/model.safetensors?range={start}'
        attempts = 0
        while not temporary.exists() or temporary.stat().st_size < expected:
            attempts += 1
            if attempts > 20:
                raise RuntimeError(f'Range {start}-{end} did not finish after 20 resumptions')
            received = temporary.stat().st_size if temporary.exists() else 0
            # Append only missing bytes. A timed-out request may still have
            # transferred useful data, which the next attempt resumes.
            with temporary.open('ab') as output:
                subprocess.run(['curl', '-f', '-sS', '--http1.1', '-L', '--connect-timeout', '30',
                    '--max-time', '120', '--range', f'{start + received}-{end}', url], stdout=output)
            if temporary.stat().st_size > expected:
                raise RuntimeError(f'Server returned too many bytes for range {start}-{end}')
        if temporary.stat().st_size != expected:
            raise RuntimeError(f'Incorrect range length at {start}')
        temporary.replace(part)
        return expected

    downloaded = 0
    failures = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        tasks = [executor.submit(download, start) for start in range(0, size, CHUNK)]
        for task in as_completed(tasks):
            try:
                downloaded += task.result()
            except Exception as error:
                failures.append(str(error))
                print('A range failed; other ranges will continue. Rerun to retry missing ranges.', flush=True)
            print(f'{downloaded / size:.1%} ({downloaded // 1048576}/{size // 1048576} MiB)', flush=True)
    if failures:
        raise RuntimeError(f'{len(failures)} ranges failed. Completed ranges are retained; rerun to resume.')
    combined = blobs / f'{checksum}.assembling'
    digest = hashlib.sha256()
    with combined.open('wb') as output:
        for start in range(0, size, CHUNK):
            with (parts / f'{start}.part').open('rb') as source:
                while block := source.read(1024 * 1024):
                    output.write(block)
                    digest.update(block)
    if digest.hexdigest() != checksum:
        raise RuntimeError('Model checksum mismatch; model was not installed')
    combined.replace(target)
    snapshot = repo / 'snapshots' / revision
    snapshot.mkdir(parents=True, exist_ok=True)
    link = snapshot / 'model.safetensors'
    if not link.exists():
        link.symlink_to(target)
    # Remove only this script's disposable chunks after verifying the full model.
    for part in parts.glob('*.part'):
        part.unlink()
    print(f'Verified SHA-256. {model} is ready.', flush=True)


if __name__ == '__main__':
    main()
