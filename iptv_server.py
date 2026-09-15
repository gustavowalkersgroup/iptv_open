#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean IPTV Server - reads .sob file, serves clean M3U and web UI."""
import os, re, sys, io, json, urllib.parse, urllib.request
from datetime import datetime
from flask import Flask, Response, render_template_string, request, stream_with_context

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

app = Flask(__name__)

# --- Parse .sob file ---
def parse_sob(sob_path):
    channels = []
    if not os.path.exists(sob_path):
        return channels
    with open(sob_path, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
    except:
        return channels
    for item in root.findall('.//backupItem'):
        serviio_link = item.find('serviioLink')
        if serviio_link is None or not serviio_link.text:
            continue
        match = re.match(r'serviio://(\w+):(\w+)\?(.+)', serviio_link.text)
        if not match:
            continue
        params = urllib.parse.parse_qs(match.group(3))
        url = params.get('url', [''])[0]
        name = urllib.parse.unquote(params.get('name', [''])[0])
        th_url = urllib.parse.unquote(params.get('thUrl', [''])[0]) if 'thUrl' in params else ''
        if url and name:
            channels.append({
                'name': name.strip(),
                'url': url,
                'type': match.group(1),
                'thumbnail': th_url,
                'order': int(item.get('order', '0'))
            })
    return sorted(channels, key=lambda x: x['order'])

# --- Load channels ---
sob_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'filtered', 'IPTV-Brasil-2026.sob')
channels = parse_sob(sob_path)

def get_br_names():
    br_kw = ['brasil','brazil','canal br','ipbr','grupo band','globo','sbt','record','band','rede','canais brasil','nacionais','bandeirantes','tv aberto','tv brasileira']
    return [c for c in channels if any(kw in c['name'].lower() for kw in br_kw)]

def get_en_names():
    br_kw = ['brasil','brazil','canal br','ipbr','grupo band','globo','sbt','record','band','rede','canais brasil','nacionais','bandeirantes','tv aberto','tv brasileira']
    return [c for c in channels if not any(kw in c['name'].lower() for kw in br_kw)]

br_list = get_br_names()
en_list = get_en_names()

print(f"Loaded {len(channels)} channels ({len(br_list)} BR, {len(en_list)} EN)")
print(f"Serving on http://0.0.0.0:8080")

