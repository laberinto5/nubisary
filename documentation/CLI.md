# Command-Line Interface (CLI) Documentation

The Nubisary command-line interface provides powerful and flexible options for generating word clouds. This document covers all available commands and options.

## Commands

### `generate`

Generate a word cloud from an input file.

**Syntax:**
```bash
python nubisary.py generate [OPTIONS]
```

**Required Options:**
- `-i, --input PATH`: Input file (text, JSON, PDF, or DOCX)
- `-l, --language LANGUAGE`: Language code for text processing (e.g., `english`, `spanish`)

**Basic Example:**
```bash
python nubisary.py generate -i text.txt -l english --theme vibrant
```

## Input Options

### Input File Types

- **Text files** (`.txt`): Plain text files
- **PDF files** (`.pdf`): Automatically converted to text
- **DOCX files** (`.docx`): Automatically converted to text
- **JSON files** (`.json`): Word frequency dictionaries in JSON format

**Note:** `.doc` files (older Word format) are not directly supported. Please convert them to `.docx` or `.txt` first.

### Text Processing Options

#### `--no-clean-text`
Deprecated. Document cleaning is always applied when converting PDF/DOCX (page numbers and chapter markers are removed).

#### `-ew, --exclude-words TEXT`
Exclude specific words or phrases from the text before processing.

**Formats:**
- Single word: `-ew "word"`
- Comma-separated list: `-ew "word1,word2,word3"`
- File path: `-ew excluded.txt` (one word/phrase per line)

**Example:**
```bash
python nubisary.py generate -i document.pdf -l spanish -ew "Título del Libro,Autor Nombre"
```

#### `--exclude-case-sensitive`
Make exclude-words matching case-sensitive (default: case-insensitive).

#### `-rr, --regex-rule TEXT`
Apply regex transformations for advanced text filtering.

**Formats:**
- Remove pattern: `-rr "pattern"` (removes all matches)
- Replace pattern: `-rr "pattern|replacement"` (replaces matches)
- File path: `-rr regex_rules.txt` (one rule per line)

**Features:**
- Supports capture groups: Use `\1`, `\2`, etc. in replacements
- Multiple rules from file are applied in order (top to bottom)
- Comments in files: Lines starting with `#` are ignored

**Examples:**
```bash
# Remove page headers
python nubisary.py generate -i document.pdf -l spanish -rr "^Página \d+"

# Replace with backreferences
python nubisary.py generate -i text.txt -l english -rr "Página (\d+)|P.\\1"

# Multiple rules from file
python nubisary.py generate -i document.pdf -l spanish -rr regex_rules.txt
```

**Regex Rules File Format:**
```
# Remove page headers
^Página \d+

# Replace page format
Página (\d+)|P.\\1

# Remove line numbers
^\d+\.\s*
```

#### `--regex-case-sensitive`
Make regex matching case-sensitive (default: case-insensitive).

## Output Options

### `-o, --output PATH`
Specify output file path (PNG image). If not specified, output filename is auto-generated based on input filename.

**Example:**
```bash
python nubisary.py generate -i text.txt -l english -o custom_output.png
```

### `--no-show`
Do not display the word cloud (only save if output is specified).

## Visual Customization

### Themes

#### `-T, --theme THEME`
Use a preset theme for instant visual appeal. See [THEMES.md](THEMES.md) for complete documentation.

**Available Themes (34 total):**

**Classic & Minimal:**
- `classic`, `minimal`, `high-contrast`

**Dark Themes:**
- `dark`, `vibrant`, `inferno`, `magma`, `hot`, `jet`, `turbo`, `dark2`

**Seasonal:**
- `spring`, `summer`, `autumn`, `winter`

**Color-Based:**
- `blues`, `greens`, `reds`, `purples`, `oranges`

**Specialized:**
- `ocean`, `sunset`, `cool`, `rainbow`

**Diverging:**
- `spectral`, `rdbu`

**Qualitative:**
- `set1`, `set2`, `pastel`, `pastel2`, `tab10`, `tab20`, `accent`

**Example:**
```bash
python nubisary.py generate -i text.txt -l english --theme vibrant
```

#### `list-themes`
List all available themes with descriptions.

```bash
python nubisary.py list-themes
```

### Color Options

#### `-B, --background COLOR`
Background color. Accepts:
- Color names: `white`, `black`, `blue`, `red`, etc.
- Hex codes: `#FF0000`, `#000000`

#### `-F, --fontcolor COLOR`
Font color (single color for all words). Same format as background color.

**Note:** `--fontcolor` is ignored when using `--colormap`.

#### `--colormap COLORMAP`
Use a matplotlib colormap for multi-color word clouds. Examples:
- `viridis`, `plasma`, `coolwarm`, `Set3`, `Pastel1`

**Note:** `--colormap` overrides `--fontcolor`.

**Example:**
```bash
python nubisary.py generate -i text.txt -l english --colormap plasma
```

### Advanced Visual Options

#### `--relative-scaling FLOAT`
Control size difference intensity (0.0-1.0, default: 0.5).
- Lower values (e.g., 0.3) = more dramatic size differences
- Higher values (e.g., 0.8) = more subtle differences
- Always respects word frequency

