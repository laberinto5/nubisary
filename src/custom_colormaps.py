"""Custom colormap registration for WordCloud themes.

This module provides functions to create and register custom colormaps
that can be used in themes (both built-in and custom).
"""

import matplotlib
from matplotlib.colors import ListedColormap
from typing import List, Optional


def register_custom_colormap(name: str, colors: List[str], description: Optional[str] = None) -> ListedColormap:
    """
    Create and register a custom colormap with matplotlib.
    
    The colormap will be available for use in themes by its name.
    Registration is very fast (< 1ms) and happens in memory only.
    
    Args:
        name: Name for the colormap (must be unique)
        colors: List of color strings (hex codes like '#FF0000' or color names like 'red')
        description: Optional description of the colormap
        
    Returns:
        The registered ListedColormap object
        
    Raises:
        ValueError: If colormap name already exists or colors are invalid
    """
    if not name or not name.strip():
        raise ValueError("Colormap name cannot be empty")
    
    name = name.strip()
    
    # Check if colormap already exists
    if name in matplotlib.colormaps:
        raise ValueError(f"Colormap '{name}' already exists")
    
    if not colors or len(colors) < 2:
        raise ValueError("Colormap must have at least 2 colors")
    
    # Create ListedColormap from color list
    # ListedColormap creates a discrete colormap from a list of colors
    custom_cmap = ListedColormap(colors, name=name, N=len(colors))
    
    # Register with matplotlib
    matplotlib.colormaps.register(custom_cmap)
    
    return custom_cmap


def register_colormaps_from_config(colormaps_config: List[dict]) -> None:
    """
    Register multiple colormaps from a configuration list.
    
    Args:
        colormaps_config: List of dictionaries, each containing:
            - 'name': Colormap name (required)
            - 'colors': List of color strings (required)
            - 'description': Optional description
            
    Raises:
        ValueError: If configuration is invalid
    """
    for cmap_config in colormaps_config:
        if not isinstance(cmap_config, dict):
            raise ValueError("Each colormap config must be a dictionary")
        
        name = cmap_config.get('name')
        colors = cmap_config.get('colors')
        
        if not name:
            raise ValueError("Colormap config missing 'name' field")
        if not colors:
            raise ValueError(f"Colormap '{name}' missing 'colors' field")
        
        description = cmap_config.get('description')
        try:
            register_custom_colormap(name, colors, description)
        except ValueError as e:
            # If it already exists, skip (allow overriding with warning)
            if "already exists" in str(e):
                import warnings
                warnings.warn(f"Colormap '{name}' already exists, skipping")
            else:
                raise


def is_colormap_registered(name: str) -> bool:
    """
    Check if a colormap is registered in matplotlib.
    
    Args:
        name: Colormap name to check
        
    Returns:
        True if colormap exists, False otherwise
    """
    return name in matplotlib.colormaps

