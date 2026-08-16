#!/usr/bin/env python3
"""v2 base-only downloader. Fresh downloads, no reuse.
Downloads: include URLs (base) -> v2-dl/base/, unknown-only -> v2-dl/unsorted/.
Filenames: <ugc-id>.<ext> via magic bytes. Writes manifest.json + failures log."""
import json, os, subprocess, sys, shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

V2 = '/home/smithers/tts-extract/v2'
DL = '/home/smithers/tts-extract/v2-dl'
TMP = os.path.join(DL, 'tmp')
BASE_DIR = os.path.join(DL, 'base')
UNS_DIR = os.path.join(DL, 'unsorted')
os.makedirs(TMP, exist_ok=True)
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(UNS_DIR, exist_ok=True)

def detect_ext(path):
    with open(path, 'rb') as f:
        head = f.read(16)
    if head.startswith(b'\x89PNG'): return '.png'
    if head.startswith(b'\xff\xd8\xff'): return '.jpg'
    if head.startswith(b'RIFF') and head[8:12] == b'WEBP': return '.webp'
    if head.startswith(b'GIF8'): return '.gif'
    if head.startswith(b'BM'): return '.bmp'
    if head.startswith(b'%PDF'): return '.pdf'
    if head.startswith(b'ID3') or head.startswith(b'\xff\xfb'): return '.mp3'
    if head.startswith(b'PK\x03\x04'): return '.zip'
    if head.startswith(b'# Blender') or head.startswith(b'# Exported'): return '.obj'
    if head.startswith(b'UnityFS') or head.startswith(b'UnityF'): return '.asset3d'
    return '.bin'

def fetch(url, dest_dir):
    ugc = url.rstrip('/').split('/')[-2]
    tmp = os.path.join(TMP, ugc + '.tmp')
    for attempt in range(3):
        r = subprocess.run(['curl', '-4', '-sS', '--connect-timeout', '15',
                            '--retry', '2', '-o', tmp, url],
                           capture_output=True)
        if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 0:
            ext = detect_ext(tmp)
            final = os.path.join(dest_dir, ugc + ext)
            # same-fs move
            if os.path.exists(final):
                os.remove(final)
            os.replace(tmp, final)
            return final, os.path.getsize(final)
        else:
            if os.path.exists(tmp):
                os.remove(tmp)
    return None, 0

verdicts = json.load(open(os.path.join(V2, 'url_verdicts.json')))
jobs = [(u, BASE_DIR) for u in verdicts['include']] + \
       [(u, UNS_DIR) for u in verdicts['unknown']]
print(f'jobs: {len(jobs)} (base {len(verdicts["include"])}, unsorted {len(verdicts["unknown"])})')

manifest = []
failures = []
done = 0
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(fetch, u, d): (u, d) for u, d in jobs}
    for fut in as_completed(futs):
        url, dest_dir = futs[fut]
        try:
            final, size = fut.result()
        except Exception as e:
            final, size = None, 0
            failures.append((url, str(e)))
        if final:
            manifest.append({'url': url, 'file': os.path.relpath(final, DL), 'size': size})
        else:
            failures.append((url, 'download failed'))
        done += 1
        if done % 100 == 0:
            print(f'  {done}/{len(jobs)} done', flush=True)

with open(os.path.join(DL, 'manifest.json'), 'w') as f:
    json.dump(manifest, f, indent=1)
with open(os.path.join(DL, 'failures.json'), 'w') as f:
    json.dump([{'url': u, 'err': e} for u, e in failures], f, indent=1)

total = sum(m['size'] for m in manifest)
print(f'OK: {len(manifest)}/{len(jobs)}   bytes: {total:,}  ({total/1e9:.2f} GB)')
if failures:
    print(f'FAILED: {len(failures)}')
    for u, e in failures[:10]:
        print(f'  {e}: {u}')
