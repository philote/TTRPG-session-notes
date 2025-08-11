#!/usr/bin/env python3
"""
TTRPG Transcript Cleanup Script - Phase 1 Improved Version

This is the modernized version of transcript_cleanup.py that uses:
- Shared configuration system with environment variable support
- Professional logging instead of colorama prints
- Shared utilities for text processing and file operations
- Better error handling and progress tracking

Usage:
    python transcript_cleanup_v2.py [--config CONFIG_FILE] [--log-level LEVEL]
"""

import argparse
import sys
import os
from pathlib import Path

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Phase 1 improvements
from shared_utils.config import get_shared_config
from shared_utils.logging_config import setup_logging, get_logger
from shared_utils.text_processing import (
    load_replacements_file,
    apply_text_replacements,
    clean_transcript_dataframe,
    split_text_with_overlap
)
from shared_utils.file_operations import (
    find_files_by_pattern,
    load_tsv_file,
    save_dataframe,
    ensure_directory_exists,
    get_file_stats
)

def process_tsv_file(file_path: Path, config, logger):
    """Process a single TSV file using shared utilities."""
    logger.info(f"Processing file: {file_path.name}")
    
    # Load TSV file
    df = load_tsv_file(file_path)
    
    # Apply full cleaning pipeline
    config_dict = {
        'short_duplicate_text_length': config.cleanup['short_duplicate_text_length'],
        'merge_threshold': config.cleanup['merge_threshold'],
        'short_text_length': config.cleanup['short_text_length'],
        'remove_silence_gibberish': config.cleanup['remove_silence_gibberish'],
        'silence_gibberish_patterns': config.silence_patterns
    }
    
    cleaned_df = clean_transcript_dataframe(df, config_dict)
    
    # Determine speaker name from filename
    speaker_name = 'Unknown'
    for key, name in config.name_mappings.items():
        if key in str(file_path):
            speaker_name = name
            break
    
    # Add speaker name column
    cleaned_df['name'] = speaker_name
    
    # Save processed file
    output_path = file_path.with_suffix('').with_suffix('.processed.csv')
    save_dataframe(cleaned_df, output_path, format_type='csv')
    
    logger.info(f"Processed {file_path.name}: {len(cleaned_df)} rows remaining")
    return cleaned_df, output_path

def merge_speaker_texts(dataframes, config, logger):
    """Merge all speaker texts chronologically."""
    logger.info("Merging speaker texts chronologically...")
    
    if not dataframes:
        logger.error("No dataframes to merge")
        return None
    
    # Combine all dataframes
    import pandas as pd
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Sort by start time
    combined_df = combined_df.sort_values('start').reset_index(drop=True)
    
    # Group consecutive rows by same speaker
    merged_rows = []
    current_group = None
    
    for _, row in combined_df.iterrows():
        if current_group is None or current_group['name'] != row['name']:
            # New speaker group
            if current_group is not None:
                merged_rows.append(current_group)
            
            current_group = {
                'start': row['start'],
                'end': row['end'],
                'text': row['text'],
                'name': row['name']
            }
        else:
            # Same speaker - merge texts
            current_group['text'] += ' ' + row['text']
            current_group['end'] = row['end']  # Update end time
    
    # Add the last group
    if current_group is not None:
        merged_rows.append(current_group)
    
    merged_df = pd.DataFrame(merged_rows)
    logger.info(f"Merged into {len(merged_df)} speaker segments")
    
    return merged_df

def apply_text_replacements_to_dataframe(df, config, logger):
    """Apply text replacements to the dataframe."""
    logger.info("Applying text replacements...")
    
    # Load replacements file
    replacements_path = Path(config.cleanup['base_path']) / config.cleanup['replacements_file']
    replacements = load_replacements_file(str(replacements_path))
    
    if not replacements:
        logger.info("No text replacements configured - transcript will not be modified")
        logger.info(f"To add corrections, edit: {replacements_path.name}")
        return df
    
    # Apply replacements to text column
    total_replacements = 0
    for idx, row in df.iterrows():
        original_text = row['text']
        replaced_text, counts = apply_text_replacements(
            original_text, 
            replacements, 
            case_insensitive=True,
            log_replacements=False
        )
        df.at[idx, 'text'] = replaced_text
        
        # Count total replacements
        for correct_term, variants in counts.items():
            total_replacements += sum(variants.values())
    
    if total_replacements > 0:
        logger.info(f"Applied {total_replacements} text replacements")
    else:
        logger.info("No text replacements were needed")
    
    return df

