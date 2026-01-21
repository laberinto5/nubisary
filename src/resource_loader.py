"""Resource loader for accessing bundled files in PyInstaller executables.

This module provides utilities to access resource files (like masks, themes, etc.)
both in development mode and when bundled as a PyInstaller executable.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource file.
    
    Works both in development mode and when bundled as PyInstaller executable.
    
    Args:
        relative_path: Relative path from project root (e.g., 'samples/masks/heart.png')
        
    Returns:
        Absolute path to the resource file
        
    Example:
        >>> mask_path = get_resource_path('samples/masks/heart.png')
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


def list_mask_files(without_extension: bool = False) -> List[str]:
    """
    List all available mask files in samples/masks/ directory.
    
    Args:
        without_extension: If True, return filenames without extension (e.g., 'circle' instead of 'circle.png')
    
    Returns:
        List of mask filenames (without path), sorted alphabetically
        Returns empty list if masks directory doesn't exist or has no images
        
    Example:
        >>> masks = list_mask_files()
        >>> print(masks)
        ['circle.png', 'heart.png', 'star.png']
        >>> masks_display = list_mask_files(without_extension=True)
        >>> print(masks_display)
        ['circle', 'heart', 'star']
    """
    masks_dir = get_resource_path('samples/masks')
    
    if not os.path.exists(masks_dir):
        return []
    
    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'}
    
    mask_files = []
    try:
        for filename in os.listdir(masks_dir):
            file_path = os.path.join(masks_dir, filename)
            # Only include files (not directories) with image extensions
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in image_extensions:
                    if without_extension:
                        # Return name without extension
                        mask_files.append(os.path.splitext(filename)[0])
                    else:
                        # Return full filename
                        mask_files.append(filename)
    except (OSError, PermissionError):
        # Directory exists but can't be read
        return []
    
    return sorted(mask_files)


def get_mask_path(mask_filename: str) -> Optional[str]:
    """
    Get full path to a mask file by filename (with or without extension).
    
    Args:
        mask_filename: Name of the mask file with or without extension (e.g., 'heart.png' or 'heart')
                      If no extension provided, tries .png first
        
    Returns:
        Full path to the mask file, or None if file doesn't exist
        
    Example:
        >>> path = get_mask_path('heart.png')
        >>> print(path)
        '/path/to/project/samples/masks/heart.png'
        >>> path = get_mask_path('heart')  # Without extension
        >>> print(path)
        '/path/to/project/samples/masks/heart.png'
    """
    if not mask_filename:
        return None
    
    # Ensure we only use the filename (no path traversal)
    filename = os.path.basename(mask_filename)
    
    # If filename has no extension, assume .png (all masks are PNG)
    if not os.path.splitext(filename)[1]:
        filename = filename + '.png'
    
    mask_path = get_resource_path(os.path.join('samples/masks', filename))
    
    if os.path.exists(mask_path) and os.path.isfile(mask_path):
        return mask_path
    
    return None


def resource_exists(relative_path: str) -> bool:
    """
    Check if a resource file exists.
    
    Args:
        relative_path: Relative path from project root
        
    Returns:
        True if file exists, False otherwise
    """
    resource_path = get_resource_path(relative_path)
    return os.path.exists(resource_path) and os.path.isfile(resource_path)

