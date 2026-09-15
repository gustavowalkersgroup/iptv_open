import os
d = r'F:\bkp\Documents\Claude\opencode\Iptv-Brasil-2026-master\filtered'

def read_urls(path):
    urls = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('EXTM3U'):
                urls.append(line)
    return urls

def read_names(path):
    names = {}
    name = None
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                name = line.split(',')[-1].strip()
            elif line and not line.startswith('#'):
                if name: names[line] = name
                name = None
    return names

br_urls = read_urls(os.path.join(d, 'Canais_BR_Filtrado_LIVE.m3u8'))
en_urls = read_urls(os.path.join(d, 'Canais_EN_Filtrado_LIVE.m3u8'))
br_names = read_names(os.path.join(d, 'Canais_BR_Filtrado.m3u8'))
en_names = read_names(os.path.join(d, 'Canais_EN_Filtrado.m3u8'))

out = os.path.join(d, 'Canais_BR_EN_Compactado.m3u8')
with open(out, 'w', encoding='utf-8') as f:
    f.write('#EXTM3U\n')
    for url in br_urls:
        nm = br_names.get(url, 'Canal BR')
        f.write(f'#EXTINF:-1 tvg-name="{nm}" group-title="BR",{nm}\n')
        f.write(url + '\n')
    for url in en_urls:
        nm = en_names.get(url, 'Canal EN')
        f.write(f'#EXTINF:-1 tvg-name="{nm}" group-title="EN",{nm}\n')
        f.write(url + '\n')

print(f'Combined: {len(br_urls)} BR + {len(en_urls)} EN = {len(br_urls)+len(en_urls)} channels')
print(f'Output: {out} ({os.path.getsize(out)} bytes)')
