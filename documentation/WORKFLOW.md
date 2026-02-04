# Text Processing Workflow

This document describes the high-level flow from input text to final word cloud, plus a concise view of the text transformation steps.

## High-Level Diagram

```
┌──────────────────────────────────────────────┐
│ Input File: TXT / PDF / DOCX / JSON          │
└──────────────────────────────────────────────┘
                     │
                     ▼
               ┌─────────┐
               │ JSON ?  │
               └─────────┘
                │       │
          yes ┌─┘       └─┐ no
              ▼           ▼
┌──────────────────────┐   ┌────────────────────────┐
│ Load Frequencies     │   │ Read / Convert to Text │
│ from JSON            │   └────────────────────────┘
└──────────────────────┘              │
            │                         ▼
            │          ┌───────────────────────────────────────────┐
            │          │ Text Transformation Module                │
            │          │ - Remove excluded text (optional)         │
            │          │ - Apply replacements (optional)           │
            │          │ - Preprocess text                         │
            │          │ - Lematize (optional)                     │
            │          │ - Generate frequencies (unigram / bigram) │
            │          └───────────────────────────────────────────┘
            │                         │
            └───────────────┬─────────┘
                            ▼
               ┌──────────────────────────────────┐
               │ Apply WordCloud Filters          │
               └──────────────────────────────────┘
                         │             │
                         ▼             ▼
           ┌────────────────────────┐  ┌───────────────────────────┐
           │ Generate Word Cloud    │  │ Export Vocabulary JSON/CSV│
           │ Image                  │  │ (optional)                │
           └────────────────────────┘  └───────────────────────────┘
                       │                            │
                       ▼                            ▼
               ┌────────────────┐           ┌────────────────┐
               │    Save PNG    │           │ Save CSV/JSON  │
               └────────────────┘           └────────────────┘
```

## Text Transformation Steps (Concise)

When the input is text (not JSON), the transformation module follows this order:

1. **Read / Convert**  
   Convert PDF/DOCX to text if needed and apply cleaning for page numbers/chapter numbers.
2. **Exclude Words/Phrases (optional)**  
   Remove exact words or phrases provided by the user.
3. **Text Replacements (optional)**  
   Apply literal replacements (single word/phrase or list) or regex replacements.
4. **Preprocess Text**  
   - Normalize punctuation to spaces  
   - **Special handling for bigrams**: When processing bigrams, sentence delimiters (`.`, `!`, `?`, `;`, and line breaks) are replaced with a special marker instead of spaces to preserve sentence boundaries. This ensures bigrams are not formed across sentence boundaries.
   - Normalize spaces  
   - Lowercase (unless case-sensitive)  
   - Remove any token containing digits if `include_numbers` is false
5. **Lematize (optional)**  
   Reduce words to base form.
6. **Tokenization & Counting**  
   - **Unigrams**: Create single-word tokens and count frequencies.
   - **Bigrams**: Create two-word consecutive tokens. The special sentence boundary markers from step 4 ensure that bigrams are only formed within sentence boundaries, not across them.

## Bigram Processing Path

Bigrams require special treatment to maintain semantic accuracy:

- **During preprocessing** (`preprocess_text` with `preserve_sentence_boundaries=True`):
  - Sentence delimiters (`.`, `!`, `?`, `;`) and line breaks are replaced with `<SENT>` markers
  - Other punctuation is replaced with spaces as usual
  - This prevents words from different sentences from being incorrectly paired

- **During tokenization** (`generate_word_count_from_text` with `ngram="bigram"`):
  - Text is split by the `<SENT>` marker to process each sentence independently
  - Bigrams are formed only within each sentence fragment
  - The marker token itself is excluded from bigram formation

This bifurcated workflow ensures that bigrams like "love. Today" are not created, maintaining the semantic integrity of word pairs.

## Notes

- WordCloud itself only uses frequencies for rendering and visual filters.  
- The vocabulary export is the **post-processing** frequency dictionary.
- Unigram processing follows the standard path without sentence boundary preservation.

