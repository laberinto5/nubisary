"""Nubisary - Word Cloud Generator CLI entry point using Typer."""

import typer
import os
from typing import Optional, List

from src.config import WordCloudConfig
from src.themes import get_theme, get_theme_names
from src.wordcloud_service import (
    generate_wordcloud, 
    WordCloudServiceError,
    process_text_to_frequencies
)
from src.wordcloud_generator import generate_word_cloud_from_frequencies
from src.statistics_exporter import export_statistics
from src.file_handlers import convert_document_to_text_file, FileHandlerError
from src.document_converter import is_convertible_document, UnsupportedFormatError
from src.custom_themes import load_custom_theme_from_json, CustomThemeError
from src.logger import setup_logger
from src.validators import generate_output_filename, validate_color_reference, ValidationError
import os

# Setup logger
logger = setup_logger()

# Create Typer app
app = typer.Typer(
    name='nubisary',
    help='Generate word clouds from text, JSON, PDF, DOC, or DOCX files.',
    add_completion=False
)


def parse_theme_argument(theme_arg: Optional[str]) -> List[str]:
    """
    Parse theme argument that can be:
    - A single theme name: "soft"
    - Multiple theme names separated by commas: "soft,playroom,jungle"
    - "all" to generate all available themes
    
    Args:
        theme_arg: Theme argument string or None
        
    Returns:
        List of theme names (empty list if theme_arg is None)
        
    Raises:
        ValueError: If "all" is used with other themes or if any theme name is invalid
    """
    if not theme_arg:
        return []
    
    # Normalize and split by comma
    theme_arg = theme_arg.strip()
    
    if theme_arg.lower() == "all":
        # Return all available theme names
        return sorted(get_theme_names())
    
    # Split by comma and strip whitespace
    themes = [t.strip() for t in theme_arg.split(',') if t.strip()]
    
    # Check if "all" is mixed with other themes
    if "all" in [t.lower() for t in themes]:
        raise ValueError('Cannot use "all" with other theme names. Use "all" alone or specific theme names.')
    
    return themes


