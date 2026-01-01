"""Integration tests for wordcloud_service module."""

import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock, mock_open

from src.wordcloud_service import generate_wordcloud, WordCloudServiceError
from src.config import WordCloudConfig
from src.validators import ValidationError, FileValidationError
from src.file_handlers import FileHandlerError


class TestGenerateWordcloud:
    """Tests for generate_wordcloud function."""
    
    @patch('src.wordcloud_service.validate_input_file')
    @patch('src.wordcloud_service.is_json_file', return_value=False)
    @patch('src.wordcloud_service.is_convertible_document', return_value=False)
    @patch('src.wordcloud_service.validate_language')
    @patch('src.wordcloud_service.validate_color_reference')
    @patch('src.wordcloud_service.read_text_file')
    @patch('src.wordcloud_service.preprocess_text')
    @patch('src.wordcloud_service.generate_word_count_from_text')
    @patch('src.wordcloud_service.generate_word_cloud_from_frequencies')
    def test_generate_from_text_file(
        self,
        mock_generate_cloud,
        mock_generate_count,
        mock_preprocess,
        mock_read_text,
        mock_validate_color,
        mock_validate_lang,
        mock_is_doc,
        mock_is_json,
        mock_validate_file
    ):
        """Test generating word cloud from text file."""
        # Setup mocks
        mock_read_text.return_value = "test text content"
        mock_preprocess.return_value = "test text content"
        mock_generate_count.return_value = {'test': 5.0, 'text': 3.0}
        mock_validate_color.side_effect = lambda x: x
        mock_validate_lang.return_value = 'english'
        
        config = WordCloudConfig()
        
        result = generate_wordcloud(
            input_file='test.txt',
            language='english',
            output_file='output.png',
            config=config,
            show=False
        )
        
        assert result == {'test': 5.0, 'text': 3.0}
        mock_validate_file.assert_called_once_with('test.txt')
        mock_read_text.assert_called_once()
        mock_preprocess.assert_called_once()
        mock_generate_count.assert_called_once()
        mock_generate_cloud.assert_called_once()
    
    @patch('src.wordcloud_service.validate_input_file')
    @patch('src.wordcloud_service.is_json_file', return_value=True)
    @patch('src.wordcloud_service.validate_json_format')
    @patch('src.wordcloud_service.read_json_file')
    @patch('src.wordcloud_service.validate_color_reference')
    @patch('src.wordcloud_service.generate_word_cloud_from_frequencies')
    def test_generate_from_json_file(
        self,
        mock_generate_cloud,
        mock_validate_color,
        mock_read_json,
        mock_validate_json,
        mock_is_json,
        mock_validate_file
    ):
        """Test generating word cloud from JSON file."""
        # Setup mocks
        mock_read_json.return_value = {'word1': 10.0, 'word2': 5.0}
        mock_validate_color.side_effect = lambda x: x
        
        config = WordCloudConfig()
        
        result = generate_wordcloud(
            input_file='test.json',
            language='english',  # Not used for JSON but required
            output_file='output.png',
            config=config,
            show=False
        )
        
        assert result == {'word1': 10.0, 'word2': 5.0}
        mock_read_json.assert_called_once_with('test.json')
        mock_generate_cloud.assert_called_once()
    
    @patch('src.wordcloud_service.validate_input_file')
    @patch('src.wordcloud_service.is_json_file', return_value=False)
    @patch('src.wordcloud_service.is_convertible_document', return_value=True)
    @patch('src.wordcloud_service.validate_language')
    @patch('src.wordcloud_service.validate_color_reference')
    @patch('src.wordcloud_service.read_text_file')
    @patch('src.wordcloud_service.preprocess_text')
    @patch('src.wordcloud_service.generate_word_count_from_text')
    @patch('src.wordcloud_service.generate_word_cloud_from_frequencies')
    def test_generate_from_pdf_file(
        self,
        mock_generate_cloud,
        mock_generate_count,
        mock_preprocess,
        mock_read_text,
        mock_validate_color,
        mock_validate_lang,
        mock_is_doc,
        mock_is_json,
        mock_validate_file
    ):
        """Test generating word cloud from PDF file (auto-conversion)."""
        mock_read_text.return_value = "converted pdf text"
        mock_preprocess.return_value = "converted pdf text"
        mock_generate_count.return_value = {'pdf': 2.0, 'text': 1.0}
        mock_validate_color.side_effect = lambda x: x
        mock_validate_lang.return_value = 'english'
        
        config = WordCloudConfig()
        
        result = generate_wordcloud(
            input_file='test.pdf',
            language='english',
            config=config,
            show=False
        )
        
        assert result == {'pdf': 2.0, 'text': 1.0}
        # Should auto-convert PDF
        mock_read_text.assert_called_once()
        mock_generate_cloud.assert_called_once()
    
    def test_validation_error_handling(self):
        """Test that validation errors are properly handled."""
        with patch('src.wordcloud_service.validate_input_file') as mock_validate:
            mock_validate.side_effect = FileValidationError('File not found')
            
            with pytest.raises(WordCloudServiceError) as exc_info:
                generate_wordcloud(
                    input_file='nonexistent.txt',
                    language='english',
                    show=False
                )
            
            assert 'File not found' in str(exc_info.value)
    
    def test_file_handler_error_handling(self):
        """Test that file handler errors are properly handled."""
        with patch('src.wordcloud_service.validate_input_file'), \
             patch('src.wordcloud_service.is_json_file', return_value=False), \
             patch('src.wordcloud_service.is_convertible_document', return_value=False), \
             patch('src.wordcloud_service.validate_language'), \
             patch('src.wordcloud_service.read_text_file') as mock_read:
            
            mock_read.side_effect = FileHandlerError('Read error')
            
            with pytest.raises(WordCloudServiceError) as exc_info:
                generate_wordcloud(
                    input_file='test.txt',
                    language='english',
                    show=False
                )
            
            assert 'Read error' in str(exc_info.value)
    
    @patch('src.wordcloud_service.validate_input_file')
    @patch('src.wordcloud_service.is_json_file', return_value=False)
    @patch('src.wordcloud_service.is_convertible_document', return_value=False)
    @patch('src.wordcloud_service.validate_language')
    @patch('src.wordcloud_service.validate_color_reference')
    @patch('src.wordcloud_service.read_text_file')
    @patch('src.wordcloud_service.preprocess_text')
    @patch('src.wordcloud_service.generate_word_count_from_text')
    @patch('src.wordcloud_service.generate_word_cloud_from_frequencies')
    def test_clean_text_parameter(
        self,
        mock_generate_cloud,
        mock_generate_count,
        mock_preprocess,
        mock_read_text,
        mock_validate_color,
        mock_validate_lang,
        mock_is_doc,
        mock_is_json,
        mock_validate_file
    ):
        """Test that clean_text parameter is passed correctly."""
        mock_read_text.return_value = "test text"
        mock_preprocess.return_value = "test text"
        mock_generate_count.return_value = {'test': 1.0}
        mock_validate_color.side_effect = lambda x: x
        mock_validate_lang.return_value = 'english'
        
        config = WordCloudConfig()
        
        # Test with clean_text=True
        generate_wordcloud(
            input_file='test.txt',
            language='english',
            config=config,
            clean_text=True,
            show=False
        )
        
        # Verify clean_text was passed to read_text_file
        call_args = mock_read_text.call_args
        assert call_args[1]['clean_text'] is True
        
        # Test with clean_text=False
        generate_wordcloud(
            input_file='test.txt',
            language='english',
            config=config,
            clean_text=False,
            show=False
        )
        
        # Verify clean_text was passed as False
        call_args = mock_read_text.call_args
        assert call_args[1]['clean_text'] is False

