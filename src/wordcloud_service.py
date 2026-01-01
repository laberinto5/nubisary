"""High-level service API for Word Cloud generation.
This module provides the main interface that can be used by both CLI and GUI.
"""

from typing import Dict, Optional
import logging

from src.config import WordCloudConfig, AppConfig
from src.validators import (
    validate_color_reference,
    validate_language,
    validate_input_file,
    validate_output_file,
    ValidationError
)
from src.file_handlers import (
    is_json_file,
    read_text_file,
    read_json_file,
    validate_json_format,
    FileHandlerError,
    JSONParseError
)
from src.document_converter import (
    is_convertible_document,
    DocumentConversionError
)
from src.text_processor import preprocess_text, generate_word_count_from_text
from src.wordcloud_generator import generate_word_cloud_from_frequencies
from src.statistics_exporter import export_statistics
from src.logger import setup_logger

# Setup logger
logger = setup_logger()


class WordCloudServiceError(Exception):
    """Base exception for service errors."""
    pass


def generate_wordcloud(
    input_file: str,
    language: str,
    output_file: Optional[str] = None,
    config: Optional[WordCloudConfig] = None,
    show: bool = True,
    clean_text: bool = True,
    export_stats: bool = False,
    stats_output: Optional[str] = None,
    stats_top_n: Optional[int] = None
) -> Dict[str, float]:
    """
    High-level function to generate a word cloud from a text or JSON file.
    
    This is the main API that should be used by both CLI and GUI interfaces.
    
    Args:
        input_file: Path to input file (text, JSON, PDF, DOC, or DOCX)
        language: Language code for text processing (required for text files)
        output_file: Optional path to save the word cloud image
        config: Optional WordCloudConfig object (uses defaults if not provided)
        show: Whether to display the word cloud (default: True)
        clean_text: If True, apply text cleaning when converting documents (default: True)
        export_stats: If True, export word frequencies to JSON and CSV (default: False)
        stats_output: Optional base path for statistics files (auto-generate if None)
        stats_top_n: Optional number of top words to export (None = all words)
        
    Returns:
        Dictionary mapping words to their frequencies
        
    Raises:
        WordCloudServiceError: For any service-level errors
        ValidationError: For validation errors
        FileHandlerError: For file I/O errors
    """
    try:
        # Initialize config if not provided
        if config is None:
            config = WordCloudConfig()
        
        # Validate and normalize output file (auto-generate if not provided)
        output_file = validate_output_file(output_file, input_file)
        
        # Validate input file
        validate_input_file(input_file)
        
        # Check if input is JSON
        is_json = is_json_file(input_file)
        
        # Check if input is a convertible document
        is_document = is_convertible_document(input_file) if not is_json else False
        
        # Validate JSON format if applicable
        if is_json:
            validate_json_format(input_file)
        else:
            # Validate language for text files (including documents that will be converted)
            validate_language(language, config.include_stopwords)
        
        # Validate colors
        if config.background_color:
            config.background_color = validate_color_reference(config.background_color)
        if config.font_color:
            config.font_color = validate_color_reference(config.font_color)
        
        # Log settings
        logger.info('Settings:')
        logger.info(f'  - Input file: {input_file}')
        logger.info(f'  - Output file: {output_file}')
        if is_json:
            logger.info(f'  - Input format: JSON')
        elif is_document:
            logger.info(f'  - Input format: Document (will be converted to text)')
        else:
            logger.info(f'  - Input format: Text')
        if not is_json:
            logger.info(f'  - Language: {language}')
            logger.info(f'  - Case sensitive: {config.case_sensitive}')
            logger.info(f'  - Stopwords included: {config.include_stopwords}')
            logger.info(f'  - Collocations: {config.collocations}')
            logger.info(f'  - Normalize plurals: {config.normalize_plurals}')
            logger.info(f'  - Include numbers: {config.include_numbers}')
        logger.info(f'  - Background color: {config.background_color}')
        if config.colormap:
            logger.info(f'  - Colormap: {config.colormap}')
        else:
            logger.info(f'  - Font color: {config.font_color}')
        logger.info(f'  - Relative scaling: {config.relative_scaling}')
        logger.info(f'  - Prefer horizontal: {config.prefer_horizontal}')
        if config.mask:
            logger.info(f'  - Mask: {config.mask}')
            if config.contour_width > 0:
                logger.info(f'  - Contour width: {config.contour_width}')
                logger.info(f'  - Contour color: {config.contour_color}')
        if config.font_path:
            logger.info(f'  - Font path: {config.font_path}')
        logger.info(f'  - Max words: {config.max_words}')
        logger.info(f'  - Min word length: {config.min_word_length}')
        logger.info(f'  - Canvas size: {config.canvas_width}x{config.canvas_height}')
        
        # Process input based on type
        if is_json:
            # Read frequencies from JSON
            frequencies = read_json_file(input_file)
            logger.info('Loaded word frequencies from JSON file')
        else:
            # Read and process text file (auto-converts documents if needed)
            if is_document:
                logger.info(f'Converting document to text...')
                if clean_text:
                    logger.info(f'Text cleaning enabled (removing page numbers, excessive blank lines)')
            text = read_text_file(input_file, auto_convert=True, clean_text=clean_text)
            if is_document:
                logger.info(f'Document converted successfully')
            text_processed = preprocess_text(text, config.case_sensitive)
            
            # Generate word frequencies
            frequencies = generate_word_count_from_text(
                text=text_processed,
                language=language,
                include_stopwords=config.include_stopwords,
                collocations=config.collocations,
                max_words=config.max_words,
                min_word_length=config.min_word_length,
                normalize_plurals=config.normalize_plurals,
                include_numbers=config.include_numbers,
                canvas_width=config.canvas_width,
                canvas_height=config.canvas_height
            )
            logger.info(f'Generated word frequencies from text ({len(frequencies)} unique words)')
        
        # Generate and display/save word cloud
        generate_word_cloud_from_frequencies(
            frequencies=frequencies,
            config=config,
            output_file=output_file,
            show=show
        )
        
        if output_file:
            logger.info(f'Word cloud saved to {output_file}')
        
        # Export statistics if requested
        if export_stats:
            # Auto-generate stats output filename if not provided
            if stats_output is None:
                import os
                from src.validators import generate_output_filename
                if output_file:
                    # Use output file base name (already sanitized)
                    stats_output = os.path.splitext(output_file)[0]
                else:
                    # Generate from input file (will be sanitized)
                    stats_output = os.path.splitext(generate_output_filename(input_file, '.png'))[0]
            
            # Export both JSON and CSV
            json_file, csv_file = export_statistics(
                frequencies=frequencies,
                base_output_file=stats_output,
                top_n=stats_top_n
            )
            logger.info(f'Statistics exported: {json_file} and {csv_file}')
        
        return frequencies
        
    except (ValidationError, FileHandlerError, JSONParseError) as e:
        logger.error(str(e))
        raise WordCloudServiceError(str(e)) from e
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        raise WordCloudServiceError(f'Unexpected error: {e}') from e

