# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Nubisary GUI application.
"""

import os
import sys
from pathlib import Path

block_cipher = None

# Determine if NLTK data should be included
# For now, we'll let NLTK download at runtime (smaller executable)
# If you want to bundle NLTK data, uncomment and modify the datas section below
nltk_data_path = None
try:
    import nltk
    nltk_data_dir = nltk.data.find('')
    if nltk_data_dir:
        nltk_data_path = os.path.dirname(nltk_data_dir)
except:
    pass

# Collect data files
datas = []
# Uncomment to bundle NLTK data (increases executable size significantly):
# if nltk_data_path and os.path.exists(nltk_data_path):
#     # Include only essential NLTK data (punkt, stopwords for common languages)
#     essential_nltk = [
#         ('tokenizers', os.path.join(nltk_data_path, 'tokenizers')),
#         ('corpora', os.path.join(nltk_data_path, 'corpora', 'stopwords')),
#     ]
#     for item in essential_nltk:
#         if os.path.exists(item[1]):
#             datas.append(item)

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    # GUI related
    'PIL._tkinter_finder',
    'PIL.ImageTk',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends.backend_agg',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    
    # Core dependencies
    'wordcloud',
    'wordcloud.wordcloud',
    'wordcloud.color_from_size',
    'nltk',
    'nltk.corpus',
    'nltk.corpus.stopwords',
    'nltk.tokenize',
    'nltk.tokenize.punkt',
    'nltk.data',
    'pypdf',
    'pypdf._reader',
    'pypdf._writer',
    'docx',
    'docx.shared',
    'docx.document',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    
    # Project modules
    'src',
    'src.config',
    'src.wordcloud_service',
    'src.wordcloud_generator',
    'src.text_processor',
    'src.file_handlers',
    'src.document_converter',
    'src.validators',
    'src.themes',
    'src.statistics_exporter',
    'src.logger',
    'gui',
    'gui.main',
]

a = Analysis(
    ['nubisary_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'pytest',
        'test',
        'tests',
        'unittest',
        'doctest',
    ],
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
    name='nubisary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression (if available)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI (windowed mode)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Can add icon file path here: 'path/to/icon.ico'
)

