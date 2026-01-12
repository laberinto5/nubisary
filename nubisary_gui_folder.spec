# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Nubisary GUI application (one-folder mode).
This creates a folder with multiple files - faster startup, but requires distributing a folder.
"""

import os
import sys
from pathlib import Path

# Encryption key (16 bytes for AES-128, 24 bytes for AES-192, or 32 bytes for AES-256)
# WARNING: This provides obfuscation, not real security. The key is embedded in the executable.
# Set to None to disable encryption, or provide a 16-character string
# Example: block_cipher = pyi_crypto.PyiBlockCipher('Your16CharKey!')
block_cipher = None  # Change to enable encryption (requires pyinstaller[encryption])

# Get the directory where this spec file is located
# PyInstaller executes spec files with exec(), so __file__ is not available
# We use the working directory (where pyinstaller is run from) as the base path
# This assumes the spec file and samples/ directory are in the same directory
spec_file_dir = os.getcwd()

# Determine if NLTK data should be included
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

# Include help documentation
help_files = [
    ('documentation/GUI_HELP_EN.md', 'documentation'),
    ('documentation/GUI_HELP_ES.md', 'documentation'),
]
datas.extend(help_files)

# Include favicon (for runtime icon changes if needed)
favicon_path = os.path.join(spec_file_dir, 'favicon.ico')
if os.path.exists(favicon_path):
    datas.append(('favicon.ico', '.'))

# Include preset masks from samples/masks/
masks_path = os.path.join(spec_file_dir, 'samples', 'masks')
if os.path.exists(masks_path):
    # Include all mask files (PNG, JPG, etc.) from samples/masks/
    mask_files = []
    for filename in os.listdir(masks_path):
        file_path = os.path.join(masks_path, filename)
        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']:
                mask_files.append(file_path)
    
    if mask_files:
        # Include masks directory with all mask files
        datas.append((masks_path, 'samples/masks'))
        print(f"Including {len(mask_files)} mask files in bundle")

# Include preset fonts from samples/fonts/
fonts_path = os.path.join(spec_file_dir, 'samples', 'fonts')
if os.path.exists(fonts_path):
    # Include all font files (TTF, OTF) from samples/fonts/
    font_files = []
    for filename in os.listdir(fonts_path):
        file_path = os.path.join(fonts_path, filename)
        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.ttf', '.otf']:
                font_files.append((file_path, 'samples/fonts'))
    
    if font_files:
        # Include fonts directory with all font files
        datas.append((fonts_path, 'samples/fonts'))
        print(f"Including {len(font_files)} font files in bundle")

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    # GUI related
    'customtkinter',  # Modern GUI framework
    'PIL._tkinter_finder',
    'PIL.ImageTk',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends.backend_agg',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.colorchooser',
    'tkcolorpicker',  # Enhanced color picker (optional, has fallback)
    
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
    
    # Matplotlib dependencies
    'pyparsing',
    'pyparsing.testing',
    'unittest',  # Needed by pyparsing.testing
    
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
    'src.custom_themes',
    'src.custom_colormaps',
    'src.resource_loader',
    'src.font_loader',
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
        # Note: Don't exclude 'unittest' - matplotlib/pyparsing needs it
        'pytest',
        'test',
        'tests',
        'doctest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# One-folder mode: executable + dependencies in separate files
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,  # Don't bundle binaries in .exe - this enables one-folder mode
    name='nubisary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX - can trigger antivirus false positives
    console=False,  # No console window for GUI (windowed mode)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',  # Application icon  # Can add icon file path here: 'path/to/icon.ico'
    version='version_info.txt',  # Windows version info (metadata)
    manifest='app.manifest',  # Windows manifest (UAC, DPI awareness, compatibility)
)

# Collect all files into a folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='nubisary',  # Folder name will be 'nubisary'
)

