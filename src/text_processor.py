"""Text preprocessing functions for Word Cloud Generator."""

import re
import os
from collections import Counter
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from nltk.corpus import stopwords

try:
    import simplemma
    SIMPLEMMA_AVAILABLE = True
except ImportError:
    SIMPLEMMA_AVAILABLE = False

from src.config import PUNCTUATION


def normalize_single_word(word: str, language: str) -> str:
    """
    Normalize a single word to its singular form using lemmatization.
    
    Args:
        word: Single word to normalize
        language: Language code (e.g., 'spanish', 'english')
        
    Returns:
        Normalized word (singular form)
    """
    if not SIMPLEMMA_AVAILABLE:
        return word
    
    # Map language codes to simplemma language codes
    lang_map = {
        'spanish': 'es',
        'english': 'en',
        'french': 'fr',
        'german': 'de',
        'italian': 'it',
        'portuguese': 'pt',
    }
    
    simplemma_lang = lang_map.get(language.lower())
    if simplemma_lang is None:
        return word
    
    # Skip if word is too short or is a number
    if len(word) < 2 or word.isdigit():
        return word
    
    try:
        # Use simplemma to get the lemma (singular form)
        lemma = simplemma.lemmatize(word, lang=simplemma_lang)
        
        # Only replace if lemma is different and makes sense
        if lemma and lemma.lower() != word.lower() and len(lemma) >= 2:
            # Preserve original case if the word was capitalized
            if word[0].isupper():
                return lemma.capitalize()
            return lemma
    except Exception:
        # If lemmatization fails, only use fallback for Spanish
        if simplemma_lang == 'es':
            word_lower = word.lower()
            
            # Handle common Spanish plural endings
            if word_lower.endswith('es') and len(word_lower) > 4:
                if word_lower.endswith('ces'):
                    # luces -> luz, voces -> voz
                    singular = word[:-3] + 'z'
                    if len(singular) >= 3:
                        return singular.capitalize() if word[0].isupper() else singular
                elif word_lower.endswith('ies'):
                    # países -> país, reyes -> rey
                    if word_lower == 'países':
                        return 'país' if word.islower() else 'País'
                    singular = word[:-3] + 'y'
                    if len(singular) >= 3:
                        return singular.capitalize() if word[0].isupper() else singular
                else:
                    # mujeres -> mujer, casas -> casa
                    singular = word[:-2]
                    if len(singular) >= 3:
                        return singular.capitalize() if word[0].isupper() else singular
            elif word_lower.endswith('s') and len(word_lower) > 3:
                # libros -> libro, casas -> casa
                singular = word[:-1]
                if len(singular) >= 3:
                    return singular.capitalize() if word[0].isupper() else singular
    
    return word


