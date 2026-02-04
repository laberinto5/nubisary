#!/usr/bin/env python3
"""Gradio entrypoint for Nubisary (no Docker)."""

from __future__ import annotations

import os
import tempfile
from typing import Optional, Tuple, Union

import gradio as gr

from src.config import WordCloudConfig, LANGUAGES_FOR_NLTK
from src.file_handlers import is_json_file
from src.statistics_exporter import export_statistics
from src.report_generator import (
    build_report_data,
    render_report_txt,
    write_report_txt,
    write_report_pdf,
    ScenarioMetadata,
    CloudMetadata,
)
from src.themes import get_theme, get_theme_names
from src.resource_loader import list_mask_files, get_mask_path
from src.font_loader import list_font_files, get_font_path
from src.custom_colormaps import register_custom_colormap, CustomColormapError
from src.wordcloud_generator import (
    apply_wordcloud_filters,
    generate_word_cloud_from_frequencies,
)
from src.wordcloud_service import process_text_to_frequencies, WordCloudServiceError
from src.file_handlers import read_text_file
from src.validators import validate_language

COMPACT_CSS = """
.gradio-container {font-size: 14px;}
.gr-block {padding-top: 8px; padding-bottom: 8px;}
.gr-form {gap: 8px;}
.gr-accordion .label-wrap {padding: 4px 8px;}

/* Accent color */
.gradio-container {
    --primary-500: #3EAFC2;
    --primary-600: #3499AB;
    --primary-700: #2D8192;
    --color-accent: #3EAFC2;
    --slider-color: #3EAFC2;
    --range-color: #3EAFC2;
}
.gradio-container .gr-button-primary,
.gradio-container .primary,
.gradio-container button.primary {
    background: #3EAFC2 !important;
    border-color: #3EAFC2 !important;
}
.gradio-container .gr-button-primary:hover,
.gradio-container .primary:hover,
.gradio-container button.primary:hover {
    background: #3499AB !important;
    border-color: #3499AB !important;
}
.gradio-container input[type="range"],
.gradio-container .gr-slider input[type="range"] {
    accent-color: #3EAFC2 !important;
}
.gradio-container input[type="range"]::-webkit-slider-thumb,
.gradio-container .gr-slider input[type="range"]::-webkit-slider-thumb {
    background: #3EAFC2;
}
.gradio-container input[type="range"]::-moz-range-thumb,
.gradio-container .gr-slider input[type="range"]::-moz-range-thumb {
    background: #3EAFC2;
}
.gradio-container input[type="range"]::-webkit-slider-runnable-track,
.gradio-container .gr-slider input[type="range"]::-webkit-slider-runnable-track {
    background: rgba(62, 175, 194, 0.35) !important;
}
.gradio-container input[type="range"]::-moz-range-track,
.gradio-container .gr-slider input[type="range"]::-moz-range-track {
    background: rgba(62, 175, 194, 0.35) !important;
}
.gradio-container #reset-btn {
    align-self: center;
    max-width: 90px;
}
.gradio-container #reset-btn,
.gradio-container .reset-btn {
    align-self: center;
    width: 36px;
    max-width: 36px;
    --button-secondary-background-fill: #CC6449;
    --button-secondary-background-fill-hover: #B75740;
    --button-secondary-border-color: #CC6449;
    --button-secondary-text-color: #FFFFFF;
}
.gradio-container #reset-btn button,
.gradio-container .reset-btn button,
.gradio-container #reset-btn .gr-button,
.gradio-container .reset-btn .gr-button {
    font-size: 11px;
    padding: 0;
    min-height: 36px;
    height: 36px;
    width: 36px;
    line-height: 1.1;
    background-color: #CC6449 !important;
    border-color: #CC6449 !important;
    color: #FFFFFF !important;
}
.gradio-container #input-name .gr-input,
.gradio-container #status-text .gr-input {
    min-height: 36px;
    height: 36px;
}
.gradio-container #reset-btn button:hover,
.gradio-container .reset-btn button:hover,
.gradio-container #reset-btn .gr-button:hover,
.gradio-container .reset-btn .gr-button:hover {
    background-color: #B75740 !important;
    border-color: #B75740 !important;
}
"""


