"""Custom theme loading from JSON files.

This module provides functions to load custom themes from JSON files.
Custom themes can use both matplotlib built-in colormaps and custom colormaps
defined in the same JSON file.
"""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path

from src.themes import Theme, register_theme
from src.custom_colormaps import register_custom_colormap, register_colormaps_from_config, CustomColormapError
from src.file_handlers import FileHandlerError


class CustomThemeError(Exception):
    """Exception raised when loading custom themes fails."""
    pass


def load_custom_theme_from_json(json_file: str) -> Theme:
    """
    Load a custom theme from a JSON file.
    
    The JSON file should contain a theme definition with optional custom colormaps.
    If custom colormaps are defined, they are registered before the theme is created.
    
    JSON Format:
    {
        "theme": {
            "name": "my-custom-theme",
            "background_color": "#1a1a2e",
            "colormap": "my_custom_colormap",  // or null to use font_color
            "font_color": null,  // or color string if not using colormap
            "relative_scaling": 0.6,
            "prefer_horizontal": 0.85,
            "description": "My custom theme description"
        },
        "custom_colormaps": [  // Optional
            {
                "name": "my_custom_colormap",
                "colors": ["#FF0000", "#00FF00", "#0000FF"],
                "description": "Custom colormap description"
            }
        ]
    }
    
    Args:
        json_file: Path to JSON file containing theme definition
        
    Returns:
        Theme object that has been registered in the themes registry
        
    Raises:
        CustomThemeError: If file cannot be read or theme definition is invalid
        FileHandlerError: If file I/O fails
    """
    if not os.path.isfile(json_file):
        raise FileHandlerError(f"Custom theme file does not exist: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise CustomThemeError(f"Invalid JSON in custom theme file {json_file}: {e}")
    except Exception as e:
        raise FileHandlerError(f"Error reading custom theme file {json_file}: {e}")
    
    # Register custom colormaps first (if any)
    if 'custom_colormaps' in data:
        if not isinstance(data['custom_colormaps'], list):
            raise CustomThemeError("'custom_colormaps' must be a list")
        
        try:
            register_colormaps_from_config(data['custom_colormaps'])
        except CustomColormapError as e:
            raise CustomThemeError(f"Error registering custom colormaps: {e}")
    
    # Load theme definition
    if 'theme' not in data:
        raise CustomThemeError("JSON file must contain a 'theme' object")
    
    theme_data = data['theme']
    
    # Validate required fields
    if 'name' not in theme_data:
        raise CustomThemeError("Theme must have a 'name' field")
    if 'background_color' not in theme_data:
        raise CustomThemeError("Theme must have a 'background_color' field")
    
    # Extract theme fields with defaults
    name = theme_data['name'].strip()
    if not name:
        raise CustomThemeError("Theme name cannot be empty")
    
    background_color = theme_data['background_color']
    colormap = theme_data.get('colormap')  # Optional
    font_color = theme_data.get('font_color')  # Optional
    relative_scaling = theme_data.get('relative_scaling', 0.5)
    prefer_horizontal = theme_data.get('prefer_horizontal', 0.9)
    description = theme_data.get('description', '')
    
    # Validate colormap/font_color: at least one should be None
    if colormap is not None and font_color is not None:
        # Both set: colormap takes precedence, but warn
        import warnings
        warnings.warn(
            f"Theme '{name}' has both 'colormap' and 'font_color' set. "
            "Colormap will be used (font_color will be ignored)."
        )
    
    # Validate numeric fields
    if not isinstance(relative_scaling, (int, float)) or relative_scaling < 0 or relative_scaling > 1:
        raise CustomThemeError(
            f"Theme '{name}' has invalid 'relative_scaling' ({relative_scaling}). "
            "Must be a number between 0.0 and 1.0"
        )
    
    if not isinstance(prefer_horizontal, (int, float)) or prefer_horizontal < 0 or prefer_horizontal > 1:
        raise CustomThemeError(
            f"Theme '{name}' has invalid 'prefer_horizontal' ({prefer_horizontal}). "
            "Must be a number between 0.0 and 1.0"
        )
    
    # Verify colormap exists (if specified)
    if colormap is not None:
        import matplotlib
        if colormap not in matplotlib.colormaps:
            raise CustomThemeError(
                f"Theme '{name}' references colormap '{colormap}' which is not registered. "
                "Make sure to define it in 'custom_colormaps' section or use a built-in matplotlib colormap."
            )
    
    # Create and register theme
    theme = Theme(
        name=name,
        background_color=background_color,
        colormap=colormap,
        font_color=font_color,
        relative_scaling=float(relative_scaling),
        prefer_horizontal=float(prefer_horizontal),
        description=description
    )
    
    # Register theme (will overwrite if name exists)
    register_theme(theme)
    
    return theme


def validate_custom_theme_json(json_file: str) -> Dict:
    """
    Validate a custom theme JSON file without registering the theme.
    
    Useful for checking JSON structure before attempting to load.
    
    Args:
        json_file: Path to JSON file
        
    Returns:
        Parsed JSON data if valid
        
    Raises:
        CustomThemeError: If JSON is invalid or theme definition is incorrect
        FileHandlerError: If file cannot be read
    """
    if not os.path.isfile(json_file):
        raise FileHandlerError(f"Custom theme file does not exist: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise CustomThemeError(f"Invalid JSON in custom theme file {json_file}: {e}")
    except Exception as e:
        raise FileHandlerError(f"Error reading custom theme file {json_file}: {e}")
    
    # Validate structure (without actually registering)
    if 'theme' not in data:
        raise CustomThemeError("JSON file must contain a 'theme' object")
    
    theme_data = data['theme']
    
    required_fields = ['name', 'background_color']
    for field in required_fields:
        if field not in theme_data:
            raise CustomThemeError(f"Theme must have a '{field}' field")
    
    if 'custom_colormaps' in data and not isinstance(data['custom_colormaps'], list):
        raise CustomThemeError("'custom_colormaps' must be a list")
    
    return data


def save_theme_to_json(theme: Theme, custom_colormap: Optional[Dict] = None, output_file: str = None) -> str:
    """
    Save a theme to a JSON file.
    
    Args:
        theme: Theme object to save
        custom_colormap: Optional dict with colormap data (name, colors, description)
        output_file: Path to output JSON file (if None, uses theme name)
        
    Returns:
        Path to the saved JSON file
        
    Raises:
        CustomThemeError: If theme is invalid or file cannot be written
        FileHandlerError: If file I/O fails
    """
    # Validate theme
    if not theme.name or not theme.name.strip():
        raise CustomThemeError("Theme name cannot be empty")
    if not theme.background_color or not theme.background_color.strip():
        raise CustomThemeError("Theme background_color cannot be empty")
    
    # Determine output file path
    if output_file is None:
        # Use theme name as filename
        safe_name = theme.name.lower().replace(' ', '_').replace('/', '_')
        output_file = f"{safe_name}_theme.json"
    
    # Ensure .json extension
    if not output_file.endswith('.json'):
        output_file = output_file + '.json'
    
    # Build JSON structure
    data = {
        "theme": {
            "name": theme.name,
            "background_color": theme.background_color,
            "colormap": theme.colormap,
            "font_color": theme.font_color,
            "relative_scaling": theme.relative_scaling,
            "prefer_horizontal": theme.prefer_horizontal,
            "description": theme.description or ""
        }
    }
    
    # Add custom colormap if provided
    if custom_colormap:
        data["custom_colormaps"] = [custom_colormap]
    
    # Write JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise FileHandlerError(f"Error writing custom theme file {output_file}: {e}")
    
    return output_file

