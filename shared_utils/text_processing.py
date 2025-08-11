"""
Common text processing utilities for TTRPG Session Notes automation.
Contains functions for text replacement, cleaning, and processing.
"""

import json
import re
import pandas as pd
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import logging

from .logging_config import get_logger

def load_replacements_file(file_path: str, base_dir: Optional[str] = None) -> Dict[str, List[str]]:
    """Load replacements from JSON file.
    
    Args:
        file_path: Path to the JSON replacements file
        base_dir: Base directory to resolve relative paths
    
    Returns:
        Dictionary mapping correct terms to lists of variants
    """
    logger = get_logger()
    
    # Convert to Path object for easier handling
    replacement_path = Path(file_path)
    
    # If relative path and base_dir provided, resolve from base_dir
    if not replacement_path.is_absolute() and base_dir:
        replacement_path = Path(base_dir) / replacement_path
    
    if not replacement_path.exists():
        logger.info(f"Replacements file not found: {replacement_path}")
        logger.info("Creating default replacements file with examples...")
        
        # Create default replacements file
        default_replacements = {
            "_comment": "Add your text corrections here. Format: 'CorrectName': ['mishear1', 'mishear2']",
            "_examples": {
                "Gandalf": ["gandolf", "gandulf", "gand off"],
                "PlayerName": ["playername", "player name"],
                "CharacterName": ["charactername", "character name"]
            }
        }
        
        try:
            # Ensure parent directory exists
            replacement_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write default file
            with open(replacement_path, 'w', encoding='utf-8') as f:
                json.dump(default_replacements, f, indent=2)
            
            logger.info(f"Created default replacements file: {replacement_path}")
            logger.info("Edit this file to add your own text corrections")
            
            # Return empty dict for now since examples are prefixed with _
            return {}
            
        except Exception as e:
            logger.warning(f"Could not create default replacements file: {e}")
            return {}
    
    try:
        with open(replacement_path, 'r', encoding='utf-8') as file:
            replacements = json.load(file)
        logger.info(f"Loaded {len(replacements)} replacement mappings from {replacement_path}")
        return replacements
    except Exception as e:
        logger.error(f"Error loading replacements file {replacement_path}: {e}")
        return {}

def apply_text_replacements(text: str, 
                          replacement_map: Dict[str, List[str]], 
                          case_insensitive: bool = True,
                          log_replacements: bool = False) -> Tuple[str, Dict[str, Dict[str, int]]]:
    """Apply text replacements using a mapping dictionary.
    
    Args:
        text: Text to process
        replacement_map: Dict mapping correct terms to lists of variants
        case_insensitive: Whether to perform case-insensitive matching
        log_replacements: Whether to log replacement statistics
    
    Returns:
        Tuple of (processed_text, replacement_counts)
    """
    logger = get_logger()
    replacement_counts = defaultdict(lambda: defaultdict(int))
    
    for correct_term, variants in replacement_map.items():
        for variant in variants:
            # Count occurrences before replacement
            flags = re.IGNORECASE if case_insensitive else 0
            matches = re.findall(re.escape(variant), text, flags=flags)
            replacement_counts[correct_term][variant] += len(matches)
            
            # Perform the replacement
            text = re.sub(re.escape(variant), correct_term, text, flags=flags)
    
    if log_replacements:
        log_replacement_statistics(replacement_counts, logger)
    
    return text, dict(replacement_counts)

def log_replacement_statistics(replacement_counts: Dict[str, Dict[str, int]], 
                             logger: Optional[logging.Logger] = None):
    """Log statistics about text replacements."""
    if logger is None:
        logger = get_logger()
    
    # Sort by total replacements per key
    sorted_counts = sorted(replacement_counts.items(), 
                          key=lambda x: sum(x[1].values()), 
                          reverse=True)
    
    total_all_replacements = 0
    for correct_term, variants in sorted_counts:
        total_replacements = sum(variants.values())
        total_all_replacements += total_replacements
        
        if total_replacements > 0:
            logger.info(f"'{correct_term}': {total_replacements} total replacements")
            for variant, count in variants.items():
                if count > 0:
                    logger.debug(f"  '{variant}': {count} occurrences")
    
    logger.info(f"Total text replacements applied: {total_all_replacements}")

