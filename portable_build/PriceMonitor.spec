# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\CursorProjects\\Coffee machines price scrapper\\portable_build\\gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\CursorProjects\\Coffee machines price scrapper\\portable_build\\config', 'config')],
    hiddenimports=['selenium', 'bs4', 'pandas', 'openpyxl', 'docx', 'win32com', 'tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='PriceMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
