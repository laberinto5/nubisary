"""Theme definitions for WordCloud visual presets.

This module provides 34 preset themes for word cloud generation.
Each theme combines background colors, colormaps, and visual settings
for beautiful, ready-to-use word clouds.

For complete theme documentation, see THEMES.md in the project root.
"""

from dataclasses import dataclass
from typing import Optional, Dict
from src.config import WordCloudConfig

# Available themes registry
THEMES: Dict[str, 'Theme'] = {}


@dataclass
class Theme:
    """Theme configuration for WordCloud generation."""
    
    name: str
    background_color: str
    colormap: Optional[str] = None  # None = use font_color
    font_color: Optional[str] = None  # None = use colormap
    relative_scaling: float = 0.5
    prefer_horizontal: float = 0.9
    description: str = ""
    
    def apply_to_config(self, config: WordCloudConfig) -> WordCloudConfig:
        """
        Apply theme settings to a WordCloudConfig.
        
        Only overrides settings that are None/default in the config.
        This allows users to override theme settings with individual flags.
        
        Args:
            config: WordCloudConfig to apply theme to
            
        Returns:
            New WordCloudConfig with theme applied
        """
        # Create a copy of the config
        new_config = WordCloudConfig(
            canvas_width=config.canvas_width,
            canvas_height=config.canvas_height,
            max_words=config.max_words,
            min_word_length=config.min_word_length,
            normalize_plurals=config.normalize_plurals,
            include_numbers=config.include_numbers,
            background_color=config.background_color or self.background_color,
            font_color=config.font_color if config.font_color is not None else self.font_color,
            colormap=config.colormap if config.colormap is not None else self.colormap,
            relative_scaling=config.relative_scaling if config.relative_scaling != 0.5 else self.relative_scaling,
            prefer_horizontal=config.prefer_horizontal if config.prefer_horizontal != 0.9 else self.prefer_horizontal,
            mask=config.mask,
            contour_width=config.contour_width,
            contour_color=config.contour_color,
            font_path=config.font_path,
            language=config.language,
            include_stopwords=config.include_stopwords,
            case_sensitive=config.case_sensitive,
            collocations=config.collocations
        )
        return new_config


def register_theme(theme: Theme) -> None:
    """Register a theme in the global themes registry."""
    THEMES[theme.name.lower()] = theme


def get_theme(name: str) -> Optional[Theme]:
    """
    Get a theme by name (case-insensitive).
    
    Args:
        name: Theme name
        
    Returns:
        Theme object or None if not found
    """
    return THEMES.get(name.lower())


def list_themes() -> Dict[str, Theme]:
    """Get all registered themes."""
    return THEMES.copy()


def get_theme_names() -> list:
    """Get list of all registered theme names."""
    return sorted(THEMES.keys())


# Define preset themes
_classic = Theme(
    name="classic",
    background_color="white",
    font_color="black",
    colormap=None,
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Classic white background with black text. Simple and clean."
)
register_theme(_classic)

_vibrant = Theme(
    name="vibrant",
    background_color="#1a1a1a",
    font_color=None,
    colormap="viridis",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Dark background with vibrant viridis colormap. Modern and colorful."
)
register_theme(_vibrant)

_ocean = Theme(
    name="ocean",
    background_color="#0a1929",
    font_color=None,
    colormap="coolwarm",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Deep blue background with cool colormap. Calm and professional."
)
register_theme(_ocean)

_sunset = Theme(
    name="sunset",
    background_color="#2d1b0e",
    font_color=None,
    colormap="plasma",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Warm orange/red background with plasma colormap. Warm and energetic."
)
register_theme(_sunset)

_minimal = Theme(
    name="minimal",
    background_color="white",
    font_color="#666666",
    colormap=None,
    relative_scaling=0.6,
    prefer_horizontal=0.95,
    description="White background with grey text. Clean and professional."
)
register_theme(_minimal)

_dark_mode = Theme(
    name="dark",
    background_color="black",
    font_color=None,
    colormap="Set3",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Black background with bright colormap. Modern and eye-catching."
)
register_theme(_dark_mode)

_pastel = Theme(
    name="pastel",
    background_color="#f5f5f5",
    font_color=None,
    colormap="Pastel1",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light background with pastel colormap. Soft and gentle."
)
register_theme(_pastel)

_high_contrast = Theme(
    name="high-contrast",
    background_color="white",
    font_color="black",
    colormap=None,
    relative_scaling=0.3,
    prefer_horizontal=0.9,
    description="High contrast white/black with dramatic size differences. Accessible and clear."
)
register_theme(_high_contrast)

# Additional themes with different colormaps
_inferno = Theme(
    name="inferno",
    background_color="#0d0d0d",
    font_color=None,
    colormap="inferno",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Dark background with inferno colormap. Fiery and intense."
)
register_theme(_inferno)

_magma = Theme(
    name="magma",
    background_color="#0c0c0c",
    font_color=None,
    colormap="magma",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Very dark background with magma colormap. Volcanic and powerful."
)
register_theme(_magma)

