# Packaging & Build Options (Nubisary GUI)

This guide consolidates how to build and package the GUI with PyInstaller.

## Prerequisites

- Python 3.8+
- Dependencies from `requirements.txt`
- PyInstaller: `pip install pyinstaller`
- Linux/WSL: `python3-tk` (`sudo apt-get install python3-tk`)
- Windows: tkinter comes with Python

## Build Rules

- PyInstaller does **not** cross-compile. Build on the target OS.
- Windows builds must be done on Windows; Linux builds on Linux.

## Build Commands

### One-file (recommended for most users)

```bash
pyinstaller nubisary_gui.spec
```

### One-folder (faster startup)

```bash
pyinstaller nubisary_gui_folder.spec
```

Outputs:
- **Windows**: `dist/nubisary.exe` (one-file) or `dist/nubisary/` (one-folder)
- **Linux**: `dist/nubisary` (one-file) or `dist/nubisary/` (one-folder)

## One-file vs One-folder

| Feature | One-file | One-folder |
|---------|----------|------------|
| Startup time | 30+ seconds | 1–3 seconds |
| Distribution | Single file | Folder (can be zipped) |
| User simplicity | Highest | Slightly lower |
| Size | ~150–200 MB | ~150–200 MB (total) |

## NLTK Data

Default: download `punkt` and `stopwords` at first run (smaller build).

To bundle data:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

Then uncomment the NLTK bundling section in `nubisary_gui.spec` and rebuild.

## Test the Executable

### Windows

1. Build on Windows or download the GitHub Actions artifact.
2. Run `dist/nubisary.exe` on a clean machine/VM.

### Linux

```bash
chmod +x dist/nubisary
./dist/nubisary
```

## Troubleshooting (Quick)

- **Failed to execute script**: missing dependency or hidden import.
- **Missing modules**: add to `hiddenimports` in `nubisary_gui.spec`.
- **Large size**: expected (includes Python + matplotlib + deps).
- **NLTK download fails**: bundle data as above.

## Distribution Tips

- Provide both builds if possible (one-file + one-folder).
- Include a short README (requirements + basic usage).
- Windows Defender may warn; code signing helps for production.

## Build Artifacts

```
nubisary/
├── build/          # Temporary build files (safe to delete)
├── dist/           # Final executables
│   └── nubisary    # or nubisary.exe on Windows
└── nubisary_gui.spec
```

