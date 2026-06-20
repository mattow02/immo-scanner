# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

datas = []
hiddenimports = ['lxml', 'lxml.etree', 'lxml._elementpath', 'cloudscraper', 'requests_toolbelt', 'charset_normalizer', 'immo_scanner.scrapers.leboncoin', 'immo_scanner.scrapers.seloger', 'immo_scanner.scrapers.bienici', 'immo_scanner.scrapers.pap', 'immo_scanner.scrapers.laforet', 'immo_scanner.scrapers.orpi', 'immo_scanner.scrapers.figaro']
datas += collect_data_files('fake_useragent')
datas += collect_data_files('curl_cffi')
datas += collect_data_files('playwright_stealth')
datas += collect_data_files('certifi')
hiddenimports += collect_submodules('fake_useragent')
hiddenimports += collect_submodules('curl_cffi')
hiddenimports += collect_submodules('playwright_stealth')
hiddenimports += collect_submodules('certifi')


a = Analysis(
    ['immo_scanner/cli.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'test'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='immo-scanner',
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
