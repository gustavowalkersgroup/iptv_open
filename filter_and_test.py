#!/usr/bin/env python3
"""Parse M3U playlists, filter to BR/EN only, and test URL liveness."""

import re
import os
import sys
import urllib.request
import urllib.error
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

WORKDIR = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 10
MAX_THREADS = 20

# --- M3U Parser ---
def parse_m3u(filepath):
    """Parse an M3U file and return list of dicts with name, url, metadata."""
    channels = []
    if not os.path.exists(filepath):
        return channels
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            extinf = line
            # Extract channel name (after last comma)
            name_match = re.search(r',(.+)$', extinf)
            name = name_match.group(1).strip() if name_match else 'Unknown'
            
            # Extract metadata
            tvg_name = re.search(r'tvg-name="([^"]*)"', extinf)
            tvg_country = re.search(r'tvg-country="([^"]*)"', extinf)
            tvg_id = re.search(r'tvg-id="([^"]*)"', extinf)
            group_title = re.search(r'group-title="([^"]*)"', extinf)
            
            i += 1
            if i < len(lines):
                url = lines[i].strip()
                if url and not url.startswith('#'):
                    channels.append({
                        'name': name,
                        'url': url,
                        'tvg_name': tvg_name.group(1) if tvg_name else '',
                        'tvg_country': tvg_country.group(1) if tvg_country else '',
                        'tvg_id': tvg_id.group(1) if tvg_id else '',
                        'group_title': group_title.group(1) if group_title else '',
                        'source_file': os.path.basename(filepath)
                    })
        i += 1
    return channels

def parse_colados_txt(filepath):
    """Parse colados.txt which has different format."""
    channels = []
    if not os.path.exists(filepath):
        return channels
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('#EXTINF:'):
            extinf = line
            name_match = re.search(r',(.+)$', extinf)
            name = name_match.group(1).strip() if name_match else 'Unknown'
            
            tvg_name = re.search(r'tvg-name="([^"]*)"', extinf)
            tvg_country = re.search(r'tvg-country="([^"]*)"', extinf)
            tvg_id = re.search(r'tvg-id="([^"]*)"', extinf)
            group_title = re.search(r'group-title="([^"]*)"', extinf)
            
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and not url.startswith('#'):
                    channels.append({
                        'name': name,
                        'url': url,
                        'tvg_name': tvg_name.group(1) if tvg_name else '',
                        'tvg_country': tvg_country.group(1) if tvg_country else '',
                        'tvg_id': tvg_id.group(1) if tvg_id else '',
                        'group_title': group_title.group(1) if group_title else '',
                        'source_file': 'colados.txt'
                    })
    return channels

def is_br_or_en(channel):
    """Determine if a channel is Brazilian (BR) or English (EN)."""
    name_lower = channel['name'].lower()
    tvg_name_lower = channel['tvg_name'].lower()
    country = channel['tvg_country'].lower() if channel['tvg_country'] else ''
    group_title_lower = channel['group_title'].lower()
    
    # Direct country code match
    if country in ['br', 'us', 'gb']:
        return True
    
    # BR indicators
    br_keywords = ['brasil', 'brazil', 'canal br', 'ipbr', 'grupo band', 'globo', 'sbt', 'record', 'band', 'rede', 'canais brasil', 'filmes | nacionais', 'nacionais']
    # EN indicators  
    en_keywords = ['english', 'en ', 'bbc world', 'cnn international', 'francis', 'dave', 'e4', 'channel 4', 'itv', 'sky', 'channel 5', 'bbc']
    
    for kw in br_keywords:
        if kw in name_lower or kw in tvg_name_lower or kw in group_title_lower:
            return True
    
    for kw in en_keywords:
        if kw in name_lower or kw in tvg_name_lower:
            return True
    
    # Check group title for Brazil/English indicators
    if 'brasil' in group_title_lower or 'brazil' in group_title_lower or 'nacionais' in group_title_lower:
        return True
    
    return False

def is_br_or_en_colados(channel):
    """Check for colados.txt channels using tvg-country codes."""
    country = channel['tvg_country'].lower() if channel['tvg_country'] else ''
    if country in ['br', 'us', 'gb']:
        return True
    return is_br_or_en(channel)