def remove_duplicate_short_text(df: pd.DataFrame, 
                               max_length: int = 4,
                               text_column: str = 'text') -> Tuple[pd.DataFrame, int]:
    """Remove duplicate short text entries from a DataFrame.
    
    Args:
        df: DataFrame containing text data
        max_length: Maximum length for text to be considered "short"
        text_column: Name of the text column
    
    Returns:
        Tuple of (cleaned_df, removed_count)
    """
    logger = get_logger()
    
    # Find short texts and duplicates
    short_texts = df[df[text_column].str.len() <= max_length]
    duplicate_texts = short_texts[short_texts.duplicated(subset=text_column, keep=False)]
    
    # Log duplicate information
    if not duplicate_texts.empty:
        duplicate_count = duplicate_texts[text_column].value_counts()
        logger.info(f"Found duplicate short text entries ({max_length} chars or less):")
        for text, count in duplicate_count.items():
            logger.debug(f"  '{text}': {count} occurrences")
    
    # Remove duplicates
    original_length = len(df)
    df_cleaned = df[~((df[text_column].str.len() <= max_length) & 
                     df.duplicated(subset=text_column, keep='first'))]
    removed_count = original_length - len(df_cleaned)
    
    if removed_count > 0:
        logger.info(f"Removed {removed_count} duplicate short text entries")
    
    return df_cleaned, removed_count

def merge_adjacent_segments(df: pd.DataFrame,
                          threshold: float = 0.01,
                          text_column: str = 'text',
                          start_column: str = 'start',
                          end_column: str = 'end') -> Tuple[pd.DataFrame, int]:
    """Merge adjacent segments based on timing threshold.
    
    Args:
        df: DataFrame with timing and text data
        threshold: Time threshold for merging adjacent segments
        text_column: Name of the text column
        start_column: Name of the start time column
        end_column: Name of the end time column
    
    Returns:
        Tuple of (merged_df, merge_count)
    """
    logger = get_logger()
    
    df = df.copy().reset_index(drop=True)
    merged_count = 0
    i = 0
    
    while i < len(df) - 1:
        # Check if current segment's end is close to next segment's start
        if abs(df.iloc[i][end_column] - df.iloc[i + 1][start_column]) <= threshold:
            # Merge the segments
            end_val = df.iloc[i + 1][end_column]
            combined_text = str(df.iloc[i][text_column]) + " " + str(df.iloc[i + 1][text_column])
            
            df.loc[i, end_column] = end_val
            df.loc[i, text_column] = combined_text
            df = df.drop(df.index[i + 1]).reset_index(drop=True)
            merged_count += 1
        else:
            i += 1
    
    if merged_count > 0:
        logger.info(f"Merged {merged_count} adjacent segments")
    
    return df, merged_count

def remove_short_text(df: pd.DataFrame,
                     min_length: int = 1,
                     text_column: str = 'text') -> Tuple[pd.DataFrame, int]:
    """Remove entries with text shorter than minimum length.
    
    Args:
        df: DataFrame containing text data
        min_length: Minimum text length to keep
        text_column: Name of the text column
    
    Returns:
        Tuple of (cleaned_df, removed_count)
    """
    logger = get_logger()
    
    # Count short text entries
    short_text_mask = df[text_column].apply(
        lambda x: len(x) if isinstance(x, str) else 0
    ) <= min_length
    short_text_count = short_text_mask.sum()
    
    # Remove short text entries
    df_cleaned = df[~short_text_mask]
    
    if short_text_count > 0:
        logger.info(f"Removed {short_text_count} entries with text ≤ {min_length} characters")
    
    return df_cleaned, short_text_count

def remove_silence_gibberish(df: pd.DataFrame,
                           patterns: List[str],
                           text_column: str = 'text') -> Tuple[pd.DataFrame, int]:
    """Remove entries that match silence gibberish patterns.
    
    Args:
        df: DataFrame containing text data
        patterns: List of patterns to remove
        text_column: Name of the text column
    
    Returns:
        Tuple of (cleaned_df, removed_count)
    """
    logger = get_logger()
    
    if not patterns:
        return df, 0
    
    original_length = len(df)
    
    # Create a mask for rows that match gibberish patterns
    gibberish_mask = df[text_column].isin(patterns)
    df_cleaned = df[~gibberish_mask]
    
    removed_count = original_length - len(df_cleaned)
    
    if removed_count > 0:
        logger.info(f"Removed {removed_count} silence gibberish entries")
    
    return df_cleaned, removed_count

