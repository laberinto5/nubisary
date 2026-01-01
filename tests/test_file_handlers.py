"""Unit tests for file_handlers module."""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open

from src.file_handlers import (
    is_json_file,
    validate_json_format,
    read_text_file,
    read_json_file,
    convert_document_to_text_file,
    FileHandlerError,
    JSONParseError
)


class TestIsJsonFile:
    """Tests for is_json_file function."""
    
    def test_json_extension(self):
        """Test files with .json extension."""
        assert is_json_file('file.json') is True
        assert is_json_file('path/to/file.json') is True
        assert is_json_file('FILE.JSON') is True  # Case insensitive
    
    def test_non_json_extension(self):
        """Test files without .json extension."""
        assert is_json_file('file.txt') is False
        assert is_json_file('file.pdf') is False
        assert is_json_file('file') is False


class TestValidateJsonFormat:
    """Tests for validate_json_format function."""
    
    def test_valid_json(self):
        """Test validation of valid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump({'key': 'value'}, tmp)
            tmp_path = tmp.name
        
        try:
            assert validate_json_format(tmp_path) is True
        finally:
            os.unlink(tmp_path)
    
    def test_invalid_json(self):
        """Test validation of invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write('{ invalid json }')
            tmp_path = tmp.name
        
        try:
            with pytest.raises(JSONParseError):
                validate_json_format(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_nonexistent_file(self):
        """Test validation of nonexistent file."""
        with pytest.raises(FileHandlerError):
            validate_json_format('/nonexistent/file.json')


class TestReadTextFile:
    """Tests for read_text_file function."""
    
    def test_read_text_file(self):
        """Test reading a text file."""
        content = 'This is test content\nWith multiple lines'
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            result = read_text_file(tmp_path, auto_convert=False)
            assert result == content
        finally:
            os.unlink(tmp_path)
    
    def test_read_text_file_with_conversion(self):
        """Test reading a file with auto-conversion disabled."""
        content = 'Test content'
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            with patch('src.file_handlers.is_convertible_document', return_value=False):
                result = read_text_file(tmp_path, auto_convert=True)
                assert result == content
        finally:
            os.unlink(tmp_path)
    
    def test_read_nonexistent_file(self):
        """Test reading nonexistent file raises error."""
        with pytest.raises(FileHandlerError):
            read_text_file('/nonexistent/file.txt', auto_convert=False)


class TestReadJsonFile:
    """Tests for read_json_file function."""
    
    def test_read_valid_json(self):
        """Test reading a valid JSON file."""
        data = {'key': 'value', 'number': 42, 'list': [1, 2, 3]}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(data, tmp)
            tmp_path = tmp.name
        
        try:
            result = read_json_file(tmp_path)
            assert result == data
        finally:
            os.unlink(tmp_path)
    
    def test_read_invalid_json(self):
        """Test reading invalid JSON raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write('{ invalid json }')
            tmp_path = tmp.name
        
        try:
            with pytest.raises(JSONParseError):
                read_json_file(tmp_path)
        finally:
            os.unlink(tmp_path)


class TestIsConvertibleDocument:
    """Tests for is_convertible_document function."""
    
    def test_pdf_file(self):
        """Test PDF file detection."""
        from src.document_converter import is_convertible_document
        
        assert is_convertible_document('file.pdf') is True
        assert is_convertible_document('file.PDF') is True
    
    def test_docx_file(self):
        """Test DOCX file detection."""
        from src.document_converter import is_convertible_document
        
        assert is_convertible_document('file.docx') is True
        assert is_convertible_document('file.DOCX') is True
    
    def test_doc_file(self):
        """Test DOC file detection."""
        from src.document_converter import is_convertible_document
        
        assert is_convertible_document('file.doc') is True
        assert is_convertible_document('file.DOC') is True
    
    def test_non_convertible_file(self):
        """Test non-convertible file detection."""
        from src.document_converter import is_convertible_document
        
        assert is_convertible_document('file.txt') is False
        assert is_convertible_document('file.json') is False


class TestConvertDocumentToTextFile:
    """Tests for convert_document_to_text_file function."""
    
    def test_convert_pdf_to_text_file(self):
        """Test converting PDF to text file."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with patch('src.file_handlers.is_convertible_document', return_value=True), \
                 patch('src.file_handlers.convert_document_to_text', return_value='Converted text'), \
                 patch('builtins.open', mock_open()) as mock_file:
                
                result = convert_document_to_text_file(tmp_path, 'output.txt')
                assert result == 'output.txt'
                mock_file.assert_called()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_convert_with_auto_generated_filename(self):
        """Test conversion with auto-generated output filename."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            import os.path
            base_name = os.path.splitext(tmp_path)[0]
            expected_output = base_name + '.txt'
            
            with patch('src.file_handlers.is_convertible_document', return_value=True), \
                 patch('src.file_handlers.convert_document_to_text', return_value='Text'), \
                 patch('builtins.open', mock_open()):
                
                result = convert_document_to_text_file(tmp_path, None)
                assert result == expected_output
                assert result.endswith('.txt')
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_convert_non_convertible_file(self):
        """Test converting non-convertible file raises error."""
        with pytest.raises(FileHandlerError) as exc_info:
            convert_document_to_text_file('file.txt', 'output.txt')
        assert 'not a convertible document' in str(exc_info.value).lower()

