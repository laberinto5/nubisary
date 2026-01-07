# Nubisary

**Nubisary** is a powerful and flexible word cloud generator that creates beautiful word clouds from text, PDF, DOCX, or JSON files. It offers both command-line and graphical interfaces, making it accessible for users of all technical levels.

## Features

- **Multiple Input Formats**: Process text files, PDFs, DOCX documents, or JSON frequency data
- **34 Preset Themes**: Beautiful color combinations for instant visual appeal
- **Advanced Text Processing**: 
  - Exclude specific words or phrases
  - Apply regex transformations for complex text filtering
  - Automatic text cleaning for converted documents
- **Flexible Customization**:
  - Custom colors and colormaps
  - Mask images for custom shapes
  - Font selection
  - Canvas size control
- **Statistics Export**: Export word frequencies to JSON and CSV
- **Multi-language Support**: Built-in stopword support for 23 languages
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

**GUI:**
```bash
python nubisary_gui.py
```

## Documentation

- **[CLI Documentation](documentation/CLI.md)** - Complete guide to the command-line interface
- **[GUI Documentation](documentation/GUI.md)** - Guide to the graphical user interface
- **[Themes](documentation/THEMES.md)** - Full documentation of all 34 preset themes
- **[Build Options](documentation/BUILD_OPTIONS.md)** - Building and packaging options
- **[Packaging](documentation/PACKAGING.md)** - Creating standalone executables
- **[Performance](documentation/PERFORMANCE.md)** - Performance considerations and optimization

## Requirements

- Python 3.10+
- See [requirements.txt](requirements.txt) for full dependency list

## License

[Add your license information here]

## Contributing

[Add your contribution guidelines here]

## Support

[Add your support information here]
