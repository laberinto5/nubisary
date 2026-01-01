"""Unit tests for themes module."""

import pytest
from src.themes import Theme, get_theme, get_theme_names, list_themes, register_theme
from src.config import WordCloudConfig


class TestTheme:
    """Tests for Theme dataclass."""
    
    def test_theme_creation(self):
        """Test creating a theme."""
        theme = Theme(
            name="test",
            background_color="white",
            font_color="black",
            description="Test theme"
        )
        assert theme.name == "test"
        assert theme.background_color == "white"
        assert theme.font_color == "black"
        assert theme.description == "Test theme"
        assert theme.relative_scaling == 0.5  # default
        assert theme.prefer_horizontal == 0.9  # default
    
    def test_theme_with_colormap(self):
        """Test theme with colormap instead of font_color."""
        theme = Theme(
            name="test",
            background_color="black",
            colormap="viridis",
            description="Test with colormap"
        )
        assert theme.colormap == "viridis"
        assert theme.font_color is None
    
    def test_apply_to_config(self):
        """Test applying theme to config."""
        theme = Theme(
            name="test",
            background_color="red",
            font_color="blue",
            relative_scaling=0.3,
            prefer_horizontal=0.7
        )
        
        config = WordCloudConfig()
        new_config = theme.apply_to_config(config)
        
        assert new_config.background_color == "red"
        assert new_config.font_color == "blue"
        assert new_config.relative_scaling == 0.3
        assert new_config.prefer_horizontal == 0.7
    
    def test_apply_to_config_preserves_custom_settings(self):
        """Test that custom config settings are preserved when applying theme."""
        theme = Theme(
            name="test",
            background_color="red",
            font_color="blue",
            relative_scaling=0.3
        )
        
        config = WordCloudConfig(
            canvas_width=800,
            max_words=100,
            background_color="green",  # Custom, should be preserved
            relative_scaling=0.8  # Custom, should be preserved
        )
        
        new_config = theme.apply_to_config(config)
        
        # Custom settings preserved
        assert new_config.canvas_width == 800
        assert new_config.max_words == 100
        assert new_config.background_color == "green"  # Custom preserved
        assert new_config.relative_scaling == 0.8  # Custom preserved
        
        # Theme settings applied where not custom
        assert new_config.font_color == "blue"  # From theme
        assert new_config.prefer_horizontal == 0.9  # Default (theme default)


class TestThemeRegistry:
    """Tests for theme registry functions."""
    
    def test_register_and_get_theme(self):
        """Test registering and retrieving a theme."""
        theme = Theme(
            name="custom",
            background_color="purple",
            font_color="yellow",
            description="Custom theme"
        )
        
        register_theme(theme)
        retrieved = get_theme("custom")
        
        assert retrieved is not None
        assert retrieved.name == "custom"
        assert retrieved.background_color == "purple"
    
    def test_get_theme_case_insensitive(self):
        """Test that get_theme is case-insensitive."""
        theme = Theme(
            name="TestTheme",
            background_color="white",
            font_color="black"
        )
        register_theme(theme)
        
        # Should work with different cases
        assert get_theme("testtheme") is not None
        assert get_theme("TESTTHEME") is not None
        assert get_theme("TestTheme") is not None
    
    def test_get_theme_not_found(self):
        """Test getting a non-existent theme."""
        result = get_theme("nonexistent")
        assert result is None
    
    def test_get_theme_names(self):
        """Test getting list of theme names."""
        names = get_theme_names()
        assert isinstance(names, list)
        assert len(names) > 0
        # Check that preset themes are included
        assert "classic" in names
        assert "vibrant" in names
    
    def test_list_themes(self):
        """Test listing all themes."""
        themes = list_themes()
        assert isinstance(themes, dict)
        assert len(themes) > 0
        assert "classic" in themes
        assert isinstance(themes["classic"], Theme)


