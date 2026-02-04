"""Configuration constants and dataclasses for Word Cloud Generator."""

from dataclasses import dataclass
from typing import Optional


# Fully supported languages (end-to-end)
# These languages are supported across tokenization, stopwords, lemmatization, and fonts.
LANGUAGES_FOR_NLTK = [
    'english',
    'spanish',
    'french',
    'german',
    'italian',
    'portuguese',
]

# Valid color names for wordcloud
WORDCLOUD_COLORS = [
    'white', 'blue', 'yellow', 'green', 'red', 'grey', 'black', 'orange'
]

# Punctuation characters to replace with spaces in text preprocessing
# All punctuation is replaced with spaces (not removed) to preserve word boundaries
PUNCTUATION = '''!()-[]{};:'",<>./?@#$%^&*_~'''

# Default canvas dimensions
DEFAULT_CANVAS_WIDTH = 800
DEFAULT_CANVAS_HEIGHT = 600

# Default max words
DEFAULT_MAX_WORDS = 200

# Default min word length
DEFAULT_MIN_WORD_LENGTH = 0


@dataclass
class WordCloudConfig:
    """Configuration for WordCloud generation."""
    
    # Canvas settings
    canvas_width: int = DEFAULT_CANVAS_WIDTH
    canvas_height: int = DEFAULT_CANVAS_HEIGHT
    
    # Word settings
    max_words: int = DEFAULT_MAX_WORDS
    min_word_length: int = DEFAULT_MIN_WORD_LENGTH
    lemmatize: bool = False
    include_numbers: bool = False
    
    # Color settings
    background_color: Optional[str] = None
    font_color: Optional[str] = None
    colormap: Optional[str] = None  # matplotlib colormap name (e.g., 'viridis', 'plasma')
    
    # Visual appearance settings
    relative_scaling: float = 0.5  # 0.0-1.0, controls size difference intensity
    prefer_horizontal: float = 0.9  # 0.0-1.0, orientation preference
    
    # Advanced settings
    mask: Optional[str] = None  # Path to mask image file
    contour_width: float = 0.0  # Outline width (only with mask)
    contour_color: Optional[str] = None  # Outline color (only with mask)
    font_path: Optional[str] = None  # Path to custom font file (TTF/OTF)
    
    # Text processing settings (only for text input, not JSON)
    language: Optional[str] = None
    include_stopwords: bool = False
    case_sensitive: bool = False
    ngram: str = "unigram"  # "unigram" or "bigram"


@dataclass
class AppConfig:
    """Application-level configuration."""
    
    input_file: str
    output_file: Optional[str] = None
    is_json: bool = False
    wordcloud_config: Optional[WordCloudConfig] = None
    
    def __post_init__(self):
        """Initialize wordcloud_config if not provided."""
        if self.wordcloud_config is None:
            self.wordcloud_config = WordCloudConfig()

