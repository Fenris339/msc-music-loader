# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Добавляем src в путь для поиска модулей
sys.path.insert(0, os.path.join(os.path.dirname(__name__), 'src'))

block_cipher = None

a = Analysis(
    ['src/main.py'],  # Указываем правильный путь к основному файлу
    pathex=[os.path.join(os.path.dirname(__name__), 'src')],  # Добавляем src в пути поиска
    binaries=[],
    datas=[
        ('src/settings.py', '.'),
        ('src/yandex_api.py', '.'),
        ('src/utils', 'utils')
    ],
    hiddenimports=[
        'settings',
        'yandex_api',  # PyInstaller преобразует дефисы в подчеркивания
        'utils.get_token'
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
    name='msc-music-loader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)