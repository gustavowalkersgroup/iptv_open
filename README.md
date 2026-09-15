# IPTV Brasil 2026

Lista de canais IPTV brasileira e internacional (BR + EN) com streams testados e funcionando.

## 📋 O que tem aqui

- **949 canais** (597 BR + 352 EN) filtrados e deduplicados
- **Teste de liveness**: 99.5% BR online, 90.6% EN online
- **Playlists M3U** prontas para uso
- **Arquivo .sob** para importação no Serviio
- **App Android** (APK) - WebView para o servidor web
- **App Windows** (EXE) - Player nativo com VLC
- **Servidor Web** (Flask) - API REST + Interface web

## 🚀 Downloads

| Plataforma | Arquivo | Tamanho |
|------------|---------|---------|
| Android | [IPTV-Brasil-2026.apk](.github/IPTV-Brasil-2026.apk) | 12 KB |
| Windows | [IPTV-Brasil-2026.exe](dist/IPTV-Brasil-2026.exe) | 26 MB |
| Playlist BR+EN | [Canais_BR_EN_Filtrado.m3u8](filtered/Canais_BR_EN_Filtrado.m3u8) | - |
| Playlist BR | [Canais_BR_Filtrado.m3u8](filtered/Canais_BR_Filtrado.m3u8) | - |
| Playlist EN | [Canais_EN_Filtrado.m3u8](filtered/Canais_EN_Filtrado.m3u8) | - |
| Serviio | [IPTV-Brasil-2026.sob](filtered/IPTV-Brasil-2026.sob) | - |

## 📺 Como usar

### Android
1. Baixe o `IPTV-Brasil-2026.apk`
2. Instale no dispositivo (permita fontes desconhecidas)
3. Abra o app - carrega automaticamente do servidor

### Windows
1. Baixe o `IPTV-Brasil-2026.exe`
2. Execute - VLC já vem embutido
3. Use filtros BR/EN, busca, proteção de conteúdo adulto (senha: `0000`)

### VLC / IPTV Players
Use a playlist direta: `filtered/IPTV-Brasil-VLC.m3u8`

### Serviio
1. Acesse o console: `http://SEU_IP:23423/console`
2. Online Content → Import → Selecione `IPTV-Brasil-2026.sob`

### Servidor Web (Auto-hospedado)
```bash
pip install flask flask-cors customtkinter python-vlc
python iptv_server.py
# Acesse http://localhost:8080
```

## 🔧 Scripts incluídos

| Script | Função |
|--------|--------|
| `filter.py` | Parseia M3U, categoriza, filtra BR/EN, remove filmes/séries |
| `test_urls.py` | Testa liveness de streams (HEAD requests) |
| `combine.py` | Une playlists BR + EN |
| `create_sob.py` | Gera .sob para Serviio |
| `iptv_server.py` | Servidor Flask com API REST + Web UI |
| `iptv_app.py` | App desktop CustomTkinter + VLC |

## 📊 Estatísticas

- **Total canais originais**: 1.076.787
- **Após filtro BR/EN + dedup**: 949 únicos
- **BR online**: 594/597 (99.5%)
- **EN online**: 319/352 (90.6%)
- **Rejeitados (internacionais)**: 41.000+

## ⚠️ Aviso Legal

> **Todos os streams foram coletados da internet.** Este projeto apenas organiza, filtra e disponibiliza. Não hospedamos, transmitimos ou re-transmitimos qualquer sinal. Use por sua conta e risco.

## 📝 Licença

Uso pessoal e educacional. Streams pertencem aos seus respectivos proprietários.

---

*Gerado em Set/2026 - Filtragem automática + teste de liveness*