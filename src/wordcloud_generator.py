"""WordCloud generation and visualization functions."""

from typing import Dict, Optional, Callable
from wordcloud import WordCloud, get_single_color_func
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from src.config import WordCloudConfig


def create_color_func(font_color: Optional[str], colormap: Optional[str]) -> Optional[Callable]:
    """
    Create a color function for WordCloud.
    
    If colormap is provided, it takes precedence over font_color.
    If font_color is provided (and colormap is None), uses single color.
    If both are None, WordCloud uses default colors.
    
    Args:
        font_color: Color string (hex code or color name) for single color
        colormap: Matplotlib colormap name (e.g., 'viridis', 'plasma') for multi-color
        
    Returns:
        Color function for WordCloud or None
    """
    if colormap is not None:
        # Use colormap - WordCloud will handle this automatically
        # We return None to let WordCloud use colormap parameter
        return None
    elif font_color is not None:
        # Use single color
        return get_single_color_func(font_color)
    else:
        # Use default WordCloud colors
        return None


def load_mask(mask_path: str) -> Optional[np.ndarray]:
    """
    Load a mask image for WordCloud shape.
    
    Args:
        mask_path: Path to mask image file
        
    Returns:
        NumPy array representing the mask, or None if loading fails
    """
    try:
        mask_image = Image.open(mask_path)
        mask_array = np.array(mask_image)
        return mask_array
    except Exception as e:
        raise ValueError(f"Failed to load mask image from {mask_path}: {e}")


def create_wordcloud_instance(config: WordCloudConfig) -> WordCloud:
    """
    Create a configured WordCloud instance.
    
    Args:
        config: WordCloud configuration
        
    Returns:
        Configured WordCloud instance
    """
    # Create color function (handles both single color and colormap)
    color_func = create_color_func(config.font_color, config.colormap)
    
    # Load mask if provided
    mask = None
    if config.mask:
        mask = load_mask(config.mask)
    
    # Build WordCloud parameters
    wordcloud_params = {
        'width': config.canvas_width,
        'height': config.canvas_height,
        'background_color': config.background_color,
        'max_words': config.max_words,
        'min_word_length': config.min_word_length,
        # Plural normalization is handled in text processing, not WordCloud
        'normalize_plurals': False,
        'include_numbers': config.include_numbers,
        'relative_scaling': config.relative_scaling,
        'prefer_horizontal': config.prefer_horizontal
    }
    
    # Add color configuration
    if config.colormap is not None:
        wordcloud_params['colormap'] = config.colormap
    elif color_func is not None:
        wordcloud_params['color_func'] = color_func
    
    # Add mask if provided
    if mask is not None:
        wordcloud_params['mask'] = mask
    
    # Add contour if mask is provided and contour is configured
    if mask is not None and config.contour_width > 0:
        wordcloud_params['contour_width'] = config.contour_width
        if config.contour_color:
            wordcloud_params['contour_color'] = config.contour_color
    
    # Add font path if provided
    if config.font_path:
        wordcloud_params['font_path'] = config.font_path
    
    wordcloud = WordCloud(**wordcloud_params)
    
    return wordcloud


def generate_word_cloud_from_frequencies(
    frequencies: Dict[str, float],
    config: WordCloudConfig,
    output_file: Optional[str] = None,
    show: bool = True
) -> WordCloud:
    """
    Generate and optionally display/save a word cloud from word frequencies.
    
    Args:
        frequencies: Dictionary mapping words to their frequencies
        config: WordCloud configuration
        output_file: Optional path to save the word cloud image
        show: Whether to display the word cloud (default: True)
        
    Returns:
        Generated WordCloud object
    """
    wordcloud = create_wordcloud_instance(config)
    wordcloud.generate_from_frequencies(frequencies)
    
    if show:
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)  # Remove padding/border around image
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove margins
        plt.show()
    
    if output_file is not None:
        # Check if file already exists and log a warning
        import os
        from src.logger import setup_logger
        logger = setup_logger()
        
        if os.path.exists(output_file):
            logger.info(f'Output file already exists: {output_file}. Overwriting with new word cloud.')
        
        wordcloud.to_file(output_file)
    
    return wordcloud


def apply_wordcloud_filters(
    frequencies: Dict[str, float],
    config: WordCloudConfig
) -> Dict[str, float]:
    """
    Apply WordCloud-related filters to a frequency dictionary.
    
    These filters are visual/generation-related, not linguistic:
    - min_word_length
    - include_numbers
    - max_words
    
    Args:
        frequencies: Raw word frequencies (after text transformations)
        config: WordCloud configuration for filters
        
    Returns:
        Filtered frequency dictionary
    """
    # Apply min length and number filters
    filtered = {}
    for word, freq in frequencies.items():
        if config.min_word_length and len(word) < config.min_word_length:
            continue
        if not config.include_numbers and word.isdigit():
            continue
        filtered[word] = freq
    
    # Apply max_words (top N by frequency)
    if config.max_words and len(filtered) > config.max_words:
        sorted_items = sorted(filtered.items(), key=lambda x: (-x[1], x[0]))
        filtered = dict(sorted_items[:config.max_words])
    
    return filtered

