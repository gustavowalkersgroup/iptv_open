#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test URLs from filtered playlists for liveness."""
import urllib.request, os, sys, io
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

WORKDIR = os.path.dirname(os.path.abspath(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
TIMEOUT = 8
MAX_THREADS = 30

def read_urls(filepath):
    urls = []
    if not os.path.exists(filepath): return urls
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('EXTM3U'):
                urls.append(line)
    return urls

def test_url(url, timeout=TIMEOUT):
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 IPTV-Tester/1.0')
        req.add_header('Accept', '*/*')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return url, True, resp.status
    except:
        try:
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Mozilla/5.0 IPTV-Tester/1.0')
            req.add_header('Range', 'bytes=0-1')
            req.add_header('Accept', '*/*')
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return url, True, resp.status
        except Exception as e:
            return url, False, str(e)[:40]

def main():
    filtered_dir = os.path.join(WORKDIR, 'filtered')
    files = {
        'Canais_BR_Filtrado.m3u8': os.path.join(filtered_dir, 'Canais_BR_Filtrado.m3u8'),
        'Canais_EN_Filtrado.m3u8': os.path.join(filtered_dir, 'Canais_EN_Filtrado.m3u8'),
    }

    for fname, fpath in files.items():
        if not os.path.exists(fpath):
            print(f"MISSING: {fpath}")
            continue

        urls = read_urls(fpath)
        total = len(urls)
        if total == 0:
            print(f"EMPTY: {fname}")
            continue

        print(f"\n{'='*60}")
        print(f"Testing: {fname} ({total} URLs)")
        print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")

        results = []
        completed = 0
        live_count = 0
        dead_count = 0

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {executor.submit(test_url, u): u for u in urls}
            for future in as_completed(futures):
                completed += 1
                url, is_live, status = future.result()
                results.append((url, is_live, status))
                if is_live: live_count += 1
                else: dead_count += 1
                if completed % 50 == 0 or completed == total:
                    pct = completed * 100 // total
                    print(f"  [{pct}%] {completed}/{total} | LIVE: {live_count} | DEAD: {dead_count}")

        out_live = os.path.join(filtered_dir, fname.replace('.m3u8', '_LIVE.m3u8'))
        out_dead = os.path.join(filtered_dir, fname.replace('.m3u8', '_DEAD.m3u8'))

        with open(out_live, 'w') as f:
            f.write('#EXTM3U\n')
            for url, is_live, status in results:
                if is_live: f.write(url + '\n')
        with open(out_dead, 'w') as f:
            f.write('#EXTM3U\n')
            for url, is_live, status in results:
                if not is_live: f.write(url + '\n')

        print(f"\n  -> LIVE: {out_live} ({live_count})")
        print(f"  -> DEAD: {out_dead} ({dead_count})")

    print(f"\n{'='*60}")
    print(f"ALL TESTS COMPLETE")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