def create_final_transcripts(df, config, logger):
    """Create final transcript files with splitting."""
    logger.info("Creating final transcript files...")
    
    base_path = Path(config.cleanup['base_path'])
    ensure_directory_exists(base_path)
    
    # Create concatenated text
    transcript_lines = []
    for _, row in df.iterrows():
        transcript_lines.append(f"{row['name']}: {row['text']}")
    
    full_transcript = '\n'.join(transcript_lines)
    
    # Split text into manageable parts
    max_length = config.cleanup['max_length']
    overlap = config.cleanup['overlap']
    
    parts = split_text_with_overlap(full_transcript, max_length, overlap)
    
    # Save individual parts
    part_files = []
    session_part = config.cleanup['part'] or 'complete'
    
    if len(parts) > 1:
        for i, part in enumerate(parts, 1):
            part_filename = f"Session_{session_part}_Final_part_{i}.txt"
            part_path = base_path / part_filename
            
            with open(part_path, 'w', encoding='utf-8') as f:
                f.write(part)
            
            part_files.append(part_path)
            logger.info(f"Saved part {i}: {part_filename} ({len(part)} characters)")
    
    # Save complete transcript
    complete_filename = f"Session_{session_part}_Final_COMPLETE.txt"
    complete_path = base_path / complete_filename
    
    with open(complete_path, 'w', encoding='utf-8') as f:
        f.write(full_transcript)
    
    logger.info(f"Saved complete transcript: {complete_filename} ({len(full_transcript)} characters)")
    
    return complete_path, part_files

def main():
    """Main processing function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="TTRPG Transcript Cleanup - Phase 1 Improved")
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--base-path', help='Override base path for session files')
    parser.add_argument('--session-name', help='Override session name')
    parser.add_argument('--part', help='Override session part')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(level=args.log_level, use_colors=True)
    logger.info("TTRPG Transcript Cleanup v2.0 (Phase 1 Improved)")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        config = get_shared_config(config_file=args.config)
        
        # Apply command line overrides
        if args.base_path:
            config.cleanup['base_path'] = args.base_path
        if args.session_name:
            config.cleanup['session_name'] = args.session_name
        if args.part:
            config.cleanup['part'] = args.part
        
        # Recompute derived values after overrides
        config._set_computed_defaults()
        
        logger.info(f"Configuration loaded:")
        logger.info(f"  Base path: {config.cleanup['base_path']}")
        logger.info(f"  Session: {config.cleanup['session_name']}")
        logger.info(f"  Part: {config.cleanup['part']}")
        
        # Check if base path exists
        base_path = Path(config.cleanup['base_path'])
        if not base_path.exists():
            logger.error(f"Base path does not exist: {base_path}")
            logger.info("Please check your configuration or create the directory")
            return False
        
        # Find TSV files
        logger.info("Searching for TSV files...")
        tsv_files = find_files_by_pattern(base_path, "*.tsv", recursive=False)
        
        if not tsv_files:
            logger.error(f"No TSV files found in: {base_path}")
            logger.info("Please ensure Whisper transcription files (.tsv) are in the base path")
            return False
        
        logger.info(f"Found {len(tsv_files)} TSV files to process")
        
        # Process each TSV file
        processed_dataframes = []
        processed_files = []
        
        for tsv_file in tsv_files:
            try:
                processed_df, output_path = process_tsv_file(tsv_file, config, logger)
                processed_dataframes.append(processed_df)
                processed_files.append(output_path)
            except Exception as e:
                logger.error(f"Error processing {tsv_file.name}: {e}")
                continue
        
        if not processed_dataframes:
            logger.error("No files were successfully processed")
            return False
        
        # Save combined processed data
        logger.info("Saving combined processed data...")
        import pandas as pd
        combined_df = pd.concat(processed_dataframes, ignore_index=True)
        combined_df = combined_df.sort_values('start').reset_index(drop=True)
        
        combined_csv_path = base_path / config.get_combined_csv_filename()
        save_dataframe(combined_df, combined_csv_path, format_type='csv')
        logger.info(f"Combined data saved: {combined_csv_path.name}")
        
        # Merge speaker texts
        merged_df = merge_speaker_texts(processed_dataframes, config, logger)
        if merged_df is None:
            return False
        
        # Save merged data
        merged_csv_path = base_path / config.get_merged_csv_filename()
        save_dataframe(merged_df, merged_csv_path, format_type='csv')
        logger.info(f"Merged data saved: {merged_csv_path.name}")
        
        # Apply text replacements
        replaced_df = apply_text_replacements_to_dataframe(merged_df, config, logger)
        
        # Create final transcript files
        complete_path, part_files = create_final_transcripts(replaced_df, config, logger)
        
        # Summary
        logger.info("Processing completed successfully!")
        logger.info("=" * 60)
        logger.info("Output files created:")
        logger.info(f"  Combined CSV: {combined_csv_path.name}")
        logger.info(f"  Merged CSV: {merged_csv_path.name}")
        logger.info(f"  Complete transcript: {complete_path.name}")
        
        if part_files:
            logger.info(f"  Split parts: {len(part_files)} files")
        
        # File statistics
        stats = get_file_stats(complete_path)
        logger.info(f"Final transcript size: {stats['size_mb']} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        logger.debug("Full error details:", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)