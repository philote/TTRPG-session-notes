"""
Process command for full pipeline automation.
Chains transcription, cleanup, and text replacement operations.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from cli.commands import transcribe_cmd, cleanup_cmd, replace_cmd


def add_parser(subparsers):
    """Add process command parser."""
    parser = subparsers.add_parser(
        'process',
        help='Full pipeline: audio → transcripts → cleaned text',
        description='Automated workflow that chains transcription, cleanup, and text replacement'
    )
    
    parser.add_argument(
        'input_path',
        help='Audio file, directory, or zip file to process'
    )
    
    parser.add_argument(
        '--output-dir',
        required=True,
        help='Output directory for all processing stages'
    )
    
    # Pipeline control
    parser.add_argument(
        '--all-steps',
        action='store_true',
        help='Run all pipeline steps (transcribe → cleanup → replace)'
    )
    
    parser.add_argument(
        '--transcribe-only',
        action='store_true',
        help='Only perform transcription step'
    )
    
    parser.add_argument(
        '--cleanup-only',
        action='store_true',
        help='Only perform cleanup step (assumes TSV files exist)'
    )
    
    # Transcription options
    parser.add_argument(
        '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'turbo'],
        default='turbo',
        help='Whisper model for transcription (default: turbo)'
    )
    
    parser.add_argument(
        '--no-fp16',
        action='store_true',
        help='Disable fp16 precision for transcription'
    )
    
    # Session info
    parser.add_argument(
        '--session-name',
        help='Name for the session'
    )
    
    parser.add_argument(
        '--session-part',
        help='Part/episode identifier for the session'
    )
    
    # Configuration
    parser.add_argument(
        '--config-file',
        help='Configuration file to use'
    )


def run(args, logger):
    """Execute the process command with full pipeline automation."""
    logger.info("TTRPG Process - Full Pipeline Automation")
    logger.info("=" * 60)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine which steps to run
    if args.transcribe_only:
        steps = ['transcribe']
    elif args.cleanup_only:
        steps = ['cleanup']
    elif args.all_steps:
        steps = ['transcribe', 'cleanup', 'replace']
    else:
        # Default: transcribe + cleanup
        steps = ['transcribe', 'cleanup']
    
    logger.info(f"Pipeline steps: {' → '.join(steps)}")
    logger.info(f"Output directory: {output_dir}")
    
    # Step 1: Transcription
    if 'transcribe' in steps:
        logger.info("\n" + "="*30 + " STEP 1: TRANSCRIPTION " + "="*30)
        
        # Create transcribe args
        transcribe_args = type('Args', (), {
            'input_path': args.input_path,
            'output_dir': str(output_dir),
            'model': args.model,
            'no_fp16': args.no_fp16,
            'language': 'en',
            'config_file': args.config_file
        })()
        
        result = transcribe_cmd.run(transcribe_args, logger)
        if result != 0:
            logger.error("Transcription failed, stopping pipeline")
            return result
            
        logger.info("✓ Transcription completed successfully")
    
    # Step 2: Cleanup
    if 'cleanup' in steps:
        logger.info("\n" + "="*30 + " STEP 2: CLEANUP " + "="*30)
        
        # For cleanup-only, use input_path as source but output to output_dir
        if args.cleanup_only:
            # Copy files to output directory first
            import shutil
            input_path = Path(args.input_path)
            
            # Copy TSV and JSON files to output directory
            for file in input_path.glob("*.tsv"):
                shutil.copy2(file, output_dir)
            for file in input_path.glob("*.json"):
                shutil.copy2(file, output_dir)
                
            cleanup_base_path = str(output_dir)
        else:
            cleanup_base_path = str(output_dir)
        
        # Create cleanup args
        cleanup_args = type('Args', (), {
            'base_path': cleanup_base_path,
            'session_name': args.session_name,
            'part': args.session_part,
            'config_file': args.config_file
        })()
        
        result = cleanup_cmd.run(cleanup_args, logger)
        if result != 0:
            logger.error("Cleanup failed, stopping pipeline")
            return result
            
        logger.info("✓ Cleanup completed successfully")
    
    # Step 3: Text Replacement (optional)
    if 'replace' in steps:
        logger.info("\n" + "="*30 + " STEP 3: TEXT REPLACEMENT " + "="*30)
        
        # Find the complete transcript file
        complete_files = list(output_dir.glob("*_Final_COMPLETE.txt"))
        if not complete_files:
            logger.warning("No complete transcript file found, skipping text replacement")
        else:
            input_file = complete_files[0]
            
            # Create replace args (construct full path to replacements file)
            replacements_file = output_dir / 'merge_replacements.json'
            replace_args = type('Args', (), {
                'input': str(input_file),
                'output': None,  # Will auto-generate
                'replacements': str(replacements_file)
            })()
            
            result = replace_cmd.run(replace_args, logger)
            if result != 0:
                logger.warning("Text replacement had issues but continuing")
            else:
                logger.info("✓ Text replacement completed successfully")
    
    # Pipeline summary
    logger.info("\n" + "="*30 + " PIPELINE COMPLETE " + "="*30)
    logger.info(f"All files saved to: {output_dir}")
    
    # List output files
    output_files = [
        f for f in output_dir.iterdir() 
        if f.is_file() and f.suffix in ['.tsv', '.csv', '.txt', '.json']
    ]
    
    if output_files:
        logger.info("Output files created:")
        for file in sorted(output_files):
            logger.info(f"  • {file.name}")
    
    return 0