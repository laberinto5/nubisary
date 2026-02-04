"""Unit tests for report_generator module."""

from src.report_generator import (
    build_report_data,
    render_report_txt,
    ScenarioMetadata,
    write_report_pdf,
)
import tempfile
import os


def test_build_report_data_basic_stats():
    frequencies = {"apple": 10.0, "banana": 2.0, "pear": 1.0}
    scenario = ScenarioMetadata(
        label="Current scenario",
        language="english",
        ngram="unigram",
        lemmatize=False,
        include_stopwords=False,
        include_numbers=False,
        case_sensitive=False,
    )

    report_data = build_report_data(
        frequencies=frequencies,
        scenario=scenario,
        comparison_frequencies=None,
        comparison_unavailable_reason="Comparison not available for JSON inputs."
    )

    analysis = report_data["analysis"]
    assert analysis["total_tokens"] == 13.0
    assert analysis["unique_tokens"] == 3
    assert round(analysis["token_ratio"], 4) == round(3 / 13, 4)

    length_stats = analysis["length_stats"]
    assert round(length_stats["avg_length"], 3) == round(66 / 13, 3)
    assert length_stats["median_length"] == 5.0
    assert length_stats["shortest_token"] == "pear"
    assert length_stats["longest_token"] == "banana"

    top_words = analysis["top_words"]
    assert top_words[0]["word"] == "apple"
    assert top_words[0]["frequency"] == 10.0

    concentration = analysis["concentration"]
    # concentration[5] is now a dict with percent_of_total and percent_of_unique
    assert round(concentration[5]["percent_of_total"], 2) == round(100.0, 2)

    hapax = analysis["hapax"]
    assert hapax["count"] == 1
    assert hapax["sample"] == ["pear"]

    hapax_stats = analysis["hapax_stats"]
    assert hapax_stats["hapax_longest"]["tokens"] == ["pear"]
    assert hapax_stats["non_hapax_longest"]["tokens"] == ["banana"]

    assert analysis["length_stats_non_hapax"]["avg_length"] is not None
    assert analysis["length_stats_hapax"]["avg_length"] is not None


def test_render_report_txt_includes_warning():
    frequencies = {"alpha": 3.0, "beta": 1.0}
    scenario = ScenarioMetadata(
        label="Current scenario",
        language="english",
        ngram="unigram",
        lemmatize=False,
        include_stopwords=False,
        include_numbers=False,
        case_sensitive=False,
    )

    report_data = build_report_data(
        frequencies=frequencies,
        scenario=scenario,
        comparison_frequencies=None,
        comparison_unavailable_reason="Comparison not available for JSON inputs.",
        generated_at="2026-01-25T00:00:00Z",
    )

    report_text = render_report_txt(report_data)
    assert "Nubisary Report" in report_text
    assert "Summary" in report_text
    assert "Comparison Scenario" in report_text
    assert "Warning: Comparison not available for JSON inputs." in report_text
    assert "Vocabulary Concentration" in report_text
    assert "Top 5 words account for" in report_text
    assert "Vocabulary variability ratio" in report_text
    assert "Longest hapax token" in report_text
    assert "Hapax legomena:" in report_text
    # "Metric" only appears in comparison table when comparison is available
    # When comparison is not available, only the warning is shown
    assert "Top 5 Words: Common Bigrams" in report_text
    assert "Top 5 Words: Context Examples" in report_text
    assert "Including hapax" in report_text
    assert "Excluding hapax" in report_text
    assert "Hapax only" in report_text

    report_text_es = render_report_txt(report_data, language="es")
    assert "Informe Nubisary" in report_text_es
    assert "Escenario de comparación" in report_text_es
    assert "Top 5 palabras: bigramas frecuentes" in report_text_es
    assert "Resumen" in report_text_es


def test_write_report_pdf_creates_file():
    frequencies = {"alpha": 3.0, "beta": 1.0}
    scenario = ScenarioMetadata(
        label="Current scenario",
        language="english",
        ngram="unigram",
        lemmatize=False,
        include_stopwords=False,
        include_numbers=False,
        case_sensitive=False,
    )
    report_data = build_report_data(
        frequencies=frequencies,
        scenario=scenario,
        comparison_frequencies=None,
        comparison_unavailable_reason="Comparison not available for JSON inputs.",
        generated_at="2026-01-25T00:00:00Z",
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, "report.pdf")
        write_report_pdf(report_data, output_path, language="en")
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

