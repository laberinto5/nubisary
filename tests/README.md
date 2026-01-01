# Word Cloud Generator - Test Suite

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### Run specific test file
```bash
pytest tests/test_validators.py
```

### Run specific test
```bash
pytest tests/test_validators.py::TestValidateColorReference::test_valid_color_name
```

### Run with verbose output
```bash
pytest -v
```

## Test Structure

- `test_validators.py` - Tests for input validation functions
- `test_file_handlers.py` - Tests for file I/O operations
- `test_text_processor.py` - Tests for text preprocessing
- `test_document_converter.py` - Tests for document conversion and text cleaning
- `test_config.py` - Tests for configuration constants and dataclasses
- `test_wordcloud_service.py` - Integration tests for the service layer

## Test Coverage

The test suite covers:
- ✅ Input validation (colors, languages, files)
- ✅ File operations (reading, JSON parsing, document detection)
- ✅ Text preprocessing (punctuation removal, case handling)
- ✅ Text cleaning (page numbers, blank lines, Roman numerals)
- ✅ Configuration management
- ✅ Service layer integration

## Notes

- Some tests use mocks to avoid external dependencies (NLTK downloads, file system operations)
- Integration tests mock WordCloud generation to avoid requiring matplotlib display
- Tests are designed to run quickly without external file dependencies

