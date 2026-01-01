"""Unit tests for config module."""

import pytest

from src.config import (
    LANGUAGES_FOR_NLTK,
    WORDCLOUD_COLORS,
    PUNCTUATION,
    DEFAULT_CANVAS_WIDTH,
    DEFAULT_CANVAS_HEIGHT,
    DEFAULT_MAX_WORDS,
    DEFAULT_MIN_WORD_LENGTH,
    WordCloudConfig,
    AppConfig
)


class TestConstants:
    """Tests for configuration constants."""
    
    def test_languages_list(self):
        """Test that LANGUAGES_FOR_NLTK contains expected languages."""
        assert 'english' in LANGUAGES_FOR_NLTK
        assert 'spanish' in LANGUAGES_FOR_NLTK
        assert 'french' in LANGUAGES_FOR_NLTK
        assert len(LANGUAGES_FOR_NLTK) > 0
        assert all(isinstance(lang, str) for lang in LANGUAGES_FOR_NLTK)
    
    def test_wordcloud_colors(self):
        """Test that WORDCLOUD_COLORS contains expected colors."""
        assert 'white' in WORDCLOUD_COLORS
        assert 'blue' in WORDCLOUD_COLORS
        assert 'red' in WORDCLOUD_COLORS
        assert len(WORDCLOUD_COLORS) > 0
    
    def test_punctuation_string(self):
        """Test that PUNCTUATION contains common punctuation."""
        assert '!' in PUNCTUATION
        assert '.' in PUNCTUATION
        assert ',' in PUNCTUATION
        assert '?' in PUNCTUATION
    
    def test_default_values(self):
        """Test default configuration values."""
        assert DEFAULT_CANVAS_WIDTH == 800
        assert DEFAULT_CANVAS_HEIGHT == 600
        assert DEFAULT_MAX_WORDS == 200
        assert DEFAULT_MIN_WORD_LENGTH == 0


class TestWordCloudConfig:
    """Tests for WordCloudConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = WordCloudConfig()
        assert config.canvas_width == DEFAULT_CANVAS_WIDTH
        assert config.canvas_height == DEFAULT_CANVAS_HEIGHT
        assert config.max_words == DEFAULT_MAX_WORDS
        assert config.min_word_length == DEFAULT_MIN_WORD_LENGTH
        assert config.normalize_plurals is False
        assert config.include_numbers is False
        assert config.background_color is None
        assert config.font_color is None
        assert config.colormap is None
        assert config.relative_scaling == 0.5
        assert config.prefer_horizontal == 0.9
        assert config.mask is None
        assert config.contour_width == 0.0
        assert config.contour_color is None
        assert config.font_path is None
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = WordCloudConfig(
            canvas_width=800,
            canvas_height=600,
            max_words=100,
            min_word_length=3,
            normalize_plurals=True,
            include_numbers=True,
            background_color='white',
            font_color='#FF0000',
            colormap='viridis',
            relative_scaling=0.3,
            prefer_horizontal=0.7,
            mask='mask.png',
            contour_width=2.0,
            contour_color='red',
            font_path='font.ttf'
        )
        assert config.canvas_width == 800
        assert config.canvas_height == 600
        assert config.max_words == 100
        assert config.min_word_length == 3
        assert config.normalize_plurals is True
        assert config.include_numbers is True
        assert config.background_color == 'white'
        assert config.font_color == '#FF0000'
        assert config.colormap == 'viridis'
        assert config.relative_scaling == 0.3
        assert config.prefer_horizontal == 0.7
        assert config.mask == 'mask.png'
        assert config.contour_width == 2.0
        assert config.contour_color == 'red'
        assert config.font_path == 'font.ttf'
    
    def test_text_processing_settings(self):
        """Test text processing settings."""
        config = WordCloudConfig(
            language='spanish',
            include_stopwords=True,
            case_sensitive=True,
            collocations=True
        )
        assert config.language == 'spanish'
        assert config.include_stopwords is True
        assert config.case_sensitive is True
        assert config.collocations is True


class TestAppConfig:
    """Tests for AppConfig dataclass."""
    
    def test_default_app_config(self):
        """Test default AppConfig values."""
        config = AppConfig(input_file='test.txt')
        assert config.input_file == 'test.txt'
        assert config.output_file is None
        assert config.is_json is False
        assert config.wordcloud_config is not None
        assert isinstance(config.wordcloud_config, WordCloudConfig)
    
    def test_custom_app_config(self):
        """Test custom AppConfig values."""
        wordcloud_config = WordCloudConfig(max_words=50)
        config = AppConfig(
            input_file='input.json',
            output_file='output.png',
            is_json=True,
            wordcloud_config=wordcloud_config
        )
        assert config.input_file == 'input.json'
        assert config.output_file == 'output.png'
        assert config.is_json is True
        assert config.wordcloud_config == wordcloud_config
        assert config.wordcloud_config.max_words == 50
    
    def test_app_config_auto_init_wordcloud_config(self):
        """Test that wordcloud_config is auto-initialized if not provided."""
        config = AppConfig(input_file='test.txt')
        assert config.wordcloud_config is not None
        assert isinstance(config.wordcloud_config, WordCloudConfig)
        # Should use defaults
        assert config.wordcloud_config.canvas_width == DEFAULT_CANVAS_WIDTH

