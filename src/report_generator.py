"""Report generation module for vocabulary statistics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple
import hashlib
import random
import re
from io import BytesIO

from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image, KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


@dataclass(frozen=True)
class ScenarioMetadata:
    """Metadata describing a processing scenario."""
    label: str
    language: str
    ngram: str
    lemmatize: bool
    include_stopwords: bool
    include_numbers: bool
    case_sensitive: bool
    exclude_words: Optional[str] = None
    exclude_case_sensitive: bool = False
    regex_rule: Optional[str] = None
    regex_case_sensitive: bool = False
    replace_stage: str = "original"


@dataclass(frozen=True)
class CloudMetadata:
    """Metadata describing word cloud settings (informational only)."""
    max_words: int
    min_word_length: int
    canvas_width: int
    canvas_height: int
    mask: Optional[str]
    contour_width: Optional[float]
    contour_color: Optional[str]
    font_path: Optional[str]
    theme: Optional[str]
    colormap: Optional[str]
    background: Optional[str]
    fontcolor: Optional[str]
    relative_scaling: Optional[float]
    prefer_horizontal: Optional[float]


def build_report_data(
    frequencies: Dict[str, float],
    *,
    scenario: ScenarioMetadata,
    comparison_frequencies: Optional[Dict[str, float]] = None,
    comparison_label: str = "Comparison (lemmatize toggled)",
    comparison_unavailable_reason: Optional[str] = None,
    cloud_metadata: Optional[CloudMetadata] = None,
    top_n: int = 20,
    source_name: Optional[str] = None,
    raw_text: Optional[str] = None,
    bigram_frequencies: Optional[Dict[str, float]] = None,
    top_terms_override: Optional[List[str]] = None,
    top_terms_note: Optional[str] = None,
    token_stats: Optional[List[Dict[str, object]]] = None,
    generated_at: Optional[str] = None,
) -> Dict[str, object]:
    """
    Build a structured report dictionary with statistics and metadata.
    """
    generated_at_value = generated_at or _utc_timestamp()
    top_word_insights = _build_top_word_insights(
        frequencies=frequencies,
        raw_text=raw_text,
        bigram_frequencies=bigram_frequencies,
        case_sensitive=scenario.case_sensitive,
        language=scenario.language,
        top_word_count=5,
        examples_per_word=5,
        context_window=7,
        top_terms_override=top_terms_override,
        top_terms_note=top_terms_note,
    )

    data = {
        "generated_at": generated_at_value,
        "source_name": source_name,
        "scenario": scenario,
        "analysis": _compute_analysis(
            frequencies,
            top_n=top_n,
        ),
        "token_stats": token_stats,
        "top_word_insights": top_word_insights,
        "cloud_metadata": cloud_metadata,
        "comparison": {
            "label": comparison_label,
            "available": comparison_frequencies is not None,
            "reason": comparison_unavailable_reason,
            "analysis": _compute_analysis(
                comparison_frequencies,
                top_n=top_n,
            )
            if comparison_frequencies
            else None,
            "current": _compute_analysis(
                frequencies,
                top_n=top_n,
            ),
            "scenario": scenario,
        },
    }
    return data


def render_report_txt(report_data: Dict[str, object], language: str = "en") -> str:
    """Render report data as a human-readable text document."""
    scenario: ScenarioMetadata = report_data["scenario"]  # type: ignore[assignment]
    analysis = report_data["analysis"]
    comparison = report_data["comparison"]
    cloud_metadata: Optional[CloudMetadata] = report_data.get("cloud_metadata")  # type: ignore[assignment]

    labels = _get_report_labels(language)

    lines: List[str] = []
    lines.append(labels["title"])
    lines.append("=" * 72)
    lines.append("")

    lines.append(labels["summary_title"])
    lines.append("-" * 72)
    lines.extend(_render_summary(report_data, labels))
    lines.append("")

    lines.append(labels["scenario_title"])
    lines.append("-" * 72)
    lines.extend(
        _render_scenario_metadata(
            scenario,
            labels,
            source_name=report_data.get("source_name"),
            generated_at=report_data.get("generated_at"),
        )
    )
    lines.append("")

    lines.append(labels["core_stats_title"])
    lines.append("-" * 72)
    lines.extend(_render_core_stats(analysis, labels))
    lines.append("")

    lines.append(labels["top_words_title"])
    lines.append("-" * 72)
    lines.extend(_render_top_words(analysis, labels))
    lines.append("")

    lines.append(labels["top_words_bigrams_title"])
    lines.append("-" * 72)
    lines.extend(_render_top_word_bigrams(report_data, labels))
    lines.append("")

    lines.append(labels["top_words_examples_title"])
    lines.append("-" * 72)
    lines.extend(_render_top_word_examples(report_data, labels))
    lines.append("")

    lines.append(labels["concentration_title"])
    lines.append("-" * 72)
    lines.extend(_render_concentration_summary(analysis, labels))
    lines.append("")

    lines.append(labels["hapax_title"])
    lines.append("-" * 72)
    lines.extend(_render_hapax(analysis, labels))
    lines.append("")

    lines.append(labels["comparison_title"])
    lines.append("-" * 72)
    lines.extend(_render_comparison_section(comparison, labels))
    lines.append("")

    lines.append(labels["cloud_meta_title"])
    lines.append("-" * 72)
    lines.extend(_render_cloud_metadata(cloud_metadata, labels))

    return "\n".join(lines).strip() + "\n"


def write_report_txt(report_text: str, output_path: str) -> str:
    """Write report text to a file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    return output_path


def write_report_pdf(report_data: Dict[str, object], output_path: str, language: str = "en") -> str:
    """Write report data to a styled PDF."""
    labels = _get_report_labels(language)
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    section_style = styles["Heading2"]
    body_style = ParagraphStyle("BodyJustified", parent=styles["BodyText"], alignment=TA_JUSTIFY)
    small_style = ParagraphStyle("Small", parent=body_style, fontSize=8, leading=10)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
        title=labels["title"],
    )

    elements: List[object] = []
    elements.append(Paragraph(labels["title"], title_style))
    elements.append(Paragraph(_render_intro(report_data, labels), body_style))
    elements.append(Spacer(1, 12))

    elements.append(KeepTogether([
        Paragraph(labels["summary_title"], section_style),
        Paragraph(
            labels["summary_intro"].format(
                stopwords=_render_stopwords_setting(report_data["scenario"], labels)
            ),
            body_style,
        ),
        Spacer(1, 6),
        _pdf_summary_table(report_data, labels),
    ]))
    elements.append(Spacer(1, 10))

    elements.append(KeepTogether([
        Paragraph(labels["token_extremes_title"], section_style),
        Paragraph(labels["token_extremes_intro"], body_style),
        Spacer(1, 6),
        _pdf_token_extremes_table(report_data["analysis"], labels),
    ]))
    elements.append(Spacer(1, 10))

    top_words_section = [
        Paragraph(labels["top_words_title"], section_style),
        Paragraph(labels["top_words_intro"], body_style),
        Spacer(1, 6),
        _pdf_top_words_with_concentration_table(report_data["analysis"], labels),
        Spacer(1, 6),
    ]
    top_words_section.extend(_render_concentration_summary_pdf(report_data["analysis"], labels, body_style))
    elements.append(KeepTogether(top_words_section))
    elements.append(Spacer(1, 10))

    # Page break before bigrams section
    elements.append(PageBreak())
    elements.append(KeepTogether([
        Paragraph(labels["top_words_insights_title"], section_style),
        Paragraph(labels["top_words_insights_intro"], body_style),
        Spacer(1, 6),
        _pdf_top_word_insights_table(report_data, labels),
    ]))
    elements.append(Spacer(1, 10))

    hapax_section = [
        Paragraph(labels["hapax_title"], section_style),
        Paragraph(labels["hapax_intro"], body_style),
        Spacer(1, 6),
    ]
    hapax_section.extend(_render_hapax_summary_pdf(report_data["analysis"], labels, body_style))
    hapax_section.append(Spacer(1, 6))
    hapax_section.append(_pdf_hapax_examples_table(report_data["analysis"], labels))
    elements.append(KeepTogether(hapax_section))
    elements.append(Spacer(1, 10))

    # Page break before technical metadata section
    elements.append(PageBreak())
    elements.append(KeepTogether([
        Paragraph(labels["metadata_title"], section_style),
        Paragraph(labels["metadata_intro"], body_style),
        Spacer(1, 6),
        _pdf_metadata_table(report_data, labels, small_style),
    ]))

    # Glossary section
    elements.append(PageBreak())
    elements.append(Paragraph(labels["glossary_title"], section_style))
    elements.append(Spacer(1, 6))
    glossary_items = [
        (labels["glossary_token_term"], labels["glossary_token_def"]),
        (labels["glossary_lemmatization_term"], labels["glossary_lemmatization_def"]),
        (labels["glossary_stopwords_term"], labels["glossary_stopwords_def"]),
        (labels["glossary_hapax_term"], labels["glossary_hapax_def"]),
        (labels["glossary_bigram_term"], labels["glossary_bigram_def"]),
        (labels["glossary_variability_term"], labels["glossary_variability_def"]),
    ]
    for term, definition in glossary_items:
        elements.append(Paragraph(f"<b>{term}</b>: {definition}", body_style))
        elements.append(Spacer(1, 4))

    doc.build(elements)
    return output_path


def _compute_analysis(
    frequencies: Optional[Dict[str, float]],
    *,
    top_n: int,
) -> Optional[Dict[str, object]]:
    if frequencies is None:
        return None

    total_tokens = float(sum(frequencies.values()))
    unique_tokens = len(frequencies)
    token_ratio = total_tokens and (unique_tokens / total_tokens) or 0.0

    length_stats = _compute_length_stats(frequencies)
    length_stats_non_hapax = _compute_length_stats(
        {word: freq for word, freq in frequencies.items() if float(freq) != 1.0}
    )
    length_stats_hapax = _compute_length_stats(
        {word: freq for word, freq in frequencies.items() if abs(float(freq) - 1.0) < 1e-9}
    )
    top_words = _top_words(frequencies, total_tokens, top_n)
    hapax = _hapax_legomena(frequencies, sample_size=20)
    hapax_stats = _compute_hapax_stats(frequencies)
    concentration = _vocabulary_concentration(frequencies, total_tokens, (5, 10, 20))

    return {
        "total_tokens": total_tokens,
        "unique_tokens": unique_tokens,
        "token_ratio": token_ratio,
        "length_stats": length_stats,
        "length_stats_non_hapax": length_stats_non_hapax,
        "length_stats_hapax": length_stats_hapax,
        "top_words": top_words,
        "hapax": hapax,
        "hapax_stats": hapax_stats,
        "concentration": concentration,
    }


