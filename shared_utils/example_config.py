"""
Unified configuration system for TTRPG Session Notes automation.
Supports environment variables, and command-line overrides.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

class SharedConfig:
    """Unified configuration management with environment variable support."""
    
    # Default settings for whisper transcription
    DEFAULT_WHISPER_CONFIG = {
        "model": "turbo",
        "condition_on_previous_text": False,
        "compression_ratio_threshold": 1.8,
        "output_format": "tsv",
        "fp16": True,
        "language": "en",
        "task": "transcribe",
        "verbose": True,
        "temperature": 0.0,
        "no_speech_threshold": 0.6,
        "logprob_threshold": -1.0,
        "word_timestamps": False,
        "initial_prompt": None,
    }
    
    # Default settings for transcript cleanup
    DEFAULT_CLEANUP_CONFIG = {
        "session_name": "session",
        "part": "01",
        "base_path": None,  # Will be computed from session_name/part
        "short_duplicate_text_length": 4,
        "merge_threshold": 0.01,
        "short_text_length": 1,
        "remove_silence_gibberish": True,
        "max_length": 50000,
        "overlap": 3000,
        "processed_csv_suffix": "_processed.csv",
        
        # Phase 2: Cleanup step enable/disable flags
        "enable_remove_duplicates": True,
        "enable_merge_segments": True, 
        "enable_remove_short": True,
        "enable_remove_final_duplicates": True,
        "enable_remove_gibberish": True,
    }
    
    # Default name mappings (these are discord usernames mapped to the player and character names)
    DEFAULT_NAME_MAPPINGS = {
        '<Discord ID>': 'Player: <Player Name> (Character: <Character Name>)',
    }
    
    # Default text replacements - based on actual transcription errors from TTRPG sessions
    # Dictionary iteration order: Python 3.7+ dictionaries maintain insertion order, so replacements are applied in the order they appear in DEFAULT_TEXT_REPLACEMENTS
    # Per-term processing: For each correct term (like "wizard"), all its variants are processed sequentially:
    # - "wizard": ["wizzard", "wisard", "wizerd"]
    # - First replaces all "wizzard" → "wizard"
    # - Then replaces all "wisard" → "wizard"
    # - Then replaces all "wizerd" → "wizard"
    # Best Practices:
    # 1. Put specific terms first (longer, more specific replacements)
    # 2. Avoid overlapping replacements
    # 3. Use consistent spacing (be careful with leading/trailing spaces)
    # 4. Test order-dependent replacements to ensure expected behavior
    DEFAULT_TEXT_REPLACEMENTS = {
        # Campaign-specific terms (from actual transcripts)
        "Dwarven Ale": ["dwarfen ale", "dwarvin ale"],
        " orc": [" Ork", " Orp"],
        " harbinger": [" Arbinger"],
        "Bells": ["Belz"],
        "Blackwharf": ["Black Wharf", "Black dwarf"],
        "barrel roll": ["barrell roll"],
        
        # Common RPG actions and terms (actual errors found)
        "armor": ["armour", "armors"],
        "wizardry": ["wizzardry", "wisardry"],
        "magical": ["magickal", "majical"],
        
        # Generic D&D terms often misheard by Whisper
        "wizard": ["wizzard", "wisard", "wizerd"],
        "rogue": ["rouge", "roag", "rog"],
        "paladin": ["palladin", "paliden", "paladeen"],
        "barbarian": ["barberian", "barbarien"],
        "cleric": ["clerik", "clerric", "claric"],
        "ranger": ["rainger", "rangur", "rainjer"],
        "dungeon": ["dunjon", "dunjun", "dungen"],
        "dragon": ["dragun", "dragan", "draggin"],
        
        # Common RPG skills and actions
        "initiative": ["inishiative", "inititive", "iniative"],
        "perception": ["perseption", "percepshun", "persepton"],
        "investigation": ["investigashun", "investagation", "invstigation"],
        "persuasion": ["persuation", "persuashun", "persasion"],
        "deception": ["deseption", "decepshun", "desepton"],
        "intimidation": ["intimidashun", "intimadation", "intimidaton"],
        
        # Common gameplay mechanics
        "advantage": ["advantige", "advantege", "advant edge"],
        "disadvantage": ["disadvantige", "disadvantege", "disadvt edge"],
        "critical": ["criical", "crittical", "critcal"],
        "damage": ["damige", "damege", "damaj"],
        "armor class": ["armer class", "armor klass", "armore class"]
    }
    
    # Default silence gibberish patterns
    DEFAULT_SILENCE_PATTERNS = [
        "you", "You", "Thank you", "Thank You", "thank you.", "Thank you.", 
        "Hmm", "hmm", "Uh", "uh", "Oh", "oh", "Ah", "ah", "Um", "um",
        "Mm", "mm", "Mm-hmm", "mm-hmm", "Uh-huh", "uh-huh", "Yeah", "yeah",
        "Yep", "yep", "Yes", "yes", "No", "no", "Okay", "okay", "OK", "ok",
        "Alright", "alright", "All right", "all right", "Right", "right",
        "Well", "well", "So", "so", "I mean", "i mean", "Like", "like"
    ]
    
    # Output configuration
    DEFAULT_OUTPUT_CONFIG = {
        "output_dir": "transcripts",
        "temp_dir": "temp_extraction",
        "create_subdirs": True,
        "preserve_input_structure": False,
    }
    
    # Progress and logging configuration
    DEFAULT_PROGRESS_CONFIG = {
        "show_progress": True,
        "show_whisper_output": True,
        "colored_output": True,
        "log_errors": True,
        "summary_report": True,
        "log_level": "INFO",
    }
    
    # AI Campaign Generation configuration
    DEFAULT_AI_CONFIG = {
        # LLM Provider settings
        "preferred_provider": "anthropic",
        "fallback_providers": ["anthropic", "openai", "google"],
        "openai_model": "gpt-4o",
        "anthropic_model": "claude-3-5-sonnet-20241022", 
        "google_model": "gemini-1.5-pro",
        
        # Generation settings
        "max_tokens": 4000,
        "temperature": 0.1,
        "timeout": 120,
        
        # Entity resolution settings
        "fuzzy_threshold": 85.0,
        "semantic_threshold": 0.7,
        "case_sensitive": False,
        "max_entities_per_type": 5,
        
        # Document management
        "merge_strategy": "intelligent",
        "create_backups": True,
        "campaign_directory": "campaign_docs",
        
        # Prompt settings
        "available_prompts": ["NPC_template", "LOCATIONS_template", "dm_simple_story_summarizer"],
        "default_prompts": ["NPC_template", "LOCATIONS_template"],
    }
    
    # Environment variable mappings
    ENV_MAPPINGS = {
        # Whisper settings
        "TTRPG_WHISPER_MODEL": ("whisper", "model"),
        "TTRPG_WHISPER_LANGUAGE": ("whisper", "language"),
        "TTRPG_WHISPER_FP16": ("whisper", "fp16", bool),
        "TTRPG_WHISPER_VERBOSE": ("whisper", "verbose", bool),
        
        # Cleanup settings
        "TTRPG_SESSION_NAME": ("cleanup", "session_name"),
        "TTRPG_SESSION_PART": ("cleanup", "part"),
        "TTRPG_BASE_PATH": ("cleanup", "base_path"),
        "TTRPG_MAX_LENGTH": ("cleanup", "max_length", int),
        "TTRPG_OVERLAP": ("cleanup", "overlap", int),
        
        # Output settings
        "TTRPG_OUTPUT_DIR": ("output", "output_dir"),
        "TTRPG_TEMP_DIR": ("output", "temp_dir"),
        
        # Progress settings
        "TTRPG_LOG_LEVEL": ("progress", "log_level"),
        "TTRPG_COLORED_OUTPUT": ("progress", "colored_output", bool),
        
        # AI Campaign Generation settings
        "TTRPG_AI_PROVIDER": ("ai", "preferred_provider"),
        "TTRPG_OPENAI_MODEL": ("ai", "openai_model"),
        "TTRPG_ANTHROPIC_MODEL": ("ai", "anthropic_model"),
        "TTRPG_GOOGLE_MODEL": ("ai", "google_model"),
        "TTRPG_AI_MAX_TOKENS": ("ai", "max_tokens", int),
        "TTRPG_AI_TEMPERATURE": ("ai", "temperature", float),
        "TTRPG_AI_FUZZY_THRESHOLD": ("ai", "fuzzy_threshold", float),
        "TTRPG_AI_MERGE_STRATEGY": ("ai", "merge_strategy"),
        "TTRPG_CAMPAIGN_DIR": ("ai", "campaign_directory"),
    }
    
    def __init__(self, config_file: Optional[str] = None, project_root: Optional[str] = None):
        """Initialize shared configuration.
        
        Args:
            config_file: Path to JSON config file
            project_root: Root directory of the project (for relative paths)
        """
        self.project_root = project_root or self._find_project_root()
        
        # Initialize configuration dictionaries
        self.whisper = self.DEFAULT_WHISPER_CONFIG.copy()
        self.cleanup = self.DEFAULT_CLEANUP_CONFIG.copy()
        self.output = self.DEFAULT_OUTPUT_CONFIG.copy()
        self.progress = self.DEFAULT_PROGRESS_CONFIG.copy()
        self.ai = self.DEFAULT_AI_CONFIG.copy()
        self.name_mappings = getattr(self, 'DEFAULT_NAME_MAPPINGS', {}).copy()
        self.silence_patterns = getattr(self, 'DEFAULT_SILENCE_PATTERNS', []).copy()
        self.text_replacements = getattr(self, 'DEFAULT_TEXT_REPLACEMENTS', {}).copy()
        
        # Set computed defaults
        self._set_computed_defaults()
        
        # Load from environment variables
        self._load_from_environment()
        
        # Load from config file if provided
        if config_file:
            self.load_from_file(config_file)
    
    def _find_project_root(self) -> str:
        """Find the project root directory."""
        current = Path.cwd()
        
        # Look for common project indicators
        indicators = ['CLAUDE.md', 'requirements.txt', '.git']
        
        while current != current.parent:
            if any((current / indicator).exists() for indicator in indicators):
                return str(current)
            current = current.parent
        
        # Fall back to current directory
        return str(Path.cwd())
    
    def _set_computed_defaults(self):
        """Set computed default values."""
        if not self.cleanup["base_path"]:
            self.cleanup["base_path"] = os.path.join(
                self.project_root,
                self.cleanup["session_name"],
                self.cleanup["part"]
            )
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        for env_var, mapping in self.ENV_MAPPINGS.items():
            value = os.environ.get(env_var)
            if value is not None:
                section, key = mapping[0], mapping[1]
                type_converter = mapping[2] if len(mapping) > 2 else str
                
                # Convert value to appropriate type
                if type_converter == bool:
                    converted_value = value.lower() in ('true', '1', 'yes', 'on')
                elif type_converter == int:
                    try:
                        converted_value = int(value)
                    except ValueError:
                        logging.warning(f"Invalid integer value for {env_var}: {value}")
                        continue
                else:
                    converted_value = value
                
                # Set the value in the appropriate section
                config_section = getattr(self, section)
                config_section[key] = converted_value
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON file."""
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = Path(self.project_root) / config_path
        
        if not config_path.exists():
            logging.warning(f"Config file not found: {config_path}")
            return
        
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            
            # Update sections with file values
            for section_name in ['whisper', 'cleanup', 'output', 'progress']:
                if section_name in file_config:
                    section = getattr(self, section_name)
                    section.update(file_config[section_name])
            
            # Handle special sections
            if 'name_mappings' in file_config:
                self.name_mappings.update(file_config['name_mappings'])
            
            if 'silence_patterns' in file_config:
                self.silence_patterns = file_config['silence_patterns']
                
            if 'text_replacements' in file_config:
                self.text_replacements.update(file_config['text_replacements'])
            
            # Recompute dependent values
            self._set_computed_defaults()
            
            logging.info(f"Loaded configuration from {config_path}")
            
        except Exception as e:
            logging.error(f"Error loading config file {config_path}: {e}")
    
    def update_from_args(self, args):
        """Update configuration from command line arguments."""
        # Whisper settings
        for attr in ['model', 'language', 'compression_ratio_threshold', 
                     'condition_on_previous_text', 'fp16', 'temperature', 'verbose']:
            if hasattr(args, attr) and getattr(args, attr) is not None:
                self.whisper[attr] = getattr(args, attr)
        
        # Cleanup settings
        for attr in ['session_name', 'part', 'base_path', 'max_length', 'overlap']:
            if hasattr(args, attr) and getattr(args, attr) is not None:
                self.cleanup[attr] = getattr(args, attr)
        
        # Output settings
        for attr in ['output_dir', 'temp_dir']:
            if hasattr(args, attr) and getattr(args, attr) is not None:
                self.output[attr] = getattr(args, attr)
        
        # Progress settings
        if hasattr(args, 'verbose') and args.verbose is not None:
            self.progress['show_whisper_output'] = args.verbose
        
        # Recompute dependent values after updates
        self._set_computed_defaults()
    
    def get_base_path(self) -> str:
        """Get the computed base path for session files."""
        return self.cleanup["base_path"]
    
    def get_combined_csv_filename(self) -> str:
        """Get the combined CSV filename."""
        return f'{self.cleanup["session_name"]}_{self.cleanup["part"]}_processed.csv'
    
    def get_merged_csv_filename(self) -> str:
        """Get the merged CSV filename."""
        return f'{self.cleanup["session_name"]}_{self.cleanup["part"]}_merged.csv'
    
    def get_final_txt_filename(self) -> str:
        """Get the final text filename."""
        return f'{self.cleanup["session_name"]}_{self.cleanup["part"]}_final.txt'
    
    def save_to_file(self, config_file: str):
        """Save current configuration to JSON file."""
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = Path(self.project_root) / config_path
        
        config_dict = {
            'whisper': self.whisper,
            'cleanup': self.cleanup,
            'output': self.output,
            'progress': self.progress,
            'name_mappings': self.name_mappings,
            'silence_patterns': self.silence_patterns,
            'text_replacements': self.text_replacements
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logging.info(f"Configuration saved to {config_path}")
    
    def create_default_config_file(self, config_file: str) -> str:
        """Create a default configuration file for user customization."""
        self.save_to_file(config_file)
        return str(config_file)

def get_shared_config(config_file: Optional[str] = None, **kwargs) -> SharedConfig:
    """Get a shared configuration instance.
    
    This is the main entry point for getting configuration.
    """
    return SharedConfig(config_file=config_file, **kwargs)