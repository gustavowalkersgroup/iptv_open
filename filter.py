#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smart IPTV filter: parse, validate, dedup, categorize BR/EN."""
import re, os, sys, io
from datetime import datetime

WORKDIR = os.path.dirname(os.path.abspath(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def clean_name(name):
    """Strip resolution tags, years, and normalize channel name for dedup."""
    n = name.strip().lower()
    n = re.sub(r'\s*\[.*?\]\s*', '', n)
    n = re.sub(r'\s*\(?\d{4}\)?\s*\[l\]?\s*$', '', n)  # (2019), (2019) [L] at end
    n = re.sub(r'\s*-\s*\d{4}\s*$', '', n)  # - 2019 at end
    n = re.sub(r'\s*(hd|fhd|4k|sd|uhd|2k|8k|h265|hdr|x265)\s*$', '', n, flags=re.I)
    n = re.sub(r'[²³⁴]\s*$', '', n)
    return n.strip()

def is_valid_channel(name, url):
    """Check if entry is a real TV channel, not a movie/series episode."""
    if not url or not url.startswith('http'): return False
    if re.search(r's\d+e\d+', name, re.I): return False
    if name.startswith('/9j/'): return False
    if len(name.strip()) < 2: return False
    # Reject movie titles with year patterns
    if re.search(r'\(?\d{4}\)?', name): return False
    if re.search(r'-\s*\d{4}$', name): return False
    return True

def parse_m3u(filepath):
    channels = []
    if not os.path.exists(filepath): return channels
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            extinf = line
            nm = re.search(r',(.+)$', extinf)
            name = nm.group(1).strip() if nm else 'Unknown'
            tg = re.search(r'tvg-name="([^"]*)"', extinf)
            tc = re.search(r'tvg-country="([^"]*)"', extinf)
            gt = re.search(r'group-title="([^"]*)"', extinf)
            i += 1
            if i < len(lines):
                url = lines[i].strip()
                if url and not url.startswith('#'):
                    ch = {'name': name, 'url': url,
                        'tvg_name': tg.group(1) if tg else '',
                        'tvg_country': tc.group(1) if tc else '',
                        'group_title': gt.group(1) if gt else '',
                        'source_file': os.path.basename(filepath)}
                    if is_valid_channel(ch['name'], ch['url']):
                        channels.append(ch)
        i += 1
    return channels

def parse_colados(filepath):
    channels = []
    if not os.path.exists(filepath): return channels
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('#EXTINF:'):
            extinf = line
            nm = re.search(r',(.+)$', extinf)
            name = nm.group(1).strip() if nm else 'Unknown'
            tg = re.search(r'tvg-name="([^"]*)"', extinf)
            tc = re.search(r'tvg-country="([^"]*)"', extinf)
            gt = re.search(r'group-title="([^"]*)"', extinf)
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and not url.startswith('#'):
                    ch = {'name': name, 'url': url,
                        'tvg_name': tg.group(1) if tg else '',
                        'tvg_country': tc.group(1) if tc else '',
                        'group_title': gt.group(1) if gt else '',
                        'source_file': 'colados.txt'}
                    if is_valid_channel(ch['name'], ch['url']):
                        channels.append(ch)
    return channels

def classify(ch):
    """Return 'BR', 'EN', or None."""
    name_l = ch['name'].lower()
    tvg_l = ch['tvg_name'].lower()
    group_l = ch['group_title'].lower()
    country = ch['tvg_country'].lower() if ch['tvg_country'] else ''

    # Reject if tvg_country is set to a non-BR/EN country
    if country and country not in ('br', 'us', 'gb'):
        # But check if the name itself indicates BR/EN
        pass  # Continue to check name-based classification

    if country == 'br': return 'BR'
    if country in ('us', 'gb'): return 'EN'

    # Also reject if tvg-country is a known non-EN country and name doesn't have EN keyword
    known_bad = ['al', 'tr', 'it', 'es', 'fr', 'de', 'pl', 'pt', 'ar', 'co', 'cl', 'mx',
                 'uy', 'py', 've', 'ec', 'bo', 'pe', 'cr', 'pa', 'do', 'hn', 'gt', 'ni',
                 'sv', 'bz', 'gy', 'sr', 'gf', 'fk', 'fk', 'zm', 'zw', 'za', 'ng', 'ke',
                 'za', 'eg', 'ma', 'tn', 'dz', 'iq', 'ir', 'pk', 'bd', 'lk', 'mm', 'kh',
                 'th', 'vn', 'ph', 'id', 'my', 'sg', 'hk', 'tw', 'jp', 'kr', 'cn', 'in',
                 'at', 'ch', 'be', 'nl', 'lu', 'ie', 'no', 'se', 'dk', 'fi', 'is', 'hr',
                 'sk', 'cz', 'hu', 'ro', 'bg', 'gr', 'tr', 'ua', 'by', 'lt', 'lv', 'ee',
                 'ru', 'ge', 'am', 'az', 'kz', 'uz', 'mn', 'jo', 'lb', 'sy', 'om', 'ye',
                 'kw', 'bh', 'qa', 'ae', 'sa', 'ye', 'zw', 'mz', 'mg', 'mu', 'sc', 'km',
                 'cd', 'cf', 'cm', 'gw', 'sn', 'ml', 'bf', 'ci', 'gh', 'tg', 'bj', 'ne']
    if country in known_bad: return None

    br_kw = ['brasil', 'brazil', 'canal br', 'ipbr', 'grupo band', 'globo', 'sbt',
             'record tv', 'record', 'rede', 'canais brasil',
             'filmes | nacionais', 'nacionais', 'bandeirantes', 'tv aberto',
             'tv brasileira', 'filmes nacionais', 'ipbr']
    en_kw = ['bbc world', 'bbc news', 'cnn international', 'cnn en',
             'animal planet', 'history', 'a&e', 'adult swim',
             'national geographic', 'nat geo', 'espn',
             'bbc america', 'bbc world news', 'discovery channel',
             'channel 4', 'itv', 'channel 5', 'e4', 'dave',
             'comedy central', 'fx', 'mtv', 'tnt', 'tbs',
             'nick jr', 'nicktoons', 'cbs', 'abc', 'nbc', 'fox']

    for kw in br_kw:
        if kw in name_l or kw in tvg_l or kw in group_l: return 'BR'
    for kw in en_kw:
        if kw in name_l or kw in tvg_l or kw in group_l: return 'EN'
    return None

def main():
    print(f"{'='*60}")
    print(f"IPTV BR/EN Filter")
    print(f"{'='*60}\n")

    # Only parse the relevant files
    # CanaisBR01/02/03 = BR content, colados.txt = has BR/EN mixed
    # CanaisEuropa, CanaisItália = all international (skip entirely)
    # Filmes-Series = Brazilian films (keep as-is, separate file)

    br_files = ['CanaisBR01.m3u8', 'CanaisBR02.m3u8', 'CanaisBR03.m3u8']
    colados_file = 'colados.txt'

    all_ch = []
    print("=== PARSING ===\n")
    for fname in br_files:
        fpath = os.path.join(WORKDIR, fname)
        ch = parse_m3u(fpath)
        print(f"  {fname}: {len(ch)} valid channels")
        all_ch.extend(ch)

    col = parse_colados(os.path.join(WORKDIR, colados_file))
    print(f"  colados.txt: {len(col)} valid channels")
    all_ch.extend(col)

    # Also copy Filmes-Series as-is
    fs_path = os.path.join(WORKDIR, 'Filmes-Series.m3u8')
    fs_ch = []
    if os.path.exists(fs_path):
        with open(fs_path, 'r', encoding='utf-8', errors='replace') as f:
            fs_content = f.read()
        # Just count and keep
        fs_count = fs_content.count('#EXTINF:')
        print(f"  Filmes-Series.m3u8: {fs_count} entries (kept as-is)")

    print(f"\nTotal valid channels to filter: {len(all_ch)}")

    # Filter and dedup
    br_map = {}
    en_map = {}
    rejected = []

    for ch in all_ch:
        cat = classify(ch)
        clean = clean_name(ch['name'])
        if not clean or clean == 'unknown': continue

        if cat == 'BR':
            if clean not in br_map: br_map[clean] = ch
        elif cat == 'EN':
            if clean not in en_map: en_map[clean] = ch
        else:
            rejected.append(ch)

    br_list = list(br_map.values())
    en_list = list(en_map.values())

    print(f"\n=== RESULTS ===")
    print(f"  BR unique channels: {len(br_list)}")
    print(f"  EN unique channels: {len(en_list)}")
    print(f"  Total kept: {len(br_list)+len(en_list)}")
    print(f"  Rejected (international): {len(rejected)}")

    os.makedirs(os.path.join(WORKDIR, 'filtered'), exist_ok=True)

    # Write filtered playlists
    write_m3u(br_list, os.path.join(WORKDIR, 'filtered', 'Canais_BR_Filtrado.m3u8'))
    write_m3u(en_list, os.path.join(WORKDIR, 'filtered', 'Canais_EN_Filtrado.m3u8'))
    write_m3u(br_list+en_list, os.path.join(WORKDIR, 'filtered', 'Canais_BR_EN_Filtrado.m3u8'))
    write_m3u(rejected, os.path.join(WORKDIR, 'filtered', 'Canais_REJEITADOS.m3u8'))

    # Copy Filmes-Series to filtered
    import shutil
    shutil.copy2(fs_path, os.path.join(WORKDIR, 'filtered', 'Filmes-Serie_BR.m3u8'))

    print(f"\n=== OUTPUT ===")
    print(f"  filtered/Canais_BR_Filtrado.m3u8 ({len(br_list)})")
    print(f"  filtered/Canais_EN_Filtrado.m3u8 ({len(en_list)})")
    print(f"  filtered/Canais_BR_EN_Filtrado.m3u8 ({len(br_list)+len(en_list)})")
    print(f"  filtered/Canais_REJEITADOS.m3u8 ({len(rejected)})")
    print(f"  filtered/Filmes-Serie_BR.m3u8 (copied)")

    # Skip printing channel lists - too long
    print(f"\n=== BR CHANNELS (first 30) ===")
    for ch in sorted(br_list, key=lambda x: x['name'])[:30]:
        print(f"  {ch['name']} [{ch['source_file']}]")
    print(f"\n=== EN CHANNELS (first 30) ===")
    for ch in sorted(en_list, key=lambda x: x['name'])[:30]:
        print(f"  {ch['name']} [{ch['source_file']}]")
    print(f"\nDone! Run test_urls.py to check URL liveness.")

def write_m3u(channels, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for ch in channels:
            extinf = f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-country="{ch["tvg_country"]}" group-title="{ch["group_title"]}"'
            f.write(extinf + '\n' + ch['url'] + '\n')

if __name__ == '__main__':
    main()
