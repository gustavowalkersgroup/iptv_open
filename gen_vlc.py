import xml.etree.ElementTree as ET, urllib.parse
root = ET.fromstring(open(r'F:\bkp\Documents\Claude\opencode\Iptv-Brasil-2026-master\filtered\IPTV-Brasil-2026.sob').read())
m3u = '#EXTM3U\n'
for item in root.findall('.//backupItem'):
    link = item.find('serviioLink').text
    params = urllib.parse.parse_qs(link.split('?')[1])
    url = urllib.parse.unquote(params['url'][0])
    name = urllib.parse.unquote(params['name'][0])
    m3u += f'#EXTINF:-1 tvg-name="{name}",{name}\n{url}\n'
with open(r'F:\bkp\Documents\Claude\opencode\Iptv-Brasil-2026-master\filtered\IPTV-Brasil-VLC.m3u8', 'w', encoding='utf-8') as f:
    f.write(m3u)
print(f'{len(root.findall(".//backupItem"))} channels written to IPTV-Brasil-VLC.m3u8')
print(f'Size: {len(m3u)} bytes')
for line in m3u.split('\n'):
    if line.startswith('http') and not line.startswith('#'):
        print(f'First URL: {line}')
        break