def _compute_length_stats(frequencies: Dict[str, float]) -> Dict[str, object]:
    if not frequencies:
        return {
            "avg_length": None,
            "median_length": None,
            "shortest_token": None,
            "longest_token": None,
        }

    total_weight = float(sum(frequencies.values()))
    length_weights: Dict[int, float] = {}
    for token, freq in frequencies.items():
        length_weights[len(token)] = length_weights.get(len(token), 0.0) + float(freq)

    avg_length = None
    if total_weight > 0:
        avg_length = sum(length * weight for length, weight in length_weights.items()) / total_weight

    median_length = _weighted_median(length_weights.items(), total_weight)
    shortest_token = min(frequencies.keys(), key=lambda token: (len(token), token))
    longest_token = max(frequencies.keys(), key=lambda token: (len(token), token))

    return {
        "avg_length": avg_length,
        "median_length": median_length,
        "shortest_token": shortest_token,
        "longest_token": longest_token,
    }


def _compute_hapax_stats(frequencies: Dict[str, float]) -> Dict[str, object]:
    hapax_tokens = [word for word, freq in frequencies.items() if abs(float(freq) - 1.0) < 1e-9]
    non_hapax_tokens = [word for word, freq in frequencies.items() if float(freq) != 1.0]

    hapax_longest = _tokens_by_length(hapax_tokens, find_max=True)
    hapax_shortest = _tokens_by_length(hapax_tokens, find_max=False)
    non_hapax_longest = _tokens_by_length(non_hapax_tokens, find_max=True)
    non_hapax_shortest = _tokens_by_length(non_hapax_tokens, find_max=False)

    return {
        "hapax_longest": hapax_longest,
        "hapax_shortest": hapax_shortest,
        "non_hapax_longest": non_hapax_longest,
        "non_hapax_shortest": non_hapax_shortest,
    }


def _weighted_median(length_weights: Iterable[Tuple[int, float]], total_weight: float) -> Optional[float]:
    if total_weight <= 0:
        return None

    sorted_items = sorted(length_weights, key=lambda item: item[0])
    cumulative = 0.0
    midpoint = total_weight / 2.0
    for length, weight in sorted_items:
        cumulative += weight
        if cumulative >= midpoint:
            return float(length)
    return float(sorted_items[-1][0])


def _top_words(
    frequencies: Dict[str, float],
    total_tokens: float,
    top_n: int,
) -> List[Dict[str, object]]:
    if not frequencies or top_n <= 0:
        return []

    sorted_items = sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))
    top_items = sorted_items[:top_n]
    return [
        {
            "word": word,
            "frequency": freq,
            "percent": _safe_percent(freq, total_tokens),
        }
        for word, freq in top_items
    ]


def _hapax_legomena(
    frequencies: Dict[str, float],
    sample_size: int,
) -> Dict[str, object]:
    tokens = [word for word, freq in frequencies.items() if abs(float(freq) - 1.0) < 1e-9]
    tokens.sort()
    seed_source = "|".join(tokens).encode("utf-8")
    seed_value = int(hashlib.sha256(seed_source).hexdigest(), 16) % (2**32)
    rng = random.Random(seed_value)
    sample = tokens[:]
    rng.shuffle(sample)
    return {
        "count": len(tokens),
        "sample": sample[:sample_size],
    }


def _vocabulary_concentration(
    frequencies: Dict[str, float],
    total_tokens: float,
    buckets: Tuple[int, ...],
) -> Dict[int, Dict[str, float]]:
    if not frequencies or total_tokens <= 0:
        return {bucket: {"percent_of_total": 0.0, "percent_of_unique": 0.0} for bucket in buckets}

    unique_tokens = len(frequencies)
    sorted_items = sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))
    cumulative = 0.0
    results: Dict[int, Dict[str, float]] = {}
    current_index = 0
    targets = sorted(buckets)
    for _, freq in sorted_items:
        cumulative += float(freq)
        current_index += 1
        while targets and current_index >= targets[0]:
            bucket = targets.pop(0)
            results[bucket] = {
                "percent_of_total": _safe_percent(cumulative, total_tokens),
                "percent_of_unique": _safe_percent(bucket, unique_tokens),
            }
        if not targets:
            break

    for bucket in buckets:
        results.setdefault(bucket, {
            "percent_of_total": _safe_percent(cumulative, total_tokens),
            "percent_of_unique": _safe_percent(bucket, unique_tokens),
        })

    return results


def _render_scenario_metadata(
    metadata: ScenarioMetadata,
    labels: Dict[str, str],
    source_name: Optional[str] = None,
    generated_at: Optional[str] = None,
) -> List[str]:
    return [
        f"{labels['label']}: {metadata.label}",
        f"{labels['source_name']}: {source_name or labels['na']}",
        f"{labels['generated_at']}: {generated_at or labels['na']}",
        f"{labels['language']}: {metadata.language}",
        f"{labels['ngram']}: {metadata.ngram}",
        f"{labels['lemmatize']}: {metadata.lemmatize}",
        f"{labels['include_stopwords']}: {metadata.include_stopwords}",
        f"{labels['include_numbers']}: {metadata.include_numbers}",
        f"{labels['case_sensitive']}: {metadata.case_sensitive}",
        f"{labels['exclude_words']}: {metadata.exclude_words or labels['none']}",
        f"{labels['exclude_case_sensitive']}: {metadata.exclude_case_sensitive}",
        f"{labels['regex_rule']}: {metadata.regex_rule or labels['none']}",
        f"{labels['regex_case_sensitive']}: {metadata.regex_case_sensitive}",
        f"{labels['replace_stage']}: {metadata.replace_stage}",
    ]