def normalize_plurals_with_lemmatization(text: str, language: str) -> str:
    """
    Lematize words to their base form using lemmatization.
    
    Uses simplemma for lemmatization when available.
    
    Args:
        text: Input text with potential plural forms
        language: Language code (e.g., 'spanish', 'english')
        
    Returns:
        Text with plurals converted to singular using lemmatization
    """
    import logging
    logger = logging.getLogger(__name__)

    if not SIMPLEMMA_AVAILABLE:
        # Fallback: return text unchanged if simplemma is not available
        logger.warning('Lemmatization skipped: simplemma is not available.')
        return text
    
    # Map language codes to simplemma language codes
    # simplemma supports: es, en, fr, de, it, pt
    lang_map = {
        'spanish': 'es',
        'english': 'en',
        'french': 'fr',
        'german': 'de',
        'italian': 'it',
        'portuguese': 'pt',
    }
    
    simplemma_lang = lang_map.get(language.lower())
    
    # If language is not supported by simplemma, return text unchanged
    if simplemma_lang is None:
        logger.warning(
            f'Language "{language}" is not supported for plural normalization by simplemma. '
            f'Supported languages: {", ".join(sorted(lang_map.keys()))}. '
            f'Plural normalization will be skipped for this language.'
        )
        return text

    logger.info(f'Using simplemma lemmatizer for language "{language}".')
    
    def lemmatize_word(match):
        word = match.group(0)
        original_word = word
        
        # Skip if word is too short or is a number
        if len(word) < 2 or word.isdigit():
            return original_word
        
        try:
            # Use simplemma to get the lemma (singular form)
            lemma = simplemma.lemmatize(word, lang=simplemma_lang)
            
            # Only replace if lemma is different and makes sense
            # (simplemma may return the same word if it's already singular or unknown)
            if lemma and lemma.lower() != word.lower() and len(lemma) >= 2:
                # Preserve original case if the word was capitalized
                if word[0].isupper():
                    return lemma.capitalize()
                return lemma
        except Exception:
            # If lemmatization fails, only use fallback for Spanish
            # For other languages, simplemma should handle it, so if it fails, skip normalization
            if simplemma_lang == 'es':
                # Fallback for Spanish: handle common Spanish plural patterns manually
                # This is only for words that simplemma might not recognize
                word_lower = word.lower()
                
                # Handle common Spanish plural endings
                if word_lower.endswith('es') and len(word_lower) > 4:
                    # Try removing 'es' for common patterns
                    if word_lower.endswith('ces'):
                        # luces -> luz, voces -> voz
                        singular = word[:-3] + 'z'
                        if len(singular) >= 3:
                            return singular.capitalize() if word[0].isupper() else singular
                    elif word_lower.endswith('ies'):
                        # países -> país, reyes -> rey
                        if word_lower == 'países':
                            return 'país' if word.islower() else 'País'
                        singular = word[:-3] + 'y'
                        if len(singular) >= 3:
                            return singular.capitalize() if word[0].isupper() else singular
                    else:
                        # mujeres -> mujer, casas -> casa
                        singular = word[:-2]
                        if len(singular) >= 3:
                            return singular.capitalize() if word[0].isupper() else singular
                elif word_lower.endswith('s') and len(word_lower) > 3:
                    # libros -> libro, casas -> casa
                    singular = word[:-1]
                    if len(singular) >= 3:
                        return singular.capitalize() if word[0].isupper() else singular
        
        return original_word
    
    # Use word boundaries to match complete words
    pattern = r'\b\w+\b'
    result = re.sub(pattern, lemmatize_word, text)
    
    return result




def preprocess_text(
    text: str,
    case_sensitive: bool = False,
    include_numbers: bool = False,
    preserve_sentence_boundaries: bool = False
) -> str:
    """
    Preprocess text by replacing punctuation with spaces and optionally lowercasing.
    
    All punctuation characters are replaced with spaces (not removed) to preserve
    word boundaries. Multiple spaces are then normalized to single spaces.
    
    Args:
        text: Raw text content
        case_sensitive: If False, convert text to lowercase
        include_numbers: Whether to keep numeric tokens (default: False)
        preserve_sentence_boundaries: If True, sentence delimiters (. ! ? ; and line breaks)
            are replaced with <SENT> markers instead of spaces. This is used for bigram
            processing to ensure word pairs are not formed across sentence boundaries.
        
    Returns:
        Preprocessed text with punctuation replaced by spaces (or <SENT> markers for
        sentence delimiters when preserve_sentence_boundaries=True)
    """
    # Optionally remove any sequence that contains digits before punctuation handling
    text_clean = text
    if not include_numbers:
        # Remove any non-space token that contains at least one digit
        # Examples: covid19, covid-19, A4, 12:30, -14, 1-2
        text_clean = re.sub(r'\S*\d\S*', ' ', text_clean)
    
    # For bigrams, preserve sentence boundaries with special markers
    if preserve_sentence_boundaries:
        # Replace sentence delimiters with a special marker
        text_clean = text_clean.replace('.', ' <SENT> ')
        text_clean = text_clean.replace('!', ' <SENT> ')
        text_clean = text_clean.replace('?', ' <SENT> ')
        text_clean = text_clean.replace(';', ' <SENT> ')
        text_clean = text_clean.replace('\n', ' <SENT> ')
        
        # Replace other punctuation with spaces
        other_punct = '''()-[]{};:'",<>./?@#$%^&*_~'''.replace('.', '').replace('!', '').replace('?', '').replace(';', '')
        for punct_char in other_punct:
            text_clean = text_clean.replace(punct_char, ' ')
    else:
        # Replace all punctuation characters with spaces
        # This is safer than removing them, as it preserves word boundaries
        for punct_char in PUNCTUATION:
            text_clean = text_clean.replace(punct_char, ' ')
    
    # Normalize multiple spaces to single space
    text_clean = re.sub(r'\s+', ' ', text_clean)
    
    # Strip leading/trailing spaces
    text_clean = text_clean.strip()
    
    # Lowercase if not case sensitive
    if not case_sensitive:
        text_clean = text_clean.lower()
    
    return text_clean