def _parse_top_n(value: str) -> Optional[int]:
    if not value:
        return None
    try:
        parsed = int(value)
        return parsed if parsed > 0 else None
    except (TypeError, ValueError):
        return None


def _file_name_from_path(path_value: Optional[Union[str, dict]]) -> str:
    if not path_value:
        return ""
    if isinstance(path_value, dict):
        name = path_value.get("orig_name") or path_value.get("name")
        return os.path.basename(name) if name else ""
    return os.path.basename(path_value)


def _handle_upload(path_value: Optional[Union[str, dict]]) -> Tuple[Optional[str], str]:
    if not path_value:
        return None, ""
    if isinstance(path_value, dict):
        file_path = path_value.get("name")
        return file_path, _file_name_from_path(path_value)
    return path_value, _file_name_from_path(path_value)


def _parse_color_list(colors_text: str) -> list:
    if not colors_text:
        return []
    return [item.strip() for item in colors_text.split(",") if item.strip()]


def _register_custom_theme_colormap(
    theme_name: str,
    colors: list,
) -> str:
    base_name = theme_name.strip().lower().replace(" ", "_") if theme_name else "custom_theme"
    colormap_name = f"{base_name}_colormap"
    try:
        register_custom_colormap(colormap_name, colors)
        return colormap_name
    except CustomColormapError:
        import time
        fallback = f"{colormap_name}_{int(time.time() * 1000)}"
        register_custom_colormap(fallback, colors)
        return fallback


def _toggle_export_outputs(enabled: bool):
    return gr.update(visible=enabled)


def _toggle_report_outputs(enabled: bool):
    return gr.update(visible=enabled)


def _reset_to_defaults(default_theme: str):
    return (
        None,  # input_file
        "",  # input_name
        "",  # status
        "spanish",  # language
        gr.update(value=default_theme),  # theme
        "unigram",  # ngram
        False,  # include_stopwords
        False,  # include_numbers
        False,  # case_sensitive
        False,  # lemmatize
        800,  # canvas_width
        600,  # canvas_height
        200,  # max_words
        0,  # min_word_length
        0.5,  # relative_scaling
        0.9,  # prefer_horizontal
        "None",  # mask_choice
        "Default",  # font_choice
        0.0,  # contour_width
        "",  # contour_color
        False,  # export_vocab
        "",  # vocab_top_n
        gr.update(visible=False),  # export_outputs
        None,  # vocab_json
        None,  # vocab_csv
        False,  # export_report
        gr.update(visible=False),  # report_outputs
        None,  # report_txt_en
        None,  # report_txt_es
        None,  # report_pdf_en
        None,  # report_pdf_es
        False,  # use_custom_theme
        "custom-theme",  # custom_theme_name
        "#FFFFFF",  # custom_background_color
        "#FF0000, #00FF00, #0000FF",  # custom_colormap_colors
        None,  # mask_file
        "",  # mask_name
        None,  # font_file
        "",  # font_name
        "",  # replace_search
        "",  # replace_with
        "single",  # replace_mode
        False,  # replace_case_sensitive
        "original",  # replace_stage
        None,  # output_image
    )


def _resolve_mask_path(mask_choice: str, uploaded_path: Optional[str]) -> Optional[str]:
    if uploaded_path:
        return uploaded_path
    if not mask_choice or mask_choice == "None":
        return None
    return get_mask_path(mask_choice)


def _resolve_font_path(font_choice: str, uploaded_path: Optional[str]) -> Optional[str]:
    if uploaded_path:
        return uploaded_path
    if not font_choice or font_choice == "Default":
        return None
    return get_font_path(font_choice)


