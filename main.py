#!/usr/bin/env python3
"""
Main CLI entry point for TTRPG Session Notes automation.
Provides a unified command-line interface with subcommands.
"""

import argparse
import sys
from pathlib import Path

from shared_utils.logging_config import setup_logging, get_logger
from shared_utils.config import load_config
from cli.commands import transcribe_cmd, cleanup_cmd, replace_cmd, process_cmd

# Command registry for dynamic dispatch
COMMANDS = {
    'transcribe': transcribe_cmd,
    'cleanup': cleanup_cmd,
    'replace': replace_cmd,
    'process': process_cmd,
}


def create_main_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog='ttrpg',
        description='TTRPG Session Notes automation toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ttrpg transcribe audio.flac --output-dir transcripts
  ttrpg cleanup --base-path transcripts --session-name my_session
  ttrpg replace --input transcript.txt --replacements corrections.json
  ttrpg process audio_files/ --output-dir session_01 --all-steps
        """
    )
    
    # Global arguments
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='TTRPG Session Notes v2.1 (Phase 2)'
    )
    
    # Create subparsers
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Add subcommands dynamically
    for command_module in COMMANDS.values():
        command_module.add_parser(subparsers)
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_main_parser()
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(level=args.log_level, use_colors=True)
    
    # Load configuration if provided
    config = None
    if args.config:
        try:
            config = load_config(args.config)
            logger.debug(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.warning(f"Failed to load config {args.config}: {e}")
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        # Execute the appropriate command dynamically
        command_module = COMMANDS.get(args.command)
        if command_module:
            return command_module.run(args, logger)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 2
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130  # Standard UNIX exit code for SIGINT
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 2
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return 77  # Standard UNIX exit code for permission denied
    except Exception as e:
        logger.error(f"Command failed: {e}")
        logger.debug("Full error details:", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())