def generate_word_count_from_text(
    text: str,
    language: str,
    include_stopwords: bool = False,
    ngram: str = "unigram",
    include_numbers: bool = False
) -> Dict[str, float]:
    """
    Generate word frequency dictionary from transformed text.
    
    This function assumes the text has already been fully transformed
    (punctuation normalization, plural normalization, regex rules, etc.).
    It only tokenizes and counts, with optional stopword filtering and
    basic collocation handling.
    
    For bigram mode, if the text contains <SENT> markers (from preprocess_text
    with preserve_sentence_boundaries=True), the text is split by these markers
    and bigrams are generated only within each sentence fragment. This ensures
    that word pairs are not formed across sentence boundaries.
    
    Args:
        text: Transformed text content (may contain <SENT> markers for bigrams)
        language: Language code for stopwords
        include_stopwords: Whether to include stopwords
        ngram: "unigram" (single words) or "bigram" (consecutive word pairs)
        include_numbers: Whether to include numeric tokens in frequencies
        
    Returns:
        Dictionary mapping words (or word pairs for bigrams) to their frequencies
    """
    # Tokenize on word boundaries (unicode-aware)
    tokens = re.findall(r'\b\w+\b', text)
    
    # Filter stopwords if needed
    if not include_stopwords:
        stopword_set = set(stopwords.words(language))
        tokens = [token for token in tokens if token not in stopword_set]
    
    # Remove pure numeric tokens if numbers are not included
    if not include_numbers:
        tokens = [token for token in tokens if not token.isdigit()]
    
    # Build frequency dictionary based on n-gram mode
    ngram = ngram.lower().strip()
    if ngram not in {"unigram", "bigram"}:
        raise ValueError(f'Invalid ngram value: {ngram}. Expected "unigram" or "bigram".')
    
    if ngram == "unigram":
        counts = Counter(tokens)
        return dict(counts)
    
    # Bigram mode: count adjacent pairs only (no unigrams)
    # Respect sentence boundaries marked by <SENT> token
    if len(tokens) < 2:
        return {}
    
    bigrams = []
    for i in range(len(tokens) - 1):
        token_a = tokens[i]
        token_b = tokens[i + 1]
        
        # Skip if either token is a sentence boundary marker
        # Note: '<SENT>' becomes 'sent' after lowercase and punctuation removal
        if token_a == 'sent' or token_b == 'sent':
            continue
        
        # Skip bigrams that contain any digits in either token (if not include_numbers)
        if not include_numbers:
            if re.search(r'\d', token_a) or re.search(r'\d', token_b):
                continue
        
        bigrams.append(f"{token_a} {token_b}")
    
    counts = Counter(bigrams)
    return dict(counts)


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


def apply_literal_replacements(
    text: str,
    replacements: List[Tuple[str, str]],
    case_sensitive: bool = False
) -> str:
    """
    Apply literal (non-regex) replacements to text.
    
    Each replacement is matched as a whole word or an exact phrase.
    Matching is case-sensitive or case-insensitive based on the flag.
    
    Args:
        text: Input text
        replacements: List of (search, replace) tuples
        case_sensitive: If False, matching is case-insensitive (default: False)
        
    Returns:
        Text with replacements applied (spaces normalized where matches occurred)
    """
    if not replacements:
        return text
    
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        normalized_line = normalize_spaces(line)
        processed_line = normalized_line
        
        for search, replacement in replacements:
            if not search.strip():
                continue
            
            normalized_search = normalize_spaces(search.strip())
            
            if ' ' in normalized_search:
                escaped_search = re.escape(normalized_search)
                pattern = escaped_search
            else:
                escaped_search = re.escape(normalized_search)
                pattern = r'\b' + escaped_search + r'\b'
            
            flags = 0 if case_sensitive else re.IGNORECASE
            processed_line = re.sub(pattern, replacement, processed_line, flags=flags)
        
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

