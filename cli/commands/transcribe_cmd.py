"""
Transcribe command for converting audio files to text transcripts.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from transcribe.whisper_transcribe import main as transcribe_main


def add_parser(subparsers):
    """Add transcribe command parser."""
    parser = subparsers.add_parser(
        'transcribe',
        help='Transcribe audio files using Whisper',
        description='Convert audio files to TSV transcripts using OpenAI Whisper'
    )
    
    parser.add_argument(
        'input_path',
        help='Audio file, directory, or zip file to transcribe'
    )
    
    parser.add_argument(
        '--output-dir',
        default='transcripts',
        help='Output directory for TSV files (default: transcripts)'
    )
    
    parser.add_argument(
        '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'turbo'],
        default='turbo',
        help='Whisper model to use (default: turbo)'
    )
    
    parser.add_argument(
        '--no-fp16',
        action='store_true',
        help='Disable fp16 precision (use for CPU-only processing)'
    )
    
    parser.add_argument(
        '--language',
        default='en',
        help='Audio language (default: en)'
    )
    
    parser.add_argument(
        '--config-file',
        help='Path to Whisper configuration file'
    )


def run(args, logger):
    """Execute the transcribe command."""
    logger.info("TTRPG Transcribe - Converting audio to text")
    logger.info("=" * 50)
    
    # Convert CLI args to format expected by transcribe_main
    transcribe_args = [
        args.input_path,
        '--output-dir', args.output_dir,
        '--model', args.model,
        '--language', args.language
    ]
    
    if args.no_fp16:
        transcribe_args.append('--no-fp16')
        
    if args.config_file:
        transcribe_args.extend(['--config', args.config_file])
    
    # Save original sys.argv and replace
    original_argv = sys.argv
    try:
        sys.argv = ['whisper_transcribe.py'] + transcribe_args  # Include all args including input_path
        return transcribe_main()
    except SystemExit as e:
        return e.code
    finally:
        sys.argv = original_argv