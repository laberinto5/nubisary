"""Unit tests for wordcloud_generator module."""

import pytest
from unittest.mock import patch, MagicMock, Mock
import numpy as np
from PIL import Image

from src.wordcloud_generator import (
    create_color_func,
    load_mask,
    create_wordcloud_instance,
    generate_word_cloud_from_frequencies
)
from src.config import WordCloudConfig


class TestCreateColorFunc:
    """Tests for create_color_func function."""
    
    @patch('src.wordcloud_generator.get_single_color_func')
    def test_single_color(self, mock_get_color_func):
        """Test creating color function with single color."""
        mock_func = Mock()
        mock_get_color_func.return_value = mock_func
        
        result = create_color_func("red", None)
        
        assert result == mock_func
        mock_get_color_func.assert_called_once_with("red")
    
    def test_colormap(self):
        """Test that colormap returns None (WordCloud handles it)."""
        result = create_color_func(None, "viridis")
        assert result is None
    
    def test_colormap_overrides_font_color(self):
        """Test that colormap takes precedence over font_color."""
        result = create_color_func("red", "plasma")
        assert result is None  # Colormap takes precedence
    
    def test_no_color(self):
        """Test with no color specified (uses default)."""
        result = create_color_func(None, None)
        assert result is None


class TestLoadMask:
    """Tests for load_mask function."""
    
    @patch('src.wordcloud_generator.Image')
    def test_load_mask_success(self, mock_image):
        """Test successfully loading a mask image."""
        # Create mock image and real array
        mock_img = MagicMock()
        expected_array = np.array([[0, 255], [255, 0]])
        # Replace np.array with a function that returns our expected array
        def mock_array_func(x):
            return expected_array
        
        mock_image.open.return_value = mock_img
        
        with patch('src.wordcloud_generator.np.array', side_effect=mock_array_func):
            result = load_mask("test_mask.png")
            
            assert result is not None
            assert isinstance(result, np.ndarray)
            assert result is expected_array
            mock_image.open.assert_called_once_with("test_mask.png")
    
    @patch('src.wordcloud_generator.Image')
    def test_load_mask_failure(self, mock_image):
        """Test handling mask loading failure."""
        mock_image.open.side_effect = IOError("File not found")
        
        with pytest.raises(ValueError, match="Failed to load mask image"):
            load_mask("nonexistent.png")


