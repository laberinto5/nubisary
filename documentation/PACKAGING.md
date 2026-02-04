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

```bash
pyinstaller nubisary_gui.spec
```

Outputs:
- **Windows**: `dist/nubisary.exe`
- **Linux**: `dist/nubisary`

The executable is built as a single file for easier distribution. First startup may take 30+ seconds as the application unpacks temporary files.

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

- Include a short README (requirements + basic usage).
- Windows Defender may warn; code signing helps for production.
- First startup may be slower (30+ seconds) as the application unpacks temporary files.

## Build Artifacts

```
nubisary/
├── build/          # Temporary build files (safe to delete)
├── dist/           # Final executables
│   └── nubisary    # or nubisary.exe on Windows
└── nubisary_gui.spec
```

