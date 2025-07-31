# hook-analyzers.py
# This file is used to collect hidden imports for the skrf_qtwidgets.analyzers

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('analyzers')

print(f"Collecting hidden imports: {hiddenimports}")    

for import_name in hiddenimports:
    print(f"Collecting hidden import: {import_name}")