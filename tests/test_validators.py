"""Unit tests for validators module."""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from src.validators import (
    validate_color_reference,
    validate_language,
    validate_input_file,
    validate_output_file,
    sanitize_filename,
    generate_output_filename,
    ColorValidationError,
    LanguageValidationError,
    FileValidationError
)


class TestValidateColorReference:
    """Tests for validate_color_reference function."""
    
    def test_valid_color_name(self):
        """Test valid color names."""
        assert validate_color_reference('white') == 'white'
        assert validate_color_reference('blue') == 'blue'
        assert validate_color_reference('red') == 'red'
    
    def test_valid_hex_color(self):
        """Test valid hex color codes."""
        assert validate_color_reference('#FF0000') == '#FF0000'
        assert validate_color_reference('#00FF00') == '#00FF00'
        assert validate_color_reference('#0000FF') == '#0000FF'
        assert validate_color_reference('#ffffff') == '#ffffff'
        assert validate_color_reference('#123ABC') == '#123ABC'
    
    def test_none_color(self):
        """Test None color returns None."""
        assert validate_color_reference(None) is None
    
    def test_invalid_color_name(self):
        """Test invalid color names raise error."""
        with pytest.raises(ColorValidationError):
            validate_color_reference('purple')
        with pytest.raises(ColorValidationError):
            validate_color_reference('invalid')
    
    def test_invalid_hex_color(self):
        """Test invalid hex color codes raise error."""
        with pytest.raises(ColorValidationError):
            validate_color_reference('#GG0000')  # Invalid hex
        with pytest.raises(ColorValidationError):
            validate_color_reference('#FF00')  # Too short
        with pytest.raises(ColorValidationError):
            validate_color_reference('#FF00000')  # Too long
        with pytest.raises(ColorValidationError):
            validate_color_reference('FF0000')  # Missing #


class TestValidateLanguage:
    """Tests for validate_language function."""
    
    def test_valid_language(self):
        """Test valid languages."""
        with patch('src.validators.nltk.download') as mock_download, \
             patch('src.validators.stopwords.words', return_value=['the', 'a', 'an']) as mock_stopwords:
            result1 = validate_language('english', include_stopwords=False)
            assert result1 == 'english'
            # nltk.download should be called for punkt
            mock_download.assert_called()
            # stopwords.words should be called when include_stopwords=False
            mock_stopwords.assert_called()
            
            # Reset mocks for second test
            mock_download.reset_mock()
            mock_stopwords.reset_mock()
            
            result2 = validate_language('spanish', include_stopwords=False)
            assert result2 == 'spanish'
    
    def test_invalid_language(self):
        """Test invalid languages raise error."""
        with pytest.raises(LanguageValidationError) as exc_info:
            validate_language('invalid_language')
        assert 'not supported' in str(exc_info.value).lower()
    
    @patch('src.validators.nltk.download')
    @patch('src.validators.stopwords.words')
    def test_language_with_stopwords_download(self, mock_stopwords, mock_download):
        """Test that NLTK resources are downloaded if needed."""
        # First call raises LookupError, second call succeeds
        mock_stopwords.side_effect = [LookupError(), ['the', 'a']]
        mock_download.return_value = None
        
        result = validate_language('english', include_stopwords=False)
        assert result == 'english'
        # Should have been called to download punkt and stopwords
        assert mock_download.called


