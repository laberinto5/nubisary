"""Text preprocessing functions for Word Cloud Generator."""

from typing import Dict
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