_spring = Theme(
    name="spring",
    background_color="#f0f8f0",
    font_color=None,
    colormap="spring",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light green background with spring colormap. Fresh and vibrant."
)
register_theme(_spring)

_summer = Theme(
    name="summer",
    background_color="#fff8e1",
    font_color=None,
    colormap="summer",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Warm yellow background with summer colormap. Bright and cheerful."
)
register_theme(_summer)

_autumn = Theme(
    name="autumn",
    background_color="#fff3e0",
    font_color=None,
    colormap="autumn",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Warm orange background with autumn colormap. Cozy and warm."
)
register_theme(_autumn)

_winter = Theme(
    name="winter",
    background_color="#e3f2fd",
    font_color=None,
    colormap="winter",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Cool blue background with winter colormap. Calm and serene."
)
register_theme(_winter)

_cool = Theme(
    name="cool",
    background_color="#e0f2f1",
    font_color=None,
    colormap="cool",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light cyan background with cool colormap. Refreshing and modern."
)
register_theme(_cool)

_hot = Theme(
    name="hot",
    background_color="#1a0000",
    font_color=None,
    colormap="hot",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Dark red background with hot colormap. Intense and energetic."
)
register_theme(_hot)

_rainbow = Theme(
    name="rainbow",
    background_color="#f5f5f5",
    font_color=None,
    colormap="rainbow",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light background with rainbow colormap. Colorful and playful."
)
register_theme(_rainbow)

_jet = Theme(
    name="jet",
    background_color="#000814",
    font_color=None,
    colormap="jet",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Very dark background with jet colormap. Classic and vibrant."
)
register_theme(_jet)

_turbo = Theme(
    name="turbo",
    background_color="#0a0a0a",
    font_color=None,
    colormap="turbo",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Dark background with turbo colormap. Modern and dynamic."
)
register_theme(_turbo)

_blues = Theme(
    name="blues",
    background_color="#e3f2fd",
    font_color=None,
    colormap="Blues",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light blue background with Blues colormap. Professional and calm."
)
register_theme(_blues)

_greens = Theme(
    name="greens",
    background_color="#e8f5e9",
    font_color=None,
    colormap="Greens",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light green background with Greens colormap. Natural and fresh."
)
register_theme(_greens)

_reds = Theme(
    name="reds",
    background_color="#ffebee",
    font_color=None,
    colormap="Reds",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light red background with Reds colormap. Bold and passionate."
)
register_theme(_reds)

_purples = Theme(
    name="purples",
    background_color="#f3e5f5",
    font_color=None,
    colormap="Purples",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light purple background with Purples colormap. Elegant and creative."
)
register_theme(_purples)

_oranges = Theme(
    name="oranges",
    background_color="#fff3e0",
    font_color=None,
    colormap="Oranges",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light orange background with Oranges colormap. Warm and inviting."
)
register_theme(_oranges)

_spectral = Theme(
    name="spectral",
    background_color="#fafafa",
    font_color=None,
    colormap="Spectral",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light grey background with Spectral colormap. Colorful and balanced."
)
register_theme(_spectral)

_rdbu = Theme(
    name="rdbu",
    background_color="#f5f5f5",
    font_color=None,
    colormap="RdBu",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light grey background with Red-Blue diverging colormap. Contrasting and clear."
)
register_theme(_rdbu)

_set1 = Theme(
    name="set1",
    background_color="#ffffff",
    font_color=None,
    colormap="Set1",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="White background with Set1 qualitative colormap. Bold and distinct colors."
)
register_theme(_set1)

_set2 = Theme(
    name="set2",
    background_color="#fafafa",
    font_color=None,
    colormap="Set2",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light grey background with Set2 qualitative colormap. Muted and harmonious."
)
register_theme(_set2)

_pastel2 = Theme(
    name="pastel2",
    background_color="#f9f9f9",
    font_color=None,
    colormap="Pastel2",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Very light background with Pastel2 colormap. Soft and gentle."
)
register_theme(_pastel2)

_dark2 = Theme(
    name="dark2",
    background_color="#1a1a1a",
    font_color=None,
    colormap="Dark2",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Dark background with Dark2 qualitative colormap. Rich and sophisticated."
)
register_theme(_dark2)

_tab10 = Theme(
    name="tab10",
    background_color="#ffffff",
    font_color=None,
    colormap="tab10",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="White background with tab10 colormap. Modern and accessible."
)
register_theme(_tab10)

_tab20 = Theme(
    name="tab20",
    background_color="#f5f5f5",
    font_color=None,
    colormap="tab20",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="Light grey background with tab20 colormap. Wide color variety."
)
register_theme(_tab20)

_accent = Theme(
    name="accent",
    background_color="#ffffff",
    font_color=None,
    colormap="Accent",
    relative_scaling=0.5,
    prefer_horizontal=0.9,
    description="White background with Accent colormap. Distinctive and vibrant."
)
register_theme(_accent)
