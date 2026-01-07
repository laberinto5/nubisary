"""Nubisary - Word Cloud Generator CLI entry point using Typer."""

import typer
from typing import Optional

from src.config import WordCloudConfig
from src.themes import get_theme, get_theme_names
from src.wordcloud_service import generate_wordcloud, WordCloudServiceError
from src.file_handlers import convert_document_to_text_file, FileHandlerError
from src.document_converter import is_convertible_document, UnsupportedFormatError
from src.logger import setup_logger

# Setup logger
logger = setup_logger()

# Create Typer app
app = typer.Typer(
    name='nubisary',
    help='Generate word clouds from text, JSON, PDF, DOC, or DOCX files.',
    add_completion=False
)


@app.command(name='generate')
def generate(
    input: str = typer.Option(
        ...,
        '-i', '--input',
        help='Path to the input file (text, JSON, PDF, or DOCX). Note: .doc files must be converted to .docx or .txt first.'
    ),
    language: str = typer.Option(
        ...,
        '-l', '--language',
        help='Language of the input (e.g., english, spanish)'
    ),
    output: Optional[str] = typer.Option(
        None,
        '-o', '--output',
        help='Path to the output file (png image). If not specified, auto-generates based on input filename in the same directory.'
    ),
    background: Optional[str] = typer.Option(
        None,
        '-B', '--background',
        help='Background color: hexadecimal codes ("#FF0000") or words (white, blue, yellow, green, red, orange, grey, black)'
    ),
    fontcolor: Optional[str] = typer.Option(
        None,
        '-F', '--fontcolor',
        help='Font color: hexadecimal codes ("#FF0000") or words (white, blue, yellow, green, red, orange, grey, black)'
    ),
    max_words: int = typer.Option(
        200,
        '-M', '--max_words',
        help='Maximum number of words to include in the word cloud (default: 200)'
    ),
    min_word_length: int = typer.Option(
        0,
        '-L', '--min_word_length',
        help='Minimum amount of chars in words included in the word cloud (default: 0)'
    ),
    normalize_plurals: bool = typer.Option(
        False,
        '-P', '--normalize_plurals',
        help='Normalize plurals (default: False)'
    ),
    include_numbers: bool = typer.Option(
        False,
        '-N', '--include_numbers',
        help='Include numbers (default: False)'
    ),
    collocations: bool = typer.Option(
        False,
        '-C', '--collocations',
        help='Include collocations (default: False)'
    ),
    include_stopwords: bool = typer.Option(
        False,
        '-W', '--include_stopwords',
        help='Include stopwords (default: False)'
    ),
    case_sensitive: bool = typer.Option(
        False,
        '-U', '--case_sensitive',
        help='Case-sensitive word cloud (default: False)'
    ),
    canvas_width: int = typer.Option(
        800,
        '-X', '--canvas_width',
        help='Width of the word cloud canvas (default: 800)'
    ),
    canvas_height: int = typer.Option(
        600,
        '-Y', '--canvas_height',
        help='Height of the word cloud canvas (default: 600)'
    ),
    no_show: bool = typer.Option(
        False,
        '--no-show',
        help='Do not display the word cloud (only save if output is specified)'
    ),
    no_clean_text: bool = typer.Option(
        False,
        '--no-clean-text',
        help='Do not clean converted text (keep page numbers, excessive blank lines)'
    ),
    export_stats: bool = typer.Option(
        False,
        '-S', '--export-stats',
        help='Export word frequency statistics to JSON and CSV files'
    ),
    stats_top_n: Optional[int] = typer.Option(
        None,
        '--stats-top-n',
        help='Export only top N words (default: all words). Example: --stats-top-n 20'
    ),
    stats_output: Optional[str] = typer.Option(
        None,
        '--stats-output',
        help='Base filename for statistics files (auto-generate if not specified)'
    ),
    theme: Optional[str] = typer.Option(
        None,
        '-T', '--theme',
        help='Preset theme name. Available themes: classic, vibrant, ocean, sunset, minimal, dark, pastel, high-contrast, inferno, magma, spring, summer, autumn, winter, cool, hot, rainbow, jet, turbo, blues, greens, reds, purples, oranges, spectral, rdbu, set1, set2, pastel2, dark2, tab10, tab20, accent. Overrides individual color settings.'
    ),
    colormap: Optional[str] = typer.Option(
        None,
        '--colormap',
        help='Matplotlib colormap name for multi-color word clouds (e.g., viridis, plasma, coolwarm, Set3, Pastel1). Overrides --fontcolor.'
    ),
    relative_scaling: Optional[float] = typer.Option(
        None,
        '--relative-scaling',
        help='Control size difference intensity (0.0-1.0, default: 0.5). Lower = more dramatic differences, higher = more subtle (always respects frequency)'
    ),
    prefer_horizontal: Optional[float] = typer.Option(
        None,
        '--prefer-horizontal',
        help='Word orientation preference (0.0-1.0, default: 0.9). 1.0 = all horizontal, 0.0 = mixed, 0.5 = balanced'
    ),
    mask: Optional[str] = typer.Option(
        None,
        '--mask',
        help='Path to mask image file (PNG/JPG). Dark areas = word placement, light/transparent = no words'
    ),
    contour_width: Optional[float] = typer.Option(
        None,
        '--contour-width',
        help='Outline width for mask shape (default: 0.0, only works with --mask)'
    ),
    contour_color: Optional[str] = typer.Option(
        None,
        '--contour-color',
        help='Outline color for mask shape (hex code or color name, only works with --mask)'
    ),
    font_path: Optional[str] = typer.Option(
        None,
        '--font-path',
        help='Path to custom font file (TTF/OTF)'
    ),
    exclude_words: Optional[str] = typer.Option(
        None,
        '-ew', '--exclude-words',
        help='Words or phrases to exclude from text. Can be: a single word, comma-separated list (e.g., "word1,word2"), or a file path (one word/phrase per line). File paths are checked first; if file does not exist, treated as text.'
    ),
    exclude_case_sensitive: bool = typer.Option(
        False,
        '--exclude-case-sensitive',
        help='Make exclude-words matching case-sensitive (default: case-insensitive)'
    ),
    regex_rule: Optional[str] = typer.Option(
        None,
        '-rr', '--regex-rule',
        help='Regex rule for advanced text transformation. Format: "pattern" (removes) or "pattern|replacement" (replaces). Can be a file path (one rule per line). Supports capture groups (\\1, \\2, etc.). Rules are applied in order.'
    ),
    regex_case_sensitive: bool = typer.Option(
        False,
        '--regex-case-sensitive',
        help='Make regex matching case-sensitive (default: case-insensitive)'
    )
):
    """
    Generate a word cloud from a text, JSON, PDF, or DOCX file.
    
    PDF and DOCX files are automatically converted to text before processing.
    Note: .doc files (older Word format) are not directly supported. 
    Please convert them to .docx or .txt first.
    
    Visual customization:
    - Use --theme for preset color combinations (recommended)
      See THEMES.md for complete theme documentation
    - Use --colormap for multi-color word clouds
    - Use --relative-scaling to control size difference intensity
    - Use --mask for custom shapes (requires prepared image)
    
    Available themes (34 total):
    Classic: classic, minimal, high-contrast
    Dark: dark, vibrant, inferno, magma, hot, jet, turbo, dark2
    Seasonal: spring, summer, autumn, winter
    Color-based: blues, greens, reds, purples, oranges
    Specialized: ocean, sunset, cool, rainbow
    Diverging: spectral, rdbu
    Qualitative: set1, set2, pastel, pastel2, tab10, tab20, accent
    
    Examples:
    
    \b
    # Generate from text file with theme (auto-generates output filename)
    python nubisary.py generate -i text.txt -l english --theme vibrant
    
    \b
    # Generate with custom output filename
    python nubisary.py generate -i text.txt -l english -o custom_output.png --theme vibrant
    
    \b
    # Generate with statistics export (auto-generates filenames based on input)
    python nubisary.py generate -i text.txt -l english --export-stats
    
    \b
    # Generate with custom colormap
    python nubisary.py generate -i text.txt -l english --colormap plasma
    
    \b
    # Generate with mask shape
    python nubisary.py generate -i text.txt -l english --mask heart.png --contour-width 2 --contour-color red
    
    \b
    # Generate from PDF (auto-converts to text) with statistics
    python nubisary.py generate -i document.pdf -l english --export-stats
    
    \b
    # Generate with custom colors and statistics
    python nubisary.py generate -i text.txt -l spanish -B white -F "#FF0000" --export-stats
    
    \b
    # Generate from JSON frequencies with statistics
    python nubisary.py generate -i frequencies.json -l english --export-stats
    
    \b
    # Generate with excluded words/phrases (removes repeated headers from PDF conversion)
    python nubisary.py generate -i document.pdf -l spanish -ew "Título del Libro,Autor Nombre"
    
    \b
    # Generate with excluded words from file (one word/phrase per line)
    python nubisary.py generate -i document.pdf -l spanish -ew excluded.txt
    
    \b
    # Generate with case-sensitive exclusion
    python nubisary.py generate -i text.txt -l english -ew "Word" --exclude-case-sensitive
    
    \b
    # Generate with regex rule to remove page headers
    python nubisary.py generate -i document.pdf -l spanish -rr "^Página \d+"
    
    \b
    # Generate with regex rule to replace pattern
    python nubisary.py generate -i text.txt -l english -rr "Página (\d+)|P.\\1"
    
    \b
    # Generate with regex rules from file (one rule per line)
    python nubisary.py generate -i document.pdf -l spanish -rr regex_rules.txt
    
    \b
    # Generate with both exclude-words and regex rules (applied in order)
    python nubisary.py generate -i document.pdf -l spanish -ew "Título,Autor" -rr "^Página \d+"
    """
    try:
        # Handle theme selection
        theme_obj = None
        if theme:
            theme_obj = get_theme(theme)
            if theme_obj is None:
                available_themes = ', '.join(get_theme_names())
                logger.error(
                    f'Unknown theme: {theme}. '
                    f'Available themes: {available_themes}'
                )
                raise typer.Exit(code=1)
            logger.info(f'Using theme: {theme_obj.name} - {theme_obj.description}')
        
        # Apply theme settings (theme overrides individual settings)
        bg_color = background
        fg_color = fontcolor
        colormap_value = colormap
        relative_scaling_value = relative_scaling
        prefer_horizontal_value = prefer_horizontal
        
        if theme_obj:
            # Theme takes precedence
            bg_color = theme_obj.background_color
            if theme_obj.colormap:
                colormap_value = theme_obj.colormap
                fg_color = None  # Colormap overrides font_color
            elif theme_obj.font_color:
                fg_color = theme_obj.font_color
                colormap_value = None
            if relative_scaling_value is None:
                relative_scaling_value = theme_obj.relative_scaling
            if prefer_horizontal_value is None:
                prefer_horizontal_value = theme_obj.prefer_horizontal
        
        # Create configuration object
        config = WordCloudConfig(
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            max_words=max_words,
            min_word_length=min_word_length,
            normalize_plurals=normalize_plurals,
            include_numbers=include_numbers,
            background_color=bg_color,
            font_color=fg_color,
            colormap=colormap_value,
            relative_scaling=relative_scaling_value if relative_scaling_value is not None else 0.5,
            prefer_horizontal=prefer_horizontal_value if prefer_horizontal_value is not None else 0.9,
            mask=mask,
            contour_width=contour_width if contour_width is not None else 0.0,
            contour_color=contour_color,
            font_path=font_path,
            language=language,
            include_stopwords=include_stopwords,
            case_sensitive=case_sensitive,
            collocations=collocations
        )
        
        # Generate word cloud
        generate_wordcloud(
            input_file=input,
            language=language,
            output_file=output,
            config=config,
            show=not no_show,
            clean_text=not no_clean_text,
            export_stats=export_stats,
            stats_output=stats_output,
            stats_top_n=stats_top_n,
            exclude_words=exclude_words,
            exclude_case_sensitive=exclude_case_sensitive,
            regex_rule=regex_rule,
            regex_case_sensitive=regex_case_sensitive
        )
        
    except WordCloudServiceError as e:
        logger.error(f'Error generating word cloud: {e}')
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        logger.info('Operation cancelled by user')
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        raise typer.Exit(code=1)