def test_url(url, timeout=TIMEOUT):
    """Test if a URL is reachable. Returns True if live."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 IPTV-Tester/1.0')
        req.add_header('Accept', '*/*')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True
    except Exception:
        try:
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Mozilla/5.0 IPTV-Tester/1.0')
            req.add_header('Range', 'bytes=0-1')
            req.add_header('Accept', '*/*')
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return True
        except Exception:
            return False

def main():
    print(f"{'='*60}")
    print(f"IPTV BR/EN Filter & URL Tester")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Parse all source files
    all_channels = []
    
    src_files = ['CanaisBR01.m3u8', 'CanaisBR02.m3u8', 'CanaisBR03.m3u8',
                 'CanaisEuropa.m3u8', 'CanaisItália.m3u', 'CanaisItalia.m3u8',
                 'Filmes-Series.m3u8']
    
    print("=== PARSING SOURCE FILES ===\n")
    for fname in src_files:
        fpath = os.path.join(WORKDIR, fname)
        if fname == 'colados.txt':
            channels = parse_colados_txt(fpath)
        else:
            channels = parse_m3u(fpath)
        print(f"  {fname}: {len(channels)} channels parsed")
        for ch in channels:
            all_channels.append(ch)
    
    print(f"\nTotal channels parsed: {len(all_channels)}")
    
    # Filter BR/EN
    print(f"\n=== FILTERING BR/EN CHANNELS ===\n")
    br_en_channels = []
    for ch in all_channels:
        if 'colados.txt' in ch['source_file']:
            if is_br_or_en_colados(ch):
                br_en_channels.append(ch)
        else:
            if is_br_or_en(ch):
                br_en_channels.append(ch)
    
    print(f"BR/EN channels found: {len(br_en_channels)}")
    
    # Categorize
    br_channels = [ch for ch in br_en_channels if is_br_channel(ch)]
    en_channels = [ch for ch in br_en_channels if ch not in br_channels]
    
    print(f"\n  BR channels: {len(br_channels)}")
    print(f"  EN channels: {len(en_channels)}")
    
    # Write filtered playlists
    print(f"\n=== CREATING FILTERED PLAYLISTS ===\n")
    
    os.makedirs(os.path.join(WORKDIR, 'filtered'), exist_ok=True)
    
    # Write BR playlist
    br_path = os.path.join(WORKDIR, 'filtered', 'CanaisBR_Filtrado.m3u8')
    write_m3u(br_channels, br_path)
    print(f"  Written: {br_path} ({len(br_channels)} channels)")
    
    # Write EN playlist
    en_path = os.path.join(WORKDIR, 'filtered', 'CanaisEN_Filtrado.m3u8')
    write_m3u(en_channels, en_path)
    print(f"  Written: {en_path} ({len(en_channels)} channels)")
    
    # Write combined BR/EN playlist
    combined_path = os.path.join(WORKDIR, 'filtered', 'Canais_BR_EN_Filtrado.m3u8')
    write_m3u(br_en_channels, combined_path)
    print(f"  Written: {combined_path} ({len(br_en_channels)} channels)")
    
    # Write rejected list
    rejected = [ch for ch in all_channels if ch not in br_en_channels]
    rejected_path = os.path.join(WORKDIR, 'filtered', 'Canais_REJEITADOS.m3u8')
    write_m3u(rejected, rejected_path)
    print(f"  Written: {rejected_path} ({len(rejected)} channels rejected)")
    
    # Test URLs
    print(f"\n=== TESTING URL LIVENESS ===\n")
    print("Testing all URLs (this may take a while)...\n")
    
    results = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(test_url, ch['url']): ch for ch in br_en_channels}
        completed = 0
        for future in as_completed(futures):
            completed += 1
            ch = futures[future]
            try:
                live = future.result()
            except Exception:
                live = False
            results.append({**ch, 'live': live})
            if completed % 50 == 0:
                print(f"  Progress: {completed}/{len(br_en_channels)} tested...")
    
    live_count = sum(1 for r in results if r['live'])
    dead_count = len(results) - live_count
    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total tested: {len(results)}")
    print(f"LIVE: {live_count}")
    print(f"DEAD: {dead_count}")
    
    # Write results
    live_path = os.path.join(WORKDIR, 'filtered', 'Canais_BR_EN_LIVE.m3u8')
    dead_path = os.path.join(WORKDIR, 'filtered', 'Canais_BR_EN_DEAD.m3u8')
    
    write_m3u([r for r in results if r['live']], live_path)
    write_m3u([r for r in results if not r['live']], dead_path)
    print(f"\n  Live playlist: {live_path} ({live_count} channels)")
    print(f"  Dead playlist: {dead_path} ({dead_count} channels)")
    
    # Print live BR channels
    print(f"\n{'='*60}")
    print(f"LIVE BR CHANNELS:")
    print(f"{'='*60}")
    for r in sorted(results, key=lambda x: x['name']):
        if r['live'] and is_br_channel(r):
            print(f"  [LIVE] {r['name']} ({r['source_file']})")
    
    print(f"\n{'='*60}")
    print(f"LIVE EN CHANNELS:")
    print(f"{'='*60}")
    for r in sorted(results, key=lambda x: x['name']):
        if r['live'] and not is_br_channel(r):
            print(f"  [LIVE] {r['name']} ({r['source_file']})")

def is_br_channel(ch):
    """Determine if a channel is specifically Brazilian."""
    name_lower = ch['name'].lower()
    tvg_name_lower = ch['tvg_name'].lower()
    country = ch['tvg_country'].lower() if ch['tvg_country'] else ''
    group_title_lower = ch['group_title'].lower()
    
    if country == 'br':
        return True
    
    br_only = ['brasil', 'brazil', 'canal br', 'ipbr', 'grupo band', 'globo', 'sbt', 
               'record', 'band', 'rede', 'canais brasil', 'filmes | nacionais', 
               'nacionais', 'bandeirantes', 'bandeirantes', 'tv aberto', 'tv brasileira',
               'bandeirantes', 'nacional']
    for kw in br_only:
        if kw in name_lower or kw in tvg_name_lower or kw in group_title_lower:
            return True
    return False

def write_m3u(channels, filepath):
    """Write channels to M3U format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for ch in channels:
            extinf = f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-country="{ch["tvg_country"]}" group-title="{ch["group_title"]}"'
            f.write(extinf + '\n')
            f.write(ch['url'] + '\n')

if __name__ == '__main__':
    main()
