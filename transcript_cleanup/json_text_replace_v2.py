#!/usr/bin/env python3
"""
TTRPG JSON Text Replace Script - Phase 1 Improved Version

This is the modernized version of json_text_replace.py that uses:
- Shared configuration system
- Professional logging instead of colorama prints  
- Shared text processing utilities
- Better error handling and file operations

Usage:
    python json_text_replace_v2.py [--input INPUT_FILE] [--replacements REPLACEMENTS_FILE] [--output OUTPUT_FILE]
"""

import argparse
import sys
from pathlib import Path

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Phase 1 improvements
from shared_utils.config import get_shared_config
from shared_utils.logging_config import setup_logging, get_logger
from shared_utils.text_processing import (
    load_replacements_file,
    apply_text_replacements,
    log_replacement_statistics
)
from shared_utils.file_operations import get_file_stats

def process_text_file(input_file: Path, replacements_file: Path, output_file: Path, logger):
    """Process a text file with replacements."""
    
    # Validate input files
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return False
    
    if not replacements_file.exists():
        logger.error(f"Replacements file not found: {replacements_file}")
        return False
    
    # Get input file stats
    input_stats = get_file_stats(input_file)
    logger.info(f"Input file: {input_file.name} ({input_stats['size_mb']} MB)")
    
    # Load replacements
    logger.info(f"Loading replacements from: {replacements_file.name}")
    replacements = load_replacements_file(str(replacements_file))
    
    if not replacements:
        logger.warning("No replacements loaded - nothing to do")
        return False
    
    # Read input text
    logger.info("Reading input file...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_text = f.read()
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return False
    
    logger.info(f"Loaded {len(original_text):,} characters from input file")
    
    # Apply replacements
    logger.info("Applying text replacements...")
    processed_text, replacement_counts = apply_text_replacements(
        original_text,
        replacements,
        case_insensitive=True,
        log_replacements=False  # We'll log manually for better control
    )
    
    # Log replacement statistics
    log_replacement_statistics(replacement_counts, logger)
    
    # Calculate total replacements
    total_replacements = sum(
        sum(variants.values()) for variants in replacement_counts.values()
    )
    
    if total_replacements == 0:
        logger.info("No replacements were made - text unchanged")
    else:
        logger.info(f"Total replacements made: {total_replacements:,}")
    
    # Save processed text
    logger.info(f"Saving processed text to: {output_file.name}")
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_text)
    except Exception as e:
        logger.error(f"Error writing output file: {e}")
        return False
    
    # Get output file stats
    output_stats = get_file_stats(output_file)
    logger.info(f"Output file: {output_file.name} ({output_stats['size_mb']} MB)")
    
    # Calculate size change
    size_change = output_stats['size_bytes'] - input_stats['size_bytes']
    if size_change > 0:
        logger.info(f"File size increased by {size_change:,} bytes")
    elif size_change < 0:
        logger.info(f"File size decreased by {abs(size_change):,} bytes")
    else:
        logger.info("File size unchanged")
    
    return True

def main():
    """Main processing function."""
    parser = argparse.ArgumentParser(description="TTRPG JSON Text Replace - Phase 1 Improved")
    parser.add_argument('--input', type=Path, help='Input text file to process')
    parser.add_argument('--replacements', type=Path, help='JSON file with replacement mappings')
    parser.add_argument('--output', type=Path, help='Output file for processed text')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(level=args.log_level, use_colors=True)
    logger.info("TTRPG JSON Text Replace v2.0 (Phase 1 Improved)")
    logger.info("=" * 60)
    
    try:
        # Load configuration for defaults
        config = get_shared_config(config_file=args.config)
        base_path = Path(config.cleanup['base_path'])
        
        # Determine file paths
        if args.input:
            input_file = args.input
        else:
            # Look for common transcript files
            possible_files = [
                base_path / "COS ALL SESSIONS.txt",
                base_path / "transcript.txt",
                base_path / "complete_transcript.txt"
            ]
            
            input_file = None
            for possible_file in possible_files:
                if possible_file.exists():
                    input_file = possible_file
                    logger.info(f"Auto-detected input file: {input_file.name}")
                    break
            
            if input_file is None:
                logger.error("No input file specified and no common transcript files found")
                logger.info("Please specify --input or place a transcript file in the base path")
                return False
        
        if args.replacements:
            replacements_file = args.replacements
        else:
            # Use default from config
            replacements_file = base_path / config.cleanup['replacements_file']
            logger.info(f"Using default replacements file: {replacements_file.name}")
        
        if args.output:
            output_file = args.output
        else:
            # Generate output filename
            output_file = input_file.with_stem(f"{input_file.stem}_UPDATED")
            logger.info(f"Auto-generated output file: {output_file.name}")
        
        # Process the file
        success = process_text_file(input_file, replacements_file, output_file, logger)
        
        if success:
            logger.info("Text replacement completed successfully!")
            logger.info("=" * 60)
            logger.info("Files processed:")
            logger.info(f"  Input: {input_file}")
            logger.info(f"  Replacements: {replacements_file}")
            logger.info(f"  Output: {output_file}")
        else:
            logger.error("Text replacement failed!")
        
        return success
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        logger.debug("Full error details:", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)