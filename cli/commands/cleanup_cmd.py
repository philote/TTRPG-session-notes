"""
Cleanup command for processing transcript files.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from transcript_cleanup.transcript_cleanup_v2 import main as cleanup_main


def add_parser(subparsers):
    """Add cleanup command parser."""
    parser = subparsers.add_parser(
        'cleanup',
        help='Clean and organize transcript files',
        description='Process TSV transcripts into organized, readable session transcripts'
    )
    
    parser.add_argument(
        '--base-path',
        required=True,
        help='Base path containing TSV files to process'
    )
    
    parser.add_argument(
        '--session-name',
        help='Override session name from config'
    )
    
    parser.add_argument(
        '--part',
        help='Override session part from config'
    )
    
    parser.add_argument(
        '--config-file',
        help='Path to configuration file'
    )
    
    # Cleanup step controls
    parser.add_argument(
        '--skip-duplicates',
        action='store_true',
        help='Skip removing duplicate short text entries'
    )
    
    parser.add_argument(
        '--skip-merge',
        action='store_true', 
        help='Skip merging adjacent segments'
    )
    
    parser.add_argument(
        '--skip-short',
        action='store_true',
        help='Skip removing short text entries'
    )
    
    parser.add_argument(
        '--skip-gibberish',
        action='store_true',
        help='Skip removing silence/gibberish patterns'
    )


def run(args, logger):
    """Execute the cleanup command."""
    logger.info("TTRPG Cleanup - Processing transcript files")
    logger.info("=" * 50)
    
    # Convert CLI args to format expected by cleanup_main
    cleanup_args = [
        '--base-path', args.base_path
    ]
    
    if args.session_name:
        cleanup_args.extend(['--session-name', args.session_name])
        
    if args.part:
        cleanup_args.extend(['--part', args.part])
        
    if args.config_file:
        cleanup_args.extend(['--config', args.config_file])
    
    # Save original sys.argv and replace
    original_argv = sys.argv
    try:
        sys.argv = ['transcript_cleanup_v2.py'] + cleanup_args
        result = cleanup_main()
        # cleanup_main returns True for success, convert to 0 for CLI
        return 0 if result else 1
    except SystemExit as e:
        return e.code if e.code is not None else 0
    finally:
        sys.argv = original_argv