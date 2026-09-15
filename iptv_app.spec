# -*- mode: python ; coding: utf-8 -*-
import os, sys, glob

block_cipher = None

vlc_src = 'C:/Program Files/VideoLAN/VLC'
sob_src = os.path.join(os.path.dirname(os.path.abspath('.')), 'filtered', 'IPTV-Brasil-2026.sob')

a = Analysis(
    ['iptv_app.py'],
    pathex=[],
    binaries=[
        (os.path.join(vlc_src, '*.dll'), 'vlc'),
        (os.path.join(vlc_src, '*.exe'), 'vlc'),
        (os.path.join(vlc_src, '*.dat'), 'vlc'),
        (os.path.join(vlc_src, '*.lua'), 'vlc'),
    ],
    datas=[
        (os.path.join(vlc_src, 'plugins/*'), 'vlc/plugins'),
        (os.path.join(vlc_src, 'libvlc.dll'), 'vlc'),
        (os.path.join(vlc_src, 'libvlccore.dll'), 'vlc'),
        (os.path.join(os.path.dirname(os.path.abspath('.')), 'filtered', 'IPTV-Brasil-2026.sob'), '.'),
    ],
    hiddenimports=[
        'customtkinter', 'ctk', 'vlc', 'xml.etree.ElementTree',
        'urllib.parse', 're', 'subprocess', 'tkinter',
        'darkdetect',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IPTV-Brasil-2026',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_serialization=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
