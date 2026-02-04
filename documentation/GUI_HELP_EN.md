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

Choose the language of your text. The GUI only lists languages with end-to-end support:

English, Spanish, French, German, Italian, Portuguese

The language setting controls stopword filtering and lemmatization.
See `documentation/LANGUAGE_SUPPORT.md` for full details.

## Text Processing Options

### Processing Options

- **Include stopwords**: Keep common words (usually unchecked)
- **Case sensitive**: Distinguish between uppercase and lowercase
- **N-gram**: Choose `unigram` (single words) or `bigram` (word pairs) tokenization. Bigrams are only formed within sentence boundaries to maintain semantic accuracy
- **Lematize**: Reduce words to their lemma (base form)
- **Include numbers**: Keep numeric values in the word cloud
- **Min word length**: Minimum characters per word (default: 0)
- **Max words**: Maximum number of words to display (default: 200)

### Text Replacements

Apply literal or regex replacements before counting words:

- **Search**: The word/phrase (or regex pattern if Regex is selected)
- **Replace**: The replacement text (leave empty to remove matches)
- **Mode**:
  - **Single word/phrase**: One exact word or phrase
  - **Comma-separated list**: Multiple words/phrases, all replaced by the same text
  - **Regex**: Pattern-based replacement (advanced)
- **Case-sensitive**: Match case exactly
- **Apply on**:
  - **Original text** (default): before preprocessing/lemmatization
  - **Processed text**: after lemmatization, right before frequencies

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

### Generate and export additional outputs

Check "Export additional outputs" to generate these additional files: 

- JSON file containing all the vocabulary and the word count.
- PDF & TXT files containing a user-friendly report on vocabulary stats and main insights.


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

- **F1**: Open this help manual
- **Ctrl+O**: Open input file (coming soon)
- **Ctrl+S**: Save word cloud (coming soon)

## Getting More Help

For detailed documentation, visit the project repository or check the CLI documentation for advanced features.

---


