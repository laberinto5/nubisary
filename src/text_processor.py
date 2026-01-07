"""Text preprocessing functions for Word Cloud Generator."""

import re
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from nltk.corpus import stopwords
from wordcloud import WordCloud

from src.config import PUNCTUATION


def preprocess_text(text: str, case_sensitive: bool = False) -> str:
    """
    Preprocess text by removing punctuation and optionally lowercasing.
    
    Args:
        text: Raw text content
        case_sensitive: If False, convert text to lowercase
        
    Returns:
        Preprocessed text
    """
    # Remove punctuation
    text_clean = "".join(char for char in text if char not in PUNCTUATION)
    
    # Lowercase if not case sensitive
    if not case_sensitive:
        text_clean = text_clean.lower()
    
    return text_clean


def generate_word_count_from_text(
    text: str,
    language: str,
    include_stopwords: bool = False,
    collocations: bool = False,
    max_words: int = 200,
    min_word_length: int = 0,
    normalize_plurals: bool = False,
    include_numbers: bool = False,
    canvas_width: int = 400,
    canvas_height: int = 200
) -> Dict[str, float]:
    """
    Generate word frequency dictionary from preprocessed text.
    
    Args:
        text: Preprocessed text content
        language: Language code for stopwords
        include_stopwords: Whether to include stopwords
        collocations: Whether to include collocations (bigrams)
        max_words: Maximum number of words to include
        min_word_length: Minimum word length
        normalize_plurals: Whether to normalize plurals
        include_numbers: Whether to include numbers
        canvas_width: Canvas width (for WordCloud initialization)
        canvas_height: Canvas height (for WordCloud initialization)
        
    Returns:
        Dictionary mapping words to their frequencies
    """
    # Create WordCloud instance for text processing
    wordcloud = WordCloud(
        width=canvas_width,
        height=canvas_height,
        collocations=collocations,
        max_words=max_words,
        min_word_length=min_word_length,
        normalize_plurals=normalize_plurals,
        include_numbers=include_numbers
    )
    
    # Set stopwords if needed
    if not include_stopwords:
        wordcloud.stopwords = set(stopwords.words(language))
    
    # Process text and generate word frequencies
    word_count = wordcloud.process_text(text)
    
    return word_count


def normalize_spaces(text: str) -> str:
    """
    Normalize multiple spaces to single space.
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized spaces
    """
    return re.sub(r'\s+', ' ', text)


def remove_excluded_text(
    text: str,
    excluded_items: List[str],
    case_sensitive: bool = False
) -> str:
    """
    Remove exact matches of words or phrases from text.
    
    Normalizes spaces before matching (multiple spaces become single space),
    but preserves punctuation. Matches are case-sensitive or case-insensitive
    based on the case_sensitive parameter.
    
    The function processes the text line by line to preserve line breaks,
    and normalizes spaces only for matching purposes.
    
    Args:
        text: Input text
        excluded_items: List of words or phrases to remove (exact matches only)
        case_sensitive: If False, matching is case-insensitive (default: False)
        
    Returns:
        Text with excluded items removed (spaces normalized where matches occurred)
    """
    if not excluded_items:
        return text
    
    # Process line by line to preserve line structure
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # Normalize spaces in the line for matching
        normalized_line = normalize_spaces(line)
        processed_line = normalized_line
        
        # Process each excluded item
        for item in excluded_items:
            if not item.strip():
                continue
            
            # Normalize spaces in the excluded item
            normalized_item = normalize_spaces(item.strip())
            
            # Build regex pattern
            # For single words, use word boundaries
            # For phrases, match exactly (spaces already normalized)
            if ' ' in normalized_item:
                # Multi-word phrase: match exactly
                # Escape special regex characters
                escaped_item = re.escape(normalized_item)
                pattern = escaped_item
            else:
                # Single word: match as whole word
                escaped_item = re.escape(normalized_item)
                pattern = r'\b' + escaped_item + r'\b'
            
            # Apply case sensitivity
            flags = 0 if case_sensitive else re.IGNORECASE
            
            # Remove all occurrences
            processed_line = re.sub(pattern, '', processed_line, flags=flags)
        
        # Clean up any double spaces that might result from removals
        processed_line = normalize_spaces(processed_line)
        
        result_lines.append(processed_line)
    
    return '\n'.join(result_lines)


