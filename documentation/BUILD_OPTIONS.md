# Build Options - One-File vs One-Folder

Nubisary supports two packaging modes for Windows:

## One-File Mode (`nubisary_gui.spec`)

**Output**: Single `nubisary.exe` file (~150-200 MB)

### Advantages ✅
- **Easy distribution**: Just one file to download and share
- **Simple for users**: Double-click and run
- **Clean**: No folder clutter

### Disadvantages ⚠️
- **Slow startup**: 30+ seconds on first run (extracts to temp directory)
- **Antivirus scanning**: Windows Defender scans extracted files
- **Disk I/O**: Extracts 150-200 MB on each execution

### Best For
- Distribution to non-technical users
- Occasional use
- When simplicity is priority

---

## One-Folder Mode (`nubisary_gui_folder.spec`)

**Output**: `nubisary/` folder with `nubisary.exe` + dependencies (~150-200 MB total)

### Advantages ✅
- **Fast startup**: 1-3 seconds (no extraction needed)
- **Better performance**: Files already on disk
- **Antivirus friendly**: Less scanning (files already extracted)

### Disadvantages ⚠️
- **Multiple files**: Need to distribute a folder (can be zipped)
- **Less convenient**: Users need to extract a ZIP file
- **Folder structure**: More complex for non-technical users

### Best For
- Power users
- Frequent use
- When startup speed is priority

---

## Comparison

| Feature | One-File | One-Folder |
|---------|----------|------------|
| Startup time | 30+ seconds | 1-3 seconds |
| Distribution | Single .exe | Folder (can ZIP) |
| User experience | Very simple | Slightly more complex |
| File count | 1 file | Many files |
| Size | ~150-200 MB | ~150-200 MB (total) |

---

## Building Both Versions

### Local Build

```bash
# Build one-file version
pyinstaller nubisary_gui.spec
# Output: dist/nubisary.exe

# Build one-folder version
pyinstaller nubisary_gui_folder.spec
# Output: dist/nubisary/ folder
```

### GitHub Actions

The workflow builds both versions automatically:
- **Artifact 1**: `nubisary-windows-onefile` - Single .exe file
- **Artifact 2**: `nubisary-windows-folder` - ZIP file with folder contents

---

## Distribution Recommendation

### For Most Users (Recommended)
- **One-file mode**: Easier to download and use
- Users can add to Windows Defender exclusions to improve startup time
- Accept that first startup may take 30 seconds

### For Power Users
- **One-folder mode**: Much faster startup
- Provide as ZIP file with instructions to extract
- Users can add the folder to Windows Defender exclusions

### Provide Both (Ideal)
- Let users choose based on their preference
- Document the trade-offs
- Power users can use folder version, casual users can use single file

## File Protection Considerations

**Note on file modification**: In one-folder mode, files are visible and could theoretically be modified. However:
- PyInstaller compiles Python code to bytecode (not easily readable)
- Dependencies are archived (harder to modify)
- Most users won't modify files (they just want to use the program)
- Modification requires technical knowledge and tools

If file protection is a concern:
- Consider using **one-file mode** (files extracted to temp directory)
- See `documentation/FILE_PROTECTION.md` for detailed discussion of protection options

---

## Switching Between Modes

To switch between modes, simply use the appropriate spec file:

```bash
# One-file mode
pyinstaller nubisary_gui.spec

# One-folder mode  
pyinstaller nubisary_gui_folder.spec
```

Both spec files are configured identically, just with different `EXE` settings.