@app.command(name='list-themes')
def list_themes():
    """
    List all available themes with their descriptions.
    
    This command displays all 34 available themes organized by category,
    making it easy to find the perfect theme for your word cloud.
    """
    from src.themes import list_themes as get_all_themes
    
    themes = get_all_themes()
    
    # Organize themes by category
    categories = {
        'Classic & Minimal': ['classic', 'minimal', 'high-contrast'],
        'Dark Themes': ['dark', 'vibrant', 'inferno', 'magma', 'hot', 'jet', 'turbo', 'dark2'],
        'Seasonal': ['spring', 'summer', 'autumn', 'winter'],
        'Color-Based': ['blues', 'greens', 'reds', 'purples', 'oranges'],
        'Specialized': ['ocean', 'sunset', 'cool', 'rainbow'],
        'Diverging': ['spectral', 'rdbu'],
        'Qualitative': ['set1', 'set2', 'pastel', 'pastel2', 'tab10', 'tab20', 'accent']
    }
    
    print("\n" + "="*70)
    print("Available Word Cloud Themes")
    print("="*70)
    print(f"\nTotal themes: {len(themes)}\n")
    
    for category, theme_names in categories.items():
        print(f"\n{category}:")
        print("-" * 70)
        for theme_name in theme_names:
            theme = themes.get(theme_name.lower())
            if theme:
                print(f"  {theme.name:20} - {theme.description}")
    
    print("\n" + "="*70)
    print("Usage: python nubisary.py generate -i file.txt -l english --theme <theme-name>")
    print("For detailed documentation, see THEMES.md")
    print("="*70 + "\n")


