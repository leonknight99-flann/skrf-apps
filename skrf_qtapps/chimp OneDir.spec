# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('.skrf_qtwidgets')
hiddenimports.append('skrf_qtwidgets.analyzers')
hiddenimports.append('skrf_qtwidgets.analyzers.analyzers_cmt')

a = Analysis(
    ['chimp.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\lkni\\Documents\\Code Files\\scikit-rf GIT and APP\\skrf-apps\\skrf_qtapps\\skrf_qtwidgets\\images\\FlannMicrowave.ico', '.')
           ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    debug='imports'
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Chimp v0.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
