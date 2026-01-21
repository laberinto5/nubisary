# Graphical User Interface (GUI) Documentation

The Nubisary GUI provides a user-friendly interface for generating word clouds without using the command line. This guide covers all GUI features and usage.

## Launching the GUI

**From Command Line:**
```bash
python nubisary_gui.py
```

**Windows Executable:**
Double-click `nubisary_gui.exe` (if built as a standalone executable).

## Main Window Overview

The GUI window is organized into several sections:

1. **Input File Selection** - Choose your source file
2. **Text Processing Options** - Configure text filtering and processing
3. **Visual Settings** - Customize appearance and colors
4. **Word Cloud Preview** - See your word cloud as you configure it
5. **Action Buttons** - Generate and save your word cloud

## Step-by-Step Guide

### 1. Select Input File

Click **"Browse..."** next to the "Input File" field to select your source file.

**Supported Formats:**
- Text files (`.txt`)
- PDF files (`.pdf`)
- DOCX files (`.docx`)
- JSON files (`.json`)

**Note:** PDF and DOCX files are automatically converted to text when processed.

### 2. Select Language

Choose the language of your text from the **Language** dropdown menu.

**Supported Languages:**
The GUI supports 18 languages with verified NLTK stopwords support:

**European Languages:**
- **English** (198 stopwords)
- **Spanish** / Español (313 stopwords)
- **French** / Français (157 stopwords)
- **Italian** / Italiano (279 stopwords)
- **Portuguese** / Português (207 stopwords)
- **German** / Deutsch (232 stopwords)
- **Dutch** / Nederlands (101 stopwords)
- **Russian** / русский (151 stopwords)
- **Greek** / Ελληνικά (265 stopwords)
- **Danish** / dansk (94 stopwords)
- **Norwegian** / norsk (176 stopwords)
- **Swedish** / svenska (114 stopwords)
- **Finnish** / suomi (235 stopwords)
- **Turkish** / Türkçe (53 stopwords)

**Other Languages:**
- **Arabic** / العربية (754 stopwords)
- **Chinese** / 中文 (841 stopwords)
- **Hebrew** / עברית (221 stopwords)
- **Indonesian** / Bahasa Indonesia (758 stopwords)

The language is used for:
- Stopword filtering (common words like "the", "a", "and" in English; "el", "la", "y" in Spanish, etc.)
- Automatic removal of language-specific common words to focus on meaningful content

### 3. Text Processing Options

#### Text Replacements

Use the **Text replacements** section to remove or replace text before counting words:

- **Search**: word/phrase, a comma-separated list, or regex pattern
- **Replace**: replacement text (leave empty to remove)
- **Mode**: Single word/phrase, Comma-separated list, or Regex
- **Case-sensitive**: match case exactly

**Examples:**
- Remove a term: Search `author`, Replace *(empty)*
- Normalize terms: Search `colour,color`, Replace `color`
- Regex: Search `^Página \d+`, Replace *(empty)*

### 4. Visual Settings

#### Theme Selection

Select a preset theme from the **Theme** dropdown. Themes provide instant, beautiful color combinations.

**Available Themes:**
- Classic & Minimal: `classic`, `minimal`, `high-contrast`
- Dark Themes: `dark`, `vibrant`, `inferno`, `magma`, `hot`, `jet`, `turbo`, `dark2`
- Seasonal: `spring`, `summer`, `autumn`, `winter`
- Color-Based: `blues`, `greens`, `reds`, `purples`, `oranges`
- And more...

**See [THEMES.md](THEMES.md) for complete theme documentation.**

#### Custom Colors

**Background Color:**
- Enter a color name (e.g., `white`, `black`, `blue`)
- Or enter a hex code (e.g., `#FF0000`, `#000000`)

**Font Color:**
- Same format as background color
- **Note:** Ignored when using a colormap

**Colormap:**
- Select a matplotlib colormap for multi-color word clouds
- Popular options: `viridis`, `plasma`, `coolwarm`, `Set3`, `Pastel1`
- **Note:** Colormap overrides font color

#### Canvas Size

Adjust the word cloud dimensions:
- **Width** (default: 800 pixels)
- **Height** (default: 600 pixels)

#### Word Limits

