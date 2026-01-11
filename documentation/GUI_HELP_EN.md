# Nubisary - User Manual

## Welcome to Nubisary

Nubisary is a powerful word cloud generator that creates beautiful visualizations from your text documents. This guide will help you get started.

## Quick Start

1. **Select Input File**: Click "Browse..." to choose a text, PDF, DOCX, or JSON file
2. **Choose Language**: Select the language of your text (default: Spanish)
3. **Select Theme**: Pick a visual theme for your word cloud
4. **Generate**: Click "Generate Word Cloud" to create your visualization
5. **Preview**: Review your word cloud in the preview area
6. **Save**: Click "Save As..." when you're satisfied with the result

## Input File

### Supported Formats
- **Text files** (`.txt`) - Plain text documents
- **PDF files** (`.pdf`) - Automatically converted to text
- **DOCX files** (`.docx`) - Microsoft Word documents (automatically converted)
- **JSON files** (`.json`) - Word frequency data

### Language Selection

Choose the language of your text to enable proper stopword filtering. Supported languages include:

**European Languages**: English, Spanish, French, Italian, Portuguese, German, Dutch, Russian, Greek, Danish, Norwegian, Swedish, Finnish, Turkish

**Other Languages**: Arabic, Chinese, Hebrew, Indonesian

The language setting helps remove common words (like "the", "a", "and" in English) to focus on meaningful content.

## Text Processing Options

### Exclude Words/Phrases

Remove specific words or phrases from your word cloud:

- **Direct input**: Enter words separated by commas (e.g., "Title, Author Name")
- **From file**: Click "Browse..." to select a file with one word/phrase per line

**Example file content:**
```
Book Title
Author Name
Collection Name
```

### Regex Rules (Advanced)

For advanced text filtering, use regular expressions:

- **Single rule**: Enter a pattern or `pattern|replacement`
- **From file**: Click "Browse..." to select a file with one rule per line

**Examples:**
- Remove page headers: `^Page \d+`
- Replace format: `Page (\d+)|P.\\1`

### Processing Options

- **Include stopwords**: Keep common words (usually unchecked)
- **Case sensitive**: Distinguish between uppercase and lowercase
- **Collocations**: Group common word pairs together
- **Normalize plurals**: Treat singular and plural forms as the same word
- **Include numbers**: Keep numeric values in the word cloud
- **Min word length**: Minimum characters per word (default: 0)
- **Max words**: Maximum number of words to display (default: 200)

## Visual Customization

### Theme Selection

Choose from 38+ preset themes for instant beautiful color combinations:

- **Classic & Minimal**: classic, minimal, high-contrast
- **Dark Themes**: dark, vibrant, inferno, magma, hot, jet, turbo
- **Seasonal**: spring, summer, autumn, winter
- **Color-Based**: blues, greens, reds, purples, oranges
- And many more!

### Custom Theme Creator

Create your own theme with custom colors:

1. Check "Create Custom Theme"
2. Select background color
3. Choose 5 colors for the colormap
4. Optionally save your theme as JSON for reuse
5. Load previously saved themes with "Load Theme from JSON..."

### Canvas Size

Adjust the dimensions of your word cloud:
- **Width**: Default 800 pixels
- **Height**: Default 600 pixels

### Word Orientation

- **Relative Scaling**: Control size difference intensity (0.0-1.0)
  - Lower values = more dramatic size differences
  - Higher values = more subtle differences
- **Prefer Horizontal**: Word orientation preference (0.0-1.0)
  - 1.0 = all horizontal
  - 0.0 = mixed orientations
  - 0.5 = balanced

## Advanced Options

### Mask Images

Use custom shapes for your word cloud:

1. Select a **Preset mask** from the dropdown (34 available shapes)
2. Or choose **Custom...** to select your own image file
3. Dark areas = word placement
4. Light/transparent areas = no words

**Contour Options** (when using a mask):
- **Contour Width**: Outline thickness (0.0 = no outline)
- **Contour Color**: Outline color (hex code or color name)

### Font Selection

Choose a font for your word cloud:

- **Default**: Uses DroidSansMono (built-in)
- **Preset fonts**: 20 beautiful fonts available:
  - Sans Serif: Comfortaa, Inter Tight, Urbanist, Outfit, Maven Pro
  - Serif: Courier Prime, Marcellus, Special Elite
  - Monospace: Kode Mono, Orbitron
  - Handwriting: Cabin Sketch, Caveat, Pacifico
  - Display: Barrio, Chelsea Market, Caesar Dressing, Pirata One, Ribeye Marrow, Saira Stencil One, Text Me One
- **Custom...**: Select a font file from your system

### Export Statistics

Export word frequency data:

- Check "Export statistics" to generate JSON and CSV files
- Optionally limit to top N words (e.g., top 20)
- Files are saved alongside your word cloud image

## Tips & Best Practices

1. **Start Simple**: Begin with default settings and a preset theme
2. **Adjust Gradually**: Make small changes and regenerate to see effects
3. **Use Exclude Words**: Remove titles, author names, and other unwanted text
4. **Try Different Themes**: Experiment with various color schemes
5. **Use Masks**: Create word clouds in custom shapes for visual impact
6. **Language Matters**: Always select the correct language for better stopword filtering

## Troubleshooting

### Word Cloud Not Generating
- Ensure input file is selected and valid
- Check that language is correctly set
- Verify file format is supported

### Words Appear as Rectangles
- This usually indicates a font encoding issue
- Try a different preset font
- Ensure custom fonts support your language's characters

### Preview Not Updating
- Click "Generate Word Cloud" again
- Check for error messages in the status area

### File Not Saving
- Ensure you've generated a word cloud first
- Use "Save As..." button to choose save location
- Check file permissions in the target directory

## Keyboard Shortcuts

- **F1**: Open this help manual (coming soon)
- **Ctrl+O**: Open input file (coming soon)
- **Ctrl+S**: Save word cloud (coming soon)

## Getting More Help

For detailed documentation, visit the project repository or check the CLI documentation for advanced features.

---

**Version**: 1.0  
**Last Updated**: January 2025