class TestCreateWordcloudInstance:
    """Tests for create_wordcloud_instance function."""
    
    @patch('src.wordcloud_generator.WordCloud')
    @patch('src.wordcloud_generator.create_color_func')
    def test_basic_config(self, mock_color_func, mock_wordcloud_class):
        """Test creating WordCloud with basic config."""
        mock_color_func.return_value = None
        mock_instance = MagicMock()
        mock_wordcloud_class.return_value = mock_instance
        
        config = WordCloudConfig(
            canvas_width=400,
            canvas_height=200,
            max_words=100,
            background_color="white"
        )
        
        result = create_wordcloud_instance(config)
        
        assert result == mock_instance
        mock_wordcloud_class.assert_called_once()
        call_args = mock_wordcloud_class.call_args[1]
        assert call_args['width'] == 400
        assert call_args['height'] == 200
        assert call_args['max_words'] == 100
        assert call_args['background_color'] == "white"
    
    @patch('src.wordcloud_generator.WordCloud')
    @patch('src.wordcloud_generator.create_color_func')
    def test_with_colormap(self, mock_color_func, mock_wordcloud_class):
        """Test creating WordCloud with colormap."""
        mock_color_func.return_value = None
        mock_instance = MagicMock()
        mock_wordcloud_class.return_value = mock_instance
        
        config = WordCloudConfig(
            colormap="viridis",
            background_color="black"
        )
        
        result = create_wordcloud_instance(config)
        
        call_args = mock_wordcloud_class.call_args[1]
        assert 'colormap' in call_args
        assert call_args['colormap'] == "viridis"
        assert 'color_func' not in call_args
    
    @patch('src.wordcloud_generator.WordCloud')
    @patch('src.wordcloud_generator.create_color_func')
    def test_with_font_color(self, mock_color_func, mock_wordcloud_class):
        """Test creating WordCloud with font color."""
        mock_color_func_obj = Mock()
        mock_color_func.return_value = mock_color_func_obj
        mock_instance = MagicMock()
        mock_wordcloud_class.return_value = mock_instance
        
        config = WordCloudConfig(
            font_color="red",
            background_color="white"
        )
        
        result = create_wordcloud_instance(config)
        
        call_args = mock_wordcloud_class.call_args[1]
        assert 'color_func' in call_args
        assert call_args['color_func'] == mock_color_func_obj
        assert 'colormap' not in call_args
    
    @patch('src.wordcloud_generator.WordCloud')
    @patch('src.wordcloud_generator.load_mask')
    @patch('src.wordcloud_generator.create_color_func')
    def test_with_mask(self, mock_color_func, mock_load_mask, mock_wordcloud_class):
        """Test creating WordCloud with mask."""
        mock_color_func.return_value = None
        mock_mask_array = np.array([[0, 255], [255, 0]])
        mock_load_mask.return_value = mock_mask_array
        mock_instance = MagicMock()
        mock_wordcloud_class.return_value = mock_instance
        
        config = WordCloudConfig(
            mask="heart.png"
        )
        
        result = create_wordcloud_instance(config)
        
        mock_load_mask.assert_called_once_with("heart.png")
        call_args = mock_wordcloud_class.call_args[1]
        assert 'mask' in call_args
        assert call_args['mask'] is mock_mask_array
    
    @patch('src.wordcloud_generator.WordCloud')
    @patch('src.wordcloud_generator.load_mask')
    @patch('src.wordcloud_generator.create_color_func')
    def test_with_mask_and_contour(self, mock_color_func, mock_load_mask, mock_wordcloud_class):
        """Test creating WordCloud with mask and contour."""
        mock_color_func.return_value = None
        mock_mask_array = np.array([[0, 255], [255, 0]])
        mock_load_mask.return_value = mock_mask_array
        mock_instance = MagicMock()
        mock_wordcloud_class.return_value = mock_instance
        
        config = WordCloudConfig(
            mask="heart.png",
            contour_width=2.0,
            contour_color="red"
        )
        
        result = create_wordcloud_instance(config)
        
        call_args = mock_wordcloud_class.call_args[1]
        assert 'mask' in call_args
        assert 'contour_width' in call_args
        assert call_args['contour_width'] == 2.0
        assert 'contour_color' in call_args
        assert call_args['contour_color'] == "red"
    
    @patch('src.wordcloud_generator.WordCloud')
    @patch('src.wordcloud_generator.create_color_func')
    def test_with_relative_scaling(self, mock_color_func, mock_wordcloud_class):
        """Test creating WordCloud with relative_scaling."""
        mock_color_func.return_value = None
        mock_instance = MagicMock()
        mock_wordcloud_class.return_value = mock_instance
        
        config = WordCloudConfig(
            relative_scaling=0.3,
            prefer_horizontal=0.7
        )
        
        result = create_wordcloud_instance(config)
        
        call_args = mock_wordcloud_class.call_args[1]
        assert call_args['relative_scaling'] == 0.3
        assert call_args['prefer_horizontal'] == 0.7
    
    @patch('src.wordcloud_generator.WordCloud')
    @patch('src.wordcloud_generator.create_color_func')
    def test_with_font_path(self, mock_color_func, mock_wordcloud_class):
        """Test creating WordCloud with custom font."""
        mock_color_func.return_value = None
        mock_instance = MagicMock()
        mock_wordcloud_class.return_value = mock_instance
        
        config = WordCloudConfig(
            font_path="custom_font.ttf"
        )
        
        result = create_wordcloud_instance(config)
        
        call_args = mock_wordcloud_class.call_args[1]
        assert 'font_path' in call_args
        assert call_args['font_path'] == "custom_font.ttf"


class TestGenerateWordCloudFromFrequencies:
    """Tests for generate_word_cloud_from_frequencies function."""
    
    @patch('src.wordcloud_generator.plt')
    @patch('src.wordcloud_generator.create_wordcloud_instance')
    def test_generate_and_show(self, mock_create_instance, mock_plt):
        """Test generating and displaying word cloud."""
        mock_wordcloud = MagicMock()
        mock_create_instance.return_value = mock_wordcloud
        
        frequencies = {'word1': 10.0, 'word2': 5.0}
        config = WordCloudConfig()
        
        result = generate_word_cloud_from_frequencies(
            frequencies=frequencies,
            config=config,
            show=True
        )
        
        assert result == mock_wordcloud
        mock_wordcloud.generate_from_frequencies.assert_called_once_with(frequencies)
        mock_plt.figure.assert_called_once()
        mock_plt.imshow.assert_called_once()
        mock_plt.axis.assert_called_once_with('off')
        mock_plt.show.assert_called_once()
    
    @patch('src.wordcloud_generator.plt')
    @patch('src.wordcloud_generator.create_wordcloud_instance')
    def test_generate_no_show(self, mock_create_instance, mock_plt):
        """Test generating without displaying."""
        mock_wordcloud = MagicMock()
        mock_create_instance.return_value = mock_wordcloud
        
        frequencies = {'word1': 10.0, 'word2': 5.0}
        config = WordCloudConfig()
        
        result = generate_word_cloud_from_frequencies(
            frequencies=frequencies,
            config=config,
            show=False
        )
        
        mock_plt.show.assert_not_called()
    
    @patch('src.wordcloud_generator.create_wordcloud_instance')
    def test_generate_and_save(self, mock_create_instance):
        """Test generating and saving word cloud."""
        mock_wordcloud = MagicMock()
        mock_create_instance.return_value = mock_wordcloud
        
        frequencies = {'word1': 10.0, 'word2': 5.0}
        config = WordCloudConfig()
        
        result = generate_word_cloud_from_frequencies(
            frequencies=frequencies,
            config=config,
            output_file="output.png",
            show=False
        )
        
        mock_wordcloud.to_file.assert_called_once_with("output.png")

