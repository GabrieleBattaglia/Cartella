# -*- mode: python ; coding: utf-8 -*-
# Cartella, ricetta di compilazione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode).
# Dalla 5.1.2 il pacchetto e' una cartella, dist\cartella, con l'eseguibile e
# _internal accanto: regola di Gabriele del 28 settembre 2026 per tutto il
# parco. Il file unico gira in due processi legati da variabili d'ambiente, e
# lo script di aggiornamento di GBUtils, nato dal secondo, le passava al
# programma rilanciato, che si fermava con "Security validation failure".
# La collezione dei suoni condivisa va portata dentro il pacchetto, altrimenti
# Acusticator non la trova e l'eseguibile resta muto. Il manuale README.txt
# invece sta accanto all'eseguibile, dove get_base_path lo cerca, e ce lo
# mette zip_maker.py.
import os

import GBUtils

COLLEZIONE = os.path.join(os.path.dirname(GBUtils.__file__), 'Acu_Collection.json')

a = Analysis(
    ['cartella.py'],
    pathex=[],
    binaries=[],
    datas=[(COLLEZIONE, '.')],
    # requests e compagni servono al controllo aggiornamenti di GBUtils:
    # senza, l'eseguibile parte ma non riesce a contattare GitHub.
    # scipy.signal lo importa Acusticator dentro le funzioni, quindi
    # PyInstaller non lo trova da solo: senza, l'eseguibile si chiude al
    # primo suono con ModuleNotFoundError. Non toglierli.
    hiddenimports=[
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'chardet',
        'scipy.signal',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5',
        'PySide2',
        'PySide6',
        'matplotlib',
        'IPython',
        'notebook',
        'nbconvert',
        'qtpy',
        'pytest',
        'tkinter',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='cartella',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cartella',
)
