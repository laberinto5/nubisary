"""Unit tests for themes module."""

import pytest
from src.themes import Theme, get_theme, get_theme_names, list_themes, register_theme
from src.custom_colormaps import is_colormap_registered
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
        # Check that custom preset themes are included
        assert "playroom" in names
        assert "jungle" in names
        assert "high_contrast" in names
    
    def test_list_themes(self):
        """Test listing all themes."""
        themes = list_themes()
        assert isinstance(themes, dict)
        assert len(themes) > 0
        assert "playroom" in themes
        assert isinstance(themes["playroom"], Theme)


class TestPresetThemes:
    """Tests for preset themes."""
    
    def test_playroom_theme(self):
        """Test playroom theme."""
        theme = get_theme("playroom")
        assert theme is not None
        assert theme.background_color == "#ffffff"
        assert theme.colormap == "crayons"
    
    def test_high_contrast_theme(self):
        """Test high_contrast theme."""
        theme = get_theme("high_contrast")
        assert theme is not None
        assert theme.background_color == "#FFFFFF"
        assert theme.colormap == "greys_dark"
    
    def test_spring_theme(self):
        """Test spring theme."""
        theme = get_theme("spring")
        assert theme is not None
        assert theme.background_color == "#1BA891"
        assert theme.colormap == "pink_light"
    
    def test_summer_theme(self):
        """Test summer theme."""
        theme = get_theme("summer")
        assert theme is not None
        assert theme.background_color == "#004697"
        assert theme.colormap == "colorful_palette"
    
    def test_autumn_theme(self):
        """Test autumn theme."""
        theme = get_theme("autumn")
        assert theme is not None
        assert theme.background_color == "#5F2E0F"
        assert theme.colormap == "goldens_dark"
    
    def test_winter_theme(self):
        """Test winter theme."""
        theme = get_theme("winter")
        assert theme is not None
        assert theme.background_color == "#6689AF"
        assert theme.colormap == "blues_light"
    
    def test_night_theme(self):
        """Test night theme."""
        theme = get_theme("night")
        assert theme is not None
        assert theme.background_color == "#1A0000"
        assert theme.colormap == "blue_green_dark"
    
    def test_bombons_theme(self):
        """Test bombons theme."""
        theme = get_theme("bombons")
        assert theme is not None
        assert theme.background_color == "#311405"
        assert theme.colormap == "crayons"
    
    def test_all_themes_registered(self):
        """Test that all themes are properly registered."""
        themes = list_themes()
        expected = {
            "playroom", "jungle", "garden", "brazil", "woods", "fluorescent", "mint",
            "stars", "lake", "river", "solarized", "office", "pinky", "neon",
            "markers", "golden", "pharaon", "cadiz", "clouds", "strawberry",
            "piruleta", "blood", "high_contrast", "soft", "grey", "elegance",
            "gum", "sakura", "gossip", "halloween", "carrots", "joy",
            "blackboard", "sauvage", "loretta", "old", "sober", "homely",
            "spring", "summer", "autumn", "winter", "night", "day",
            "radical", "bombons"
        }
        # Registry can include extra themes added by other tests
        assert expected.issubset(set(themes.keys()))


class TestCustomColormaps:
    """Tests for custom colormaps registered for themes."""

    def test_custom_colormaps_registered(self):
        expected = {
            "greens_dark", "greens_light", "blues_dark", "blues_bright", "blues_light",
            "reds_dark", "reds_light", "goldens_dark", "goldens_light",
            "greys_dark", "greys_light", "neon", "pastels", "grey_blue_dark",
            "crayons", "pinkies", "pink_dark", "pink_light", "sakura_palette",
            "pumpkins", "blue_ocre_grey", "blue_green_dark", "blue_green_vibrant",
            "blue_green_light", "garden_with_flowers", "sober_colors", "colorful_palette"
        }
        for cmap in expected:
            assert is_colormap_registered(cmap) is True