def _render_core_stats(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> List[str]:
    if not analysis:
        return [labels["no_data"]]

    length_stats = analysis["length_stats"]
    length_stats_non_hapax = analysis["length_stats_non_hapax"]
    length_stats_hapax = analysis["length_stats_hapax"]
    hapax_percentage = _safe_percent(analysis["hapax"]["count"], analysis["unique_tokens"])
    hapax_token_share = _safe_percent(analysis["hapax"]["count"], analysis["total_tokens"])
    hapax_stats = analysis["hapax_stats"]
    lines = [
        labels["core_including_hapax"],
        f"- {labels['total_tokens']}: {_format_number(analysis['total_tokens'])}",
        f"- {labels['unique_tokens']}: {_format_number(analysis['unique_tokens'])}",
        f"- {labels['variability_ratio']}: {_format_ratio(analysis['token_ratio'])}",
        f"- {labels['hapax_legomena']}: {_format_number(analysis['hapax']['count'])} "
        f"({_format_percent(hapax_percentage)} {labels['of_unique']}, "
        f"{_format_percent(hapax_token_share)} {labels['of_total']})",
        f"- {labels['avg_token_length']}: {_format_number(length_stats['avg_length'])}",
        f"- {labels['median_token_length']}: {_format_number(length_stats['median_length'])}",
        f"- {labels['shortest_token']}: {length_stats['shortest_token'] or labels['na']}",
        f"- {labels['longest_token']}: {length_stats['longest_token'] or labels['na']}",
        "",
        labels["core_excluding_hapax"],
        f"- {labels['avg_token_length_non_hapax']}: {_format_number(length_stats_non_hapax['avg_length'])}",
        f"- {labels['median_token_length_non_hapax']}: {_format_number(length_stats_non_hapax['median_length'])}",
        f"- {labels['shortest_non_hapax']}: {_format_tokens_with_length(hapax_stats['non_hapax_shortest'], labels)}",
        f"- {labels['longest_non_hapax']}: {_format_tokens_with_length(hapax_stats['non_hapax_longest'], labels)}",
        "",
        labels["core_hapax_only"],
        f"- {labels['avg_token_length_hapax']}: {_format_number(length_stats_hapax['avg_length'])}",
        f"- {labels['median_token_length_hapax']}: {_format_number(length_stats_hapax['median_length'])}",
        f"- {labels['shortest_hapax']}: {_format_tokens_with_length(hapax_stats['hapax_shortest'], labels)}",
        f"- {labels['longest_hapax']}: {_format_tokens_with_length(hapax_stats['hapax_longest'], labels)}",
    ]
    return lines


def _render_top_words(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> List[str]:
    if not analysis or not analysis["top_words"]:
        return [labels["no_data"]]
    return [
        f"{index + 1:>2}. {item['word']} - { _format_number(item['frequency']) } "
        f"({ _format_percent(item['percent']) })"
        for index, item in enumerate(analysis["top_words"])
    ]


def _render_concentration_summary(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> List[str]:
    if not analysis or not analysis["concentration"]:
        return [labels["no_data"]]
    concentration = analysis["concentration"]
    top5_data = concentration.get(5, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    top10_data = concentration.get(10, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    top20_data = concentration.get(20, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    return [
        f"{labels['top_5_concentration']} { _format_percent(top5_data['percent_of_total']) } {labels['of_total']}, "
        f"{ _format_percent(top5_data['percent_of_unique']) } {labels['of_unique']}",
        f"{labels['top_10_concentration']} { _format_percent(top10_data['percent_of_total']) } {labels['of_total']}, "
        f"{ _format_percent(top10_data['percent_of_unique']) } {labels['of_unique']}",
        f"{labels['top_20_concentration']} { _format_percent(top20_data['percent_of_total']) } {labels['of_total']}, "
        f"{ _format_percent(top20_data['percent_of_unique']) } {labels['of_unique']}",
    ]


def _render_hapax(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> List[str]:
    if not analysis or not analysis["hapax"]:
        return [labels["no_data"]]
    hapax = analysis["hapax"]
    count = hapax["count"]
    sample = hapax["sample"]
    hapax_stats = analysis["hapax_stats"]
    hapax_percentage = _safe_percent(count, analysis["unique_tokens"])
    hapax_token_share = _safe_percent(count, analysis["total_tokens"])
    lines = [
        f"{labels['count']}: {count} ({_format_percent(hapax_percentage)} {labels['of_unique']}, "
        f"{_format_percent(hapax_token_share)} {labels['of_total']})",
    ]
    lines.append(f"{labels['longest_hapax_tokens']}: {_format_tokens_with_length(hapax_stats['hapax_longest'], labels)}")
    if not sample:
        lines.append(f"{labels['sample_up_to_20']}: {labels['none']}")
        return lines

    lines.append(f"{labels['sample_up_to_20']}:")
    for row in _chunk_list(sample, 5):
        lines.append("  " + ", ".join(row))
    return lines


def _render_summary(report_data: Dict[str, object], labels: Dict[str, str]) -> List[str]:
    analysis = report_data.get("analysis")
    if not analysis:
        return [labels["no_data"]]
    top_words = analysis.get("top_words") or []
    top_terms = ", ".join([item["word"] for item in top_words[:5]]) if top_words else labels["na"]
    hapax_percentage = _safe_percent(analysis["hapax"]["count"], analysis["unique_tokens"])

    top5_concentration = analysis['concentration'].get(5, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    lines = [
        f"{labels['summary_tokens']}: {_format_number(analysis['total_tokens'])}",
        f"{labels['summary_unique']}: {_format_number(analysis['unique_tokens'])}",
        f"{labels['summary_hapax']}: {_format_number(analysis['hapax']['count'])} ({_format_percent(hapax_percentage)} {labels['of_unique']})",
        f"{labels['summary_top5']}: {top_terms}",
        f"{labels['summary_concentration']}: "
        f"{_format_percent(top5_concentration['percent_of_total'])} {labels['of_all_tokens']}",
    ]

    comparison = report_data.get("comparison")
    if comparison and comparison.get("available") and comparison.get("analysis"):
        current_unique = analysis["unique_tokens"]
        comparison_unique = comparison["analysis"]["unique_tokens"]
        if current_unique:
            delta = ((comparison_unique - current_unique) / current_unique) * 100.0
            lines.append(
                f"{labels['summary_comparison']}: {labels['lemmatized_unique_change']} {delta:+.1f}%"
            )
    token_stats_lines = _render_token_stats(report_data, labels)
    if token_stats_lines:
        lines.append("")
        lines.extend(token_stats_lines)
    return lines


def _render_intro(report_data: Dict[str, object], labels: Dict[str, str]) -> str:
    source_name = report_data.get("source_name") or labels["na"]
    return labels["intro_text"].format(source_name=source_name)


def _render_stopwords_setting(scenario: ScenarioMetadata, labels: Dict[str, str]) -> str:
    return labels["stopwords_included"] if scenario.include_stopwords else labels["stopwords_excluded"]


def _render_hapax_summary(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> str:
    if not analysis:
        return labels["no_data"]
    hapax = analysis["hapax"]
    hapax_pct_unique = _safe_percent(hapax["count"], analysis["unique_tokens"])
    hapax_pct_total = _safe_percent(hapax["count"], analysis["total_tokens"])
    return labels["hapax_summary_text"].format(
        count=_format_number(hapax["count"]),
        pct_unique=_format_percent(hapax_pct_unique),
        pct_total=_format_percent(hapax_pct_total),
        of_unique=labels["of_unique"],
        of_total=labels["of_total"],
    )


def _render_hapax_summary_pdf(analysis: Optional[Dict[str, object]], labels: Dict[str, str], body_style) -> List:
    """Render hapax summary as bullet points for PDF."""
    if not analysis:
        return [Paragraph(labels["no_data"], body_style)]
    
    hapax = analysis["hapax"]
    hapax_pct_unique = _safe_percent(hapax["count"], analysis["unique_tokens"])
    hapax_pct_total = _safe_percent(hapax["count"], analysis["total_tokens"])
    
    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=body_style,
        leftIndent=20,
        bulletIndent=10,
        spaceBefore=3,
        spaceAfter=3,
    )
    
    items = [
        Paragraph(labels["hapax_data_intro"], body_style),
        Paragraph(
            f"• {labels['hapax_count_label']}: <b>{_format_number(hapax['count'])}</b>",
            bullet_style
        ),
        Paragraph(
            f"• {labels['hapax_pct_unique_label']}: <b>{_format_percent(hapax_pct_unique)}</b>",
            bullet_style
        ),
        Paragraph(
            f"• {labels['hapax_pct_total_label']}: <b>{_format_percent(hapax_pct_total)}</b>",
            bullet_style
        ),
        Paragraph(labels["hapax_examples_note"], body_style),
    ]
    
    return items


def _render_top_word_bigrams(report_data: Dict[str, object], labels: Dict[str, str]) -> List[str]:
    insights = report_data.get("top_word_insights", {})
    bigrams_info = insights.get("bigrams", {})
    if not bigrams_info or not bigrams_info.get("available"):
        reason = bigrams_info.get("reason") if bigrams_info else labels["not_available"]
        return [f"{labels['not_available']}: {reason}"]

    items = bigrams_info.get("items", {})
    if not items:
        return [labels["no_data"]]

    lines: List[str] = []
    note = bigrams_info.get("note")
    if note:
        lines.append(f"{labels['note']}: {note}")
    for word, bigrams in items.items():
        lines.append(f"{word}:")
        if not bigrams:
            lines.append(f"  {labels['no_examples_found']}")
            continue
        for entry in bigrams:
            lines.append(f"  - {entry['bigram']} ({_format_number(entry['count'])})")
    return lines


def _render_top_word_examples(report_data: Dict[str, object], labels: Dict[str, str]) -> List[str]:
    insights = report_data.get("top_word_insights", {})
    examples_info = insights.get("examples", {})
    if not examples_info or not examples_info.get("available"):
        reason = examples_info.get("reason") if examples_info else labels["not_available"]
        return [f"{labels['not_available']}: {reason}"]

    items = examples_info.get("items", {})
    if not items:
        return [labels["no_data"]]

    lines: List[str] = []
    note = examples_info.get("note")
    if note:
        lines.append(f"{labels['note']}: {note}")
    for word, examples in items.items():
        lines.append(f"{word}:")
        if not examples:
            lines.append(f"  {labels['no_examples_found']}")
            continue
        for example in examples:
            lines.append(f"  - {example}")
    return lines


def _render_comparison_summary(comparison: Dict[str, object], labels: Dict[str, str]) -> List[str]:
    analysis = comparison.get("analysis")
    if not analysis:
        return []
    length_stats = analysis["length_stats"]
    hapax_stats = analysis["hapax_stats"]
    return [
        labels["comparison_summary_title"],
        f"- {labels['total_tokens']}: {_format_number(analysis['total_tokens'])}",
        f"- {labels['unique_tokens']}: {_format_number(analysis['unique_tokens'])}",
        f"- {labels['variability_ratio_short']}: {_format_ratio(analysis['token_ratio'])}",
        f"- {labels['hapax_legomena']}: {_format_number(analysis['hapax']['count'])}",
        f"- {labels['avg_token_length_short']}: {_format_number(length_stats['avg_length'])}",
        f"- {labels['median_token_length_short']}: {_format_number(length_stats['median_length'])}",
        f"- {labels['longest_non_hapax']}: {_format_tokens_with_length(hapax_stats['non_hapax_longest'], labels)}",
        f"- {labels['longest_hapax']}: {_format_tokens_with_length(hapax_stats['hapax_longest'], labels)}",
    ]


def _render_comparison_table(comparison: Dict[str, object], labels: Dict[str, str], current: Dict[str, object]) -> List[str]:
    analysis = comparison.get("analysis")
    if not analysis:
        return []
    scenario = comparison.get("scenario")
    not_lemma_current = current
    lemma_current = analysis
    if scenario and scenario.lemmatize:
        not_lemma_current = analysis
        lemma_current = current
    rows = [
        (labels["total_tokens"], _format_number(not_lemma_current["total_tokens"]), _format_number(lemma_current["total_tokens"])),
        (labels["unique_tokens"], _format_number(not_lemma_current["unique_tokens"]), _format_number(lemma_current["unique_tokens"])),
        (labels["variability_ratio_short"], _format_ratio(not_lemma_current["token_ratio"]), _format_ratio(lemma_current["token_ratio"])),
        (
            labels["hapax_legomena_pct_unique"],
            _format_percent(_safe_percent(not_lemma_current["hapax"]["count"], not_lemma_current["unique_tokens"])),
            _format_percent(_safe_percent(lemma_current["hapax"]["count"], lemma_current["unique_tokens"])),
        ),
        (
            labels["avg_token_length_short"],
            _format_number(not_lemma_current["length_stats"]["avg_length"]),
            _format_number(lemma_current["length_stats"]["avg_length"]),
        ),
        (
            labels["median_token_length_short"],
            _format_number(not_lemma_current["length_stats"]["median_length"]),
            _format_number(lemma_current["length_stats"]["median_length"]),
        ),
    ]
    header = f"{labels['metric_header']:<28} {labels['not_lemmatized_header']:<16} {labels['lemmatized_header']:<16}"
    lines = [header, "-" * len(header)]
    for label, current_val, comparison_val in rows:
        lines.append(f"{label:<28} {current_val:<12} {comparison_val:<12}")
    return lines


def _pdf_bullets(lines: List[str], style: ParagraphStyle) -> List[object]:
    elements: List[object] = []
    for line in lines:
        if not line:
            elements.append(Spacer(1, 6))
            continue
        text = line
        if line.startswith("- "):
            text = f"• {line[2:]}"
        elements.append(Paragraph(text, style))
    elements.append(Spacer(1, 8))
    return elements


def _pdf_key_value_block(lines: List[str], style: ParagraphStyle) -> List[object]:
    rows = []
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            rows.append([key, value])
        else:
            rows.append([line, ""])
    table = Table(rows, colWidths=[180, 330], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return [table, Spacer(1, 10)]


def _pdf_summary(report_data: Dict[str, object], labels: Dict[str, str], style: ParagraphStyle) -> List[object]:
    summary_lines = _render_summary(report_data, labels)
    return _pdf_bullets(summary_lines, style)


def _pdf_summary_table(report_data: Dict[str, object], labels: Dict[str, str]) -> Table:
    analysis = report_data.get("analysis")
    comparison = report_data.get("comparison", {})
    comparison_analysis = comparison.get("analysis") if comparison.get("available") else None
    scenario = report_data.get("scenario")
    not_lemma_header = labels["not_lemmatized_header"]
    lemma_header = labels["lemmatized_header"]

    not_lemma_analysis = analysis
    lemma_analysis = comparison_analysis
    if scenario and scenario.lemmatize:
        not_lemma_analysis = comparison_analysis
        lemma_analysis = analysis

    rows = [[labels["metric_header"], not_lemma_header, lemma_header]]
    if analysis:
        rows.append([
            labels["total_tokens"],
            _format_number(not_lemma_analysis["total_tokens"]) if not_lemma_analysis else labels["na"],
            _format_number(lemma_analysis["total_tokens"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["unique_tokens"],
            _format_number(not_lemma_analysis["unique_tokens"]) if not_lemma_analysis else labels["na"],
            _format_number(lemma_analysis["unique_tokens"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["variability_ratio_short"],
            _format_ratio(not_lemma_analysis["token_ratio"]) if not_lemma_analysis else labels["na"],
            _format_ratio(lemma_analysis["token_ratio"]) if lemma_analysis else labels["na"],
        ])
        hapax_pct_unique = _safe_percent(not_lemma_analysis["hapax"]["count"], not_lemma_analysis["unique_tokens"]) if not_lemma_analysis else 0.0
        hapax_comp_pct = _safe_percent(lemma_analysis["hapax"]["count"], lemma_analysis["unique_tokens"]) if lemma_analysis else 0.0
        rows.append([
            labels["hapax_legomena_count"],
            _format_number(not_lemma_analysis["hapax"]["count"]) if not_lemma_analysis else labels["na"],
            _format_number(lemma_analysis["hapax"]["count"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["hapax_legomena_pct_unique"],
            _format_percent(hapax_pct_unique) if not_lemma_analysis else labels["na"],
            _format_percent(hapax_comp_pct) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["avg_token_length_short"],
            _format_number(not_lemma_analysis["length_stats"]["avg_length"]) if not_lemma_analysis else labels["na"],
            _format_number(lemma_analysis["length_stats"]["avg_length"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["median_token_length_short"],
            _format_number(not_lemma_analysis["length_stats"]["median_length"]) if not_lemma_analysis else labels["na"],
            _format_number(lemma_analysis["length_stats"]["median_length"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["avg_token_length_non_hapax"],
            _format_number(not_lemma_analysis["length_stats_non_hapax"]["avg_length"]) if not_lemma_analysis else labels["na"],
            _format_number(lemma_analysis["length_stats_non_hapax"]["avg_length"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["avg_token_length_hapax"],
            _format_number(not_lemma_analysis["length_stats_hapax"]["avg_length"]) if not_lemma_analysis else labels["na"],
            _format_number(lemma_analysis["length_stats_hapax"]["avg_length"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["median_token_length_non_hapax"],
            _format_number(not_lemma_analysis["length_stats_non_hapax"]["median_length"]) if not_lemma_analysis else labels["na"],
            _format_number(lemma_analysis["length_stats_non_hapax"]["median_length"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["median_token_length_hapax"],
            _format_number(not_lemma_analysis["length_stats_hapax"]["median_length"]) if not_lemma_analysis else labels["na"],
            _format_number(lemma_analysis["length_stats_hapax"]["median_length"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["top_5_concentration_short"],
            _format_percent(not_lemma_analysis["concentration"].get(5, {"percent_of_total": 0.0})["percent_of_total"]) if not_lemma_analysis else labels["na"],
            _format_percent(lemma_analysis["concentration"].get(5, {"percent_of_total": 0.0})["percent_of_total"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["top_10_concentration_short"],
            _format_percent(not_lemma_analysis["concentration"].get(10, {"percent_of_total": 0.0})["percent_of_total"]) if not_lemma_analysis else labels["na"],
            _format_percent(lemma_analysis["concentration"].get(10, {"percent_of_total": 0.0})["percent_of_total"]) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["top_20_concentration_short"],
            _format_percent(not_lemma_analysis["concentration"].get(20, {"percent_of_total": 0.0})["percent_of_total"]) if not_lemma_analysis else labels["na"],
            _format_percent(lemma_analysis["concentration"].get(20, {"percent_of_total": 0.0})["percent_of_total"]) if lemma_analysis else labels["na"],
        ])

    table = Table(rows, colWidths=[200, 140, 140], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    return table


def _pdf_token_stats_table(report_data: Dict[str, object], labels: Dict[str, str]) -> Optional[Table]:
    token_stats = report_data.get("token_stats")
    if not token_stats:
        return None
    rows = [[labels["token_stats_header"], labels["total_tokens"], labels["unique_tokens"]]]
    for entry in token_stats:
        scenario_label = _format_scenario_label(
            None,
            labels,
            lemmatize_override=entry["lemmatize"],
            stopwords_override=entry["include_stopwords"],
        )
        rows.append([
            scenario_label,
            _format_number(entry["total_tokens"]),
            _format_number(entry["unique_tokens"]),
        ])
    table = Table(rows, colWidths=[220, 140, 140], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    return table


def _pdf_core_stats_table(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> Table:
    if not analysis:
        return Table([[labels["no_data"]]])

    hapax_stats = analysis["hapax_stats"]
    rows = [
        [labels["core_including_hapax"], ""],
        [labels["total_tokens"], _format_number(analysis["total_tokens"])],
        [labels["unique_tokens"], _format_number(analysis["unique_tokens"])],
        [labels["variability_ratio"], _format_ratio(analysis["token_ratio"])],
        [labels["avg_token_length"], _format_number(analysis["length_stats"]["avg_length"])],
        [labels["median_token_length"], _format_number(analysis["length_stats"]["median_length"])],
        [labels["shortest_token"], analysis["length_stats"]["shortest_token"] or labels["na"]],
        [labels["longest_token"], analysis["length_stats"]["longest_token"] or labels["na"]],
        ["", ""],
        [labels["core_excluding_hapax"], ""],
        [labels["avg_token_length_non_hapax"], _format_number(analysis["length_stats_non_hapax"]["avg_length"])],
        [labels["median_token_length_non_hapax"], _format_number(analysis["length_stats_non_hapax"]["median_length"])],
        [labels["shortest_non_hapax"], _format_tokens_with_length(hapax_stats["non_hapax_shortest"], labels)],
        [labels["longest_non_hapax"], _format_tokens_with_length(hapax_stats["non_hapax_longest"], labels)],
        ["", ""],
        [labels["core_hapax_only"], ""],
        [labels["avg_token_length_hapax"], _format_number(analysis["length_stats_hapax"]["avg_length"])],
        [labels["median_token_length_hapax"], _format_number(analysis["length_stats_hapax"]["median_length"])],
        [labels["shortest_hapax"], _format_tokens_with_length(hapax_stats["hapax_shortest"], labels)],
        [labels["longest_hapax"], _format_tokens_with_length(hapax_stats["hapax_longest"], labels)],
    ]
    table = Table(rows, colWidths=[230, 250], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("BACKGROUND", (0, 0), (0, 0), colors.lightgrey),
                ("BACKGROUND", (0, 9), (0, 9), colors.lightgrey),
                ("BACKGROUND", (0, 15), (0, 15), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return table


def _pdf_token_extremes_table(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> Table:
    if not analysis:
        return Table([[labels["no_data"]]], splitByRow=0)

    hapax_stats = analysis["hapax_stats"]
    shortest_token = analysis["length_stats"]["shortest_token"]
    longest_token = analysis["length_stats"]["longest_token"]
    rows = [
        [labels["metric_header"], labels["length_header"], labels["examples_header"]],
        [
            labels["shortest_token"],
            str(len(shortest_token)) if shortest_token else labels["na"],
            shortest_token or labels["na"],
        ],
        [
            labels["longest_token"],
            str(len(longest_token)) if longest_token else labels["na"],
            longest_token or labels["na"],
        ],
        [
            labels["shortest_non_hapax"],
            _format_number(hapax_stats["non_hapax_shortest"]["length"]),
            _format_tokens_examples(hapax_stats["non_hapax_shortest"], labels),
        ],
        [
            labels["longest_non_hapax"],
            _format_number(hapax_stats["non_hapax_longest"]["length"]),
            _format_tokens_examples(hapax_stats["non_hapax_longest"], labels),
        ],
        [
            labels["shortest_hapax"],
            _format_number(hapax_stats["hapax_shortest"]["length"]),
            _format_tokens_examples(hapax_stats["hapax_shortest"], labels),
        ],
        [
            labels["longest_hapax"],
            _format_number(hapax_stats["hapax_longest"]["length"]),
            _format_tokens_examples(hapax_stats["hapax_longest"], labels),
        ],
    ]
    table = Table(rows, colWidths=[200, 70, 210], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ]
        )
    )
    return table


def _pdf_top_word_insights_table(report_data: Dict[str, object], labels: Dict[str, str]) -> Table:
    insights = report_data.get("top_word_insights", {})
    bigrams_info = insights.get("bigrams", {})
    examples_info = insights.get("examples", {})
    top_terms = insights.get("top_terms") or []

    rows = [[labels["word_header"], labels["bigrams_header"], labels["examples_header"]]]
    for term in top_terms:
        bigrams = bigrams_info.get("items", {}).get(term, [])
        bigram_text = "<br/>".join(
            [f"{entry['bigram']} ({_format_number(entry['count'])})" for entry in bigrams]
        ) or labels["no_examples_found"]
        examples = examples_info.get("items", {}).get(term, [])
        example_text = "<br/>".join(examples) or labels["no_examples_found"]
        rows.append([term, Paragraph(bigram_text, getSampleStyleSheet()["BodyText"]), Paragraph(example_text, getSampleStyleSheet()["BodyText"])])

    table = Table(rows, colWidths=[90, 160, 240], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def _pdf_concentration_table(report_data: Dict[str, object], labels: Dict[str, str]) -> Table:
    analysis = report_data.get("analysis")
    comparison = report_data.get("comparison", {})
    comparison_analysis = comparison.get("analysis") if comparison.get("available") else None
    scenario = report_data.get("scenario")
    not_lemma_header = labels["not_lemmatized_header"]
    lemma_header = labels["lemmatized_header"]
    not_lemma_analysis = analysis
    lemma_analysis = comparison_analysis
    if scenario and scenario.lemmatize:
        not_lemma_analysis = comparison_analysis
        lemma_analysis = analysis
    rows = [[labels["metric_header"], not_lemma_header, lemma_header]]
    if analysis:
        rows.append([
            labels["top_5_concentration_short"],
            _format_percent(not_lemma_analysis["concentration"].get(5, 0.0)) if not_lemma_analysis else labels["na"],
            _format_percent(lemma_analysis["concentration"].get(5, 0.0)) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["top_10_concentration_short"],
            _format_percent(not_lemma_analysis["concentration"].get(10, 0.0)) if not_lemma_analysis else labels["na"],
            _format_percent(lemma_analysis["concentration"].get(10, 0.0)) if lemma_analysis else labels["na"],
        ])
        rows.append([
            labels["top_20_concentration_short"],
            _format_percent(not_lemma_analysis["concentration"].get(20, 0.0)) if not_lemma_analysis else labels["na"],
            _format_percent(lemma_analysis["concentration"].get(20, 0.0)) if lemma_analysis else labels["na"],
        ])
    table = Table(rows, colWidths=[200, 140, 140], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    return table


def _pdf_hapax_examples_table(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> Table:
    if not analysis:
        return Table([[labels["no_data"]]], splitByRow=0)
    hapax_stats = analysis["hapax_stats"]
    longest_tokens = hapax_stats["hapax_longest"]["tokens"]
    shortest_tokens = hapax_stats["hapax_shortest"]["tokens"]
    rows = [
        [labels["hapax_longest_examples"], labels["hapax_shortest_examples"]],
        [
            _format_examples_list(longest_tokens, labels, max_items=5),
            _format_examples_list(shortest_tokens, labels, max_items=5),
        ],
    ]
    table = Table(rows, colWidths=[250, 250], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def _pdf_metadata_table(report_data: Dict[str, object], labels: Dict[str, str], style: ParagraphStyle) -> Table:
    scenario_lines = _render_scenario_metadata(
        report_data["scenario"],
        labels,
        source_name=report_data.get("source_name"),
        generated_at=report_data.get("generated_at"),
    )
    cloud_lines = _render_cloud_metadata(report_data["cloud_metadata"], labels)
    rows = [[labels["metadata_scenario_header"], labels["metadata_cloud_header"]]]
    rows.append([Paragraph("<br/>".join(scenario_lines), style), Paragraph("<br/>".join(cloud_lines), style)])
    table = Table(rows, colWidths=[250, 250], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def _render_token_stats(report_data: Dict[str, object], labels: Dict[str, str]) -> List[str]:
    token_stats = report_data.get("token_stats")
    if not token_stats:
        return []
    lines = [labels["token_stats_title"]]
    header = f"{labels['token_stats_header']}: {labels['token_stats_columns']}"
    lines.append(header)
    for entry in token_stats:
        scenario_label = _format_scenario_label(
            None,
            labels,
            lemmatize_override=entry["lemmatize"],
            stopwords_override=entry["include_stopwords"],
        )
        lines.append(
            f"- {scenario_label}: {_format_number(entry['total_tokens'])} / {_format_number(entry['unique_tokens'])}"
        )
    return lines


def _format_scenario_label(
    scenario: Optional[ScenarioMetadata],
    labels: Dict[str, str],
    lemmatize_override: Optional[bool] = None,
    stopwords_override: Optional[bool] = None,
) -> str:
    lemmatize_value = lemmatize_override if lemmatize_override is not None else (scenario.lemmatize if scenario else False)
    stopwords_value = stopwords_override if stopwords_override is not None else (scenario.include_stopwords if scenario else False)
    lemmatize_text = labels["yes"] if lemmatize_value else labels["no"]
    stopwords_text = labels["yes"] if stopwords_value else labels["no"]
    return f"{labels['lemmatize_short']}={lemmatize_text}, {labels['stopwords_short']}={stopwords_text}"


def _pdf_top_words_table(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> Table:
    if not analysis or not analysis["top_words"]:
        return Table([[labels["no_data"]]])
    rows = [["#", labels["word_header"], labels["count_header"], labels["percent_header"]]]
    for idx, item in enumerate(analysis["top_words"], start=1):
        rows.append([
            str(idx), 
            item["word"], 
            _format_number(item["frequency"]), 
            _format_percent(item["percent"])
        ])
    table = Table(rows, colWidths=[24, 180, 80, 80], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (2, 1), (3, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ]
        )
    )
    return table


def _pdf_top_words_with_concentration_table(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> Table:
    """Combined table showing top 20 words with their frequency and percentage contribution."""
    if not analysis or not analysis["top_words"]:
        return Table([[labels["no_data"]]])
    rows = [["#", labels["word_header"], labels["count_header"], labels["percent_header"]]]
    for idx, item in enumerate(analysis["top_words"], start=1):
        rows.append([
            str(idx), 
            item["word"], 
            _format_number(item["frequency"]), 
            _format_percent(item["percent"])
        ])
    table = Table(rows, colWidths=[24, 180, 80, 80], splitByRow=0)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (2, 1), (3, -1), "RIGHT"),  # Right-align numbers
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ]
        )
    )
    return table


def _render_concentration_summary_pdf(analysis: Optional[Dict[str, object]], labels: Dict[str, str], body_style: ParagraphStyle) -> List:
    """Generate concentration summary as a bullet list showing cumulative coverage of top 5, 10, and 20 words."""
    if not analysis or not analysis.get("concentration"):
        return [Paragraph(labels["no_data"], body_style)]
    
    concentration = analysis["concentration"]
    top5_data = concentration.get(5, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    top10_data = concentration.get(10, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    top20_data = concentration.get(20, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    
    items = [
        ListItem(Paragraph(labels["concentration_top5"].format(
            pct_total=_format_percent(top5_data["percent_of_total"]),
            pct_unique=_format_percent(top5_data["percent_of_unique"])
        ), body_style)),
        ListItem(Paragraph(labels["concentration_top10"].format(
            pct_total=_format_percent(top10_data["percent_of_total"]),
            pct_unique=_format_percent(top10_data["percent_of_unique"])
        ), body_style)),
        ListItem(Paragraph(labels["concentration_top20"].format(
            pct_total=_format_percent(top20_data["percent_of_total"]),
            pct_unique=_format_percent(top20_data["percent_of_unique"])
        ), body_style)),
    ]
    
    bullet_list = ListFlowable(items, bulletType='bullet', start='•')
    return [
        Paragraph(labels["concentration_intro_text"], body_style),
        Spacer(1, 4),
        bullet_list
    ]



def _build_concentration_chart(analysis: Optional[Dict[str, object]], labels: Dict[str, str]) -> Optional[Image]:
    if not analysis or not analysis.get("concentration"):
        return None
    concentration = analysis["concentration"]
    categories = [labels["top5_short"], labels["top10_short"], labels["top20_short"]]
    top5_data = concentration.get(5, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    top10_data = concentration.get(10, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    top20_data = concentration.get(20, {"percent_of_total": 0.0, "percent_of_unique": 0.0})
    values = [
        top5_data["percent_of_total"],
        top10_data["percent_of_total"],
        top20_data["percent_of_total"],
    ]
    fig, ax = plt.subplots(figsize=(4.5, 2.2))
    ax.bar(categories, values, color="#4C78A8")
    ax.set_ylim(0, max(values + [1]) * 1.2)
    ax.set_ylabel(labels["percent_label"])
    ax.set_title(labels["concentration_chart_title"])
    for idx, value in enumerate(values):
        ax.text(idx, value + 0.3, f"{value:.2f}%", ha="center", va="bottom", fontsize=8)
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    image = Image(buf, width=320, height=160)
    return image


def _render_comparison_section(comparison: Dict[str, object], labels: Dict[str, str]) -> List[str]:
    if not comparison["available"]:
        reason = comparison.get("reason") or "Comparison not available for this input."
        return [
            f"{comparison['label']}: {labels['not_available']}",
            f"{labels['warning']}: {reason}",
        ]

    analysis = comparison["analysis"]
    if not analysis:
        return ["No data available."]

    lines = [
        f"{comparison['label']}:",
        "",
    ]
    lines.extend(_render_comparison_table(comparison, labels, current=comparison["current"]))
    lines.append("")
    lines.append(labels["top_words_title"])
    lines.append("-" * 24)
    lines.extend(_render_top_words(analysis, labels))
    lines.append("")
    lines.append(labels["concentration_title"])
    lines.append("-" * 24)
    lines.extend(_render_concentration_summary(analysis, labels))
    lines.append("")
    lines.append(labels["hapax_title"])
    lines.append("-" * 24)
    lines.extend(_render_hapax(analysis, labels))
    return lines


def _render_cloud_metadata(metadata: Optional[CloudMetadata], labels: Dict[str, str]) -> List[str]:
    if metadata is None:
        return [labels["cloud_meta_na"]]

    return [
        f"{labels['max_words']}: {metadata.max_words}",
        f"{labels['min_word_length']}: {metadata.min_word_length}",
        f"{labels['canvas_size']}: {metadata.canvas_width}x{metadata.canvas_height}",
        f"{labels['theme']}: {metadata.theme or labels['none']}",
        f"{labels['colormap']}: {metadata.colormap or labels['none']}",
        f"{labels['background']}: {metadata.background or labels['none']}",
        f"{labels['font_color']}: {metadata.fontcolor or labels['none']}",
        f"{labels['relative_scaling']}: {_format_number(metadata.relative_scaling)}",
        f"{labels['prefer_horizontal']}: {_format_number(metadata.prefer_horizontal)}",
        f"{labels['mask']}: {metadata.mask or labels['none']}",
        f"{labels['contour_width']}: {_format_number(metadata.contour_width)}",
        f"{labels['contour_color']}: {metadata.contour_color or labels['none']}",
        f"{labels['font_path']}: {metadata.font_path or labels['none']}",
    ]


def _safe_percent(freq: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return (float(freq) / total) * 100.0


def _format_number(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return str(value)
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _format_ratio(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _format_percent(value: float) -> str:
    return f"{value:.2f}%"


def _tokens_by_length(tokens: List[str], find_max: bool) -> Dict[str, object]:
    if not tokens:
        return {"length": None, "tokens": []}
    extreme_length = max(len(token) for token in tokens) if find_max else min(len(token) for token in tokens)
    selected = sorted([token for token in tokens if len(token) == extreme_length])
    return {"length": extreme_length, "tokens": selected}


def _format_tokens_with_length(data: Dict[str, object], labels: Dict[str, str]) -> str:
    if not data or data.get("length") is None:
        return labels["na"]
    tokens = data.get("tokens") or []
    tokens_text = ", ".join(tokens[:3]) if tokens else labels["na"]
    return f"{data['length']} {labels['chars']} ({tokens_text}, {labels['showing_up_to_3']})"


def _format_tokens_examples(data: Dict[str, object], labels: Dict[str, str]) -> str:
    if not data or data.get("length") is None:
        return labels["na"]
    tokens = data.get("tokens") or []
    if not tokens:
        return labels["na"]
    return "\n".join(tokens[:3])


def _format_examples_list(tokens: List[str], labels: Dict[str, str], max_items: int = 5) -> str:
    if not tokens:
        return labels["na"]
    return "\n".join(tokens[:max_items])


def _get_report_labels(language: str) -> Dict[str, str]:
    if language.lower().startswith("es"):
        return {
            "title": "Informe Nubisary",
            "generated_at": "Generado (UTC)",
            "summary_title": "Resumen",
            "intro_text": "Este informe ofrece un análisis detallado del vocabulario del texto de entrada. Se presentan métricas comparativas (con y sin lematización), palabras más frecuentes, concentración del vocabulario, hapax legomena (palabras únicas) y metadatos técnicos del procesamiento. El texto analizado proviene del archivo: {source_name}",
            "summary_intro": "Este apartado ofrece una visión comparativa de las métricas principales del texto, tanto en su forma original como después de aplicar la lematización (reducción de cada palabra a su forma base). Los cálculos se realizaron excluyendo las palabras funcionales habituales (stopwords). En pocas palabras, el cuadro muestra cuántas palabras aparecen en total, cuántas son distintas y cuánta variabilidad léxica contiene el documento.",
            "token_extremes_intro": "Se indican la longitud más corta y la más larga de los tokens detectados en el corpus, distinguiendo entre palabras que aparecen una sola vez (hapax) y aquellas que se repiten. Este desglose permite identificar rápidamente términos poco frecuentes o de carácter especializado.",
            "top_words_intro": "Aquí aparecen las veinte palabras con mayor número de apariciones antes de la lematización, acompañadas del recuento exacto y del porcentaje que representan respecto al total de tokens. Esta información revela los conceptos temáticos centrales del texto. Al final de la tabla se muestra cuánto del texto total está cubierto por los 5, 10 y 20 términos más habituales, lo que indica la concentración léxica del documento.",
            "top_words_insights_intro": "Para cada una de las cinco palabras más frecuentes se presentan ejemplos de bigramas (pares de palabras consecutivas) y fragmentos de contexto donde aparecen. De este modo se muestra cómo se utilizan esas palabras dentro de frases reales y cuál es su relación con otros conceptos del texto.",
            "concentration_intro": "Esta tabla indica la proporción del total de palabras que está compuesta por los 5, 10 y 20 términos más habituales. Cuando una gran parte del texto está formada por unas pocas palabras, el vocabulario es menos diverso; por el contrario, una cobertura más baja indica una mayor riqueza léxica.",
            "hapax_intro": "Los hapax legomena (del griego «una sola vez») son palabras que aparecen exactamente una vez en el documento completo. Pueden indicar tanto riqueza léxica como errores tipográficos, nombres propios o términos especializados poco frecuentes.",
            "hapax_data_intro": "Datos cuantitativos:",
            "hapax_count_label": "Total de hapax",
            "hapax_pct_unique_label": "Porcentaje del vocabulario único",
            "hapax_pct_total_label": "Porcentaje del total de palabras",
            "hapax_examples_note": "A continuación se muestran ejemplos de los hapax más largos y más cortos para ilustrar esta diversidad:",
            "metadata_intro": "En este apartado se describen los criterios técnicos empleados para el análisis (idioma, tipo de n-grama, aplicación de lematización, exclusión de stopwords, sensibilidad a mayúsculas, etc.) y la fecha y hora exactas de generación del reporte (UTC). Esta información resulta útil para reproducir el estudio o ajustar la configuración en futuros análisis.",
            "summary_tokens": "Tokens totales",
            "summary_unique": "Tokens únicos",
            "summary_hapax": "Hapax legomena",
            "summary_top5": "Top 5 palabras",
            "summary_concentration": "Top 5 palabras concentran",
            "summary_comparison": "Comparación (lematizado)",
            "lemmatized_unique_change": "variación de tokens únicos",
            "scenario_title": "Ajustes de procesamiento",
            "core_stats_title": "Estadísticas principales",
            "token_extremes_title": "Análisis de longitud de palabras",
            "core_including_hapax": "Incluyendo hapax",
            "core_excluding_hapax": "Excluyendo hapax",
            "core_hapax_only": "Solo hapax",
            "top_words_title": "Palabras más frecuentes y su peso en el vocabulario",
            "top_words_bigrams_title": "Top 5 palabras: bigramas frecuentes",
            "top_words_examples_title": "Top 5 palabras: ejemplos en contexto",
            "top_words_insights_title": "Top 5 palabras: bigramas y contexto",
            "concentration_title": "Concentración del vocabulario",
            "concentration_summary": "Las 5 palabras más frecuentes cubren el {top5} del texto; las 10 cubren el {top10}; y las 20 cubren el {top20}. (Calculado sobre {total} tokens sin lematizar).",
            "concentration_intro_text": "A continuación, se muestra el porcentaje que ocupan las palabras más frecuentes respecto al total de tokens y respecto al vocabulario único:",
            "concentration_top5": "Las 5 palabras más frecuentes: {pct_total} del total, {pct_unique} de únicos",
            "concentration_top10": "Las 10 palabras más frecuentes: {pct_total} del total, {pct_unique} de únicos",
            "concentration_top20": "Las 20 palabras más frecuentes: {pct_total} del total, {pct_unique} de únicos",
            "percent_header": "% del total",
            "of_unique": "de únicos",
            "hapax_title": "Hapax legomena (frecuencia = 1)",
            "comparison_title": "Escenario de comparación",
            "metric_header": "Métrica",
            "current_header": "Actual",
            "comparison_header": "Lematizado",
            "length_header": "Longitud",
            "not_lemmatized_header": "Sin lematizar",
            "lemmatized_header": "Lematizado",
            "stopwords_included": "incluidas",
            "stopwords_excluded": "excluidas",
            "showing_up_to_5": "mostrando hasta 5",
            "hapax_summary_text": "Hapax legomena: {count} ({pct_unique} {of_unique}, {pct_total} {of_total}). Se incluyen hasta 5 ejemplos de los hapax más largos y más cortos.",
            "hapax_longest_examples": "Hapax más largos (ejemplos)",
            "hapax_shortest_examples": "Hapax más cortos (ejemplos)",
            "word_header": "Palabra",
            "count_header": "Conteo",
            "percent_header": "%",
            "bigrams_header": "Bigramas",
            "examples_header": "Ejemplos",
            "top5_short": "Top 5",
            "top10_short": "Top 10",
            "top20_short": "Top 20",
            "percent_label": "Porcentaje",
            "concentration_chart_title": "Concentración del vocabulario",
            "top_5_concentration_short": "Top 5",
            "top_10_concentration_short": "Top 10",
            "top_20_concentration_short": "Top 20",
            "hapax_legomena_count": "Hapax (conteo)",
            "hapax_legomena_pct_unique": "Hapax (% de únicos)",
            "metadata_title": "Metadatos técnicos",
            "metadata_scenario_header": "Procesamiento",
            "metadata_cloud_header": "Nube de palabras",
        "source_name": "Archivo",
            "cloud_meta_title": "Parámetros de la nube (informativo)",
            "token_stats_title": "Conteo de tokens por configuración",
            "token_stats_header": "Configuración",
            "token_stats_columns": "Total / Únicos",
            "lemmatize_short": "Lematizar",
            "stopwords_short": "Stopwords",
            "yes": "sí",
            "no": "no",
            "label": "Etiqueta",
            "language": "Idioma",
            "ngram": "N-grama",
            "lemmatize": "Lematizar",
            "include_stopwords": "Incluir stopwords",
            "include_numbers": "Incluir números",
            "case_sensitive": "Sensible a mayúsculas",
            "exclude_words": "Excluir palabras",
            "exclude_case_sensitive": "Exclusión sensible a mayúsculas",
            "regex_rule": "Regla regex",
            "regex_case_sensitive": "Regex sensible a mayúsculas",
            "replace_stage": "Etapa de reemplazo",
            "none": "Ninguno",
            "na": "N/A",
            "no_data": "Sin datos disponibles.",
            "not_available": "No disponible",
            "warning": "Aviso",
            "note": "Nota",
            "no_examples_found": "No se encontraron ejemplos.",
            "total_tokens": "Tokens totales",
            "unique_tokens": "Tokens únicos",
            "variability_ratio": "Ratio de variabilidad del vocabulario (unique/total)",
            "variability_ratio_short": "Ratio de variabilidad (unique/total)",
            "hapax_legomena": "Hapax legomena",
            "avg_token_length": "Longitud media de token",
            "median_token_length": "Longitud mediana de token",
            "avg_token_length_non_hapax": "Longitud media (excluyendo hapax)",
            "median_token_length_non_hapax": "Longitud mediana (excluyendo hapax)",
            "avg_token_length_hapax": "Longitud media (solo hapax)",
            "median_token_length_hapax": "Longitud mediana (solo hapax)",
            "avg_token_length_short": "Longitud media",
            "median_token_length_short": "Longitud mediana",
            "shortest_token": "Token más corto",
            "longest_token": "Token más largo",
            "shortest_non_hapax": "Token más corto (excluyendo hapax)",
            "longest_non_hapax": "Token más largo (excluyendo hapax)",
            "shortest_hapax": "Token más corto (solo hapax)",
            "longest_hapax": "Token más largo (solo hapax)",
            "of_unique": "de tokens únicos",
            "of_total": "del total",
            "top_5_concentration": "Las 5 palabras más frecuentes suman",
            "top_10_concentration": "Las 10 palabras más frecuentes suman",
            "top_20_concentration": "Las 20 palabras más frecuentes suman",
            "of_all_tokens": "del total de tokens.",
            "count": "Cantidad",
            "sample_up_to_20": "Ejemplo (hasta 20)",
            "longest_hapax_tokens": "Hapax más largo(s)",
            "comparison_summary_title": "Resumen rápido vs escenario actual:",
            "cloud_meta_na": "No aplica (análisis standalone).",
            "max_words": "Máx. palabras",
            "min_word_length": "Longitud mínima",
            "canvas_size": "Tamaño del lienzo",
            "theme": "Tema",
            "colormap": "Colormap",
            "background": "Fondo",
            "font_color": "Color de fuente",
            "relative_scaling": "Escalado relativo",
            "prefer_horizontal": "Preferencia horizontal",
            "mask": "Máscara",
            "contour_width": "Ancho de contorno",
            "contour_color": "Color de contorno",
            "font_path": "Ruta de fuente",
            "chars": "caracteres",
            "showing_up_to_3": "mostrando hasta 3",
            "glossary_title": "Glosario",
            "glossary_token_term": "Token",
            "glossary_token_def": "Unidad mínima de texto analizada. En este contexto, generalmente equivale a una palabra después del procesamiento (limpieza, exclusión de stopwords, etc.).",
            "glossary_lemmatization_term": "Lematización",
            "glossary_lemmatization_def": "Proceso de reducir cada palabra a su forma base o lema. Por ejemplo, 'corriendo', 'corrió' y 'correr' se agrupan bajo el lema 'correr'.",
            "glossary_stopwords_term": "Stopwords",
            "glossary_stopwords_def": "Palabras funcionales muy comunes (como 'el', 'la', 'de', 'y') que suelen excluirse del análisis porque no aportan información temática relevante.",
            "glossary_hapax_term": "Hapax legomena",
            "glossary_hapax_def": "Palabras que aparecen una única vez en todo el texto. Su prevalencia indica la diversidad léxica del documento.",
            "glossary_bigram_term": "Bigrama",
            "glossary_bigram_def": "Par de palabras consecutivas en el texto. Por ejemplo, en 'cielo azul', el bigrama es ('cielo', 'azul').",
            "glossary_variability_term": "Ratio de variabilidad",
            "glossary_variability_def": "Proporción entre el número de palabras distintas (tipos) y el total de palabras (tokens). Un ratio alto indica mayor riqueza léxica.",
        }

    return {
        "title": "Nubisary Report",
        "generated_at": "Generated (UTC)",
        "summary_title": "Summary",
        "intro_text": "This report provides a detailed analysis of the vocabulary in the input text. It presents comparative metrics (with and without lemmatization), most frequent words, vocabulary concentration, hapax legomena (unique words), and technical metadata of the processing. The analyzed text comes from the file: {source_name}",
        "summary_intro": "This section offers a comparative overview of the text's main metrics, both in its original form and after applying lemmatization (reducing each word to its base form). Calculations were performed excluding common functional words (stopwords). In short, the table shows how many words appear in total, how many are distinct, and how much lexical variability the document contains.",
        "token_extremes_intro": "The shortest and longest token lengths detected in the corpus are indicated, distinguishing between words that appear only once (hapax) and those that are repeated. This breakdown allows for quick identification of infrequent or specialized terms.",
        "top_words_intro": "Here are the twenty words with the highest number of occurrences before lemmatization, accompanied by the exact count and the percentage they represent of the total tokens. This information reveals the central thematic concepts of the text. At the end of the table, the cumulative coverage of the top 5, 10, and 20 most common terms is shown, indicating the lexical concentration of the document.",
        "top_words_insights_intro": "For each of the five most frequent words, examples of bigrams (consecutive word pairs) and context fragments where they appear are presented. This shows how these words are used within real sentences and their relationship with other concepts in the text.",
        "concentration_intro": "This table indicates the proportion of total words that is composed of the 5, 10, and 20 most common terms. When a large part of the text is formed by a few words, the vocabulary is less diverse; conversely, lower coverage indicates greater lexical richness.",
        "hapax_intro": "Hapax legomena (from Greek «only once») are words that appear exactly once in the complete document. They can indicate both lexical richness and typographical errors, proper names, or infrequent specialized terms.",
        "hapax_data_intro": "Quantitative data:",
        "hapax_count_label": "Total hapax",
        "hapax_pct_unique_label": "Percentage of unique vocabulary",
        "hapax_pct_total_label": "Percentage of total words",
        "hapax_examples_note": "Below are examples of the longest and shortest hapax to illustrate this diversity:",
        "metadata_intro": "This section describes the technical criteria used for the analysis (language, n-gram type, lemmatization application, stopwords exclusion, case sensitivity, etc.) and the exact date and time of report generation (UTC). This information is useful for reproducing the study or adjusting the configuration in future analyses.",
        "summary_tokens": "Total tokens",
        "summary_unique": "Unique tokens",
        "summary_hapax": "Hapax legomena",
        "summary_top5": "Top 5 words",
        "summary_concentration": "Top 5 words concentration",
        "summary_comparison": "Comparison (lemmatized)",
        "lemmatized_unique_change": "unique tokens change",
        "scenario_title": "Processing Settings",
        "core_stats_title": "Core Statistics",
        "token_extremes_title": "Word Length Analysis",
        "core_including_hapax": "Including hapax",
        "core_excluding_hapax": "Excluding hapax",
        "core_hapax_only": "Hapax only",
        "top_words_title": "Most Frequent Words and Their Weight in the Vocabulary",
        "top_words_bigrams_title": "Top 5 Words: Common Bigrams",
        "top_words_examples_title": "Top 5 Words: Context Examples",
        "top_words_insights_title": "Top 5 Words: Bigrams & Context",
        "concentration_title": "Vocabulary Concentration",
        "concentration_summary": "The top 5 most frequent words cover {top5} of the text; the top 10 cover {top10}; and the top 20 cover {top20}. (Calculated over {total} tokens without lemmatization).",
        "concentration_intro_text": "The following percentages show the coverage of the most frequent words relative to total tokens and unique vocabulary:",
        "concentration_top5": "The top 5 most frequent words: {pct_total} of total, {pct_unique} of unique",
        "concentration_top10": "The top 10 most frequent words: {pct_total} of total, {pct_unique} of unique",
        "concentration_top20": "The top 20 most frequent words: {pct_total} of total, {pct_unique} of unique",
        "percent_header": "% of total",
        "of_unique": "of unique",
        "hapax_title": "Hapax Legomena (frequency = 1)",
        "comparison_title": "Comparison Scenario",
        "metric_header": "Metric",
        "current_header": "Current",
        "comparison_header": "Lemmatized",
        "length_header": "Length",
        "not_lemmatized_header": "Not lemmatized",
        "lemmatized_header": "Lemmatized",
        "stopwords_included": "included",
        "stopwords_excluded": "excluded",
        "showing_up_to_5": "showing up to 5",
        "hapax_summary_text": "Hapax legomena: {count} ({pct_unique} {of_unique}, {pct_total} {of_total}). Up to 5 examples of the longest and shortest hapax are included.",
        "hapax_longest_examples": "Longest hapax (examples)",
        "hapax_shortest_examples": "Shortest hapax (examples)",
        "word_header": "Word",
        "count_header": "Count",
        "percent_header": "%",
        "bigrams_header": "Bigrams",
        "examples_header": "Examples",
        "top5_short": "Top 5",
        "top10_short": "Top 10",
        "top20_short": "Top 20",
        "percent_label": "Percent",
        "concentration_chart_title": "Vocabulary Concentration",
        "top_5_concentration_short": "Top 5",
        "top_10_concentration_short": "Top 10",
        "top_20_concentration_short": "Top 20",
        "hapax_legomena_count": "Hapax (count)",
        "hapax_legomena_pct_unique": "Hapax (% of unique)",
        "metadata_title": "Technical Metadata",
        "metadata_scenario_header": "Processing",
        "metadata_cloud_header": "Word Cloud",
        "source_name": "Source file",
        "cloud_meta_title": "Word Cloud Settings (informational)",
        "token_stats_title": "Token counts by configuration",
        "token_stats_header": "Configuration",
        "token_stats_columns": "Total / Unique",
        "lemmatize_short": "Lemmatize",
        "stopwords_short": "Stopwords",
        "yes": "yes",
        "no": "no",
        "label": "Label",
        "language": "Language",
        "ngram": "N-gram",
        "lemmatize": "Lemmatize",
        "include_stopwords": "Include stopwords",
        "include_numbers": "Include numbers",
        "case_sensitive": "Case sensitive",
        "exclude_words": "Exclude words",
        "exclude_case_sensitive": "Exclude case sensitive",
        "regex_rule": "Regex rule",
        "regex_case_sensitive": "Regex case sensitive",
        "replace_stage": "Replace stage",
        "none": "None",
        "na": "N/A",
        "no_data": "No data available.",
        "not_available": "Not available",
        "warning": "Warning",
        "note": "Note",
        "no_examples_found": "No examples found.",
        "total_tokens": "Total tokens",
        "unique_tokens": "Unique tokens",
        "variability_ratio": "Vocabulary variability ratio (unique/total)",
        "variability_ratio_short": "Vocabulary variability ratio",
        "hapax_legomena": "Hapax legomena",
        "avg_token_length": "Average token length",
        "median_token_length": "Median token length",
        "avg_token_length_non_hapax": "Average token length (excluding hapax)",
        "median_token_length_non_hapax": "Median token length (excluding hapax)",
        "avg_token_length_hapax": "Average token length (hapax only)",
        "median_token_length_hapax": "Median token length (hapax only)",
        "avg_token_length_short": "Average token length",
        "median_token_length_short": "Median token length",
        "shortest_token": "Shortest token",
        "longest_token": "Longest token",
        "shortest_non_hapax": "Shortest token (excluding hapax)",
        "longest_non_hapax": "Longest token (excluding hapax)",
        "shortest_hapax": "Shortest token (hapax only)",
        "longest_hapax": "Longest token (hapax only)",
        "of_unique": "of unique tokens",
        "of_total": "of total",
        "top_5_concentration": "Top 5 words account for",
        "top_10_concentration": "Top 10 words account for",
        "top_20_concentration": "Top 20 words account for",
        "of_all_tokens": "of all tokens.",
        "count": "Count",
        "sample_up_to_20": "Sample (up to 20)",
        "longest_hapax_tokens": "Longest hapax token(s)",
        "comparison_summary_title": "Quick comparison vs current scenario:",
        "cloud_meta_na": "Not applicable (standalone analysis).",
        "max_words": "Max words",
        "min_word_length": "Min word length",
        "canvas_size": "Canvas size",
        "theme": "Theme",
        "colormap": "Colormap",
        "background": "Background",
        "font_color": "Font color",
        "relative_scaling": "Relative scaling",
        "prefer_horizontal": "Prefer horizontal",
        "mask": "Mask",
        "contour_width": "Contour width",
        "contour_color": "Contour color",
        "font_path": "Font path",
        "chars": "chars",
        "showing_up_to_3": "showing up to 3",
        "glossary_title": "Glossary",
        "glossary_token_term": "Token",
        "glossary_token_def": "Minimum unit of text analyzed. In this context, it generally corresponds to a word after processing (cleaning, stopwords exclusion, etc.).",
        "glossary_lemmatization_term": "Lemmatization",
        "glossary_lemmatization_def": "Process of reducing each word to its base or dictionary form (lemma). For example, 'running', 'ran', and 'run' are grouped under the lemma 'run'.",
        "glossary_stopwords_term": "Stopwords",
        "glossary_stopwords_def": "Very common functional words (such as 'the', 'a', 'of', 'and') that are usually excluded from analysis because they do not provide relevant thematic information.",
        "glossary_hapax_term": "Hapax legomena",
        "glossary_hapax_def": "Words that appear only once in the entire text. Their prevalence indicates the lexical diversity of the document.",
        "glossary_bigram_term": "Bigram",
        "glossary_bigram_def": "Pair of consecutive words in the text. For example, in 'blue sky', the bigram is ('blue', 'sky').",
        "glossary_variability_term": "Variability ratio",
        "glossary_variability_def": "Proportion between the number of distinct words (types) and the total number of words (tokens). A high ratio indicates greater lexical richness.",
    }

def _chunk_list(values: List[str], size: int) -> List[List[str]]:
    if size <= 0:
        return [values]
    return [values[i:i + size] for i in range(0, len(values), size)]


def _build_top_word_insights(
    frequencies: Dict[str, float],
    raw_text: Optional[str],
    bigram_frequencies: Optional[Dict[str, float]],
    case_sensitive: bool,
    language: str,
    top_word_count: int,
    examples_per_word: int,
    context_window: int,
    top_terms_override: Optional[List[str]],
    top_terms_note: Optional[str],
) -> Dict[str, object]:
    top_terms = top_terms_override
    if not top_terms:
        top_words = sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))[:top_word_count]
        top_terms = [word for word, _ in top_words]

    bigrams_info: Dict[str, object] = {"available": False, "reason": "N/A", "items": {}, "note": top_terms_note}
    bigrams_items = {}
    if bigram_frequencies:
        bigrams_info["available"] = True
        bigrams_info["reason"] = ""
        bigrams_items = _top_word_bigrams(top_terms, bigram_frequencies)
        bigrams_info["items"] = bigrams_items
    else:
        bigrams_info["reason"] = "Bigram data not available for this input."

    examples_info: Dict[str, object] = {"available": False, "reason": "N/A", "items": {}, "note": top_terms_note}
    if raw_text:
        examples_info["available"] = True
        examples_info["reason"] = ""
        examples_info["items"] = {}
        for term in top_terms:
            # Extract examples for the bigrams of this term
            # We want 1 example per bigram (up to 5 examples total)
            term_bigrams = bigrams_items.get(term, [])
            term_examples = []
            
            # Try to get examples for top bigrams, with fallback
            bigram_index = 0
            while len(term_examples) < examples_per_word and bigram_index < len(term_bigrams):
                bigram_item = term_bigrams[bigram_index]
                bigram = bigram_item["bigram"]
                bigram_examples = _extract_bigram_context_examples(
                    raw_text,
                    bigram,
                    case_sensitive=case_sensitive,
                    language=language,
                    max_examples=1,  # 1 example per bigram (the "purest" one)
                    context_words=1,  # 1 word before and after
                )
                if bigram_examples:
                    term_examples.extend(bigram_examples)
                # Move to next bigram (whether we found an example or not)
                bigram_index += 1
            
            examples_info["items"][term] = term_examples
    else:
        examples_info["reason"] = "Original text not available for this input."

    return {
        "top_terms": top_terms,
        "bigrams": bigrams_info,
        "examples": examples_info,
    }


def _top_word_bigrams(
    top_terms: List[str],
    bigram_frequencies: Dict[str, float],
    max_bigrams: int = 5,
) -> Dict[str, List[Dict[str, object]]]:
    results: Dict[str, List[Dict[str, object]]] = {term: [] for term in top_terms}
    if not top_terms:
        return results

    for term in top_terms:
        matches = []
        for bigram, count in bigram_frequencies.items():
            parts = bigram.split()
            if len(parts) != 2:
                continue
            if parts[0] == term or parts[1] == term:
                matches.append({"bigram": bigram, "count": count})
        matches.sort(key=lambda item: (-item["count"], item["bigram"]))
        results[term] = matches[:max_bigrams]
    return results


def _extract_context_examples(
    raw_text: str,
    term: str,
    case_sensitive: bool,
    max_examples: int,
    window: int,
) -> List[str]:
    examples: List[str] = []
    if not term:
        return examples

    term_cmp = term if case_sensitive else term.lower()
    lines = raw_text.splitlines()
    for line in lines:
        if not line.strip():
            continue
        sentences = line.split(".")
        for sentence in sentences:
            tokens = _tokenize_words(sentence)
            if not tokens:
                continue
            tokens_cmp = tokens if case_sensitive else [t.lower() for t in tokens]
            for idx, token in enumerate(tokens_cmp):
                if token != term_cmp:
                    continue
                left = max(0, idx - window)
                right = min(len(tokens) - 1, idx + window)
                context = " ".join(tokens[left:right + 1])
                if not _is_context_useful(context, term, case_sensitive):
                    continue
                examples.append(context)
                if len(examples) >= max_examples:
                    return examples
    return examples


def _extract_bigram_context_examples(
    raw_text: str,
    bigram: str,
    case_sensitive: bool,
    language: str,
    max_examples: int,
    context_words: int,
) -> List[str]:
    """
    Extract context examples that contain the specific bigram.
    The bigram was calculated after removing stopwords, so we need to:
    1. Search for word1 followed by word2 (allowing stopwords and newlines in between)
    2. No sentence delimiters (. ; ? !) allowed between word1 and word2
    3. Validate that removing stopwords from the match gives us the bigram
    4. Add context (N words before and after) from the same lines
    5. Add "(...)" when context is truncated
    6. Convert to lowercase if the entire example is uppercase
    7. Prefer "purer" matches (fewer words between word1 and word2)
    """
    if not bigram:
        return []

    bigram_parts = bigram.split()
    if len(bigram_parts) != 2:
        return []

    word1, word2 = bigram_parts
    
    # Get stopwords for this language
    try:
        stopword_set = set(stopwords.words(language))
    except Exception:
        # If language not supported, use empty set
        stopword_set = set()
    
    word1_cmp = word1 if case_sensitive else word1.lower()
    word2_cmp = word2 if case_sensitive else word2.lower()
    
    # Split text into lines
    lines = raw_text.splitlines()
    
    candidates = []  # List of (distance, context) tuples for sorting by purity
    
    # Process lines, allowing bigrams to span across consecutive lines
    for line_idx in range(len(lines)):
        # Get current line and potentially next line(s)
        current_lines = [lines[line_idx]]
        
        # Look ahead up to 2 more lines for word2 (if word1 is at the end of current line)
        for next_offset in range(1, min(3, len(lines) - line_idx)):
            current_lines.append(lines[line_idx + next_offset])
        
        # Join with newline preserved temporarily as a marker
        combined = "\n".join(current_lines)
        
        # Check if there are sentence delimiters that would invalidate the bigram
        # Split by sentence delimiters
        sentence_parts = re.split(r'[.;?!]', combined)
        
        for sentence_part in sentence_parts:
            if not sentence_part.strip():
                continue
            
            # Now we can work with this part, replacing \n with space for tokenization
            sentence_normalized = sentence_part.replace("\n", " ")
            
            tokens = _tokenize_words(sentence_normalized)
            if len(tokens) < 2:
                continue
            
            tokens_cmp = tokens if case_sensitive else [t.lower() for t in tokens]
            
            # Search for word1 followed by word2 (with max 4 words in between)
            for i in range(len(tokens_cmp)):
                if tokens_cmp[i] != word1_cmp:
                    continue
                
                # Look for word2 in the next 5 positions (0-4 words between)
                for j in range(i + 1, min(i + 6, len(tokens_cmp) + 1)):
                    if j >= len(tokens_cmp):
                        break
                    if tokens_cmp[j] != word2_cmp:
                        continue
                    
                    # Found a match! Now validate by removing stopwords
                    words_between = tokens_cmp[i:j+1]
                    # Remove stopwords from the segment
                    filtered = [w for w in words_between if w not in stopword_set]
                    
                    # Check if after removing stopwords we have our bigram
                    if len(filtered) == 2 and filtered[0] == word1_cmp and filtered[1] == word2_cmp:
                        # Valid bigram! Extract context: N words before, the match, N words after
                        start = max(0, i - context_words)
                        end = min(len(tokens), j + context_words + 1)
                        
                        # Check if context is truncated
                        prefix = "(...) " if start > 0 else ""
                        suffix = " (...)" if end < len(tokens) else ""
                        
                        context_tokens = tokens[start:end]
                        context = " ".join(context_tokens)
                        
                        # Convert to lowercase if entire context is uppercase
                        if context.isupper():
                            context = context.lower()
                        
                        context = prefix + context + suffix
                        
                        # Calculate distance (number of words between word1 and word2)
                        distance = j - i - 1
                        
                        if context:
                            candidates.append((distance, context))
                        break  # Found word2, move to next word1
    
    # Sort by distance (prefer purer matches with fewer words in between)
    # Then remove duplicates while preserving order
    candidates.sort(key=lambda x: x[0])
    seen = set()
    examples = []
    for _, context in candidates:
        if context not in seen:
            seen.add(context)
            examples.append(context)
            if len(examples) >= max_examples:
                break
    
    return examples


def _tokenize_words(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text, flags=re.UNICODE)


def _is_context_useful(context: str, term: str, case_sensitive: bool) -> bool:
    tokens = _tokenize_words(context)
    if not tokens:
        return False
    if len(tokens) < 2:
        return False
    term_cmp = term if case_sensitive else term.lower()
    tokens_cmp = tokens if case_sensitive else [t.lower() for t in tokens]
    if all(token == term_cmp for token in tokens_cmp):
        return False
    return True


def _utc_timestamp() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

