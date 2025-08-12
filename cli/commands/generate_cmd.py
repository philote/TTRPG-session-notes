"""
CLI command for AI-powered campaign document generation.
Supports both standalone operation and integration with existing workflow.
"""

import argparse
import logging
from pathlib import Path
from typing import List, Optional

from shared_utils.config import SharedConfig
from shared_utils.campaign_generator import CampaignGenerator, GenerationRequest
from shared_utils.entity_resolver import EntityType


def add_parser(subparsers):
    """Add generate command parser to the main parser."""
    
    parser = subparsers.add_parser(
        'generate',
        help='Generate AI-powered campaign documents from transcripts',
        description='Use AI to generate NPCs, locations, and other campaign documents from session transcripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all documents from a transcript
  python main.py generate transcript.txt --output-dir my_campaign --all-types
  
  # Generate only NPCs and locations
  python main.py generate transcript.txt --output-dir my_campaign --types NPC LOCATION
  
  # Use specific AI provider
  python main.py generate transcript.txt --output-dir my_campaign --provider openai
  
  # Generate from completed session output
  python main.py generate session_01/Session_*_Final_COMPLETE.txt --output-dir campaign_docs
  
  # Custom prompts
  python main.py generate transcript.txt --output-dir my_campaign --prompts NPC_template LOCATIONS_template
        """
    )
    
    # Input arguments
    parser.add_argument(
        'transcript',
        help='Path to transcript file or session directory'
    )
    
    parser.add_argument(
        '--output-dir',
        required=True,
        help='Output directory for campaign documents'
    )
    
    # Entity type selection
    entity_group = parser.add_mutually_exclusive_group()
    
    entity_group.add_argument(
        '--all-types',
        action='store_true',
        help='Generate all available document types'
    )
    
    entity_group.add_argument(
        '--types',
        nargs='+',
        choices=['NPC', 'LOCATION', 'ITEM', 'FACTION', 'ENCOUNTER', 'STORY'],
        help='Specific entity types to generate'
    )
    
    entity_group.add_argument(
        '--prompts',
        nargs='+',
        help='Specific prompt templates to use (e.g., NPC_template, LOCATIONS_template)'
    )
    
    # AI provider settings
    parser.add_argument(
        '--provider',
        choices=['anthropic', 'openai', 'google'],
        help='Preferred AI provider (default: from config)'
    )
    
    parser.add_argument(
        '--model',
        help='Specific model to use (overrides provider default)'
    )
    
    # Generation settings
    parser.add_argument(
        '--session-name',
        help='Name of the session for context'
    )
    
    parser.add_argument(
        '--merge-strategy',
        choices=['intelligent', 'append'],
        help='How to merge with existing documents (default: intelligent)'
    )
    
    parser.add_argument(
        '--max-entities',
        type=int,
        default=5,
        help='Maximum entities to generate per type (default: 5)'
    )
    
    # Advanced options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without creating files'
    )
    
    parser.add_argument(
        '--force-new',
        action='store_true',
        help='Always create new documents (ignore existing matches)'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        default=True,
        help='Create backups of existing files (default: True)'
    )
    
    parser.add_argument(
        '--no-backup',
        dest='backup',
        action='store_false',
        help='Skip creating backups of existing files'
    )


def run(args, logger: logging.Logger) -> int:
    """Execute the generate command."""
    
    try:
        # Load configuration
        config = SharedConfig(args.config if hasattr(args, 'config') else None)
        
        # Resolve transcript file
        transcript_path = Path(args.transcript)
        transcript_content = _load_transcript_content(transcript_path, logger)
        
        if not transcript_content:
            logger.error(f"Could not load transcript from: {transcript_path}")
            return 1
        
        # Setup output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure LLM settings
        llm_config = _build_llm_config(config, args)
        
        # Initialize campaign generator
        generator = CampaignGenerator(
            campaign_directory=output_dir,
            llm_config=llm_config
        )
        
        # Determine what to generate
        prompts_to_use = _determine_prompts(args, generator, logger)
        
        if not prompts_to_use:
            logger.error("No prompts to generate. Use --all-types, --types, or --prompts")
            return 1
        
        # Show generation plan
        _show_generation_plan(prompts_to_use, transcript_path, output_dir, args, logger)
        
        if args.dry_run:
            logger.info("Dry run complete - no files were created")
            return 0
        
        # Generate documents
        session_name = args.session_name or transcript_path.stem
        provider = args.provider or config.ai.get('preferred_provider', 'anthropic')
        
        logger.info(f"Starting document generation with {provider}")
        
        results = generator.generate_campaign_documents(
            transcript_content=transcript_content,
            session_name=session_name,
            prompt_types=prompts_to_use,
            preferred_provider=provider
        )
        
        # Report results
        _report_results(results, logger)
        
        # Return appropriate exit code
        successful_results = [r for r in results if r.success]
        if successful_results:
            logger.info(f"Generated {len(successful_results)} documents successfully")
            return 0
        else:
            logger.error("No documents were generated successfully")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Generation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        logger.debug("Full error details:", exc_info=True)
        return 1


def _load_transcript_content(transcript_path: Path, logger: logging.Logger) -> Optional[str]:
    """Load transcript content from file or directory."""
    
    if not transcript_path.exists():
        logger.error(f"Transcript path does not exist: {transcript_path}")
        return None
    
    if transcript_path.is_file():
        # Single file
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Loaded transcript: {transcript_path} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Failed to read transcript file: {e}")
            return None
    
    elif transcript_path.is_dir():
        # Directory - look for final transcript files
        final_files = list(transcript_path.glob("*Final_COMPLETE.txt"))
        
        if not final_files:
            # Look for any text files
            text_files = list(transcript_path.glob("*.txt"))
            if text_files:
                final_files = text_files[:1]  # Use first text file
        
        if not final_files:
            logger.error(f"No transcript files found in directory: {transcript_path}")
            return None
        
        # Use the first (most recent) final transcript
        transcript_file = final_files[0]
        try:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Loaded transcript: {transcript_file} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Failed to read transcript file: {e}")
            return None
    
    else:
        logger.error(f"Invalid transcript path: {transcript_path}")
        return None


def _build_llm_config(config: SharedConfig, args) -> dict:
    """Build LLM configuration from config and arguments."""
    
    llm_config = config.ai.copy()
    
    # Override with command line arguments
    if args.provider:
        llm_config['preferred_provider'] = args.provider
    
    if args.model:
        # Set the model for the preferred provider
        provider = llm_config['preferred_provider']
        llm_config[f'{provider}_model'] = args.model
    
    if args.merge_strategy:
        llm_config['merge_strategy'] = args.merge_strategy
    
    if args.max_entities:
        llm_config['max_entities_per_type'] = args.max_entities
    
    return llm_config


def _determine_prompts(args, generator: CampaignGenerator, logger: logging.Logger) -> List[str]:
    """Determine which prompts to use based on arguments."""
    
    available_prompts = generator.get_available_prompts()
    
    if args.prompts:
        # Specific prompts requested
        invalid_prompts = [p for p in args.prompts if p not in available_prompts]
        if invalid_prompts:
            logger.warning(f"Unknown prompts (will be skipped): {invalid_prompts}")
        
        return [p for p in args.prompts if p in available_prompts]
    
    elif args.all_types:
        # All available prompts
        return available_prompts
    
    elif args.types:
        # Map entity types to prompts
        type_to_prompt = {
            'NPC': 'NPC_template',
            'LOCATION': 'LOCATIONS_template',
            'ENCOUNTER': 'dm_encounter_template',
            'STORY': 'dm_simple_story_summarizer',
        }
        
        prompts = []
        for entity_type in args.types:
            prompt = type_to_prompt.get(entity_type)
            if prompt and prompt in available_prompts:
                prompts.append(prompt)
            else:
                logger.warning(f"No prompt available for entity type: {entity_type}")
        
        return prompts
    
    else:
        # No specific selection - return empty list
        return []


def _show_generation_plan(prompts: List[str], 
                         transcript_path: Path, 
                         output_dir: Path, 
                         args, 
                         logger: logging.Logger):
    """Show what will be generated."""
    
    logger.info("=" * 60)
    logger.info("AI Campaign Document Generation Plan")
    logger.info("=" * 60)
    logger.info(f"Transcript: {transcript_path}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info(f"Prompts to Use: {', '.join(prompts)}")
    logger.info(f"AI Provider: {args.provider or 'from config'}")
    logger.info(f"Merge Strategy: {args.merge_strategy or 'intelligent'}")
    logger.info(f"Max Entities: {args.max_entities}")
    logger.info(f"Backup Files: {args.backup}")
    logger.info("=" * 60)


def _report_results(results: List, logger: logging.Logger):
    """Report generation results to user."""
    
    logger.info("=" * 60)
    logger.info("Generation Results")
    logger.info("=" * 60)
    
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")
    
    if successful:
        logger.info("\nSuccessful generations:")
        for result in successful:
            merge_info = f" ({result.merge_type})" if result.was_merged else " (new)"
            logger.info(f"  ✓ {result.entity_name} -> {result.file_path.name}{merge_info}")
    
    if failed:
        logger.info("\nFailed generations:")
        for result in failed:
            error_info = f" - {result.error}" if result.error else ""
            logger.info(f"  ✗ {result.entity_name}{error_info}")
    
    logger.info("=" * 60)