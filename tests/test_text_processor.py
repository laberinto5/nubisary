"""Unit tests for text_processor module."""

import pytest
from unittest.mock import patch, MagicMock

from src.text_processor import (
    preprocess_text,
    generate_word_count_from_text,
    normalize_spaces,
    remove_excluded_text,
    parse_exclude_words_argument,
    parse_regex_rule_argument,
    apply_regex_transformations,
    RegexRule,
    _normalize_backreferences
)
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


class TestNormalizeSpaces:
    """Tests for normalize_spaces function."""
    
    def test_single_space(self):
        """Test that single spaces are preserved."""
        text = "hello world"
        assert normalize_spaces(text) == "hello world"
    
    def test_multiple_spaces(self):
        """Test that multiple spaces are normalized to single space."""
        text = "hello    world"
        assert normalize_spaces(text) == "hello world"
    
    def test_tabs_and_newlines(self):
        """Test that tabs and newlines are normalized to spaces."""
        text = "hello\t\tworld\n\n"
        result = normalize_spaces(text)
        assert "hello" in result
        assert "world" in result
        assert "\t" not in result
        assert "\n" not in result
    
    def test_empty_string(self):
        """Test empty string."""
        assert normalize_spaces("") == ""
    
    def test_only_spaces(self):
        """Test string with only spaces."""
        assert normalize_spaces("   ") == " "


class TestRemoveExcludedText:
    """Tests for remove_excluded_text function."""
    
    def test_no_exclusions(self):
        """Test that text is unchanged when no exclusions."""
        text = "hello world"
        result = remove_excluded_text(text, [])
        assert result == text
    
    def test_single_word_case_insensitive(self):
        """Test removing a single word (case-insensitive)."""
        text = "Hello world hello WORLD"
        result = remove_excluded_text(text, ["hello"], case_sensitive=False)
        assert "hello" not in result.lower()
        assert "world" in result.lower()
    
    def test_single_word_case_sensitive(self):
        """Test removing a single word (case-sensitive)."""
        text = "Hello world hello"
        result = remove_excluded_text(text, ["Hello"], case_sensitive=True)
        assert "Hello" not in result
        assert "hello" in result
        assert "world" in result
    
    def test_phrase_case_insensitive(self):
        """Test removing a phrase (case-insensitive)."""
        text = "This is a test. This is a test again."
        result = remove_excluded_text(text, ["this is a test"], case_sensitive=False)
        assert "this is a test" not in result.lower()
    
    def test_normalize_spaces_in_matching(self):
        """Test that multiple spaces are normalized for matching."""
        text = "hello    world"
        result = remove_excluded_text(text, ["hello world"], case_sensitive=False)
        assert "hello" not in result.lower()
        assert "world" not in result.lower()
    
    def test_preserve_punctuation(self):
        """Test that punctuation is preserved and affects matching."""
        text = "Hello world. Hello world again"
        # Should match "Hello world" but not "Hello world."
        result = remove_excluded_text(text, ["Hello world"], case_sensitive=False)
        # The phrase without period should be removed, but "Hello world." should remain
        assert "Hello world again" not in result.lower()  # "Hello world" part removed
        # The period should remain in the text
        assert "." in result
    
    def test_multiple_exclusions(self):
        """Test removing multiple words/phrases."""
        text = "hello world test phrase"
        result = remove_excluded_text(text, ["hello", "test"], case_sensitive=False)
        assert "hello" not in result.lower()
        assert "test" not in result.lower()
        assert "world" in result.lower()
        assert "phrase" in result.lower()
    
    def test_word_boundaries(self):
        """Test that single words match only as whole words."""
        text = "casa casamiento"
        result = remove_excluded_text(text, ["casa"], case_sensitive=False)
        # "casa" as a whole word should be removed
        # Check that "casa" is not a standalone word (but may appear in "casamiento")
        words = result.split()
        assert "casa" not in words  # "casa" as whole word should be gone
        assert "casamiento" in words  # "casamiento" should remain
    
    def test_preserve_line_breaks(self):
        """Test that line breaks are preserved."""
        text = "line one\nline two\nline three"
        result = remove_excluded_text(text, ["line two"], case_sensitive=False)
        assert "\n" in result
        assert "line one" in result
        assert "line two" not in result.lower()
        assert "line three" in result
    
    def test_empty_excluded_item(self):
        """Test that empty excluded items are ignored."""
        text = "hello world"
        result = remove_excluded_text(text, ["", "   ", "hello"], case_sensitive=False)
        assert "hello" not in result.lower()
        assert "world" in result.lower()