def parse_exclude_words_argument(exclude_words_arg: Optional[str]) -> List[str]:
    """
    Parse the --exclude-words argument.
    
    If the argument is a file path that exists, reads lines from the file.
    Otherwise, treats it as a comma-separated list of words/phrases.
    
    Args:
        exclude_words_arg: The argument value (file path or comma-separated string)
        
    Returns:
        List of words/phrases to exclude (empty list if argument is None or empty)
        
    Raises:
        FileHandlerError: If file exists but cannot be read
    """
    if not exclude_words_arg or not exclude_words_arg.strip():
        return []
    
    exclude_words_arg = exclude_words_arg.strip()
    
    # Check if it's a file path that exists
    if os.path.isfile(exclude_words_arg):
        try:
            with open(exclude_words_arg, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # Remove empty lines and strip whitespace
            items = [line.strip() for line in lines if line.strip()]
            return items
        except Exception as e:
            from src.file_handlers import FileHandlerError
            raise FileHandlerError(f'Error reading exclude words file {exclude_words_arg}: {e}')
    
    # Not a file, treat as comma-separated list
    # Split by comma and strip whitespace
    items = [item.strip() for item in exclude_words_arg.split(',') if item.strip()]
    return items


@dataclass
class RegexRule:
    """Represents a regex transformation rule."""
    pattern: str
    replacement: Optional[str] = None  # None means remove (empty replacement)


def parse_regex_rule_argument(regex_rule_arg: Optional[str]) -> List[RegexRule]:
    """
    Parse the --regex-rule argument.
    
    If the argument is a file path that exists, reads lines from the file.
    Otherwise, treats it as a single regex rule.
    
    Format: "pattern" or "pattern|replacement"
    - If no pipe (|), treats as pattern only (removes matches)
    - If pipe present, treats as pattern|replacement (replaces matches)
    
    Multiple rules can be provided by using the argument multiple times
    or by reading from a file (one rule per line).
    
    Args:
        regex_rule_arg: The argument value (file path or regex rule string)
        
    Returns:
        List of RegexRule objects (empty list if argument is None or empty)
        
    Raises:
        FileHandlerError: If file exists but cannot be read
        ValueError: If regex pattern is invalid
    """
    if not regex_rule_arg or not regex_rule_arg.strip():
        return []
    
    regex_rule_arg = regex_rule_arg.strip()
    
    # Check if it's a file path that exists
    if os.path.isfile(regex_rule_arg):
        try:
            with open(regex_rule_arg, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            rules = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                
                try:
                    rule = _parse_single_regex_rule(line)
                    if rule:
                        rules.append(rule)
                except ValueError as e:
                    from src.file_handlers import FileHandlerError
                    raise FileHandlerError(
                        f'Invalid regex rule at line {line_num} in {regex_rule_arg}: {e}'
                    )
            
            return rules
        except Exception as e:
            from src.file_handlers import FileHandlerError
            if isinstance(e, FileHandlerError):
                raise
            raise FileHandlerError(f'Error reading regex rules file {regex_rule_arg}: {e}')
    
    # Not a file, treat as single regex rule
    try:
        rule = _parse_single_regex_rule(regex_rule_arg)
        return [rule] if rule else []
    except ValueError as e:
        from src.file_handlers import FileHandlerError
        raise FileHandlerError(f'Invalid regex rule: {e}')


def _parse_single_regex_rule(rule_string: str) -> Optional[RegexRule]:
    """
    Parse a single regex rule string.
    
    Format: "pattern" or "pattern|replacement"
    - If no pipe (|), treats as pattern only (removes matches)
    - If pipe present, splits on first pipe: pattern|replacement
    
    Backreferences in replacement: Use \\1, \\2, etc. in command line,
    or \1, \2, etc. in files. Python will handle the escaping automatically.
    
    Args:
        rule_string: The rule string to parse
        
    Returns:
        RegexRule object or None if rule_string is empty
        
    Raises:
        ValueError: If regex pattern is invalid
    """
    rule_string = rule_string.strip()
    if not rule_string:
        return None
    
    # Check if it contains a pipe (separator for pattern|replacement)
    if '|' in rule_string:
        # Split on first pipe only (replacement might contain pipes)
        parts = rule_string.split('|', 1)
        pattern = parts[0].strip()
        replacement = parts[1].strip() if len(parts) > 1 else ''
        
        # Empty replacement after pipe means remove (same as no pipe)
        if not replacement:
            replacement = None
        else:
            # Normalize backreferences: convert \x01, \x02, etc. to \1, \2, etc.
            # This handles cases where \1 was read as a byte from file/command line
            # We only do this for ASCII control characters that are valid backreferences (1-9)
            replacement = _normalize_backreferences(replacement)
    else:
        # No pipe, treat as pattern only (remove matches)
        pattern = rule_string
        replacement = None
    
    if not pattern:
        return None
    
    # Validate regex pattern by compiling it
    try:
        re.compile(pattern)
    except re.error as e:
        raise ValueError(f'Invalid regex pattern "{pattern}": {e}')
    
    return RegexRule(pattern=pattern, replacement=replacement)


def _normalize_backreferences(replacement: str) -> str:
    """
    Normalize backreferences in replacement string.
    
    Converts byte representations of backreferences (\\x01-\\x09) back to
    string representations (\\1-\\9) that re.sub can use.
    
    This handles cases where backreferences were read from files or
    command line arguments and got converted to control characters.
    
    Args:
        replacement: Replacement string that may contain byte-encoded backreferences
        
    Returns:
        Replacement string with normalized backreferences
    """
    result = []
    i = 0
    while i < len(replacement):
        char = replacement[i]
        # Check if this is a control character that could be a backreference
        # Backreferences are \1 through \9 (bytes 1-9)
        # Only treat as backreference if not preceded by backslash
        if ord(char) >= 1 and ord(char) <= 9 and (i == 0 or replacement[i-1] != '\\'):
            # This looks like a backreference byte, convert to string representation
            backref_num = ord(char)
            result.append(f'\\{backref_num}')
            i += 1
        else:
            result.append(char)
            i += 1
    
    return ''.join(result)


def apply_regex_transformations(
    text: str,
    rules: List[RegexRule],
    case_sensitive: bool = False
) -> str:
    """
    Apply regex transformation rules to text in order.
    
    Rules are applied sequentially, so earlier rules affect the result of later rules.
    Supports both removal (no replacement) and replacement (with capture groups).
    
    Args:
        text: Input text
        rules: List of RegexRule objects to apply (in order)
        case_sensitive: If False, matching is case-insensitive (default: False)
        
    Returns:
        Text with regex transformations applied
        
    Raises:
        ValueError: If a regex pattern is invalid or replacement has invalid backreferences
    """
    if not rules:
        return text
    
    result = text
    
    # Apply rules in order
    # Use MULTILINE flag so ^ and $ match at start/end of each line
    flags = re.MULTILINE
    if not case_sensitive:
        flags |= re.IGNORECASE
    
    for rule in rules:
        if not rule.pattern:
            continue
        
        try:
            if rule.replacement is None:
                # Remove matches (empty replacement)
                result = re.sub(rule.pattern, '', result, flags=flags)
            else:
                # Replace matches
                # Note: Python's re.sub uses backreferences like \1, \2, etc.
                result = re.sub(rule.pattern, rule.replacement, result, flags=flags)
        except re.error as e:
            raise ValueError(f'Error applying regex rule "{rule.pattern}": {e}')
        except Exception as e:
            # Handle backreference errors (e.g., \10 when only 1 group exists)
            raise ValueError(
                f'Error applying regex replacement "{rule.pattern}|{rule.replacement}": {e}'
            )
    
    return result