def generate_output_file_with_theme_suffix(
    base_output: Optional[str],
    input_file: str,
    theme_name: str,
    has_theme: bool = True
) -> str:
    """
    Generate output filename with theme suffix.
    
    Always adds the theme name as a suffix before the extension when a theme is used.
    If no theme is used (custom colors), doesn't add a suffix.
    
    Args:
        base_output: User-provided output filename (can be None)
        input_file: Input file path (used for auto-generation)
        theme_name: Name of the theme (used as suffix, or "custom" if no theme)
        has_theme: Whether a theme is being used (if False, doesn't add suffix)
        
    Returns:
        Output filename with theme suffix if has_theme is True, otherwise base filename
    """
    # Determine base filename
    if base_output:
        base, ext = os.path.splitext(base_output)
        if not ext:
            ext = '.png'
        base_filename = base
    else:
        # Auto-generate from input file
        base_output = generate_output_filename(input_file, '.png')
        base, ext = os.path.splitext(base_output)
        base_filename = base
    
    # Add theme suffix if a theme is being used
    if has_theme:
        return f"{base_filename}_{theme_name}{ext}"
    else:
        # No theme, use base filename as-is
        return f"{base_filename}{ext}"


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
        help='Preset theme name(s). Can be: a single theme, multiple themes separated by commas (e.g., "soft,playroom,jungle"), or "all" to generate all available themes. Each theme generates a separate output file with the theme name as suffix. Overrides individual color settings.'
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
    ),
    custom_theme: Optional[str] = typer.Option(
        None,
        '--custom-theme',
        help='Path to JSON file containing custom theme definition. See documentation for JSON format. Custom theme will override --theme if both are specified.'
    )
):
    """
    Generate a word cloud from a text, JSON, PDF, or DOCX file.
    
    PDF and DOCX files are automatically converted to text before processing.
    Note: .doc files (older Word format) are not directly supported. 
    Please convert them to .docx or .txt first.
    
    Visual customization:
    - Use --theme for preset color combinations (recommended)
      Can specify multiple themes separated by commas or use "all" to generate all themes
      Each theme generates a separate output file with theme name as suffix
      See THEMES.md for complete theme documentation or use 'list-themes' command
    - Use --colormap for multi-color word clouds
    - Use --relative-scaling to control size difference intensity
    - Use --mask for custom shapes (requires prepared image)
    
    Examples:
    
    \b
    # Generate from text file with single theme (auto-generates output filename)
    python nubisary.py generate -i text.txt -l english --theme soft
    
    \b
    # Generate with multiple themes (creates separate files: text_soft.png, text_playroom.png)
    python nubisary.py generate -i text.txt -l english --theme soft,playroom,jungle
    
    \b
    # Generate all available themes (creates one file per theme with theme name suffix)
    python nubisary.py generate -i text.txt -l english --theme all
    
    \b
    # Generate with custom output filename and multiple themes (base_name_theme.png)
    python nubisary.py generate -i text.txt -l english -o output.png --theme soft,playroom
    
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
    
    \b
    # Generate with custom theme from JSON file
    python nubisary.py generate -i text.txt -l english --custom-theme my_theme.json
    
    \b
    # Generate with custom theme (overrides --theme if both specified)
    python nubisary.py generate -i text.txt -l english --theme vibrant --custom-theme my_theme.json
    """
    try:
        # ========================================================================
        # STEP 1: Validate all themes FIRST (before any text processing)
        # ========================================================================
        theme_list = []
        theme_names = []
        
        if custom_theme:
            # Handle custom theme first (if specified)
            # Custom theme only supports single theme generation
            try:
                logger.info(f'Loading custom theme from: {custom_theme}')
                theme_obj = load_custom_theme_from_json(custom_theme)
                logger.info(f'Custom theme loaded: {theme_obj.name} - {theme_obj.description}')
                if theme:
                    logger.warning(f'Both --theme ({theme}) and --custom-theme ({custom_theme}) specified. Custom theme takes precedence.')
                
                # Generate single word cloud with custom theme
                theme_list = [theme_obj]
                theme_names = [theme_obj.name]
            except (CustomThemeError, FileHandlerError) as e:
                logger.error(f'Error loading custom theme: {e}')
                raise typer.Exit(code=1)
        else:
            # Parse theme argument to get list of theme names
            theme_names_list = []
            if theme:
                try:
                    theme_names_list = parse_theme_argument(theme)
                except ValueError as e:
                    logger.error(f'Invalid theme argument: {e}')
                    raise typer.Exit(code=1)
            
            # If no themes specified, use None (will use individual color settings)
            if not theme_names_list:
                theme_list = [None]
                theme_names = ["default"]
            else:
                # Validate ALL themes exist BEFORE processing
                available_themes = get_theme_names()
                invalid_themes = []
                
                for theme_name in theme_names_list:
                    theme_obj = get_theme(theme_name)
                    if theme_obj is None:
                        invalid_themes.append(theme_name)
                
                # If any theme is invalid, report ALL invalid themes at once
                if invalid_themes:
                    logger.error(
                        f'Unknown theme(s): {", ".join(invalid_themes)}. '
                        f'Available themes: {", ".join(sorted(available_themes))}'
                    )
                    raise typer.Exit(code=1)
                
                # All themes are valid, now get Theme objects
                for theme_name in theme_names_list:
                    theme_obj = get_theme(theme_name)
                    theme_list.append(theme_obj)
                    theme_names.append(theme_obj.name)  # Use actual theme name from Theme object
                    logger.info(f'Theme validated: {theme_obj.name} - {theme_obj.description}')
        
        # Determine if we're generating multiple themes
        multiple_themes = len(theme_list) > 1
        
        # ========================================================================
        # STEP 2: Process text ONCE (before generating any word clouds)
        # ========================================================================
        logger.info('Processing input file (text processing happens once for all themes)...')
        
        # Create base config for text processing (doesn't need color/theme settings)
        base_config = WordCloudConfig(
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            max_words=max_words,
            min_word_length=min_word_length,
            normalize_plurals=normalize_plurals,
            include_numbers=include_numbers,
            language=language,
            include_stopwords=include_stopwords,
            case_sensitive=case_sensitive,
            collocations=collocations
        )
        
        # Process text once to get frequencies
        frequencies = process_text_to_frequencies(
            input_file=input,
            language=language,
            config=base_config,
            clean_text=not no_clean_text,
            exclude_words=exclude_words,
            exclude_case_sensitive=exclude_case_sensitive,
            regex_rule=regex_rule,
            regex_case_sensitive=regex_case_sensitive
        )
        
        logger.info(f'Text processing complete. Generated {len(frequencies)} unique words.')
        
        # ========================================================================
        # STEP 3: Generate word clouds for each theme (only image generation)
        # ========================================================================
        # If multiple themes, adjust show behavior (don't display all, just save)
        show_clouds = not no_show and not multiple_themes
        
        if multiple_themes:
            logger.info(f'Generating {len(theme_list)} word clouds (one per theme). Each output file will have theme name as suffix (e.g., filename_theme.png).')
        elif len(theme_list) == 1 and theme_list[0] is not None:
            logger.info(f'Generating word cloud with theme: {theme_list[0].name}. Output file will have theme name as suffix (e.g., filename_{theme_list[0].name}.png).')
        elif len(theme_list) == 1 and theme_list[0] is None:
            logger.info('Generating word cloud without theme (using individual color settings). Output file will NOT have theme suffix.')
        
        # Generate word cloud for each theme
        for idx, theme_obj in enumerate(theme_list):
            theme_name = theme_names[idx] if idx < len(theme_names) else "default"
            if theme_obj:
                if multiple_themes:
                    logger.info(f'Generating word cloud {idx + 1}/{len(theme_list)}: {theme_obj.name}')
                else:
                    logger.info(f'Generating word cloud with theme: {theme_obj.name} - {theme_obj.description}')
            else:
                logger.info('Generating word cloud without theme (using individual color settings)')
            
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
            
            # Validate colors if provided manually (theme colors are already validated)
            if bg_color and not theme_obj:
                try:
                    bg_color = validate_color_reference(bg_color)
                except ValidationError as e:
                    logger.error(f'Invalid background color: {e}')
                    raise typer.Exit(code=1)
            if fg_color and not theme_obj:
                try:
                    fg_color = validate_color_reference(fg_color)
                except ValidationError as e:
                    logger.error(f'Invalid font color: {e}')
                    raise typer.Exit(code=1)
            
            # Generate output filename with theme suffix (always add suffix when theme is used)
            theme_output = generate_output_file_with_theme_suffix(
                base_output=output,
                input_file=input,
                theme_name=theme_name if theme_name else "default",
                has_theme=(theme_obj is not None)
            )
            
            # Create configuration object for this theme (only visual settings)
            theme_config = WordCloudConfig(
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
            
            # Generate word cloud from frequencies (only image generation, no text processing)
            show_this_one = show_clouds and idx == 0
            
            generate_word_cloud_from_frequencies(
                frequencies=frequencies,
                config=theme_config,
                output_file=theme_output,
                show=show_this_one
            )
            
            logger.info(f'Word cloud saved to {theme_output}')
        
        # Export statistics if requested (only once, for the first theme)
        if export_stats:
            # Auto-generate stats output filename if not provided
            if stats_output is None:
                if output:
                    stats_output = os.path.splitext(output)[0]
                else:
                    stats_output = os.path.splitext(generate_output_filename(input, '.png'))[0]
            
            # Export both JSON and CSV
            json_file, csv_file = export_statistics(
                frequencies=frequencies,
                base_output_file=stats_output,
                top_n=stats_top_n
            )
            logger.info(f'Statistics exported: {json_file} and {csv_file}')
        
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
    
    This command displays all available themes organized by category,
    making it easy to find the perfect theme for your word cloud.
    """
    from src.themes import list_themes as get_all_themes
    
    themes = get_all_themes()
    
    # Organize themes by category (based on current themes)
    # All themes listed here are built-in themes defined in themes.py
    # Each theme appears only once in its most appropriate category
    categories = {
        'Dark': [
            'blackboard', 'blood', 'bombons', 'fluorescent', 'halloween', 
            'neon', 'night', 'pinky', 'sauvage', 'markers', 'loretta', 'gossip'
        ],
        'Light': [
            'day', 'garden', 'high_contrast', 'homely', 'office', 
            'playroom', 'sakura', 'soft', 'clouds', 'cadiz'
        ],
        'Vibrant': [
            'brazil', 'carrots', 'golden', 'gum', 'piruleta', 'radical', 
            'solarized', 'spring', 'strawberry', 'summer', 'autumn', 'mint'
        ],
        'Elegant': [
            'elegance', 'grey', 'joy', 'old', 'pharaon', 'river', 
            'winter', 'sober'
        ],
        'Nature': [
            'jungle', 'woods', 'stars', 'lake'
        ]
    }
    
    # Track which themes have been categorized
    categorized_themes = set()
    for theme_names_list in categories.values():
        categorized_themes.update(theme_name.lower() for theme_name in theme_names_list)
    
    # Find uncategorized themes
    all_theme_names = set(themes.keys())
    uncategorized = all_theme_names - categorized_themes
    
    print("\n" + "="*70)
    print("Available Word Cloud Themes")
    print("="*70)
    print(f"\nTotal themes: {len(themes)}\n")
    
    # Print categorized themes
    for category, theme_names in categories.items():
        found_themes = []
        for theme_name in theme_names:
            theme = themes.get(theme_name.lower())
            if theme:
                found_themes.append(theme)
        
        if found_themes:  # Only print category if it has themes
            print(f"\n{category}:")
            print("-" * 70)
            for theme in found_themes:
                print(f"  {theme.name:20} - {theme.description}")
    
    # Print uncategorized themes if any
    if uncategorized:
        print(f"\nOther:")
        print("-" * 70)
        for theme_name in sorted(uncategorized):
            theme = themes.get(theme_name.lower())
            if theme:
                print(f"  {theme.name:20} - {theme.description}")
    
    print("\n" + "="*70)
    print("Usage: python nubisary.py generate -i file.txt -l english --theme <theme-name>")
    print("Note: All themes above are built-in themes (defined in themes.py)")
    print("      For custom themes from JSON files, use --custom-theme")
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

