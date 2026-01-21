"""Integration tests for wordcloud_service module."""

import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock, mock_open

from src.wordcloud_service import generate_wordcloud, process_text_to_frequencies, WordCloudServiceError
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
        """Test that document cleaning is always applied."""
        mock_read_text.return_value = "test text"
        mock_preprocess.return_value = "test text"
        mock_generate_count.return_value = {'test': 1.0}
        mock_validate_color.side_effect = lambda x: x
        mock_validate_lang.return_value = 'english'
        
        config = WordCloudConfig()
        
        # Test with clean_text=True (always cleaned)
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


class TestProcessTextToFrequencies:
    """Tests for process_text_to_frequencies pipeline."""

    @patch('src.wordcloud_service.validate_input_file')
    @patch('src.wordcloud_service.is_json_file', return_value=False)
    @patch('src.wordcloud_service.is_convertible_document', return_value=False)
    @patch('src.wordcloud_service.validate_language')
    @patch('src.wordcloud_service.read_text_file')
    @patch('src.wordcloud_service.remove_excluded_text')
    @patch('src.wordcloud_service.apply_literal_replacements')
    @patch('src.wordcloud_service.apply_regex_transformations')
    @patch('src.wordcloud_service.preprocess_text')
    @patch('src.wordcloud_service.normalize_plurals_with_lemmatization')
    @patch('src.wordcloud_service.generate_word_count_from_text')
    def test_pipeline_order_with_lemmatize(
        self,
        mock_generate_count,
        mock_normalize,
        mock_preprocess,
        mock_apply_regex,
        mock_apply_literal,
        mock_remove_excluded,
        mock_read_text,
        mock_validate_lang,
        mock_is_doc,
        mock_is_json,
        mock_validate_file
    ):
        """Test ordered pipeline: read -> exclude -> replace -> regex -> preprocess -> lemmatize -> count."""
        mock_read_text.return_value = "RAW"
        mock_remove_excluded.return_value = "EXCLUDED"
        mock_apply_literal.return_value = "REPLACED"
        mock_apply_regex.return_value = "REGEX"
        mock_preprocess.return_value = "PREPROC"
        mock_normalize.return_value = "LEMMA"
        mock_generate_count.return_value = {"foo": 1}

        config = WordCloudConfig(
            include_stopwords=True,
            case_sensitive=False,
            ngram="bigram",
            lemmatize=True,
            include_numbers=False
        )

        result = process_text_to_frequencies(
            input_file="test.txt",
            language="spanish",
            config=config,
            clean_text=True,
            exclude_words="foo,bar",
            exclude_case_sensitive=False,
            regex_rule="foo|bar",
            regex_case_sensitive=False,
            replace_search="foo,bar",
            replace_with="baz",
            replace_mode="list",
            replace_case_sensitive=False
        )

        assert result == {"foo": 1}
        mock_read_text.assert_called_once_with("test.txt", auto_convert=True, clean_text=True)
        mock_remove_excluded.assert_called_once_with("RAW", ["foo", "bar"], False)
        mock_apply_literal.assert_called_once()
        mock_apply_regex.assert_called_once()
        mock_preprocess.assert_called_once_with("REGEX", False, include_numbers=False)
        mock_normalize.assert_called_once_with("PREPROC", "spanish")
        mock_generate_count.assert_called_once_with(
            text="LEMMA",
            language="spanish",
            include_stopwords=True,
            ngram="bigram",
            include_numbers=False
        )

    @patch('src.wordcloud_service.validate_input_file')
    @patch('src.wordcloud_service.is_json_file', return_value=False)
    @patch('src.wordcloud_service.is_convertible_document', return_value=False)
    @patch('src.wordcloud_service.validate_language')
    @patch('src.wordcloud_service.read_text_file')
    @patch('src.wordcloud_service.preprocess_text')
    @patch('src.wordcloud_service.normalize_plurals_with_lemmatization')
    @patch('src.wordcloud_service.generate_word_count_from_text')
    def test_pipeline_skips_lemmatize_when_disabled(
        self,
        mock_generate_count,
        mock_normalize,
        mock_preprocess,
        mock_read_text,
        mock_validate_lang,
        mock_is_doc,
        mock_is_json,
        mock_validate_file
    ):
        """Test that lemmatization is skipped when disabled."""
        mock_read_text.return_value = "RAW"
        mock_preprocess.return_value = "PREPROC"
        mock_generate_count.return_value = {"foo": 1}

        config = WordCloudConfig(lemmatize=False, include_stopwords=True)

        result = process_text_to_frequencies(
            input_file="test.txt",
            language="spanish",
            config=config,
            clean_text=True
        )

        assert result == {"foo": 1}
        mock_normalize.assert_not_called()
        
        # Test with clean_text=False (still cleaned)
        generate_wordcloud(
            input_file='test.txt',
            language='english',
            config=config,
            clean_text=False,
            show=False
        )
        
        # Verify clean_text was still passed as True
        call_args = mock_read_text.call_args
        assert call_args[1]['clean_text'] is True