def _build_config(
    theme_name: str,
    use_custom_theme: bool,
    custom_theme_name: str,
    custom_background_color: str,
    custom_colormap_colors: str,
    canvas_width: int,
    canvas_height: int,
    max_words: int,
    min_word_length: int,
    relative_scaling: float,
    prefer_horizontal: float,
    include_stopwords: bool,
    include_numbers: bool,
    case_sensitive: bool,
    lemmatize: bool,
    ngram: str,
    mask_path: Optional[str],
    contour_width: float,
    contour_color: Optional[str],
    font_path: Optional[str],
) -> WordCloudConfig:
    config = WordCloudConfig(
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        max_words=max_words,
        min_word_length=min_word_length,
        relative_scaling=relative_scaling,
        prefer_horizontal=prefer_horizontal,
        include_stopwords=include_stopwords,
        include_numbers=include_numbers,
        case_sensitive=case_sensitive,
        lemmatize=lemmatize,
        ngram=ngram,
        mask=mask_path or None,
        contour_width=contour_width,
        contour_color=contour_color or None,
        font_path=font_path or None,
    )

    if use_custom_theme:
        colors = _parse_color_list(custom_colormap_colors)
        if len(colors) < 2:
            raise gr.Error("Custom theme requires at least 2 colors.")
        colormap_name = _register_custom_theme_colormap(custom_theme_name, colors)
        config.background_color = custom_background_color or "#FFFFFF"
        config.colormap = colormap_name
        config.font_color = None
        return config

    theme = get_theme(theme_name)
    if theme is None:
        raise gr.Error(f"Theme not found: {theme_name}")

    return theme.apply_to_config(config)


