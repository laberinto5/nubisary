"""Font loader for accessing bundled font files in PyInstaller executables.

This module provides utilities to access font files (TTF, OTF)
both in development mode and when bundled as a PyInstaller executable.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource file.
    
    Works both in development mode and when bundled as a PyInstaller executable.
    
    Args:
        relative_path: Relative path from project root (e.g., 'samples/fonts/roboto.ttf')
        
    Returns:
        Absolute path to the resource file
        
    Example:
        >>> font_path = get_resource_path('samples/fonts/roboto.ttf')
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # This is the base path where PyInstaller extracts bundled files
        base_path = sys._MEIPASS
    except AttributeError:
        # Not running as PyInstaller bundle, use current script directory
        # Get the project root (assuming this file is in src/)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


# Mapping from font filename (without extension) to friendly display name
FONT_DISPLAY_NAMES: Dict[str, str] = {
    # Sans Serif (modernas)
    'comfortaa-latin-400-normal': 'Comfortaa',
    'inter-tight-latin-400-normal': 'Inter Tight',
    'urbanist-latin-400-normal': 'Urbanist',
    'outfit-latin-400-normal': 'Outfit',
    'maven-pro-latin-400-normal': 'Maven Pro',
    # Serif (clásicas)
    'courier-prime-latin-400-normal': 'Courier Prime',
    'marcellus-latin-400-normal': 'Marcellus',
    'special-elite-latin-400-normal': 'Special Elite',
    # Monospace (code)
    'kode-mono-latin-400-normal': 'Kode Mono',
    'orbitron-latin-400-normal': 'Orbitron',
    # Handwriting (manuscritas)
    'caveat-latin-400-normal': 'Caveat',
    'pacifico-latin-400-normal': 'Pacifico',
    'cabin-sketch-latin-400-normal': 'Cabin Sketch',
    # Display (decorativas)
    'barrio-latin-400-normal': 'Barrio',
    'chelsea-market-latin-400-normal': 'Chelsea Market',
    'saira-stencil-one-latin-400-normal': 'Saira Stencil One',
    'ribeye-marrow-latin-400-normal': 'Ribeye Marrow',
    'caesar-dressing-latin-400-normal': 'Caesar Dressing',
    'pirata-one-latin-400-normal': 'Pirata One',
    'text-me-one-latin-400-normal': 'Text Me One',
}


def get_font_display_name(font_filename: str) -> str:
    """
    Get friendly display name for a font filename.
    
    Args:
        font_filename: Font filename with or without extension
        
    Returns:
        Friendly display name, or the filename (without extension) if no mapping exists
        
    Example:
        >>> get_font_display_name('roboto-latin-400-normal.ttf')
        'Roboto'
        >>> get_font_display_name('roboto-latin-400-normal')
        'Roboto'
    """
    # Remove extension if present
    font_name = os.path.splitext(os.path.basename(font_filename))[0]
    return FONT_DISPLAY_NAMES.get(font_name, font_name)


def list_font_files(without_extension: bool = False, with_display_names: bool = False) -> List[str]:
    """
    List all available font files in samples/fonts/ directory.
    
    Args:
        without_extension: If True, return filenames without extension (e.g., 'roboto' instead of 'roboto.ttf')
        with_display_names: If True, return display names instead of filenames (e.g., 'Roboto' instead of 'roboto-latin-400-normal')
                           This option requires without_extension=True
    
    Returns:
        List of font filenames or display names (without path), sorted alphabetically
        Returns empty list if fonts directory doesn't exist or has no fonts
        
    Example:
        >>> fonts = list_font_files()
        >>> print(fonts)
        ['montserrat-latin-400-normal.ttf', 'roboto-latin-400-normal.ttf']
        >>> fonts_display = list_font_files(without_extension=True)
        >>> print(fonts_display)
        ['montserrat-latin-400-normal', 'roboto-latin-400-normal']
        >>> fonts_friendly = list_font_files(without_extension=True, with_display_names=True)
        >>> print(fonts_friendly)
        ['Montserrat', 'Roboto']
    """
    if with_display_names and not without_extension:
        raise ValueError("with_display_names=True requires without_extension=True")
    
    fonts_dir = get_resource_path('samples/fonts')
    
    if not os.path.exists(fonts_dir):
        return []
    
    # Supported font extensions
    font_extensions = {'.ttf', '.otf'}
    
    font_files = []
    try:
        for filename in os.listdir(fonts_dir):
            file_path = os.path.join(fonts_dir, filename)
            # Only include files (not directories) with font extensions
            # Exclude Zone.Identifier and other metadata files
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in font_extensions:
                    if with_display_names:
                        # Return friendly display name
                        font_name = os.path.splitext(filename)[0]
                        display_name = get_font_display_name(font_name)
                        font_files.append(display_name)
                    elif without_extension:
                        # Return name without extension
                        font_files.append(os.path.splitext(filename)[0])
                    else:
                        # Return full filename
                        font_files.append(filename)
    except (OSError, PermissionError):
        # Directory exists but can't be read
        return []
    
    # Sort alphabetically, but if using display names, sort by display name
    if with_display_names:
        # Sort by display name, but keep track of original for consistent ordering
        font_files_with_key = [(get_font_display_name(f), f) for f in font_files]
        font_files = [name for name, _ in sorted(font_files_with_key, key=lambda x: x[0])]
    else:
        font_files = sorted(font_files)
    
    return font_files


def get_font_path(font_filename: str) -> Optional[str]:
    """
    Get full path to a font file by filename (with or without extension).
    Works with both technical filenames and display names.
    
    Args:
        font_filename: Name of the font file with or without extension (e.g., 'roboto.ttf', 'roboto', or 'Roboto')
                      If display name provided, will try to find matching font file
                      If no extension provided, tries .ttf first, then .otf
        
    Returns:
        Full path to the font file, or None if file doesn't exist
        
    Example:
        >>> path = get_font_path('roboto.ttf')
        >>> print(path)
        '/path/to/project/samples/fonts/roboto.ttf'
        >>> path = get_font_path('Roboto')  # Display name
        >>> print(path)
        '/path/to/project/samples/fonts/roboto-latin-400-normal.ttf'
        >>> path = get_font_path('roboto')  # Without extension
        >>> print(path)
        '/path/to/project/samples/fonts/roboto.ttf'
    """
    if not font_filename:
        return None
    
    # Check if it's a display name - find matching filename
    font_name = os.path.splitext(os.path.basename(font_filename))[0]
    
    # Reverse lookup: find filename by display name
    for filename, display_name in FONT_DISPLAY_NAMES.items():
        if display_name == font_name:
            # Found matching display name, use the technical filename
            font_name = filename
            break
    
    # Ensure we only use the filename (no path traversal)
    filename = os.path.basename(font_name)
    
    # If filename has no extension, try .ttf first, then .otf
    if not os.path.splitext(filename)[1]:
        # Try .ttf first
        font_path = get_resource_path(os.path.join('samples/fonts', filename + '.ttf'))
        if os.path.exists(font_path) and os.path.isfile(font_path):
            return font_path
        # Try .otf
        font_path = get_resource_path(os.path.join('samples/fonts', filename + '.otf'))
        if os.path.exists(font_path) and os.path.isfile(font_path):
            return font_path
        return None
    
    font_path = get_resource_path(os.path.join('samples/fonts', filename))
    
    if os.path.exists(font_path) and os.path.isfile(font_path):
        return font_path
    
    return None