#### `--prefer-horizontal FLOAT`
Word orientation preference (0.0-1.0, default: 0.9).
- `1.0` = all horizontal
- `0.0` = mixed orientations
- `0.5` = balanced

#### `--mask PATH`
Use a mask image for custom word cloud shapes (PNG/JPG).
- Dark areas = word placement
- Light/transparent areas = no words

**Example:**
```bash
python nubisary.py generate -i text.txt -l english --mask heart.png
```

#### `--contour-width FLOAT`
Outline width for mask shape (default: 0.0). Only works with `--mask`.

#### `--contour-color COLOR`
Outline color for mask shape. Hex code or color name. Only works with `--mask`.

**Example:**
```bash
python nubisary.py generate -i text.txt -l english --mask heart.png --contour-width 2 --contour-color red
```

#### `--font-path PATH`
Path to custom font file (TTF/OTF).

#### `-X, --canvas-width INT`
Width of the word cloud canvas in pixels (default: 800).

#### `-Y, --canvas-height INT`
Height of the word cloud canvas in pixels (default: 600).

## Word Processing Options

### `-M, --max-words INT`
Maximum number of words to include in the word cloud (default: 200).

### `-L, --min-word-length INT`
Minimum character length for words included in the word cloud (default: 0).

### `-P, --lematize`
Lematize words before generating the word cloud.

### `-N, --include-numbers`
Include numbers in the word cloud (default: numbers are excluded). When disabled, any token containing digits is removed.

### `-W, --include-stopwords`
Include stopwords (default: stopwords are filtered out).

### `--ngram`
Tokenization mode for frequency generation. Options:
- `unigram` (default)
- `bigram`

### `-U, --case-sensitive`
Make word processing case-sensitive (default: case-insensitive).

## Vocabulary Export

### `-V, --vocabulary`
Export processed vocabulary to JSON and CSV files.

### `--vocabulary-top-n INT`
Export only the top N words (default: all words).

**Example:**
```bash
python nubisary.py generate -i text.txt -l english --vocabulary --vocabulary-top-n 20
```

**Output Files:**
- `{base}_vocabulary.json`: Word frequencies in JSON format
- `{base}_vocabulary.csv`: Word frequencies in CSV format

## Command: `convert`

Convert a document (PDF or DOCX) to a plain text file for review or editing.

**Syntax:**
```bash
python nubisary.py convert [OPTIONS]
```

**Required Options:**
- `-i, --input PATH`: Document file to convert (PDF or DOCX)

**Optional Options:**
- `-o, --output PATH`: Output text file path (default: input filename with `.txt` extension)
- `--no-clean-text`: Deprecated (cleaning is always applied)

**Example:**
```bash
python nubisary.py convert -i document.pdf -o document.txt
```

**Note:** Vocabulary export (`--vocabulary`) is only available with the `generate` command.

## Common Usage Patterns

### Basic Word Cloud
```bash
python nubisary.py generate -i text.txt -l english --theme vibrant
```

### From PDF with Text Cleaning
```bash
python nubisary.py generate -i document.pdf -l spanish --theme dark --vocabulary
```

### Exclude Repeated Headers
```bash
python nubisary.py generate -i document.pdf -l spanish -ew "Título del Libro" -rr "^Página \d+" --theme vibrant
```

### Custom Colors and Vocabulary
```bash
python nubisary.py generate -i text.txt -l english -B white -F "#FF0000" --vocabulary --vocabulary-top-n 50
```

### Advanced Regex Processing
```bash
# Create regex_rules.txt:
# ^Página \d+
# Página (\d+)|P.\\1
# ^\d+\.\s*

python nubisary.py generate -i document.pdf -l spanish -rr regex_rules.txt --theme vibrant
```

### Custom Shape with Mask
```bash
python nubisary.py generate -i text.txt -l english --mask heart.png --contour-width 2 --contour-color red --theme vibrant
```

### Multi-color with Colormap
```bash
python nubisary.py generate -i text.txt -l english --colormap plasma --background black
```

## Processing Order

Understanding the processing order helps you use options effectively:

1. **Document Conversion** (if PDF/DOCX)
2. **Text Cleaning** (page/chapter numbers, extra blank lines)
3. **Word/Phrase Exclusion** (`--exclude-words`)
4. **Regex Transformations** (`--regex-rule`) - applied in order
5. **Text Preprocessing** (punctuation → spaces, spacing, casing; digit tokens removed if disabled)
6. **Lematize** (if enabled)
7. **Word Frequency Generation** (unigram or bigram)
8. **Word Cloud Generation** (visual settings + filters)
9. **Vocabulary Export** (if `--vocabulary`)

## Error Handling

The CLI provides clear error messages for:
- Invalid file paths
- Unsupported file formats
- Invalid regex patterns
- Invalid color codes
- Missing required options
- File I/O errors

## Tips

- Use `--theme` for quick, professional results
- Combine `--exclude-words` and `--regex-rule` for complex text filtering
- Export vocabulary (`--vocabulary`) to analyze word frequencies separately
- Use `--colormap` for vibrant, multi-color word clouds
- Test regex patterns with small samples before processing large documents
- Use `convert` command to review converted text before generating word clouds

