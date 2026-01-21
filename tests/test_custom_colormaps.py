"""Unit tests for custom_colormaps module."""

import pytest
import matplotlib
from matplotlib.colors import ListedColormap

from src.custom_colormaps import (
    register_custom_colormap,
    register_colormaps_from_config,
    is_colormap_registered,
    CustomColormapError
)


class TestRegisterCustomColormap:
    """Tests for register_custom_colormap function."""
    
    def test_register_simple_colormap(self):
        """Test registering a simple colormap."""
        colors = ['#FF0000', '#00FF00', '#0000FF']
        cmap = register_custom_colormap('test_simple', colors)
        
        assert isinstance(cmap, ListedColormap)
        assert cmap.name == 'test_simple'
        assert cmap.N == 3
        assert is_colormap_registered('test_simple')
    
    def test_register_colormap_with_description(self):
        """Test registering colormap with description."""
        colors = ['#FF0000', '#00FF00']
        cmap = register_custom_colormap('test_desc', colors, 'Test description')
        
        assert cmap.name == 'test_desc'
        assert is_colormap_registered('test_desc')
    
    def test_register_empty_name_raises_error(self):
        """Test that empty name raises error."""
        with pytest.raises(CustomColormapError) as exc_info:
            register_custom_colormap('', ['#FF0000'])
        assert "cannot be empty" in str(exc_info.value)
    
    def test_register_duplicate_name_raises_error(self):
        """Test that duplicate name raises error."""
        colors = ['#FF0000', '#00FF00']
        register_custom_colormap('test_duplicate', colors)
        
        with pytest.raises(CustomColormapError) as exc_info:
            register_custom_colormap('test_duplicate', colors)
        assert "already exists" in str(exc_info.value)
    
    def test_register_too_few_colors_raises_error(self):
        """Test that less than 2 colors raises error."""
        with pytest.raises(CustomColormapError) as exc_info:
            register_custom_colormap('test_few', ['#FF0000'])
        assert "at least 2" in str(exc_info.value)
    
    def test_register_empty_colors_raises_error(self):
        """Test that empty colors list raises error."""
        with pytest.raises(CustomColormapError) as exc_info:
            register_custom_colormap('test_empty', [])
        assert "at least 2" in str(exc_info.value)
    
    def test_register_multiple_colors(self):
        """Test registering colormap with many colors."""
        colors = ['#FF0000', '#FF3300', '#FF6600', '#FF9900', '#FFCC00', '#FFFF00']
        cmap = register_custom_colormap('test_many', colors)
        
        assert cmap.N == 6
        assert is_colormap_registered('test_many')


class TestRegisterColormapsFromConfig:
    """Tests for register_colormaps_from_config function."""
    
    def test_register_multiple_colormaps(self):
        """Test registering multiple colormaps from config."""
        config = [
            {'name': 'test_cmap1', 'colors': ['#FF0000', '#00FF00']},
            {'name': 'test_cmap2', 'colors': ['#0000FF', '#FFFF00']}
        ]
        
        register_colormaps_from_config(config)
        
        assert is_colormap_registered('test_cmap1')
        assert is_colormap_registered('test_cmap2')
    
    def test_register_config_missing_name_raises_error(self):
        """Test that config without name raises error."""
        config = [{'colors': ['#FF0000']}]
        
        with pytest.raises(CustomColormapError) as exc_info:
            register_colormaps_from_config(config)
        assert "missing 'name'" in str(exc_info.value)
    
    def test_register_config_missing_colors_raises_error(self):
        """Test that config without colors raises error."""
        config = [{'name': 'test_no_colors'}]
        
        with pytest.raises(CustomColormapError) as exc_info:
            register_colormaps_from_config(config)
        assert "missing 'colors'" in str(exc_info.value)
    
    def test_register_config_with_description(self):
        """Test registering config with description."""
        config = [{
            'name': 'test_with_desc',
            'colors': ['#FF0000', '#00FF00'],
            'description': 'Test description'
        }]
        
        register_colormaps_from_config(config)
        assert is_colormap_registered('test_with_desc')


class TestIsColormapRegistered:
    """Tests for is_colormap_registered function."""
    
    def test_check_registered_colormap(self):
        """Test checking a registered colormap."""
        register_custom_colormap('test_check', ['#FF0000', '#00FF00'])
        
        assert is_colormap_registered('test_check') is True
    
    def test_check_builtin_colormap(self):
        """Test checking a built-in matplotlib colormap."""
        assert is_colormap_registered('viridis') is True
    
    def test_check_nonexistent_colormap(self):
        """Test checking a non-existent colormap."""
        assert is_colormap_registered('nonexistent_cmap_xyz123') is False

