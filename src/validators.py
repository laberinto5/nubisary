"""Validation functions for Word Cloud Generator."""

import os
import re
from typing import Optional
import nltk
from nltk.corpus import stopwords

from src.config import LANGUAGES_FOR_NLTK, WORDCLOUD_COLORS


class ValidationError(Exception):
    """Base exception for validation errors."""
    pass


class ColorValidationError(ValidationError):
    """Exception raised when color validation fails."""
    pass


class LanguageValidationError(ValidationError):
    """Exception raised when language validation fails."""
    pass


class FileValidationError(ValidationError):
    """Exception raised when file validation fails."""
    pass


def validate_color_reference(color: Optional[str]) -> Optional[str]:
    """
    Validate a color reference (hex code or color name).
    
    Args:
        color: Color string (hex code like "#FF0000" or color name like "red")
        
    Returns:
        Validated color string or None if invalid
        
    Raises:
        ColorValidationError: If color format is invalid
    """
    if color is None:
        return None
        
    if not color.startswith('#'):
        # Color name validation
        if color not in WORDCLOUD_COLORS:
            raise ColorValidationError(
                f'Invalid color reference: {color}. '
                f'Valid colors are: {WORDCLOUD_COLORS} or hex codes like "#FF0000"'
            )
    else:
        # Hex code validation
        if len(color) != 7 or not all(c in '0123456789ABCDEFabcdef' for c in color[1:]):
            raise ColorValidationError(
                f'Invalid hex color code: {color}. '
                f'Expected format: "#RRGGBB" (e.g., "#FF0000")'
            )
    
    return color


def validate_language(language: str, include_stopwords: bool = False) -> str:
    """
    Validate language and ensure NLTK resources are available.
    
    Args:
        language: Language code (e.g., 'english', 'spanish')
        include_stopwords: Whether stopwords will be used
        
    Returns:
        Validated language string
        
    Raises:
        LanguageValidationError: If language is not supported or resources unavailable
    """
    if language not in LANGUAGES_FOR_NLTK:
        raise LanguageValidationError(
            f'Language "{language}" is not supported. '
            f'Supported languages: {LANGUAGES_FOR_NLTK}'
        )
    
    # Download required NLTK resources
    try:
        nltk.download('punkt', quiet=True)
    except Exception as e:
        raise LanguageValidationError(
            f'Failed to download NLTK punkt tokenizer: {e}'
        )
    
    # Check if stopwords are available (needed if not including stopwords)
    if not include_stopwords:
        try:
            stopwords.words(language)
        except LookupError:
            try:
                nltk.download('stopwords', quiet=True)
                # Verify it worked
                stopwords.words(language)
            except Exception as e:
                raise LanguageValidationError(
                    f'Failed to download or access NLTK stopwords for {language}: {e}'
                )
    
    return language


def validate_input_file(input_file: str) -> str:
    """
    Validate that input file exists and is readable.
    
    Args:
        input_file: Path to input file
        
    Returns:
        Validated file path
        
    Raises:
        FileValidationError: If file does not exist or is not readable
    """
    if not os.path.isfile(input_file):
        raise FileValidationError(
            f'Input file does not exist: {input_file}'
        )
    
    if not os.access(input_file, os.R_OK):
        raise FileValidationError(
            f'Input file is not readable: {input_file}'
        )
    
    return input_file


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Keeps only letters, numbers, hyphens, and underscores.
    Replaces spaces and other invalid characters with underscores.
    
    Args:
        filename: Original filename (without extension)
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove extension if present
    name_without_ext = os.path.splitext(filename)[0]
    
    # Replace spaces and invalid characters with underscores
    # Keep only alphanumeric, hyphens, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name_without_ext)
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # If empty after sanitization, use a default name
    if not sanitized:
        sanitized = 'wordcloud'
    
    return sanitized


def generate_output_filename(input_file: str, extension: str = '.png') -> str:
    """
    Generate output filename based on input file.
    
    The output file will be in the same directory as the input file,
    with the same base name (sanitized) and the specified extension.
    
    Args:
        input_file: Path to input file
        extension: File extension (default: '.png')
        
    Returns:
        Full path to output file
    """
    # Get directory and base name from input file
    input_dir = os.path.dirname(os.path.abspath(input_file))
    input_basename = os.path.basename(input_file)
    
    # Sanitize the filename
    sanitized_name = sanitize_filename(input_basename)
    
    # Construct output path
    output_file = os.path.join(input_dir, sanitized_name + extension)
    
    return output_file


def validate_output_file(output_file: Optional[str], input_file: Optional[str] = None) -> Optional[str]:
    """
    Validate and normalize output file path.
    
    If output_file is None and input_file is provided, automatically generates
    output filename based on input file (same directory, sanitized name, .png extension).
    
    Args:
        output_file: Path to output file (can be None)
        input_file: Path to input file (used for auto-generation if output_file is None)
        
    Returns:
        Normalized output file path with .png extension, or None if no output needed
    """
    # Auto-generate output filename if not provided
    if output_file is None and input_file is not None:
        output_file = generate_output_filename(input_file, '.png')
    
    if output_file is None:
        return None
    
    # Ensure .png extension
    if not output_file.endswith('.png'):
        output_file = output_file + '.png'
    
    return output_file