@app.command(name='convert')
def convert(
    input: str = typer.Option(
        ...,
        '-i', '--input',
        help='Path to the document file (PDF or DOCX). Note: .doc files must be converted to .docx or .txt first.'
    ),
    output: Optional[str] = typer.Option(
        None,
        '-o', '--output',
        help='Path to the output text file (default: input filename with .txt extension)'
    ),
    no_clean_text: bool = typer.Option(
        False,
        '--no-clean-text',
        help='Do not clean converted text (keep page numbers, excessive blank lines)'
    )
):
    """
    Convert a document (PDF, DOC, or DOCX) to a plain text file.
    
    This allows you to review and edit the extracted text before generating a word cloud.
    Note: Statistics export (--export-stats) is only available with the 'generate' command.
    
    Examples:
    
    \b
    # Convert PDF to text
    python nubisary.py convert -i document.pdf -o document.txt
    
    \b
    # Convert DOCX to text (auto-generates output filename)
    python nubisary.py convert -i document.docx
    
    \b
    # Then generate word cloud with statistics from the converted text
    python nubisary.py generate -i document.txt -l english -o cloud.png --export-stats
    """
    try:
        # Check if file is convertible
        if not is_convertible_document(input):
            logger.error(
                f'File is not a convertible document: {input}. '
                'Supported formats: PDF, DOC, DOCX'
            )
            raise typer.Exit(code=1)
        
        # Convert document to text file
        output_file = convert_document_to_text_file(input, output, clean_text=not no_clean_text)
        logger.info(f'Document converted successfully: {output_file}')
        logger.info(f'You can now review/edit the text file before generating a word cloud.')
        
    except (FileHandlerError, UnsupportedFormatError) as e:
        logger.error(f'Error converting document: {e}')
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        logger.info('Operation cancelled by user')
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        raise typer.Exit(code=1)


# Note: Users can call either:
#   python nubisary.py generate -i file.txt -l english
#   python nubisary.py convert -i file.pdf -o file.txt


if __name__ == '__main__':
    app()