def split_text_with_overlap(text: str,
                          max_length: int = 50000,
                          overlap: int = 3000) -> List[str]:
    """Split long text into chunks with overlap.
    
    Args:
        text: Text to split
        max_length: Maximum length per chunk
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    logger = get_logger()
    
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position
        end = min(start + max_length, len(text))
        
        # If this isn't the last chunk, try to break at a word boundary
        if end < len(text):
            # Look for a good break point (sentence end, then word boundary)
            sentence_breaks = ['. ', '! ', '? ']
            best_break = -1
            
            # Look for sentence breaks in the last part of the chunk
            search_start = max(start + max_length - 1000, start)
            for i in range(end - 1, search_start - 1, -1):
                for break_pattern in sentence_breaks:
                    if text[i:i+len(break_pattern)] == break_pattern:
                        best_break = i + len(break_pattern)
                        break
                if best_break != -1:
                    break
            
            # If no sentence break, look for word boundary
            if best_break == -1:
                search_start = max(start + max_length - 200, start)
                for i in range(end - 1, search_start - 1, -1):
                    if text[i] == ' ':
                        best_break = i + 1
                        break
            
            if best_break != -1:
                end = best_break
        
        # Extract chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position (with overlap)
        if end >= len(text):
            break
        start = max(start + max_length - overlap, end - overlap)
    
    logger.info(f"Split text into {len(chunks)} chunks (max_length={max_length}, overlap={overlap})")
    return chunks

def clean_transcript_dataframe(df: pd.DataFrame,
                             config_dict: Dict[str, Any]) -> pd.DataFrame:
    """Apply full cleaning pipeline to a transcript DataFrame.
    
    Args:
        df: DataFrame with transcript data
        config_dict: Configuration dictionary with cleaning parameters
    
    Returns:
        Cleaned DataFrame
    """
    # Try to use the new configurable pipeline first
    try:
        # Import here to avoid circular dependencies
        import sys
        from pathlib import Path
        
        # Add transcript_cleanup to path
        transcript_cleanup_path = Path(__file__).parent.parent / 'transcript_cleanup'
        if str(transcript_cleanup_path) not in sys.path:
            sys.path.insert(0, str(transcript_cleanup_path))
        
        from cleanup_steps import run_cleanup_pipeline
        return run_cleanup_pipeline(df, config_dict)
        
    except ImportError:
        # Fallback to the original pipeline if cleanup_steps is not available
        logger = get_logger()
        logger.warning("Using legacy cleanup pipeline - cleanup_steps.py not found")
        return _legacy_clean_transcript_dataframe(df, config_dict)


def _legacy_clean_transcript_dataframe(df: pd.DataFrame,
                                     config_dict: Dict[str, Any]) -> pd.DataFrame:
    """Legacy cleaning pipeline for backward compatibility."""
    logger = get_logger()
    logger.info(f"Starting legacy transcript cleaning pipeline with {len(df)} rows")
    
    # Step 1: Remove duplicate short text
    if config_dict.get('short_duplicate_text_length', 0) > 0:
        df, removed = remove_duplicate_short_text(
            df, 
            max_length=config_dict['short_duplicate_text_length']
        )
    
    # Step 2: Merge adjacent segments
    if config_dict.get('merge_threshold', 0) > 0:
        df, merged = merge_adjacent_segments(
            df, 
            threshold=config_dict['merge_threshold']
        )
    
    # Step 3: Remove short text
    if config_dict.get('short_text_length', 0) > 0:
        df, removed = remove_short_text(
            df, 
            min_length=config_dict['short_text_length']
        )
    
    # Step 4: Remove final duplicates
    original_len = len(df)
    df = df.drop_duplicates(subset='text', keep='first')
    final_removed = original_len - len(df)
    if final_removed > 0:
        logger.info(f"Removed {final_removed} final duplicate entries")
    
    # Step 5: Remove silence gibberish
    if (config_dict.get('remove_silence_gibberish', False) and 
        config_dict.get('silence_gibberish_patterns')):
        df, removed = remove_silence_gibberish(
            df, 
            patterns=config_dict['silence_gibberish_patterns']
        )
    
    logger.info(f"Legacy transcript cleaning complete: {len(df)} rows remaining")
    return df