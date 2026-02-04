---
title: Nubisary
emoji: ☁️
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "6.3.0"
app_file: app.py
pinned: false
---

# Nubisary

**Nubisary** is a powerful and flexible word cloud generator that creates beautiful word clouds from text, PDF, DOCX, or JSON files. It offers both command-line and graphical interfaces, making it accessible for users of all technical levels.

## Features

- **Multiple Input Formats**: Process text files, PDFs, DOCX documents, or JSON frequency data
- **38+ Preset Themes**: Beautiful color combinations for instant visual appeal (including custom colormaps)
- **Advanced Text Processing**: 
  - Exclude specific words or phrases
  - Apply regex transformations for complex text filtering
  - Automatic text cleaning for converted documents
-  - Lematize words to their base form
-  - N-gram frequency mode (unigram or bigram)
- **Flexible Customization**:
  - Custom colors and colormaps
  - Mask images for custom shapes
  - Font selection
  - Canvas size control
- **Vocabulary Export**: Export word frequencies to JSON and CSV
- **Vocabulary Report**: Human-readable TXT reports in English and Spanish
- **Multi-language Support**: End-to-end support for English, Spanish, French, German, Italian, Portuguese (see `documentation/LANGUAGE_SUPPORT.md`)
- **Dual Interface**: 
  - Command-line tool for automation and advanced users
  - Graphical user interface for ease of use

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

**Command-line:**
```bash
python nubisary.py generate -i document.pdf -l english --theme vibrant
```
```bash
python nubisary.py generate -i document.pdf -l english --report
```
```bash
python nubisary.py analyze -i document.pdf -l english
```

**GUI:**
```bash
python nubisary_gui.py
```

**Web (Gradio, local):**
```bash
python app.py
```

## Documentation

- **[CLI Documentation](documentation/CLI.md)** - Complete guide to the command-line interface
- **[GUI Documentation](documentation/GUI.md)** - Guide to the graphical user interface
- **[Web App (Gradio) Deploy](documentation/GRADIO_WEB_DEPLOY.md)** - Local and Hugging Face deployment guide
- **[Themes & Custom Themes](documentation/THEMES.md)** - Built-in themes and custom JSON themes
- **[Text Processing Workflow](documentation/WORKFLOW.md)** - High-level flow and transformation steps
- **[Packaging](documentation/PACKAGING.md)** - Build and packaging options
- **[Performance](documentation/PERFORMANCE.md)** - Performance considerations and optimization
- **[Language Support](documentation/LANGUAGE_SUPPORT.md)** - Stopwords vs lemmatization coverage

## Web App (Hugging Face)

The Gradio web app can be deployed to Hugging Face Spaces.
Space: https://huggingface.co/spaces/laberintos/nubisary  
The public app URL is shown in the Space once the build finishes.

## Requirements

- Python 3.10+
- See [requirements.txt](requirements.txt) for full dependency list

## Notes

If you find an issue or have suggestions, please open an issue on GitHub.
