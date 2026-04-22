import sys
import os
from pathlib import Path

block_cipher = None

a = Analysis(
    ['mod_builder.py', 'updater.py'],
    pathex=[],
    binaries=[
        ('tools/KwasTools', 'tools/KwasTools'),
    ],
    datas=[
        ('tools', 'tools'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirected_variants=False,
    win_private_assembliesemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CrossWorlds Music Editor',
    debug=False,
    bootloader_ignore_binaries=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['tools/ico.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_compress=False,
    name='CrossWorlds Music Editor',
)