class TestValidateInputFile:
    """Tests for validate_input_file function."""
    
    def test_existing_file(self):
        """Test validation of existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            result = validate_input_file(tmp_path)
            assert result == tmp_path
        finally:
            os.unlink(tmp_path)
    
    def test_nonexistent_file(self):
        """Test that nonexistent file raises error."""
        with pytest.raises(FileValidationError) as exc_info:
            validate_input_file('/nonexistent/file/path.txt')
        assert 'does not exist' in str(exc_info.value).lower()
    
    def test_unreadable_file(self):
        """Test that unreadable file raises error."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Make file unreadable (if possible on this system)
            os.chmod(tmp_path, 0o000)
            try:
                with pytest.raises(FileValidationError) as exc_info:
                    validate_input_file(tmp_path)
                assert 'not readable' in str(exc_info.value).lower()
            except PermissionError:
                # On some systems, we can't test this
                pass
        finally:
            os.chmod(tmp_path, 0o644)
            os.unlink(tmp_path)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""
    
    def test_simple_filename(self):
        """Test simple filename is unchanged."""
        assert sanitize_filename('simple') == 'simple'
        assert sanitize_filename('test123') == 'test123'
    
    def test_filename_with_spaces(self):
        """Test filename with spaces gets spaces replaced."""
        assert sanitize_filename('my file') == 'my_file'
        assert sanitize_filename('file with spaces') == 'file_with_spaces'
    
    def test_filename_with_special_chars(self):
        """Test filename with special characters gets sanitized."""
        assert sanitize_filename('file@name#123') == 'file_name_123'
        assert sanitize_filename('file!name$test') == 'file_name_test'
        assert sanitize_filename('file(name)test') == 'file_name_test'
    
    def test_filename_with_hyphens_underscores(self):
        """Test filename keeps hyphens and underscores."""
        assert sanitize_filename('file-name') == 'file-name'
        assert sanitize_filename('file_name') == 'file_name'
        assert sanitize_filename('file-name_test') == 'file-name_test'
    
    def test_filename_with_multiple_spaces(self):
        """Test multiple spaces become single underscore."""
        assert sanitize_filename('file   name') == 'file_name'
        assert sanitize_filename('file    name   test') == 'file_name_test'
    
    def test_filename_with_leading_trailing_underscores(self):
        """Test leading/trailing underscores are removed."""
        assert sanitize_filename('_filename_') == 'filename'
        assert sanitize_filename('__file__name__') == 'file_name'
    
    def test_empty_filename(self):
        """Test empty filename gets default name."""
        assert sanitize_filename('') == 'wordcloud'
        assert sanitize_filename('___') == 'wordcloud'
    
    def test_filename_with_extension(self):
        """Test extension is removed before sanitization."""
        assert sanitize_filename('file name.txt') == 'file_name'
        assert sanitize_filename('my file.pdf') == 'my_file'


class TestGenerateOutputFilename:
    """Tests for generate_output_filename function."""
    
    def test_simple_input(self):
        """Test simple input filename generation."""
        result = generate_output_filename('/path/to/input.txt', '.png')
        assert result.endswith('.png')
        assert 'input' in result
        assert os.path.dirname(result) == os.path.abspath('/path/to')
    
    def test_input_with_spaces(self):
        """Test input filename with spaces gets sanitized."""
        result = generate_output_filename('/path/to/my file.txt', '.png')
        assert result.endswith('.png')
        assert 'my_file' in result
        assert ' ' not in os.path.basename(result)
    
    def test_input_with_special_chars(self):
        """Test input filename with special chars gets sanitized."""
        result = generate_output_filename('/path/to/file@name#123.txt', '.png')
        assert result.endswith('.png')
        assert 'file_name_123' in result
        assert '@' not in os.path.basename(result)
        assert '#' not in os.path.basename(result)
    
    def test_input_in_current_directory(self):
        """Test input in current directory."""
        result = generate_output_filename('input.txt', '.png')
        assert result.endswith('.png')
        assert 'input' in result
        assert os.path.dirname(result) == os.path.abspath('.')


class TestValidateOutputFile:
    """Tests for validate_output_file function."""
    
    def test_none_output_no_input(self):
        """Test None output with no input returns None."""
        assert validate_output_file(None) is None
    
    def test_none_output_with_input(self):
        """Test None output with input auto-generates filename."""
        result = validate_output_file(None, '/path/to/input.txt')
        assert result is not None
        assert result.endswith('.png')
        assert 'input' in result
        assert os.path.dirname(result) == os.path.abspath('/path/to')
    
    def test_output_with_png_extension(self):
        """Test output with .png extension is unchanged."""
        assert validate_output_file('output.png') == 'output.png'
        assert validate_output_file('output.png', '/path/to/input.txt') == 'output.png'
    
    def test_output_without_extension(self):
        """Test output without extension gets .png added."""
        assert validate_output_file('output') == 'output.png'
    
    def test_output_with_other_extension(self):
        """Test output with other extension gets .png added."""
        assert validate_output_file('output.jpg') == 'output.jpg.png'
        assert validate_output_file('output.txt') == 'output.txt.png'
    
    def test_auto_generate_with_spaces(self):
        """Test auto-generation sanitizes spaces in filename."""
        result = validate_output_file(None, '/path/to/my file.txt')
        assert result.endswith('.png')
        assert 'my_file' in result
        assert ' ' not in os.path.basename(result)
    
    def test_auto_generate_with_special_chars(self):
        """Test auto-generation sanitizes special characters."""
        result = validate_output_file(None, '/path/to/file@name.txt')
        assert result.endswith('.png')
        assert '@' not in os.path.basename(result)
        assert 'file_name' in result