def generate_wordcloud(
    input_file: Optional[str],
    language: str,
    theme_name: str,
    use_custom_theme: bool,
    custom_theme_name: str,
    custom_background_color: str,
    custom_colormap_colors: str,
    include_stopwords: bool,
    include_numbers: bool,
    case_sensitive: bool,
    lemmatize: bool,
    ngram: str,
    replace_search: str,
    replace_with: str,
    replace_mode: str,
    replace_case_sensitive: bool,
    replace_stage: str,
    canvas_width: int,
    canvas_height: int,
    max_words: int,
    min_word_length: int,
    relative_scaling: float,
    prefer_horizontal: float,
    mask_choice: str,
    mask_file: Optional[str],
    contour_width: float,
    contour_color: str,
    font_choice: str,
    font_file: Optional[str],
    # Note: No export flags needed - Gradio always generates all outputs
) -> Tuple[
    Optional[object],  # image
    Optional[str],  # vocab_json
    Optional[str],  # report_pdf_en
    Optional[str],  # report_pdf_es
    Optional[str],  # report_txt_en
    Optional[str],  # report_txt_es
    str,  # status
]:
    if not input_file:
        raise gr.Error("Please upload an input file.")

    if not os.path.exists(input_file):
        raise gr.Error("Uploaded file not found on disk.")

    language_value = language or "english"
    if is_json_file(input_file):
        language_value = "english"

    try:
        resolved_mask = _resolve_mask_path(mask_choice, mask_file)
        resolved_font = _resolve_font_path(font_choice, font_file)

        config = _build_config(
            theme_name=theme_name,
            use_custom_theme=use_custom_theme,
            custom_theme_name=custom_theme_name,
            custom_background_color=custom_background_color,
            custom_colormap_colors=custom_colormap_colors,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            max_words=max_words,
            min_word_length=min_word_length,
            relative_scaling=relative_scaling,
            prefer_horizontal=prefer_horizontal,
            include_stopwords=include_stopwords,
            include_numbers=include_numbers,
            case_sensitive=case_sensitive,
            lemmatize=lemmatize,
            ngram=ngram,
            mask_path=resolved_mask,
            contour_width=contour_width,
            contour_color=contour_color,
            font_path=resolved_font,
        )

        if not is_json_file(input_file):
            validate_language(language_value, include_stopwords=config.include_stopwords)

        frequencies = process_text_to_frequencies(
            input_file=input_file,
            language=language_value,
            config=config,
            clean_text=True,
            replace_search=replace_search or None,
            replace_with=replace_with,
            replace_mode=replace_mode,
            replace_case_sensitive=replace_case_sensitive,
            replace_stage=replace_stage,
        )

        filtered = apply_wordcloud_filters(frequencies, config)
        wordcloud = generate_word_cloud_from_frequencies(
            frequencies=filtered,
            config=config,
            output_file=None,
            show=False,
        )
        image = wordcloud.to_image()

        vocab_json = None
        report_txt_en = None
        report_txt_es = None
        report_pdf_en = None
        report_pdf_es = None

        # Always export vocabulary JSON
        temp_dir_vocab = tempfile.mkdtemp(prefix="nubisary_vocab_")
        base_output_vocab = os.path.join(temp_dir_vocab, "vocabulary")
        vocab_json, _ = export_statistics(
            frequencies=frequencies,
            base_output_file=base_output_vocab,
        )

        # Always generate reports
        temp_dir = tempfile.mkdtemp(prefix="nubisary_report_")
        report_base = os.path.join(temp_dir, "report")
        raw_text = None
        bigram_frequencies = None
        top_terms_override = None
        top_terms_note = None
        token_stats = None
        comparison_frequencies = None
        comparison_reason = None

        if not is_json_file(input_file):
            raw_text = read_text_file(input_file, auto_convert=True, clean_text=False)
            token_stats = []
            for lemma_value in (False, True):
                for stop_value in (True, False):
                    token_config = WordCloudConfig(
                        canvas_width=config.canvas_width,
                        canvas_height=config.canvas_height,
                        max_words=config.max_words,
                        min_word_length=config.min_word_length,
                        relative_scaling=config.relative_scaling,
                        prefer_horizontal=config.prefer_horizontal,
                        include_stopwords=stop_value,
                        include_numbers=config.include_numbers,
                        case_sensitive=config.case_sensitive,
                        lemmatize=lemma_value,
                        ngram="unigram",
                    )
                    token_freqs = process_text_to_frequencies(
                        input_file=input_file,
                        language=language_value,
                        config=token_config,
                        clean_text=True,
                        replace_search=replace_search or None,
                        replace_with=replace_with,
                        replace_mode=replace_mode,
                        replace_case_sensitive=replace_case_sensitive,
                        replace_stage=replace_stage,
                    )
                    token_stats.append({
                        "lemmatize": lemma_value,
                        "include_stopwords": stop_value,
                        "total_tokens": float(sum(token_freqs.values())),
                        "unique_tokens": len(token_freqs),
                    })

            if ngram == "unigram":
                if lemmatize:
                    no_lemma_config = WordCloudConfig(
                        canvas_width=config.canvas_width,
                        canvas_height=config.canvas_height,
                        max_words=config.max_words,
                        min_word_length=config.min_word_length,
                        relative_scaling=config.relative_scaling,
                        prefer_horizontal=config.prefer_horizontal,
                        include_stopwords=config.include_stopwords,
                        include_numbers=config.include_numbers,
                        case_sensitive=config.case_sensitive,
                        lemmatize=False,
                        ngram="unigram",
                    )
                    frequencies_no_lemma = process_text_to_frequencies(
                        input_file=input_file,
                        language=language_value,
                        config=no_lemma_config,
                        clean_text=True,
                        replace_search=replace_search or None,
                        replace_with=replace_with,
                        replace_mode=replace_mode,
                        replace_case_sensitive=replace_case_sensitive,
                        replace_stage=replace_stage,
                    )
                    top_terms_override = [
                        word for word, _ in sorted(
                            frequencies_no_lemma.items(),
                            key=lambda item: (-item[1], item[0])
                        )[:5]
                    ]
                    top_terms_note = "Top terms are taken from the non-lemmatized analysis to match the original text."
                    bigram_config = WordCloudConfig(
                        canvas_width=config.canvas_width,
                        canvas_height=config.canvas_height,
                        max_words=config.max_words,
                        min_word_length=config.min_word_length,
                        relative_scaling=config.relative_scaling,
                        prefer_horizontal=config.prefer_horizontal,
                        include_stopwords=config.include_stopwords,
                        include_numbers=config.include_numbers,
                        case_sensitive=config.case_sensitive,
                        lemmatize=False,
                        ngram="bigram",
                    )
                else:
                    bigram_config = WordCloudConfig(
                        canvas_width=config.canvas_width,
                        canvas_height=config.canvas_height,
                        max_words=config.max_words,
                        min_word_length=config.min_word_length,
                        relative_scaling=config.relative_scaling,
                        prefer_horizontal=config.prefer_horizontal,
                        include_stopwords=config.include_stopwords,
                        include_numbers=config.include_numbers,
                        case_sensitive=config.case_sensitive,
                        lemmatize=config.lemmatize,
                        ngram="bigram",
                    )

                bigram_frequencies = process_text_to_frequencies(
                    input_file=input_file,
                    language=language_value,
                    config=bigram_config,
                    clean_text=True,
                    replace_search=replace_search or None,
                    replace_with=replace_with,
                    replace_mode=replace_mode,
                    replace_case_sensitive=replace_case_sensitive,
                    replace_stage=replace_stage,
                )

        if is_json_file(input_file):
            comparison_reason = "Comparison not available for JSON inputs."
        else:
            comparison_config = WordCloudConfig(
                canvas_width=config.canvas_width,
                canvas_height=config.canvas_height,
                max_words=config.max_words,
                min_word_length=config.min_word_length,
                relative_scaling=config.relative_scaling,
                prefer_horizontal=config.prefer_horizontal,
                include_stopwords=config.include_stopwords,
                include_numbers=config.include_numbers,
                case_sensitive=config.case_sensitive,
                lemmatize=not config.lemmatize,
                ngram=config.ngram,
            )
            comparison_frequencies = process_text_to_frequencies(
                input_file=input_file,
                language=language_value,
                config=comparison_config,
                clean_text=True,
                replace_search=replace_search or None,
                replace_with=replace_with,
                replace_mode=replace_mode,
                replace_case_sensitive=replace_case_sensitive,
                replace_stage=replace_stage,
            )

            scenario = ScenarioMetadata(
            label="Current scenario",
            language=language_value,
            ngram=ngram,
            lemmatize=lemmatize,
            include_stopwords=include_stopwords,
            include_numbers=include_numbers,
            case_sensitive=case_sensitive,
            exclude_words=None,
            exclude_case_sensitive=False,
            regex_rule=None,
            regex_case_sensitive=False,
            replace_stage=replace_stage,
            )

            cloud_metadata = CloudMetadata(
            max_words=config.max_words,
            min_word_length=config.min_word_length,
            canvas_width=config.canvas_width,
            canvas_height=config.canvas_height,
            mask=config.mask,
            contour_width=config.contour_width,
            contour_color=config.contour_color,
            font_path=config.font_path,
            theme=theme_name,
            colormap=config.colormap,
            background=config.background_color,
            fontcolor=config.font_color,
            relative_scaling=config.relative_scaling,
            prefer_horizontal=config.prefer_horizontal,
            )

            report_data = build_report_data(
            frequencies=frequencies,
            scenario=scenario,
            comparison_frequencies=comparison_frequencies,
            comparison_unavailable_reason=comparison_reason,
            cloud_metadata=cloud_metadata,
            source_name=os.path.basename(input_file),
            raw_text=raw_text,
            bigram_frequencies=bigram_frequencies,
            top_terms_override=top_terms_override,
            top_terms_note=top_terms_note,
            token_stats=token_stats,
            )

            report_txt_en = f"{report_base}_report_en.txt"
            report_txt_es = f"{report_base}_report_es.txt"
            report_pdf_en = f"{report_base}_report_en.pdf"
            report_pdf_es = f"{report_base}_report_es.pdf"
        write_report_txt(render_report_txt(report_data, language="en"), report_txt_en)
        write_report_txt(render_report_txt(report_data, language="es"), report_txt_es)
        write_report_pdf(report_data, report_pdf_en, language="en")
        write_report_pdf(report_data, report_pdf_es, language="es")
        
        status = "Word cloud generated. Vocabulary and reports exported."
        return image, vocab_json, report_pdf_en, report_pdf_es, report_txt_en, report_txt_es, status
    except WordCloudServiceError as exc:
        raise gr.Error(str(exc)) from exc
    except Exception as exc:
        raise gr.Error(f"Unexpected error: {exc}") from exc


