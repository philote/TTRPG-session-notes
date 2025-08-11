"""
Replace command for applying text replacements to transcripts.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from transcript_cleanup.json_text_replace_v2 import main as replace_main


def add_parser(subparsers):
    """Add replace command parser."""
    parser = subparsers.add_parser(
        'replace',
        help='Apply text replacements to transcript files',
        description='Apply name/term corrections using JSON replacement mappings'
    )
    
    parser.add_argument(
        '--input',
        help='Input text file to process (auto-detects if not specified)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path (defaults to input + _corrected suffix)'
    )
    
    parser.add_argument(
        '--replacements',
        default='merge_replacements.json',
        help='JSON file with replacement mappings (default: merge_replacements.json)'
    )
    
    parser.add_argument(
        '--base-path',
        help='Base directory for file operations'
    )


def run(args, logger):
    """Execute the replace command."""
    logger.info("TTRPG Replace - Applying text corrections")
    logger.info("=" * 50)
    
    # Convert CLI args to format expected by replace_main
    replace_args = []
    
    if args.input:
        replace_args.extend(['--input', args.input])
        
    if args.output:
        replace_args.extend(['--output', args.output])
        
    if args.replacements:
        replace_args.extend(['--replacements', args.replacements])
        
    # Note: base_path is handled by passing full paths to files
    
    # Save original sys.argv and replace
    original_argv = sys.argv
    try:
        sys.argv = ['json_text_replace_v2.py'] + replace_args
        return replace_main()
    except SystemExit as e:
        return e.code if e.code is not None else 0
    finally:
        sys.argv = original_argv