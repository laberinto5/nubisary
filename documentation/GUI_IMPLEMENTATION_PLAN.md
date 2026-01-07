# GUI Implementation Plan - Nubisary

## Overview

This document outlines the plan to create a desktop GUI application using Tkinter and package it as a standalone executable with PyInstaller for Windows (and optionally Linux) distribution.

## Objectives

- Create a simple, functional GUI for non-technical users
- Package as standalone .exe (no installation required)
- Maintain existing CLI functionality
- Keep architecture clean (GUI uses same service layer as CLI)

---

## Phase 1: Project Structure

### Directory Organization

```
nubisary/
├── src/                    # Core modules (no changes)
├── gui/                    # NEW: GUI module
│   ├── __init__.py
│   ├── main.py            # Main window
│   └── widgets.py         # Custom widgets (if needed)
├── nubisary.py            # CLI (existing)
├── nubisary_gui.py        # NEW: GUI entry point
├── requirements.txt
└── nubisary_gui.spec      # NEW: PyInstaller spec file
```

---

## Phase 2: GUI Design

### Main Window Components

#### Layout Structure (vertical flow):

1. **Input Section**
   - File selection button + path display
   - File type indicator (Text/PDF/DOCX/JSON)
   - Language selector (dropdown)

2. **Processing Options Section**
   - Checkboxes: Include stopwords, Case sensitive, Collocations, Normalize plurals, Include numbers
   - Min word length (spinbox)
   - Max words (spinbox)

3. **Visual Customization Section**
   - Theme selector (dropdown with 34 themes)
   - Canvas size (width x height spinboxes)
   - Relative scaling (slider)
   - Prefer horizontal (slider)

4. **Advanced Options (Collapsible/Optional)**
   - Custom colors (Background/Font color inputs)
   - Colormap selector
   - Mask file selection
   - Contour options (if mask selected)
   - Custom font path
   - Export statistics checkbox

5. **Action Buttons**
   - "Generate Word Cloud" (primary button)
   - Progress bar/status label

6. **Output Section**
   - Output file path display
   - "Save As..." button
   - Preview area (image display)

---

## Phase 3: Implementation Steps

### Step 1: Create GUI Module Structure
1. Create `gui/` directory
2. Create `gui/__init__.py`
3. Create `gui/main.py` with basic window structure
4. Create `nubisary_gui.py` entry point

### Step 2: Implement Basic Window
- Basic Tkinter window with title and geometry
- Menu bar (optional)
- Status bar

### Step 3: Implement Input Section
- File selection dialog (`filedialog.askopenfilename`)
- Language dropdown (`ttk.Combobox` with languages from config)
- File type detection (from file extension)

### Step 4: Implement Options Sections
- Checkboxes for boolean options
- Spinboxes for numeric inputs
- Theme dropdown (populate from `list_themes()`)
- Color inputs (Entry widgets with hex validation)

### Step 5: Implement Generate Logic
- Collect all inputs from GUI
- Create `WordCloudConfig` object
- Call `generate_wordcloud()` from service layer
- Handle errors gracefully with user-friendly messages
- Display preview/result

### Step 6: Implement Preview/Display
- Use PIL `ImageTk` to display PNG in GUI
- Update preview when word cloud is generated
- Handle image resizing for display

### Step 7: Error Handling & Validation
- Validate file paths before processing
- Validate color codes (hex format)
- Show user-friendly error messages in dialogs
- Disable/enable buttons based on state

---

## Phase 4: PyInstaller Packaging

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Create Spec File

Create `nubisary_gui.spec` with proper configuration for:
- Hidden imports (PIL, matplotlib, wordcloud, nltk, etc.)
- NLTK data handling
- One-file executable mode
- No console window (windowed mode)

### Step 3: Handle NLTK Data

**Recommended approach**: Download at runtime on first run
- Check for NLTK data on startup
- Download if missing (with user prompt/notification)
- Smaller executable, requires internet on first run
- Alternative: Bundle minimal NLTK data (punkt, stopwords for common languages)

### Step 4: Build Executable
```bash
# Basic build
pyinstaller --onefile --windowed nubisary_gui.py

# With spec file (recommended)
pyinstaller nubisary_gui.spec
```

### Step 5: Test Executable
- Test on clean Windows machine (or VM)
- Verify all functionality works
- Check file size (~150-200 MB expected)
- Test error handling

---

## Phase 5: Technical Considerations

### Matplotlib Backend
Use TkAgg backend for GUI compatibility:
```python
import matplotlib
matplotlib.use('TkAgg')  # Must be before pyplot import
```

### Image Display in Tkinter
```python
from PIL import Image, ImageTk

img = Image.open(image_path)
img_tk = ImageTk.PhotoImage(img)
label = tk.Label(root, image=img_tk)
label.image = img_tk  # Keep reference
```

### Threading for Long Operations
Use threading to prevent GUI freeze during word cloud generation:
```python
import threading

def generate_in_thread(self):
    thread = threading.Thread(target=self._generate_wordcloud)
    thread.daemon = True
    thread.start()
    # Update GUI in main thread using root.after()
```

---

## Phase 6: Entry Point Example

### nubisary_gui.py

```python
#!/usr/bin/env python3
"""GUI entry point for Nubisary."""

import sys
import tkinter as tk

# Set matplotlib backend before any matplotlib imports
import matplotlib
matplotlib.use('TkAgg')

from gui.main import WordCloudGUI

def main():
    root = tk.Tk()
    app = WordCloudGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
```

### gui/main.py Structure

```python
"""Main GUI window for Nubisary."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import threading

from src.wordcloud_service import generate_wordcloud, WordCloudServiceError
from src.config import WordCloudConfig, LANGUAGES_FOR_NLTK
from src.themes import list_themes, get_theme

class WordCloudGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
    
    def setup_window(self):
        self.root.title("Nubisary - Word Cloud Generator")
        self.root.geometry("900x1000")
    
    def setup_variables(self):
        # Initialize all tkinter variables
        pass
    
    def create_widgets(self):
        # Create all UI components
        pass
    
    def on_select_file(self):
        # File selection logic
        pass
    
    def on_generate(self):
        # Generate word cloud logic
        pass
```

---

## Phase 7: Distribution

### Build Process
1. Build executable: `pyinstaller nubisary_gui.spec`
2. Test thoroughly on clean Windows system
3. Package as single .exe file (one-file mode)

### File Size Expectations
- **One-file mode**: ~150-200 MB
- **Distribution**: Single .exe file

### Distribution Channels
- GitHub Releases (recommended)
- Direct download link

---

## Implementation Timeline

### Week 1: Basic GUI
- Day 1-2: Set up structure, basic window
- Day 3-4: Input section, file dialogs
- Day 5: Options sections (basic)

### Week 2: Core Functionality
- Day 1-2: Generate logic integration
- Day 3: Preview/image display
- Day 4: Error handling
- Day 5: Polish and testing

### Week 3: Packaging
- Day 1-2: PyInstaller setup and configuration
- Day 3: NLTK data handling
- Day 4: Build and test executable
- Day 5: Documentation and final testing

---

## Notes

- Keep GUI code separate from core logic (already done!)
- GUI should only call `wordcloud_service.generate_wordcloud()`
- All business logic stays in `src/` modules
- CLI remains unchanged and functional
- Start simple, iterate and improve

