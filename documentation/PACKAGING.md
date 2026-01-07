# Packaging Guide - Nubisary GUI

This document describes how to build standalone executables for the Nubisary GUI application using PyInstaller.

## Prerequisites

### For Building Executables

- Python 3.8+ installed
- All dependencies from `requirements.txt` installed
- PyInstaller installed: `pip install pyinstaller`
- For Linux/WSL: `python3-tk` package installed (`sudo apt-get install python3-tk`)
- For Windows: tkinter comes with Python

### For Users (No Prerequisites Needed)

- **No Python installation required**
- **No dependencies required**
- Just download and run the executable

## Building Executables

**Important**: PyInstaller cannot cross-compile. You must build executables on the target platform:
- **Windows .exe**: Build on Windows
- **Linux binary**: Build on Linux

### Option 1: Build on Windows (Direct)

If you have Windows available:

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build executable (one-file mode)
pyinstaller nubisary_gui.spec
```

The executable will be created in the `dist/` directory as `nubisary.exe`.

### Option 2: Build with GitHub Actions (Recommended)

Use the GitHub Actions workflow to automatically build Windows executables:

1. Push your code to GitHub
2. Go to Actions tab
3. Select "Build Windows Executable" workflow
4. Click "Run workflow"
5. Download the artifact when complete

The workflow can also be triggered by:
- Creating a release
- Pushing a version tag (v1.0.0, etc.)
- Manual workflow dispatch

### Build Options

The `nubisary_gui.spec` file is already configured with recommended settings:

- **One-file mode**: Single executable file (easier distribution)
- **Windowed mode**: No console window (GUI application)
- **Hidden imports**: All necessary modules included
- **NLTK data**: Downloads at runtime (smaller executable)

### Build Output

#### One-File Mode (nubisary_gui.spec)

- **Windows**: `dist/nubisary.exe` (~150-200 MB) - Single executable file
  - ✅ Easy distribution (one file)
  - ⚠️ Slower startup (30+ seconds on first run)
  - ⚠️ Extracts to temp directory on each run

#### One-Folder Mode (nubisary_gui_folder.spec)

- **Windows**: `dist/nubisary/` folder (~150-200 MB total) - Multiple files
  - ✅ Fast startup (1-3 seconds)
  - ✅ No extraction needed
  - ⚠️ Requires distributing a folder (can be zipped)

#### Linux

- **Linux**: `dist/nubisary` (~150-200 MB) - Single executable file

## NLTK Data Handling

The executable is configured to download NLTK data on first run (punkt, stopwords). This keeps the executable smaller.

### Option 1: Runtime Download (Default)

- Smaller executable size
- Requires internet connection on first run
- Downloads only needed resources

### Option 2: Bundle NLTK Data

To include NLTK data in the executable (larger but fully self-contained):

1. Download NLTK data first:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

2. Edit `nubisary_gui.spec` and uncomment the NLTK data bundling section

3. Rebuild the executable

## Testing the Executable

### Windows

1. **If built locally**: The `dist/nubisary.exe` file is ready to use
2. **If built with GitHub Actions**: Download the artifact from the Actions tab
3. Copy to a clean Windows machine (or VM) - no Python or dependencies needed
4. Double-click `nubisary.exe` to run
5. Test all functionality

### Linux

1. Build on Linux: `pyinstaller nubisary_gui.spec`
2. Copy `dist/nubisary` to a clean Linux system
3. Make executable: `chmod +x nubisary`
4. Run: `./nubisary`

## Troubleshooting

### "Failed to execute script" Error

- Check that all dependencies are installed in the build environment
- Verify hidden imports in the spec file
- Try building with `--debug=all` for more information

### Large Executable Size

- Normal size: 150-200 MB (includes Python, all dependencies, matplotlib, etc.)
- To reduce size: Use `--onefile` mode is already optimized
- Exclude unnecessary modules in the spec file

### Missing Modules in Executable

- Add missing modules to `hiddenimports` in `nubisary_gui.spec`
- Rebuild the executable

### NLTK Data Issues

- If NLTK data download fails, bundle it in the executable (see above)
- Or provide instructions for users to download NLTK data manually

## Distribution

### Single Executable

Distribute just the `.exe` (Windows) or binary (Linux) file.

### With Documentation

Include a simple README with:
- System requirements
- Basic usage instructions
- Troubleshooting tips

### GitHub Releases

1. Build executable for target platform
2. Create a GitHub release
3. Attach the executable file
4. Add release notes

## Platform-Specific Notes

### Windows

- Executable should work on Windows 10 and Windows 11
- No additional dependencies needed
- May trigger Windows Defender (false positive) - code signing recommended for production

### Linux

- Tested on Ubuntu 24.04 LTS
- Should work on most modern Linux distributions
- May need to set executable permissions: `chmod +x nubisary`

## Build Directory Structure

After building:

```
nubisary/
├── build/          # Temporary build files (can be deleted)
├── dist/           # Final executables (distribute these)
│   └── nubisary    # or nubisary.exe on Windows
└── nubisary_gui.spec  # PyInstaller spec file
```

**Note**: The `build/` directory can be safely deleted after building. The `dist/` directory contains the final executables.

