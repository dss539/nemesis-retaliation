#!/usr/bin/env python3
"""Download all TTS mod assets and organize into a categorized directory tree."""

import json, os, subprocess, struct, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = '/home/smithers/nemesis-retaliation/assets/tts-mod'
MANIFEST_PATH = '/home/smithers/tts-extract/manifest.json'

def detect_ext(filepath):
    """Detect file extension by magic bytes."""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(16)
        if header[:4] == b'\x89PNG':
            return '.png'
        if header[:3] == b'\xff\xd8\xff':
            return '.jpg'
        if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
            return '.webp'
        if header[:6] == b'GIF8':
            return '.gif'
        if header[:2] == b'BM':
            return '.bmp'
        if header[:9] == b'# Blender' or header[:8] == b'# Export':
            return '.obj'
        if header[:7] in (b'UnityFS', b'UnityF'):
            return '.asset3d'
        if header[:3] == b'ID3' or header[:2] == b'\xff\xfb':
            return '.mp3'
        if header[:5] == b'%PDF-':
            return '.pdf'
        if header[:4] == b'PK\x03\x04':
            return '.zip'
        # Check for OGG
        if header[:4] == b'OggS':
            return '.ogg'
        # Check for WAV
        if header[:4] == b'RIFF' and header[8:12] == b'WAVE':
            return '.wav'
    except:
        pass
    return '.bin'

def download_one(entry):
    """Download a single URL, detect type, and move to final location."""
    url = entry['url']
    dest_dir = os.path.join(BASE_DIR, entry['dir'])
    dest_name = entry['filename_base']

    # Temp download path
    tmp_path = f'/tmp/tts_download_{dest_name}.tmp'

    try:
        # Download with curl
        result = subprocess.run(
            ['curl', '-4', '-sS', '-L', '--retry', '3', '--retry-delay', '2',
             '--connect-timeout', '15', '--max-time', '120',
             '--resolve', 'steamusercontent-a.akamaihd.net:443:23.62.61.236',
             '-o', tmp_path, url],
            capture_output=True, timeout=180
        )

        if result.returncode != 0:
            return {'url': url, 'status': 'curl_error', 'error': result.stderr.decode()[:200]}

        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            return {'url': url, 'status': 'empty', 'error': 'zero-size download'}

        # Detect extension
        ext = detect_ext(tmp_path)

        # Final filename: hash + extension
        final_name = dest_name + ext
        final_path = os.path.join(dest_dir, final_name)

        # Create directory and move file
        os.makedirs(dest_dir, exist_ok=True)

        # If file already exists (same hash), skip
        if os.path.exists(final_path):
            os.remove(tmp_path)
            return {'url': url, 'status': 'duplicate', 'path': final_path}

        os.rename(tmp_path, final_path)

        size = os.path.getsize(final_path)
        return {'url': url, 'status': 'ok', 'path': final_path, 'ext': ext, 'size': size}

    except subprocess.TimeoutExpired:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return {'url': url, 'status': 'timeout', 'error': 'curl timed out'}
    except Exception as e:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except: pass
        return {'url': url, 'status': 'error', 'error': str(e)[:200]}

def main():
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    print(f"Downloading {len(manifest)} assets to {BASE_DIR}")
    print(f"Using 12 parallel workers")
    print()

    results = []
    ok_count = 0
    error_count = 0
    dup_count = 0
    total_bytes = 0

    ext_counts = {}

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(download_one, entry): entry for entry in manifest}

        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            results.append(result)

            status = result['status']
            if status == 'ok':
                ok_count += 1
                total_bytes += result['size']
                ext = result.get('ext', '.bin')
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
            elif status == 'duplicate':
                dup_count += 1
            else:
                error_count += 1

            done = i + 1
            if done % 50 == 0 or done == len(manifest):
                print(f"  Progress: {done}/{len(manifest)} | OK: {ok_count} | Dup: {dup_count} | Err: {error_count} | {total_bytes/(1024*1024):.1f} MB")

    # Save results
    with open('/home/smithers/tts-extract/download_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n=== Download Complete ===")
    print(f"OK: {ok_count}  Duplicates: {dup_count}  Errors: {error_count}")
    print(f"Total size: {total_bytes/(1024*1024*1024):.2f} GB")
    print(f"\nFile types:")
    for ext, count in sorted(ext_counts.items(), key=lambda x: -x[1]):
        print(f"  {count:4d}  {ext}")

    # Show errors
    errors = [r for r in results if r['status'] not in ('ok', 'duplicate')]
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors[:20]:
            print(f"  {e['status']}: {e.get('error', '')[:80]}")
            print(f"    URL: {e['url'][:80]}")

if __name__ == '__main__':
    main()