"""File I/O operations for Word Cloud Generator."""

import json
from typing import Dict, Any, Optional

from src.validators import FileValidationError
from src.document_converter import (
    is_convertible_document,
    convert_document_to_text,
    DocumentConversionError
)


class FileHandlerError(Exception):
    """Base exception for file handler errors."""
    pass


class JSONParseError(FileHandlerError):
    """Exception raised when JSON parsing fails."""
    pass


def is_json_file(file_path: str) -> bool:
    """
    Check if a file is a JSON file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file has .json extension, False otherwise
    """
    return file_path.lower().endswith('.json')


def validate_json_format(file_path: str) -> bool:
    """
    Validate that a file contains valid JSON without loading the full content.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        True if JSON is valid
        
    Raises:
        FileHandlerError: If file cannot be read
        JSONParseError: If JSON is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json.load(file)
        return True
    except json.JSONDecodeError as e:
        raise JSONParseError(f'Invalid JSON file: {e}')
    except Exception as e:
        raise FileHandlerError(f'Error reading JSON file: {e}')


def read_text_file(file_path: str, auto_convert: bool = True, clean_text: bool = True) -> str:
    """
    Read text content from a file.
    Automatically converts PDF/DOC/DOCX to text if auto_convert is True.
    
    Args:
        file_path: Path to the text file (or PDF/DOC/DOCX)
        auto_convert: If True, automatically convert PDF/DOC/DOCX to text
        clean_text: If True, apply text cleaning (remove page numbers, excessive blank lines)
        
    Returns:
        File content as string
        
    Raises:
        FileHandlerError: If file cannot be read
        DocumentConversionError: If document conversion fails
    """
    # Check if file needs conversion
    if auto_convert and is_convertible_document(file_path):
        try:
            # Always apply document cleaning (page numbers/roman numerals/blank lines)
            return convert_document_to_text(file_path, clean_text=True)
        except DocumentConversionError as e:
            raise FileHandlerError(f'Error converting document {file_path}: {e}')
    
    # Read as plain text file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise FileHandlerError(f'Error reading text file {file_path}: {e}')


def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON content as dictionary
        
    Raises:
        FileHandlerError: If file cannot be read
        JSONParseError: If JSON is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise JSONParseError(f'Invalid JSON file {file_path}: {e}')
    except Exception as e:
        raise FileHandlerError(f'Error reading JSON file {file_path}: {e}')


def convert_document_to_text_file(
    input_file: str,
    output_file: Optional[str] = None,
    clean_text: bool = True
) -> str:
    """
    Convert a document (PDF/DOC/DOCX) to a text file.
    
    Args:
        input_file: Path to the document file
        output_file: Optional path for output text file.
                     If None, generates output filename automatically.
        clean_text: If True, apply text cleaning (remove page numbers, excessive blank lines)
        
    Returns:
        Path to the created text file
        
    Raises:
        FileHandlerError: If conversion fails
        UnsupportedFormatError: If file format is not supported
    """
    if not is_convertible_document(input_file):
        raise FileHandlerError(
            f'File is not a convertible document: {input_file}. '
            'Supported formats: PDF, DOC, DOCX'
        )
    
    try:
        # Convert document to text
        # Always apply document cleaning (page numbers/roman numerals/blank lines)
        text_content = convert_document_to_text(input_file, clean_text=True)
        
        # Generate output filename if not provided
        if output_file is None:
            import os
            base_name = os.path.splitext(input_file)[0]
            output_file = f'{base_name}.txt'
        
        # Ensure .txt extension
        if not output_file.endswith('.txt'):
            output_file = output_file + '.txt'
        
        # Write text to file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(text_content)
        
        return output_file
        
    except DocumentConversionError as e:
        raise FileHandlerError(f'Error converting document: {e}')
    except Exception as e:
        raise FileHandlerError(f'Error writing output file {output_file}: {e}')

