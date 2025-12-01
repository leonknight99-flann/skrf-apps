# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['flannalyser.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\lkni\\Documents\\Code Files\\scikit-rf GIT and APP\\skrf-apps\\skrf_qtapps\\skrf_qtwidgets\\images\\FlannMicrowave.ico', '.'),
           ('C:\\Users\\lkni\\Documents\\Code Files\\scikit-rf GIT and APP\\skrf-apps\\skrf_qtapps\\skrf_qtwidgets\\analyzers', '.\\skrf_qtwidgets\\analyzers')],
    hiddenimports=['pyvisa_py', 'pyvisa', 'gpib_ctypes'],
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
    name='Flannalyser v0.2',
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
    icon=['flannalyser.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Flannalyser v0.2',
)
