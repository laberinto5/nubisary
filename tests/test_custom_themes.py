"""Unit tests for custom_themes module."""

import pytest
import json
import tempfile
import os
from pathlib import Path

from src.custom_themes import (
    load_custom_theme_from_json,
    validate_custom_theme_json,
    CustomThemeError
)
from src.themes import get_theme, Theme
from src.file_handlers import FileHandlerError
from src.custom_colormaps import register_custom_colormap


class TestLoadCustomThemeFromJson:
    """Tests for load_custom_theme_from_json function."""
    
    def test_load_theme_with_custom_colormap(self):
        """Test loading theme with custom colormap."""
        theme_data = {
            'custom_colormaps': [
                {
                    'name': 'test_cmap',
                    'colors': ['#FF0000', '#00FF00', '#0000FF']
                }
            ],
            'theme': {
                'name': 'test-theme',
                'background_color': '#000000',
                'colormap': 'test_cmap',
                'font_color': None,
                'relative_scaling': 0.6,
                'prefer_horizontal': 0.85,
                'description': 'Test theme'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            theme = load_custom_theme_from_json(temp_file)
            
            assert isinstance(theme, Theme)
            assert theme.name == 'test-theme'
            assert theme.background_color == '#000000'
            assert theme.colormap == 'test_cmap'
            assert theme.relative_scaling == 0.6
            assert theme.prefer_horizontal == 0.85
            
            # Verify theme is registered
            retrieved = get_theme('test-theme')
            assert retrieved is not None
            assert retrieved.name == 'test-theme'
        finally:
            os.unlink(temp_file)
    
    def test_load_theme_with_font_color(self):
        """Test loading theme with single font color."""
        theme_data = {
            'theme': {
                'name': 'test-single-color',
                'background_color': 'white',
                'colormap': None,
                'font_color': '#FF0000',
                'relative_scaling': 0.5,
                'prefer_horizontal': 0.9,
                'description': 'Single color theme'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            theme = load_custom_theme_from_json(temp_file)
            
            assert theme.name == 'test-single-color'
            assert theme.background_color == 'white'
            assert theme.colormap is None
            assert theme.font_color == '#FF0000'
        finally:
            os.unlink(temp_file)
    
    def test_load_theme_with_builtin_colormap(self):
        """Test loading theme with built-in matplotlib colormap."""
        theme_data = {
            'theme': {
                'name': 'test-builtin',
                'background_color': '#000000',
                'colormap': 'viridis',
                'description': 'Theme with built-in colormap'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            theme = load_custom_theme_from_json(temp_file)
            
            assert theme.name == 'test-builtin'
            assert theme.colormap == 'viridis'
        finally:
            os.unlink(temp_file)
    
    def test_load_theme_minimal_fields(self):
        """Test loading theme with minimal required fields."""
        theme_data = {
            'theme': {
                'name': 'minimal-theme',
                'background_color': 'white'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            theme = load_custom_theme_from_json(temp_file)
            
            assert theme.name == 'minimal-theme'
            assert theme.background_color == 'white'
            # Defaults should be applied
            assert theme.relative_scaling == 0.5
            assert theme.prefer_horizontal == 0.9
        finally:
            os.unlink(temp_file)
    
    def test_load_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises error."""
        with pytest.raises(FileHandlerError) as exc_info:
            load_custom_theme_from_json('nonexistent_file.json')
        assert "does not exist" in str(exc_info.value)
    
    def test_load_invalid_json_raises_error(self):
        """Test that invalid JSON raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ invalid json }')
            temp_file = f.name
        
        try:
            with pytest.raises(CustomThemeError) as exc_info:
                load_custom_theme_from_json(temp_file)
            assert "Invalid JSON" in str(exc_info.value)
        finally:
            os.unlink(temp_file)
    
    def test_load_missing_theme_raises_error(self):
        """Test that missing theme object raises error."""
        theme_data = {'custom_colormaps': []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(CustomThemeError) as exc_info:
                load_custom_theme_from_json(temp_file)
            assert "must contain a 'theme' object" in str(exc_info.value)
        finally:
            os.unlink(temp_file)
    
    def test_load_missing_name_raises_error(self):
        """Test that missing name field raises error."""
        theme_data = {
            'theme': {
                'background_color': 'white'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(CustomThemeError) as exc_info:
                load_custom_theme_from_json(temp_file)
            assert "must have a 'name' field" in str(exc_info.value)
        finally:
            os.unlink(temp_file)
    
    def test_load_missing_background_raises_error(self):
        """Test that missing background_color field raises error."""
        theme_data = {
            'theme': {
                'name': 'test'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(CustomThemeError) as exc_info:
                load_custom_theme_from_json(temp_file)
            assert "must have a 'background_color' field" in str(exc_info.value)
        finally:
            os.unlink(temp_file)
    
    def test_load_invalid_relative_scaling_raises_error(self):
        """Test that invalid relative_scaling raises error."""
        theme_data = {
            'theme': {
                'name': 'test',
                'background_color': 'white',
                'relative_scaling': 1.5  # Invalid: > 1.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(CustomThemeError) as exc_info:
                load_custom_theme_from_json(temp_file)
            assert "invalid 'relative_scaling'" in str(exc_info.value)
        finally:
            os.unlink(temp_file)
    
    def test_load_nonexistent_colormap_raises_error(self):
        """Test that nonexistent colormap raises error."""
        theme_data = {
            'theme': {
                'name': 'test',
                'background_color': 'white',
                'colormap': 'nonexistent_colormap_xyz123'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(CustomThemeError) as exc_info:
                load_custom_theme_from_json(temp_file)
            assert "not registered" in str(exc_info.value)
        finally:
            os.unlink(temp_file)
    
    def test_load_theme_with_multiple_colormaps(self):
        """Test loading theme with multiple custom colormaps."""
        theme_data = {
            'custom_colormaps': [
                {
                    'name': 'cmap1',
                    'colors': ['#FF0000', '#00FF00']
                },
                {
                    'name': 'cmap2',
                    'colors': ['#0000FF', '#FFFF00']
                }
            ],
            'theme': {
                'name': 'test-multi-cmap',
                'background_color': 'black',
                'colormap': 'cmap1'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            theme = load_custom_theme_from_json(temp_file)
            
            assert theme.name == 'test-multi-cmap'
            assert theme.colormap == 'cmap1'
            
            # Both colormaps should be registered
            import matplotlib
            assert 'cmap1' in matplotlib.colormaps
            assert 'cmap2' in matplotlib.colormaps
        finally:
            os.unlink(temp_file)


class TestValidateCustomThemeJson:
    """Tests for validate_custom_theme_json function."""
    
    def test_validate_valid_json(self):
        """Test validating a valid JSON."""
        theme_data = {
            'theme': {
                'name': 'test-valid',
                'background_color': 'white'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            result = validate_custom_theme_json(temp_file)
            assert 'theme' in result
            assert result['theme']['name'] == 'test-valid'
        finally:
            os.unlink(temp_file)
    
    def test_validate_invalid_json_raises_error(self):
        """Test that invalid JSON raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ invalid json }')
            temp_file = f.name
        
        try:
            with pytest.raises(CustomThemeError) as exc_info:
                validate_custom_theme_json(temp_file)
            assert "Invalid JSON" in str(exc_info.value)
        finally:
            os.unlink(temp_file)
    
    def test_validate_missing_theme_raises_error(self):
        """Test that missing theme raises error."""
        theme_data = {}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(CustomThemeError) as exc_info:
                validate_custom_theme_json(temp_file)
            assert "must contain a 'theme' object" in str(exc_info.value)
        finally:
            os.unlink(temp_file)

