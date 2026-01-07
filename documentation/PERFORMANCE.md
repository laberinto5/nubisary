# Performance Notes - Windows Executable Startup

## Problem: Slow Startup Time (30+ seconds)

The Windows `.exe` built with PyInstaller in one-file mode can take 30+ seconds to start, especially on first run. This is a known limitation of PyInstaller's one-file mode.

## Why Is It Slow?

### PyInstaller One-File Mode

In one-file mode, PyInstaller:
1. **Extracts everything** to a temporary directory on each execution
2. **Runs the Python interpreter** from the temporary directory
3. **Cleans up** when the application exits

With a 150-200 MB executable containing:
- Python interpreter
- All dependencies (matplotlib, wordcloud, numpy, etc.)
- All libraries and DLLs

This extraction process can take 10-30 seconds, especially:
- On slower hard drives (HDD vs SSD)
- When Windows Defender/Antivirus scans the extracted files
- On first run (cold start)

## Solutions

### Option 1: Disable UPX Compression (Already Applied)

UPX compression can trigger antivirus false positives and slow startup. The spec file now has `upx=False`.

### Option 2: Add to Windows Defender Exclusions

This can significantly improve startup time:

1. Open **Windows Security**
2. Go to **Virus & threat protection**
3. Click **Manage settings** under Virus & threat protection settings
4. Scroll to **Exclusions** → Click **Add or remove exclusions**
5. Add:
   - The `nubisary.exe` file itself
   - The folder containing it
   - Optionally: `C:\Users\<YourUser>\AppData\Local\Temp` (if you want to exclude all temp extractions)

### Option 3: Use One-Folder Mode (Faster Startup)

One-folder mode doesn't extract on each run, so startup is much faster (1-3 seconds):

**Trade-offs:**
- ✅ Faster startup (1-3 seconds vs 30+ seconds)
- ✅ Better for frequent use
- ❌ Multiple files to distribute (folder with .exe + dependencies)
- ❌ Less convenient for users (need to distribute a folder, not just one file)

**To use one-folder mode:**

Edit `nubisary_gui.spec` and change the `EXE` section:

```python
# Option A: Keep one-file (current, slower startup but single file)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],  # Empty list = one-file mode
    ...
)

# Option B: Switch to one-folder (faster startup, multiple files)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,  # Don't bundle binaries in .exe
    name='nubisary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='nubisary',
)
```

Then distribute the entire `dist/nubisary/` folder (not just the .exe).

### Option 4: Use SSD (Hardware)

If the user has the executable on an SSD instead of HDD, startup will be significantly faster (5-10 seconds instead of 30+).

### Option 5: First Run vs Subsequent Runs

- **First run**: Slowest (30+ seconds) - extraction + antivirus scan
- **Subsequent runs**: Faster (15-20 seconds) - Windows may cache some things
- **With antivirus exclusion**: Much faster (5-10 seconds)

## Recommendation

**For end users (non-technical):**
- Keep one-file mode (single file is easier)
- Recommend adding to Windows Defender exclusions
- Accept that first startup may be slow
- Note that once running, the application is fast

**For power users or frequent use:**
- Consider one-folder mode for faster startup
- Or use the CLI version (`nubisary.py`) which starts instantly

## Current Configuration

The spec file is currently configured for:
- ✅ One-file mode (single .exe file)
- ✅ UPX disabled (faster startup, fewer antivirus issues)
- ✅ Windowed mode (no console)

This provides the best user experience (single file) with reasonable performance after the first startup.

## Alternative: Code Signing

Signing the executable with a code signing certificate can:
- Reduce Windows warnings
- Potentially improve startup time (less aggressive scanning)
- Increase user trust

However, code signing certificates cost money ($100-500/year) and require verification, so this is typically only done for commercial software.

