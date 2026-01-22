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
   - Normalize spaces  
   - Lowercase (unless case-sensitive)  
   - Remove any token containing digits if `include_numbers` is false
5. **Lematize (optional)**  
   Reduce words to base form.
6. **Tokenization & Counting**  
   Create unigram or bigram tokens and count frequencies.

## Notes

- WordCloud itself only uses frequencies for rendering and visual filters.  
- The vocabulary export is the **post-processing** frequency dictionary.

