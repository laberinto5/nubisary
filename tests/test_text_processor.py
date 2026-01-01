"""Unit tests for text_processor module."""

import pytest
from unittest.mock import patch, MagicMock

from src.text_processor import preprocess_text, generate_word_count_from_text
from src.config import PUNCTUATION


class TestPreprocessText:
    """Tests for preprocess_text function."""
    
    def test_remove_punctuation(self):
        """Test that punctuation is removed."""
        text = "Hello, world! How are you?"
        result = preprocess_text(text, case_sensitive=True)
        assert ',' not in result
        assert '!' not in result
        assert '?' not in result
        assert 'Hello' in result
        assert 'world' in result
    
    def test_lowercase_when_not_case_sensitive(self):
        """Test that text is lowercased when case_sensitive is False."""
        text = "Hello WORLD"
        result = preprocess_text(text, case_sensitive=False)
        assert result == "hello world"
    
    def test_preserve_case_when_case_sensitive(self):
        """Test that case is preserved when case_sensitive is True."""
        text = "Hello WORLD"
        result = preprocess_text(text, case_sensitive=True)
        assert 'Hello' in result
        assert 'WORLD' in result
    
    def test_all_punctuation_removed(self):
        """Test that all punctuation characters are removed."""
        text = PUNCTUATION + "test" + PUNCTUATION
        result = preprocess_text(text, case_sensitive=True)
        assert result == "test"
    
    def test_empty_string(self):
        """Test empty string handling."""
        assert preprocess_text("", case_sensitive=True) == ""
        assert preprocess_text("", case_sensitive=False) == ""
    
    def test_only_punctuation(self):
        """Test string with only punctuation."""
        text = "!@#$%^&*()"
        result = preprocess_text(text, case_sensitive=True)
        assert result == ""


class TestGenerateWordCountFromText:
    """Tests for generate_word_count_from_text function."""
    
    @patch('src.text_processor.WordCloud')
    @patch('src.text_processor.stopwords')
    def test_generate_word_count_basic(self, mock_stopwords, mock_wordcloud_class):
        """Test basic word count generation."""
        # Setup mocks
        mock_wordcloud = MagicMock()
        mock_wordcloud.process_text.return_value = {'hello': 5.0, 'world': 3.0}
        mock_wordcloud_class.return_value = mock_wordcloud
        mock_stopwords.words.return_value = ['the', 'a', 'an']
        
        text = "hello world hello"
        result = generate_word_count_from_text(
            text=text,
            language='english',
            include_stopwords=False
        )
        
        assert result == {'hello': 5.0, 'world': 3.0}
        mock_wordcloud_class.assert_called_once()
        mock_wordcloud.process_text.assert_called_once_with(text)
    
    @patch('src.text_processor.WordCloud')
    @patch('src.text_processor.stopwords')
    def test_generate_word_count_with_stopwords(self, mock_stopwords, mock_wordcloud_class):
        """Test word count generation with stopwords included."""
        mock_wordcloud = MagicMock()
        mock_wordcloud.process_text.return_value = {'hello': 5.0, 'the': 2.0}
        mock_wordcloud_class.return_value = mock_wordcloud
        
        text = "hello the world"
        result = generate_word_count_from_text(
            text=text,
            language='english',
            include_stopwords=True
        )
        
        # When include_stopwords is True, stopwords should not be set
        # (the code only sets stopwords when include_stopwords is False)
        assert result == {'hello': 5.0, 'the': 2.0}
        # Verify stopwords.words was not called when include_stopwords is True
        mock_stopwords.words.assert_not_called()
    
    @patch('src.text_processor.WordCloud')
    @patch('src.text_processor.stopwords')
    def test_generate_word_count_parameters(self, mock_stopwords, mock_wordcloud_class):
        """Test that WordCloud is initialized with correct parameters."""
        mock_wordcloud = MagicMock()
        mock_wordcloud.process_text.return_value = {}
        mock_wordcloud_class.return_value = mock_wordcloud
        mock_stopwords.words.return_value = []
        
        generate_word_count_from_text(
            text="test",
            language='english',
            include_stopwords=False,
            collocations=True,
            max_words=100,
            min_word_length=3,
            normalize_plurals=True,
            include_numbers=False,
            canvas_width=800,
            canvas_height=400
        )
        
        # Verify WordCloud was called with correct parameters
        mock_wordcloud_class.assert_called_once()
        # call_args is a tuple: (args, kwargs) or a CallArgs object
        if hasattr(mock_wordcloud_class.call_args, 'kwargs'):
            call_kwargs = mock_wordcloud_class.call_args.kwargs
        else:
            call_kwargs = mock_wordcloud_class.call_args[1] if len(mock_wordcloud_class.call_args) > 1 else {}
        
        assert call_kwargs.get('width') == 800
        assert call_kwargs.get('height') == 400
        assert call_kwargs.get('collocations') is True
        assert call_kwargs.get('max_words') == 100
        assert call_kwargs.get('min_word_length') == 3
        assert call_kwargs.get('normalize_plurals') is True
        assert call_kwargs.get('include_numbers') is False

