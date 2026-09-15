import urllib.request, urllib.error, re, json, os, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime

base = 'http://192.168.1.5:23423'

# Read the filtered M3U live channels
m3u_path = 'F:/bkp/Documents/Claude/opencode/Iptv-Brasil-2026-master/filtered/Canais_BR_EN_Filtrado.m3u8'
sob_path = 'F:/bkp/Documents/Claude/opencode/Iptv-Brasil-2026-master/filtered/IPTV-Brasil-EN-2026.sob'

# Parse M3U to get channel names and URLs
channels = []
with open(m3u_path, 'r', encoding='utf-8') as f:
    name = None
    for line in f:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            # Extract name from tvg-name attribute or from after comma
            tg_match = re.search(r'tvg-name="([^"]*)"', line)
            if tg_match:
                name = tg_match.group(1)
            else:
                comma_match = line.split(',')[-1].strip()
                name = comma_match if comma_match else None
        elif line and not line.startswith('#') and not line.startswith('EXTM3U'):
            if name:
                channels.append({'name': name, 'url': line})
                name = None

print(f"Parsed {len(channels)} channels from M3U")

# Generate serviio links and create .sob XML
root = ET.Element('onlineRepositoriesBackup')
items = ET.SubElement(root, 'items')

for i, ch in enumerate(channels, 1):
    # Encode the URL and name for serviio link
    url_encoded = urllib.parse.quote(ch['url'], safe='')
    name_encoded = urllib.parse.quote(ch['name'], safe='')
    
    # Build serviio link
    serviio_link = f"serviio://video:live?url={url_encoded}&name={name_encoded}"
    
    backup_item = ET.SubElement(items, 'backupItem', {
        'enabled': 'true',
        'order': str(i)
    })
    
    serviio_link_elem = ET.SubElement(backup_item, 'serviioLink')
    serviio_link_elem.text = serviio_link
    
    access_group = ET.SubElement(backup_item, 'accessGroupIds')
    id_elem = ET.SubElement(access_group, 'id')
    id_elem.text = '1'

# Create XML string
xml_str = '<?xml version="1.0" encoding="UTF-8" ?>\n' + ET.tostring(root, encoding='unicode')

# Save .sob file
sob_path = r'F:\bkp\Documents\Claude\opencode\Iptv-Brasil-2026-master\filtered\IPTV-Brasil-2026.sob'
with open(sob_path, 'w', encoding='utf-8') as f:
    f.write(xml_str)

print(f"Created .sob file: {sob_path}")
print(f"Size: {len(xml_str)} bytes")
print(f"Channels: {len(channels)}")
print(f"\nSample serviio link: {channels[0]['name']}")
print(f"  {serviio_link}")

# Try to import the .sob file
print("\n--- Trying to import .sob file ---")
with open(sob_path, 'rb') as f:
    content = f.read()

# Try PUT with application/xml (since server accepted that format before with errorCode:505)
try:
    req = urllib.request.Request(base + '/rest/import-export/online', method='PUT')
    req.add_header('Content-Type', 'application/xml')
    req.add_header('Accept', 'application/json')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header('Origin', base)
    req.add_header('Referer', 'http://192.168.1.5:23423/console/#/app/library/online')
    req.data = content
    r = urllib.request.urlopen(req, timeout=15)
    body = r.read().decode('utf-8', errors='replace')[:500]
    print(f"  PUT application/xml: {r.status} -> {body[:300]}")
except urllib.error.HTTPError as e:
    try:
        body = e.read().decode('utf-8', errors='replace')[:500]
        print(f"  PUT application/xml: {e.code} -> {body[:300]}")
    except:
        print(f"  PUT application/xml: {e.code}")

# Try PUT with text/xml
try:
    req = urllib.request.Request(base + '/rest/import-export/online', method='PUT')
    req.add_header('Content-Type', 'text/xml')
    req.add_header('Accept', 'application/json')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header('Origin', base)
    req.add_header('Referer', 'http://192.168.1.5:23423/console/#/app/library/online')
    req.data = content
    r = urllib.request.urlopen(req, timeout=15)
    body = r.read().decode('utf-8', errors='replace')[:500]
    print(f"  PUT text/xml: {r.status} -> {body[:300]}")
except urllib.error.HTTPError as e:
    try:
        body = e.read().decode('utf-8', errors='replace')[:500]
        print(f"  PUT text/xml: {e.code} -> {body[:300]}")
    except:
        print(f"  PUT text/xml: {e.code}")

# Try PUT with text/plain
try:
    req = urllib.request.Request(base + '/rest/import-export/online', method='PUT')
    req.add_header('Content-Type', 'text/plain')
    req.add_header('Accept', 'application/json')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header('Origin', base)
    req.add_header('Referer', 'http://192.168.1.5:23423/console/#/app/library/online')
    req.data = content
    r = urllib.request.urlopen(req, timeout=15)
    body = r.read().decode('utf-8', errors='replace')[:500]
    print(f"  PUT text/plain: {r.status} -> {body[:300]}")
except urllib.error.HTTPError as e:
    try:
        body = e.read().decode('utf-8', errors='replace')[:500]
        print(f"  PUT text/plain: {e.code} -> {body[:300]}")
    except:
        print(f"  PUT text/plain: {e.code}")

# Also try POST
try:
    req = urllib.request.Request(base + '/rest/import-export/online', method='POST')
    req.add_header('Content-Type', 'application/xml')
    req.add_header('Accept', 'application/json')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header('Origin', base)
    req.add_header('Referer', 'http://192.168.1.5:23423/console/#/app/library/online')
    req.data = content
    r = urllib.request.urlopen(req, timeout=15)
    body = r.read().decode('utf-8', errors='replace')[:500]
    print(f"  POST application/xml: {r.status} -> {body[:300]}")
except urllib.error.HTTPError as e:
    try:
        body = e.read().decode('utf-8', errors='replace')[:500]
        print(f"  POST application/xml: {e.code} -> {body[:300]}")
    except:
        print(f"  POST application/xml: {e.code}")