class TestParseExcludeWordsArgument:
    """Tests for parse_exclude_words_argument function."""
    
    def test_none_argument(self):
        """Test that None returns empty list."""
        result = parse_exclude_words_argument(None)
        assert result == []
    
    def test_empty_string(self):
        """Test that empty string returns empty list."""
        result = parse_exclude_words_argument("")
        assert result == []
    
    def test_whitespace_only(self):
        """Test that whitespace-only string returns empty list."""
        result = parse_exclude_words_argument("   ")
        assert result == []
    
    def test_single_word(self):
        """Test parsing a single word."""
        result = parse_exclude_words_argument("hello")
        assert result == ["hello"]
    
    def test_comma_separated_list(self):
        """Test parsing comma-separated list."""
        result = parse_exclude_words_argument("hello,world,test")
        assert result == ["hello", "world", "test"]
    
    def test_comma_separated_with_spaces(self):
        """Test parsing comma-separated list with spaces."""
        result = parse_exclude_words_argument("hello, world , test")
        assert result == ["hello", "world", "test"]
    
    def test_file_path(self, tmp_path):
        """Test reading from file."""
        # Create a temporary file
        exclude_file = tmp_path / "exclude.txt"
        exclude_file.write_text("word1\nword2\nphrase with spaces\n")
        
        result = parse_exclude_words_argument(str(exclude_file))
        assert result == ["word1", "word2", "phrase with spaces"]
    
    def test_file_path_nonexistent(self):
        """Test that nonexistent file is treated as text."""
        result = parse_exclude_words_argument("nonexistent_file.txt")
        # Should be treated as a single word, not a file
        assert result == ["nonexistent_file.txt"]
    
    def test_file_path_with_comma(self, tmp_path):
        """Test that file path takes priority over comma-separated interpretation."""
        # Create a temporary file
        exclude_file = tmp_path / "exclude.txt"
        exclude_file.write_text("word1\nword2\n")
        
        # Even if it looks like comma-separated, if file exists, read from file
        result = parse_exclude_words_argument(str(exclude_file))
        assert result == ["word1", "word2"]
    
    def test_file_with_empty_lines(self, tmp_path):
        """Test that empty lines in file are skipped."""
        exclude_file = tmp_path / "exclude.txt"
        exclude_file.write_text("word1\n\nword2\n   \nword3\n")
        
        result = parse_exclude_words_argument(str(exclude_file))
        assert result == ["word1", "word2", "word3"]


class TestNormalizeBackreferences:
    """Tests for _normalize_backreferences function."""
    
    def test_normalize_byte_backreference(self):
        """Test that byte backreferences are normalized to string backreferences."""
        # \x01 is byte representation of \1
        input_str = 'P.\x01'
        result = _normalize_backreferences(input_str)
        assert result == 'P.\\1'
    
    def test_preserve_normal_text(self):
        """Test that normal text is preserved."""
        input_str = 'P.1 Hello World'
        result = _normalize_backreferences(input_str)
        assert result == 'P.1 Hello World'
    
    def test_multiple_backreferences(self):
        """Test multiple backreferences."""
        input_str = 'P.\x01 Q.\x02 R.\x03'
        result = _normalize_backreferences(input_str)
        assert result == 'P.\\1 Q.\\2 R.\\3'


class TestParseRegexRuleArgument:
    """Tests for parse_regex_rule_argument function."""
    
    def test_none_argument(self):
        """Test that None returns empty list."""
        result = parse_regex_rule_argument(None)
        assert result == []
    
    def test_empty_string(self):
        """Test that empty string returns empty list."""
        result = parse_regex_rule_argument("")
        assert result == []
    
    def test_whitespace_only(self):
        """Test that whitespace-only string returns empty list."""
        result = parse_regex_rule_argument("   ")
        assert result == []
    
    def test_single_pattern_remove(self):
        """Test parsing a single pattern (removes matches)."""
        result = parse_regex_rule_argument("^Página \\d+")
        assert len(result) == 1
        assert result[0].pattern == "^Página \\d+"
        assert result[0].replacement is None
    
    def test_single_pattern_with_replacement(self):
        """Test parsing pattern with replacement."""
        result = parse_regex_rule_argument("Página (\\d+)|P.\\1")
        assert len(result) == 1
        assert result[0].pattern == "Página (\\d+)"
        assert result[0].replacement == "P.\\1"
    
    def test_file_path(self, tmp_path):
        """Test reading from file."""
        exclude_file = tmp_path / "regex_rules.txt"
        exclude_file.write_text("^Página \\d+\nPágina (\\d+)|P.\\1\n^\\d+\\.\\s*\n")
        
        result = parse_regex_rule_argument(str(exclude_file))
        assert len(result) == 3
        assert result[0].pattern == "^Página \\d+"
        assert result[0].replacement is None
        assert result[1].pattern == "Página (\\d+)"
        assert result[1].replacement == "P.\\1"
        assert result[2].pattern == "^\\d+\\.\\s*"
        assert result[2].replacement is None
    
    def test_file_path_nonexistent(self):
        """Test that nonexistent file is treated as pattern."""
        result = parse_regex_rule_argument("nonexistent_file.txt")
        assert len(result) == 1
        assert result[0].pattern == "nonexistent_file.txt"
    
    def test_file_with_empty_lines(self, tmp_path):
        """Test that empty lines in file are skipped."""
        exclude_file = tmp_path / "regex_rules.txt"
        exclude_file.write_text("^Página \\d+\n\nPágina (\\d+)|P.\\1\n   \n^\\d+\\.\\s*\n")
        
        result = parse_regex_rule_argument(str(exclude_file))
        assert len(result) == 3
    
    def test_file_with_comments(self, tmp_path):
        """Test that lines starting with # are treated as comments."""
        exclude_file = tmp_path / "regex_rules.txt"
        exclude_file.write_text("# This is a comment\n^Página \\d+\n# Another comment\nPágina (\\d+)|P.\\1\n")
        
        result = parse_regex_rule_argument(str(exclude_file))
        assert len(result) == 2
    
    def test_invalid_regex_pattern(self):
        """Test that invalid regex pattern raises error."""
        import pytest
        from src.file_handlers import FileHandlerError
        with pytest.raises(FileHandlerError) as exc_info:
            parse_regex_rule_argument("[invalid regex")
        assert "Invalid regex" in str(exc_info.value)