class TestPresetThemes:
    """Tests for preset themes."""
    
    def test_classic_theme(self):
        """Test classic theme."""
        theme = get_theme("classic")
        assert theme is not None
        assert theme.background_color == "white"
        assert theme.font_color == "black"
        assert theme.colormap is None
    
    def test_vibrant_theme(self):
        """Test vibrant theme."""
        theme = get_theme("vibrant")
        assert theme is not None
        assert theme.background_color == "#1a1a1a"
        assert theme.colormap == "viridis"
        assert theme.font_color is None
    
    def test_ocean_theme(self):
        """Test ocean theme."""
        theme = get_theme("ocean")
        assert theme is not None
        assert theme.background_color == "#0a1929"
        assert theme.colormap == "coolwarm"
    
    def test_sunset_theme(self):
        """Test sunset theme."""
        theme = get_theme("sunset")
        assert theme is not None
        assert theme.background_color == "#2d1b0e"
        assert theme.colormap == "plasma"
    
    def test_minimal_theme(self):
        """Test minimal theme."""
        theme = get_theme("minimal")
        assert theme is not None
        assert theme.background_color == "white"
        assert theme.font_color == "#666666"
        assert theme.relative_scaling == 0.6
        assert theme.prefer_horizontal == 0.95
    
    def test_dark_theme(self):
        """Test dark theme."""
        theme = get_theme("dark")
        assert theme is not None
        assert theme.background_color == "black"
        assert theme.colormap == "Set3"
    
    def test_pastel_theme(self):
        """Test pastel theme."""
        theme = get_theme("pastel")
        assert theme is not None
        assert theme.background_color == "#f5f5f5"
        assert theme.colormap == "Pastel1"
    
    def test_high_contrast_theme(self):
        """Test high-contrast theme."""
        theme = get_theme("high-contrast")
        assert theme is not None
        assert theme.background_color == "white"
        assert theme.font_color == "black"
        assert theme.relative_scaling == 0.3  # More dramatic differences
    
    def test_inferno_theme(self):
        """Test inferno theme."""
        theme = get_theme("inferno")
        assert theme is not None
        assert theme.colormap == "inferno"
        assert theme.background_color == "#0d0d0d"
    
    def test_magma_theme(self):
        """Test magma theme."""
        theme = get_theme("magma")
        assert theme is not None
        assert theme.colormap == "magma"
        assert theme.background_color == "#0c0c0c"
    
    def test_spring_theme(self):
        """Test spring theme."""
        theme = get_theme("spring")
        assert theme is not None
        assert theme.colormap == "spring"
        assert theme.background_color == "#f0f8f0"
    
    def test_summer_theme(self):
        """Test summer theme."""
        theme = get_theme("summer")
        assert theme is not None
        assert theme.colormap == "summer"
        assert theme.background_color == "#fff8e1"
    
    def test_autumn_theme(self):
        """Test autumn theme."""
        theme = get_theme("autumn")
        assert theme is not None
        assert theme.colormap == "autumn"
        assert theme.background_color == "#fff3e0"
    
    def test_winter_theme(self):
        """Test winter theme."""
        theme = get_theme("winter")
        assert theme is not None
        assert theme.colormap == "winter"
        assert theme.background_color == "#e3f2fd"
    
    def test_blues_theme(self):
        """Test blues theme."""
        theme = get_theme("blues")
        assert theme is not None
        assert theme.colormap == "Blues"
        assert theme.background_color == "#e3f2fd"
    
    def test_greens_theme(self):
        """Test greens theme."""
        theme = get_theme("greens")
        assert theme is not None
        assert theme.colormap == "Greens"
        assert theme.background_color == "#e8f5e9"
    
    def test_reds_theme(self):
        """Test reds theme."""
        theme = get_theme("reds")
        assert theme is not None
        assert theme.colormap == "Reds"
        assert theme.background_color == "#ffebee"
    
    def test_purples_theme(self):
        """Test purples theme."""
        theme = get_theme("purples")
        assert theme is not None
        assert theme.colormap == "Purples"
        assert theme.background_color == "#f3e5f5"
    
    def test_spectral_theme(self):
        """Test spectral theme."""
        theme = get_theme("spectral")
        assert theme is not None
        assert theme.colormap == "Spectral"
    
    def test_set1_theme(self):
        """Test set1 theme."""
        theme = get_theme("set1")
        assert theme is not None
        assert theme.colormap == "Set1"
    
    def test_tab10_theme(self):
        """Test tab10 theme."""
        theme = get_theme("tab10")
        assert theme is not None
        assert theme.colormap == "tab10"
    
    def test_all_themes_registered(self):
        """Test that all themes are properly registered."""
        themes = list_themes()
        # Should have at least 30+ themes
        assert len(themes) >= 30
        # Check some key themes exist
        assert "classic" in themes
        assert "vibrant" in themes
        assert "inferno" in themes
        assert "magma" in themes
        assert "spring" in themes
        assert "blues" in themes
        assert "greens" in themes
        assert "set1" in themes
        assert "tab10" in themes