- **Max Words**: Maximum number of words to include (default: 200)
- **Min Word Length**: Minimum character length (default: 0)

#### Advanced Options

**Processing Options:**
- ☑ **Include Stopwords**: Include common words (unchecked by default)
- ☑ **Case Sensitive**: Preserve case in word processing (unchecked by default)
- ☑ **Lematize**: Reduce words to their lemma (unchecked by default)
- ☑ **Include Numbers**: Include numbers in word cloud (unchecked by default)
- **N-gram**: Choose `unigram` or `bigram` tokenization for frequencies

**Visual Options:**
- **Relative Scaling**: Control size difference intensity (0.0-1.0, default: 0.5)
- **Prefer Horizontal**: Word orientation preference (0.0-1.0, default: 0.9)

### 5. Generate Word Cloud

Click the **"Generate Word Cloud"** button to create your word cloud.

**What happens:**
1. Input file is processed (converted if PDF/DOCX)
2. Text is cleaned and filtered according to your settings
3. Word frequencies are calculated
4. Word cloud is generated with your visual settings
5. Preview is displayed in the GUI window

### 6. Save Word Cloud

After generating:
1. Click **"Save As..."** button
2. Choose a location and filename
3. File is saved as PNG image

### 7. Export Vocabulary (Optional)

If you want the processed vocabulary with frequencies:

1. Check **"Export vocabulary (JSON/CSV)"** before generating
2. Vocabulary is automatically saved to:
   - `{filename}_vocabulary.json` - Word frequencies in JSON format
   - `{filename}_vocabulary.csv` - Word frequencies in CSV format

**Save Vocabulary (JSON only):**
- Use **"Save Vocabulary (Frequencies JSON)"** to export the latest vocabulary without saving a new PNG

**Top N Words:**
- Leave blank to export all words
- Enter a number (e.g., `50`) to export only top N words

## Tips for Using the GUI

### Working with PDFs/DOCX

1. **Convert first** (optional): Use the `convert` command in CLI to review the text first
2. **Text cleaning**: The GUI always cleans converted text
3. **Remove headers**: Use Text replacements (Regex mode) to remove repeated headers

### Text Filtering Best Practices

1. **Start simple**: Use text replacements for basic filtering
2. **Use regex for complex patterns**: Switch Mode to Regex
3. **Test with small files first**: Verify your filters work correctly before processing large documents

### Visual Customization

1. **Use themes**: Themes provide professional, tested color combinations
2. **Adjust canvas size**: Larger canvases work better for high word counts
3. **Experiment with colormaps**: Colormaps create vibrant, multi-color word clouds

### Performance

- **Large files**: Processing large PDFs may take a few moments
- **Preview updates**: The preview updates automatically after generation
- **Save regularly**: Save your word clouds as you refine your settings

## Limitations

- **JSON input**: When using JSON files, language selection doesn't affect processing
- **.doc files**: Older Word format (`.doc`) is not supported - convert to `.docx` or `.txt` first

## Troubleshooting

### "File not found" Error

- Verify the file path is correct
- Ensure the file exists at the specified location
- Check file permissions

### "Invalid regex pattern" Error

- Verify your regex syntax is correct
- Test patterns in a regex tester online
- Check for special characters that need escaping

### "No words found" Error

- Your text filtering may be too aggressive
- Try reducing or removing exclude words/regex rules
- Check that your input file contains text

### Preview Not Updating

- Click "Generate Word Cloud" again
- Verify all required fields are filled (Input File, Language)
- Check for error messages in the status area

## Keyboard Shortcuts

- **Tab**: Move between fields
- **Enter** (in input fields): Generate word cloud
- **Ctrl+S** or **Cmd+S**: Save word cloud (when generated)

## Differences from CLI

The GUI provides the same core functionality as the CLI, with some differences:

- **Easier for beginners**: No command-line knowledge required
- **Visual feedback**: See your word cloud as you configure it
- **Some advanced options**: Some CLI options may not be available in GUI (check version notes)
- **Batch processing**: CLI is better suited for processing multiple files

## Getting Help

If you need help:

1. Check the [CLI Documentation](CLI.md) for detailed option descriptions
2. Review [THEMES.md](THEMES.md) for theme information
3. Check error messages - they provide specific guidance
4. Try the CLI version for more advanced features and better error messages