# --- HTML Template ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Brasil 2026</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0a; color: #fff; }
        .header { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 20px; text-align: center; border-bottom: 2px solid #e94560; }
        .header h1 { font-size: 28px; color: #e94560; }
        .header p { color: #888; margin-top: 5px; }
        .stats { display: flex; justify-content: center; gap: 30px; margin-top: 15px; }
        .stat { background: #1a1a2e; padding: 10px 20px; border-radius: 8px; }
        .stat .num { font-size: 24px; color: #e94560; font-weight: bold; }
        .stat .label { font-size: 12px; color: #888; }
        .tabs { display: flex; justify-content: center; background: #1a1a2e; }
        .tab { padding: 12px 24px; cursor: pointer; color: #888; border-bottom: 3px solid transparent; transition: all 0.3s; }
        .tab:hover { color: #fff; }
        .tab.active { color: #e94560; border-bottom-color: #e94560; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .search { width: 100%; padding: 15px; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 16px; margin-bottom: 20px; }
        .search::placeholder { color: #666; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
        .card { background: #1a1a2e; border-radius: 10px; overflow: hidden; transition: transform 0.2s; border: 1px solid #2a2a4e; }
        .card:hover { transform: translateY(-2px); border-color: #e94560; }
        .card-thumb { width: 100%; height: 160px; background: #0d0d1a; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .card-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .card-thumb .no-img { color: #444; font-size: 48px; }
        .card-info { padding: 15px; }
        .card-info h3 { font-size: 14px; color: #fff; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .badge-br { background: #e94560; color: #fff; }
        .badge-en { background: #0f3460; color: #fff; }
        .card-info .url { font-size: 11px; color: #666; word-break: break-all; margin-top: 5px; }
        .play-btn { background: #e94560; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 13px; margin-top: 8px; }
        .play-btn:hover { background: #c73652; }
        .m3u-link { display: block; background: #e94560; color: #fff; text-align: center; padding: 15px; text-decoration: none; font-size: 18px; font-weight: bold; margin: 20px 0; border-radius: 8px; }
        .m3u-link:hover { background: #c73652; }
        .footer { text-align: center; padding: 20px; color: #444; font-size: 12px; }
        .footer a { color: #e94560; }
        .video-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 1000; display: none; }
        .video-container.show { display: block; }
        .video-container video { width: 100%; height: 100%; }
        .close-video { position: absolute; top: 10px; right: 15px; color: #fff; font-size: 30px; cursor: pointer; z-index: 1001; background: rgba(0,0,0,0.5); width: 40px; height: 40px; border-radius: 50%; text-align: center; line-height: 40px; }
        .filter-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .filter-btn { padding: 8px 16px; background: #1a1a2e; border: 1px solid #333; color: #888; border-radius: 20px; cursor: pointer; font-size: 13px; }
        .filter-btn.active { background: #e94560; color: #fff; border-color: #e94560; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📺 IPTV Brasil 2026</h1>
        <p>Servidor IPTV Local - Sem anúncios</p>
        <div class="stats">
            <div class="stat"><div class="num">{{ total }}</div><div class="label">Canais</div></div>
            <div class="stat"><div class="num">{{ br }}</div><div class="label">BR</div></div>
            <div class="stat"><div class="num">{{ en }}</div><div class="label">EN</div></div>
        </div>
    </div>
    <div class="tabs">
        <div class="tab active" onclick="showTab('all')">Todos</div>
        <div class="tab" onclick="showTab('br')">🇧🇷 BR</div>
        <div class="tab" onclick="showTab('en')">🇺🇸 EN</div>
    </div>
    <div class="container">
        <input type="text" class="search" id="search" placeholder="🔍 Buscar canal..." oninput="filterChannels()">
        <div class="filter-bar">
            <button class="filter-btn active" onclick="setFilter('all', this)">Todos</button>
            <button class="filter-btn" onclick="setFilter('BR', this)">BR</button>
            <button class="filter-btn" onclick="setFilter('EN', this)">EN</button>
        </div>
        <div id="channelGrid" class="grid"></div>
        <a href="/m3u" class="m3u-link">📋 Baixar Playlist M3U</a>
        <a href="/m3u/br" class="m3u-link" style="background:#0f3460">🇧🇷 M3U Apenas BR</a>
        <a href="/m3u/en" class="m3u-link" style="background:#0f3460">🇺🇸 M3U Apenas EN</a>
    </div>
    <div class="video-container" id="videoContainer">
        <span class="close-video" onclick="closeVideo()">✕</span>
        <video id="videoPlayer" controls autoplay></video>
    </div>
    <div class="footer">
        IPTV Server © 2026 | {{ total }} canais | <a href="/m3u">Baixar M3U</a>
    </div>
    <script>
        const channels = {{ channels|tojson }};
        let currentFilter = 'all';
        
        function showTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            currentFilter = tab;
            renderChannels();
        }
        
        function setFilter(f, btn) {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = f;
            renderChannels();
        }
        
        function isBR(c) {
            const n = c.name.toLowerCase();
            return ['brasil','brazil','canal br','ipbr','grupo band','globo','sbt','record','band','rede','canais brasil','nacionais','bandeirantes','tv aberto','tv brasileira'].some(k => n.includes(k));
        }
        
        function renderChannels() {
            const search = document.getElementById('search').value.toLowerCase();
            const grid = document.getElementById('channelGrid');
            let filtered = channels;
            if (currentFilter === 'br') filtered = filtered.filter(isBR);
            else if (currentFilter === 'en') filtered = filtered.filter(c => !isBR(c));
            if (search) filtered = filtered.filter(c => c.name.toLowerCase().includes(search));
            grid.innerHTML = filtered.map(c => `
                <div class="card">
                    <div class="card-thumb">
                        ${c.thumbnail ? `<img src="${c.thumbnail}" onerror="this.parentElement.innerHTML='<div class=\\'no-img\\'>📺</div>'">` : '<div class="no-img">📺</div>'}
                    </div>
                    <div class="card-info">
                        <h3>${c.name}</h3>
                        <span class="badge ${isBR(c) ? 'badge-br' : 'badge-en'}">${isBR(c) ? 'BR' : 'EN'}</span>
                        <div class="url">${c.url.substring(0, 60)}...</div>
                        <button class="play-btn" onclick="playChannel('${c.url.replace("'", "\\'").replace("\\\\", "\\\\\\\\")}')">▶ Assistir</button>
                    </div>
                </div>
            `).join('');
        }
        
        function filterChannels() { renderChannels(); }
        
        function playChannel(url) {
            const container = document.getElementById('videoContainer');
            const video = document.getElementById('videoPlayer');
            video.src = '/proxy?url=' + encodeURIComponent(url);
            container.classList.add('show');
            video.play();
        }
        
        function closeVideo() {
            document.getElementById('videoContainer').classList.remove('show');
            document.getElementById('videoPlayer').src = '';
        }
        
        renderChannels();
    </script>
</body>
</html>
'''

# --- Routes ---
@app.route('/')
def index():
    br_count = len(br_list)
    en_count = len(en_list)
    return render_template_string(HTML_TEMPLATE,
        total=len(channels), br=br_count, en=en_count, channels=channels)

@app.route('/m3u')
def m3u():
    m3u = '#EXTM3U\n'
    for c in channels:
        m3u += f'#EXTINF:-1 tvg-name="{c["name"]}",{c["name"]}\nhttp://127.0.0.1:8080/proxy?url={urllib.parse.quote(c["url"], safe="")}\n'
    return Response(m3u, mimetype='audio/x-mpegurl')

@app.route('/m3u/br')
def m3u_br():
    m3u = '#EXTM3U\n'
    for c in br_list:
        m3u += f'#EXTINF:-1 tvg-name="{c["name"]}",{c["name"]}\nhttp://127.0.0.1:8080/proxy?url={urllib.parse.quote(c["url"], safe="")}\n'
    return Response(m3u, mimetype='audio/x-mpegurl')

@app.route('/m3u/en')
def m3u_en():
    m3u = '#EXTM3U\n'
    for c in en_list:
        m3u += f'#EXTINF:-1 tvg-name="{c["name"]}",{c["name"]}\nhttp://127.0.0.1:8080/proxy?url={urllib.parse.quote(c["url"], safe="")}\n'
    return Response(m3u, mimetype='audio/x-mpegurl')

@app.route('/proxy')
def proxy():
    url = request.args.get('url', '')
    if not url:
        return Response('No URL', status=400)
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 IPTV-Client/1.0')
        req.add_header('Accept', '*/*')
        resp = urllib.request.urlopen(req, timeout=30)
        ct = resp.headers.get('Content-Type', 'video/mp2t')
        def gen():
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                yield chunk
        return Response(stream_with_context(gen()), mimetype=ct)
    except Exception as e:
        return Response(f'Error: {str(e)}', status=502)

@app.route('/api/channels')
def api_channels():
    return Response(json.dumps(channels, ensure_ascii=False), mimetype='application/json; charset=utf-8')

if __name__ == '__main__':
    print(f"\n{'='*50}")
    print(f"  IPTV BRASIL 2026 - LOCAL SERVER")
    print(f"{'='*50}")
    print(f"  📺 {len(channels)} canais ({len(br_list)} BR, {len(en_list)} EN)")
    print(f"  🌐 http://0.0.0.0:8080")
    print(f"  📋 http://0.0.0.0:8080/m3u")
    print(f"{'='*50}\n")
    app.run(host='0.0.0.0', port=8080, debug=False)
