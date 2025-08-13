# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['chimp.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\lkni\\Documents\\Code Files\\scikit-rf GIT and APP\\skrf-apps\\skrf_qtapps\\skrf_qtwidgets\\images\\FlannMicrowave.ico', '.'),
           ('C:\\Users\\lkni\\Documents\\Code Files\\scikit-rf GIT and APP\\skrf-apps\\skrf_qtapps\\skrf_qtwidgets\\analyzers', '.\\skrf_qtwidgets\\analyzers')],
    hiddenimports=['pyvisa_py'],
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
    [],
    exclude_binaries=True,
    name='Chimp v0.1',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['waves.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Chimp v0.1',
)
