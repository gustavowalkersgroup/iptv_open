import urllib.request, json

base = 'http://127.0.0.1:8080'

# Test M3U
r = urllib.request.urlopen(base + '/m3u', timeout=5)
content = r.read().decode('utf-8')
lines = [l for l in content.split('\n') if l.strip()]
print(f'M3U: {len(lines)//2} channels')
print(f'First 3:')
for l in lines[:6]:
    print(f'  {l[:80]}')

# Test API
r = urllib.request.urlopen(base + '/api/channels', timeout=5)
data = json.loads(r.read())
print(f'\nAPI: {len(data)} channels')
print(f'First: {data[0]["name"]} -> {data[0]["url"][:60]}')

# Test M3U BR
r = urllib.request.urlopen(base + '/m3u/br', timeout=5)
br_content = r.read().decode('utf-8')
br_lines = [l for l in br_content.split('\n') if l.strip()]
print(f'\nM3U BR: {len(br_lines)//2} channels')

# Test M3U EN
r = urllib.request.urlopen(base + '/m3u/en', timeout=5)
en_content = r.read().decode('utf-8')
en_lines = [l for l in en_content.split('\n') if l.strip()]
print(f'M3U EN: {len(en_lines)//2} channels')

# Test HTML page
r = urllib.request.urlopen(base + '/', timeout=5)
html = r.read().decode('utf-8')
print(f'\nWeb UI: {len(html)} bytes, status {r.status}')

# Test proxy
r = urllib.request.urlopen(base + '/proxy?url=' + urllib.parse.quote('http://up.kiwi/351921603109/34939156/184', safe=''), timeout=10)
proxy_content = r.read()
print(f'\nProxy test: {r.status}, {len(proxy_content)} bytes, type={r.headers.get("Content-Type")}')

import urllib.parse
print('\nAll endpoints working!')
