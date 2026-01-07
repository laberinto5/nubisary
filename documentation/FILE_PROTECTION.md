# File Protection in One-Folder Mode

## Current Protection Level

PyInstaller already provides some protection:

1. **Compiled Python code**: `.py` files are compiled to `.pyc` (bytecode)
2. **Archived libraries**: Dependencies are packaged in `.pyz` archives
3. **Binary format**: Not easily readable as plain text
4. **Requires tools**: Modification requires PyInstaller, decompilers, or hex editors

**However**: Determined users with technical knowledge can still:
- Decompile `.pyc` files back to readable Python
- Modify DLLs and binaries
- Replace files in the folder

## PyInstaller Encryption Option (--key)

PyInstaller supports bytecode encryption using the `--key` parameter. This encrypts Python bytecode before storing it in the executable.

### How to Enable

1. **Install PyInstaller with encryption support**:
   ```bash
   pip install pyinstaller[encryption]
   ```

2. **Generate a 16-character key** (or use a longer key for AES-192/256)

3. **Edit the spec file** to enable encryption:
   ```python
   # In nubisary_gui_folder.spec, uncomment and set:
   from PyInstaller.utils import crypto as pyi_crypto
   block_cipher = pyi_crypto.PyiBlockCipher('Your16CharKey!!')
   ```

4. **Rebuild** the executable

### Limitations

⚠️ **Important**: This provides **obfuscation**, not real security:
- The decryption key is embedded in the executable
- Determined users can extract the key through reverse engineering
- Makes casual modification harder, but not impossible
- Does NOT prevent modification, only makes it more difficult

### When to Use

- ✅ To deter casual file modification
- ✅ To make reverse engineering slightly harder
- ❌ NOT for protecting sensitive code/algorithms
- ❌ NOT for preventing determined attackers

## Alternative: Integrity Checking

Detect if files have been modified (doesn't prevent, but detects):

```python
# Add to your application startup code
import hashlib
import os
import sys

def verify_integrity():
    """Check if critical files have been modified."""
    # Compute checksums of critical files at build time
    # Store in a separate file or embed in code
    expected_checksums = {
        'nubisary.exe': 'abc123...',  # Replace with actual hash
        # Add other critical files
    }
    
    base_dir = os.path.dirname(sys.executable)
    for file, expected_hash in expected_checksums.items():
        file_path = os.path.join(base_dir, file)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            if actual_hash != expected_hash:
                from tkinter import messagebox
                messagebox.showerror(
                    "Integrity Check Failed",
                    "Application files have been modified. Please reinstall from original source."
                )
                sys.exit(1)
```

**Limitations**:
- Can be bypassed by modifying the check itself
- Requires maintaining checksums for each build
- User experience: shows error if files are modified

## Recommendation for Nubisary

### For Most Use Cases

**PyInstaller's default protection is sufficient**:
- Most users won't modify files (they just want to use the program)
- Modification requires technical knowledge and tools
- No performance impact
- No additional complexity

### If You Need Additional Protection

**Option 1: Use PyInstaller encryption** (`--key`)
- Provides obfuscation (makes modification harder)
- Easy to enable in spec file
- Understand it's not real security

**Option 2: Use one-file mode instead**
- Files extracted to temp directory (harder to find)
- Cleaned up after execution
- More difficult for casual users to access

**Option 3: Accept the risk**
- For free/open source software, file modification is usually not a major concern
- Technical users who modify files are likely developers who could benefit from seeing the code

## Real-World Perspective

**What users typically do**:
- ✅ Double-click `nubisary.exe` and use it
- ✅ Don't look inside folders
- ✅ Don't have tools/knowledge to decompile

**What technical users could do**:
- Could modify files even with encryption (reverse engineering)
- Would need a good reason to do so (curiosity, customization, learning)
- For open source software, this might actually be desirable

**Conclusion**: For Nubisary (a free word cloud generator), default protection is likely sufficient. If you want to add encryption for peace of mind, it's easy to enable but understand its limitations.