class TestApplyRegexTransformations:
    """Tests for apply_regex_transformations function."""
    
    def test_no_rules(self):
        """Test that text is unchanged when no rules."""
        text = "hello world"
        result = apply_regex_transformations(text, [])
        assert result == text
    
    def test_single_rule_remove(self):
        """Test removing matches with single rule."""
        text = "Página 1\nTexto\nPágina 2"
        rules = [RegexRule(pattern="^Página \\d+", replacement=None)]
        result = apply_regex_transformations(text, rules, case_sensitive=False)
        # With MULTILINE flag, ^ matches at start of each line
        assert "Página 1" not in result
        assert "Página 2" not in result
        assert "Texto" in result
    
    def test_single_rule_replace(self):
        """Test replacing matches with single rule."""
        text = "Página 1\nTexto\nPágina 2"
        rules = [RegexRule(pattern="Página (\\d+)", replacement="P.\\1")]
        result = apply_regex_transformations(text, rules, case_sensitive=False)
        assert "P.1" in result
        assert "P.2" in result
        assert "Página" not in result
    
    def test_multiple_rules_ordered(self):
        """Test that rules are applied in order."""
        text = "Página 1\n1. Primera línea\nTexto\nPágina 2\n2. Segunda línea"
        rules = [
            RegexRule(pattern="^Página \\d+", replacement=None),
            RegexRule(pattern="^\\d+\\.\\s*", replacement=None)
        ]
        result = apply_regex_transformations(text, rules, case_sensitive=False)
        assert "Página" not in result
        assert "1. " not in result
        assert "2. " not in result
        assert "Primera línea" in result
        assert "Segunda línea" in result
    
    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        text = "PÁGINA 1\npágina 2\nPágina 3"
        rules = [RegexRule(pattern="página \\d+", replacement=None)]
        result = apply_regex_transformations(text, rules, case_sensitive=False)
        assert "PÁGINA 1" not in result
        assert "página 2" not in result
        assert "Página 3" not in result
    
    def test_case_sensitive(self):
        """Test case-sensitive matching."""
        text = "PÁGINA 1\npágina 2\nPágina 3"
        rules = [RegexRule(pattern="página \\d+", replacement=None)]
        result = apply_regex_transformations(text, rules, case_sensitive=True)
        assert "PÁGINA 1" in result
        assert "página 2" not in result
        assert "Página 3" in result
    
    def test_backreferences_in_replacement(self):
        """Test that backreferences work in replacements."""
        text = "Autor: Juan Pérez\nTítulo: Mi Libro"
        rules = [RegexRule(pattern="(\\w+): (.*)", replacement="\\1 -> \\2")]
        result = apply_regex_transformations(text, rules, case_sensitive=False)
        assert "Autor -> Juan Pérez" in result
        assert "Título -> Mi Libro" in result
    
    def test_multiple_replacements_with_backreferences(self):
        """Test multiple replacements using backreferences."""
        text = "Página 1, Sección 2, Capítulo 3"
        rules = [
            RegexRule(pattern="Página (\\d+)", replacement="P.\\1"),
            RegexRule(pattern="Sección (\\d+)", replacement="Sec.\\1"),
            RegexRule(pattern="Capítulo (\\d+)", replacement="Cap.\\1")
        ]
        result = apply_regex_transformations(text, rules, case_sensitive=False)
        assert "P.1" in result
        assert "Sec.2" in result
        assert "Cap.3" in result
    
    def test_invalid_regex_pattern_error(self):
        """Test that invalid regex pattern raises error."""
        import pytest
        with pytest.raises(ValueError) as exc_info:
            rules = [RegexRule(pattern="[invalid", replacement=None)]
            apply_regex_transformations("test", rules, case_sensitive=False)
        assert "Error applying regex" in str(exc_info.value)
    
    def test_invalid_backreference_error(self):
        """Test that invalid backreference raises error."""
        import pytest
        with pytest.raises(ValueError) as exc_info:
            rules = [RegexRule(pattern="(\\d+)", replacement="\\10")]  # Only 1 group, can't use \\10
            apply_regex_transformations("123", rules, case_sensitive=False)
        assert "Error applying regex" in str(exc_info.value) or "invalid group" in str(exc_info.value)