def build_app() -> gr.Blocks:
    theme_names = get_theme_names()
    default_theme = "spring" if "spring" in theme_names else theme_names[0]
    mask_names = ["None"] + list_mask_files(without_extension=True)
    font_names = ["Default"] + list_font_files(without_extension=True, with_display_names=True)

    with gr.Blocks(title="Nubisary") as demo:
        gr.Markdown("## Nubisary - Word Cloud Generator")

        gr.Markdown("### Input")
        with gr.Row():
            with gr.Column(scale=1, min_width=160):
                input_upload = gr.UploadButton(
                    "Upload input file",
                    file_types=[".txt", ".pdf", ".docx", ".json"],
                    file_count="single",
                )
                generate_btn = gr.Button("Generate", variant="primary")
            with gr.Column(scale=3):
                input_file = gr.File(type="filepath", visible=False)
                with gr.Row():
                    input_name = gr.Textbox(
                        label="Selected file",
                        value="",
                        interactive=False,
                        elem_id="input-name",
                    )
                    status = gr.Textbox(
                        label="Status",
                        value="",
                        interactive=False,
                        elem_id="status-text",
                    )
                    reset_btn = gr.Button(
                        "Reset",
                        variant="secondary",
                        elem_id="reset-btn",
                        elem_classes=["reset-btn"],
                    )
        with gr.Row():
            language = gr.Dropdown(
                choices=LANGUAGES_FOR_NLTK,
                value="spanish",
                label="Language (ignored for JSON)",
            )
            theme = gr.Dropdown(
                choices=theme_names,
                value=default_theme,
                label="Theme",
            )
            ngram = gr.Dropdown(
                choices=["unigram", "bigram"],
                value="unigram",
                label="N-gram",
            )
        with gr.Row():
            include_stopwords = gr.Checkbox(label="Include stopwords", value=False)
            include_numbers = gr.Checkbox(label="Include numbers", value=False)
            case_sensitive = gr.Checkbox(label="Case sensitive", value=False)
            lemmatize = gr.Checkbox(label="Lemmatize", value=False)

        gr.Markdown("### Preview")
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("#### Visual basics")
                with gr.Row():
                    canvas_width = gr.Number(label="Width", value=800, precision=0)
                    canvas_height = gr.Number(label="Height", value=600, precision=0)
                with gr.Row():
                    max_words = gr.Number(label="Max words", value=200, precision=0)
                    min_word_length = gr.Number(label="Min length", value=0, precision=0)
                relative_scaling = gr.Slider(
                    label="Relative scaling", minimum=0.0, maximum=1.0, value=0.5
                )
                prefer_horizontal = gr.Slider(
                    label="Prefer horizontal", minimum=0.0, maximum=1.0, value=0.9
                )
                with gr.Row():
                    mask_choice = gr.Dropdown(
                        choices=mask_names,
                        value="None",
                        label="Built-in mask",
                    )
                    font_choice = gr.Dropdown(
                        choices=font_names,
                        value="Default",
                        label="Built-in font",
                    )
                with gr.Row():
                    contour_width = gr.Number(label="Contour width", value=0.0)
                    contour_color = gr.Textbox(label="Contour color", value="")
            with gr.Column(scale=2):
                output_image = gr.Image(label="Word cloud preview", type="pil")

        gr.Markdown("### Options")
        with gr.Row(equal_height=True):
            with gr.Column(scale=1, min_width=320):
                with gr.Accordion("Export vocabulary", open=False):
                    export_vocab = gr.Checkbox(label="Export JSON/CSV", value=False)
                    vocab_top_n = gr.Textbox(label="Top N words", value="")
                    export_outputs = gr.Group(visible=False)
                    with export_outputs:
                        with gr.Row():
                            vocab_json = gr.File(label="Vocabulary JSON")
                            vocab_csv = gr.File(label="Vocabulary CSV")
                with gr.Accordion("Export report (TXT/PDF)", open=False):
                    export_report = gr.Checkbox(label="Export report", value=False)
                    report_outputs = gr.Group(visible=False)
                    with report_outputs:
                        with gr.Row():
                            report_txt_en = gr.File(label="Report TXT (EN)")
                            report_txt_es = gr.File(label="Report TXT (ES)")
                        with gr.Row():
                            report_pdf_en = gr.File(label="Report PDF (EN)")
                            report_pdf_es = gr.File(label="Report PDF (ES)")

                with gr.Accordion("Advanced options", open=False):
                    gr.Markdown("#### Custom theme")
                    use_custom_theme = gr.Checkbox(label="Use custom theme (override built-in)", value=False)
                    custom_theme_name = gr.Textbox(label="Custom theme name", value="custom-theme")
                    custom_background_color = gr.Textbox(label="Background color", value="#FFFFFF")
                    custom_colormap_colors = gr.Textbox(
                        label="Colormap colors (comma-separated)",
                        value="#FF0000, #00FF00, #0000FF",
                    )

                    gr.Markdown("#### Custom mask / font")
                    mask_upload = gr.UploadButton(
                        "Upload mask image",
                        file_types=[".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"],
                        file_count="single",
                    )
                    mask_file = gr.File(type="filepath", visible=False)
                    mask_name = gr.Textbox(label="Mask file", value="", interactive=False)
                    font_upload = gr.UploadButton(
                        "Upload font file",
                        file_types=[".ttf", ".otf"],
                        file_count="single",
                    )
                    font_file = gr.File(type="filepath", visible=False)
                    font_name = gr.Textbox(label="Font file", value="", interactive=False)

                    gr.Markdown("#### Text replacements")
                    replace_search = gr.Textbox(label="Search", value="")
                    replace_with = gr.Textbox(label="Replace", value="")
                    with gr.Row():
                        replace_mode = gr.Dropdown(
                            choices=["single", "list", "regex"],
                            value="single",
                            label="Mode",
                        )
                        replace_case_sensitive = gr.Checkbox(label="Case-sensitive", value=False)
                    replace_stage = gr.Dropdown(
                        choices=["original", "processed"],
                        value="original",
                        label="Apply on",
                    )

        input_upload.upload(_handle_upload, inputs=input_upload, outputs=[input_file, input_name])
        mask_upload.upload(_handle_upload, inputs=mask_upload, outputs=[mask_file, mask_name])
        font_upload.upload(_handle_upload, inputs=font_upload, outputs=[font_file, font_name])
        export_vocab.change(_toggle_export_outputs, inputs=export_vocab, outputs=export_outputs)
        export_report.change(_toggle_report_outputs, inputs=export_report, outputs=report_outputs)
        reset_btn.click(
            _reset_to_defaults,
            inputs=[gr.State(default_theme)],
            outputs=[
                input_file,
                input_name,
                status,
                language,
                theme,
                ngram,
                include_stopwords,
                include_numbers,
                case_sensitive,
                lemmatize,
                canvas_width,
                canvas_height,
                max_words,
                min_word_length,
                relative_scaling,
                prefer_horizontal,
                mask_choice,
                font_choice,
                contour_width,
                contour_color,
                export_vocab,
                vocab_top_n,
                export_outputs,
                vocab_json,
                vocab_csv,
                export_report,
                report_outputs,
                report_txt_en,
                report_txt_es,
                report_pdf_en,
                report_pdf_es,
                use_custom_theme,
                custom_theme_name,
                custom_background_color,
                custom_colormap_colors,
                mask_file,
                mask_name,
                font_file,
                font_name,
                replace_search,
                replace_with,
                replace_mode,
                replace_case_sensitive,
                replace_stage,
                output_image,
            ],
        )

        inputs = [
            input_file,
            language,
            theme,
            use_custom_theme,
            custom_theme_name,
            custom_background_color,
            custom_colormap_colors,
            include_stopwords,
            include_numbers,
            case_sensitive,
            lemmatize,
            ngram,
            replace_search,
            replace_with,
            replace_mode,
            replace_case_sensitive,
            replace_stage,
            canvas_width,
            canvas_height,
            max_words,
            min_word_length,
            relative_scaling,
            prefer_horizontal,
            mask_choice,
            mask_file,
            contour_width,
            contour_color,
            font_choice,
            font_file,
            export_vocab,
            vocab_top_n,
            export_report,
        ]
        outputs = [output_image, vocab_json, vocab_csv, report_txt_en, report_txt_es, report_pdf_en, report_pdf_es, status]
        generate_btn.click(generate_wordcloud, inputs=inputs, outputs=outputs)

    demo.css = COMPACT_CSS
    return demo


app = build_app()

if __name__ == "__main__":
    app.launch()

