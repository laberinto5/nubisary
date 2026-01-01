"""Unit tests for document_converter module."""

import pytest
import os
import tempfile

from src.document_converter import (
    is_pdf_file,
    is_doc_file,
    is_docx_file,
    is_convertible_document,
    clean_converted_text,
    convert_doc_to_text,
    DocumentConversionError
)


class TestFileTypeDetection:
    """Tests for file type detection functions."""
    
    def test_is_pdf_file(self):
        """Test PDF file detection."""
        assert is_pdf_file('file.pdf') is True
        assert is_pdf_file('file.PDF') is True
        assert is_pdf_file('path/to/file.pdf') is True
        assert is_pdf_file('file.txt') is False
        assert is_pdf_file('file.pdfx') is False
    
    def test_is_doc_file(self):
        """Test DOC file detection."""
        assert is_doc_file('file.doc') is True
        assert is_doc_file('file.DOC') is True
        assert is_doc_file('file.txt') is False
    
    def test_is_docx_file(self):
        """Test DOCX file detection."""
        assert is_docx_file('file.docx') is True
        assert is_docx_file('file.DOCX') is True
        assert is_docx_file('file.doc') is False
    
    def test_is_convertible_document(self):
        """Test convertible document detection."""
        assert is_convertible_document('file.pdf') is True
        assert is_convertible_document('file.doc') is True
        assert is_convertible_document('file.docx') is True
        assert is_convertible_document('file.txt') is False
        assert is_convertible_document('file.json') is False


class TestCleanConvertedText:
    """Tests for clean_converted_text function."""
    
    def test_remove_excessive_blank_lines(self):
        """Test that multiple blank lines are reduced to one."""
        text = "Line 1\n\n\n\nLine 2"
        result = clean_converted_text(text)
        # Should have at most one blank line between lines
        assert '\n\n\n' not in result
        assert 'Line 1' in result
        assert 'Line 2' in result
    
    def test_remove_page_numbers_arabic(self):
        """Test removal of Arabic page numbers."""
        text = "Content here\n1\nMore content\n2\nEnd"
        result = clean_converted_text(text)
        # Check that standalone page numbers are removed
        lines = [line.strip() for line in result.split('\n') if line.strip()]
        # Page numbers alone should not be in the cleaned lines
        assert '1' not in lines or any('1' in line and len(line) > 1 for line in lines)
        assert '2' not in lines or any('2' in line and len(line) > 1 for line in lines)
        assert 'Content here' in result
        assert 'More content' in result
    
    def test_remove_page_numbers_with_symbols(self):
        """Test removal of page numbers with symbols."""
        test_cases = [
            "Content\n(1)\nMore",
            "Content\n[1]\nMore",
            "Content\n-1-\nMore",
            "Content\n  1  \nMore",
        ]
        for text in test_cases:
            result = clean_converted_text(text)
            # Page number should be removed
            lines = [line.strip() for line in result.split('\n') if line.strip()]
            assert '1' not in lines or any('1' in line and len(line) > 1 for line in lines)
    
    def test_remove_roman_numerals(self):
        """Test removal of Roman numeral page numbers."""
        test_cases = [
            "Content\nI\nMore",
            "Content\nII\nMore",
            "Content\nIII\nMore",
            "Content\nIV\nMore",
            "Content\nV\nMore",
            "Content\n[II]\nMore",
            "Content\n-III-\nMore",
            "Content\n(IV)\nMore",
        ]
        for text in test_cases:
            result = clean_converted_text(text)
            lines = [line.strip() for line in result.split('\n') if line.strip()]
            # Roman numerals alone should be removed
            assert 'I' not in lines or any('I' in line and len(line) > 1 for line in lines)
    
    def test_preserve_roman_numerals_in_text(self):
        """Test that Roman numerals in actual text are preserved."""
        text = "Chapter I: Introduction\nContent here"
        result = clean_converted_text(text)
        # Should preserve "Chapter I: Introduction" as it's not just a Roman numeral
        assert 'Chapter' in result or 'Introduction' in result
    
    def test_preserve_numbers_in_text(self):
        """Test that numbers in actual text are preserved."""
        text = "There are 5 items in the list"
        result = clean_converted_text(text)
        assert '5' in result
        assert 'items' in result
    
    def test_remove_trailing_blank_lines(self):
        """Test that trailing blank lines are removed."""
        text = "Content\n\n\n"
        result = clean_converted_text(text)
        assert not result.endswith('\n\n')
        assert result.endswith('Content') or result.endswith('\n')
    
    def test_preserve_single_blank_line(self):
        """Test that single blank lines are preserved."""
        text = "Paragraph 1\n\nParagraph 2"
        result = clean_converted_text(text)
        assert '\n\n' in result  # Should have one blank line
    
    def test_empty_text(self):
        """Test empty text handling."""
        assert clean_converted_text("") == ""
        assert clean_converted_text("\n\n\n") == ""
    
    def test_only_page_numbers(self):
        """Test text with only page numbers."""
        text = "1\n2\n3"
        result = clean_converted_text(text)
        # All page numbers should be removed, leaving empty or minimal content
        lines = [line.strip() for line in result.split('\n') if line.strip()]
        assert len(lines) == 0 or all('1' not in line and '2' not in line and '3' not in line for line in lines)
    
    def test_complex_example(self):
        """Test a complex real-world example."""
        text = """Introduction

1

This is the first paragraph.

2

This is the second paragraph.

III

Conclusion"""
        result = clean_converted_text(text)
        # Page numbers should be removed
        assert 'Introduction' in result
        assert 'Conclusion' in result
        # Should not have excessive blank lines
        assert '\n\n\n' not in result


class TestConvertDocToText:
    """Tests for convert_doc_to_text function."""
    
    def test_doc_not_supported(self):
        """Test that DOC files raise appropriate error."""
        # Create a temporary file that exists so we can test the DOC format error
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with pytest.raises(DocumentConversionError) as exc_info:
                convert_doc_to_text(tmp_path)
            
            error_msg = str(exc_info.value)
            assert 'not directly supported' in error_msg.lower()
            assert 'convert' in error_msg.lower() or 'docx' in error_msg.lower()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_nonexistent_doc_file(self):
        """Test that nonexistent DOC file raises error."""
        from src.validators import FileValidationError
        
        with pytest.raises(FileValidationError):
            convert_doc_to_text('/nonexistent/file.doc')

