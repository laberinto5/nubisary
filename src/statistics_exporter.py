"""Statistics export module for word frequency data."""

import json
import csv
from typing import Dict, Optional, Tuple
import os

from src.logger import setup_logger

logger = setup_logger()


def get_top_words(frequencies: Dict[str, float], n: int) -> Dict[str, float]:
    """
    Get top N words by frequency.
    
    Args:
        frequencies: Dictionary mapping words to their frequencies
        n: Number of top words to return
        
    Returns:
        Dictionary with top N words, sorted by frequency (descending)
    """
    if n is None or n <= 0:
        return frequencies
    
    # Sort by frequency (descending) and take top N
    sorted_words = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_words[:n])


def export_statistics_json(
    frequencies: Dict[str, float],
    output_file: str,
    top_n: Optional[int] = None
) -> str:
    """
    Export word frequencies to JSON file.
    
    Args:
        frequencies: Dictionary mapping words to their frequencies
        output_file: Path to output JSON file
        top_n: If specified, export only top N words (None = all words)
        
    Returns:
        Path to the created JSON file
    """
    # Get frequencies to export (all or top N)
    if top_n is not None:
        data_to_export = get_top_words(frequencies, top_n)
        logger.info(f'Exporting top {top_n} words to JSON')
    else:
        data_to_export = frequencies
        logger.info(f'Exporting all {len(frequencies)} words to JSON')
    
    # Sort by frequency (descending) for better readability
    sorted_data = dict(sorted(data_to_export.items(), key=lambda x: x[1], reverse=True))
    
    # Ensure .json extension
    if not output_file.endswith('.json'):
        output_file = output_file + '.json'
    
    # Write JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=2, ensure_ascii=False)
        logger.info(f'Statistics exported to {output_file}')
        return output_file
    except Exception as e:
        logger.error(f'Error exporting JSON statistics: {e}')
        raise


def export_statistics_csv(
    frequencies: Dict[str, float],
    output_file: str,
    top_n: Optional[int] = None
) -> str:
    """
    Export word frequencies to CSV file.
    
    Args:
        frequencies: Dictionary mapping words to their frequencies
        output_file: Path to output CSV file
        top_n: If specified, export only top N words (None = all words)
        
    Returns:
        Path to the created CSV file
    """
    # Get frequencies to export (all or top N)
    if top_n is not None:
        data_to_export = get_top_words(frequencies, top_n)
        logger.info(f'Exporting top {top_n} words to CSV')
    else:
        data_to_export = frequencies
        logger.info(f'Exporting all {len(frequencies)} words to CSV')
    
    # Sort by frequency (descending)
    sorted_data = sorted(data_to_export.items(), key=lambda x: x[1], reverse=True)
    
    # Ensure .csv extension
    if not output_file.endswith('.csv'):
        output_file = output_file + '.csv'
    
    # Write CSV file
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['word', 'frequency'])
            # Write data
            for word, frequency in sorted_data:
                writer.writerow([word, frequency])
        logger.info(f'Statistics exported to {output_file}')
        return output_file
    except Exception as e:
        logger.error(f'Error exporting CSV statistics: {e}')
        raise


def export_statistics(
    frequencies: Dict[str, float],
    base_output_file: str,
    top_n: Optional[int] = None
) -> Tuple[str, str]:
    """
    Export word frequencies to both JSON and CSV files.
    
    Args:
        frequencies: Dictionary mapping words to their frequencies
        base_output_file: Base path for output files (without extension)
        top_n: If specified, export only top N words (None = all words)
        
    Returns:
        Tuple of (json_file_path, csv_file_path)
    """
    # Ensure base name doesn't have extensions
    base_name = os.path.splitext(base_output_file)[0]
    json_file = base_name + '_vocabulary.json'
    csv_file = base_name + '_vocabulary.csv'
    
    # Export both formats
    json_path = export_statistics_json(frequencies, json_file, top_n=top_n)
    csv_path = export_statistics_csv(frequencies, csv_file, top_n=top_n)
    
    return (json_path, csv_path)

