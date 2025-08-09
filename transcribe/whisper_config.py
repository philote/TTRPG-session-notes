# whisper_config.py
"""
Configuration file for Whisper transcription settings
Based on requirements from Project Planning.md
"""

import os
import json
from pathlib import Path

# Default Whisper settings as specified in Next Steps
DEFAULT_WHISPER_CONFIG = {
    "model": "turbo",
    "condition_on_previous_text": False,
    "compression_ratio_threshold": 1.8,
    "output_format": "tsv",
    "fp16": True,
    "language": "en",
    "task": "transcribe",
    "verbose": True,
}

# Additional Whisper options that can be configured
EXTENDED_WHISPER_CONFIG = {
    "temperature": 0.0,
    "no_speech_threshold": 0.6,
    "logprob_threshold": -1.0,
    "word_timestamps": False,
    "prepend_punctuations": "\"'\"([{-",
    "append_punctuations": "\"'.,:!?)]}",
    "initial_prompt": None,
}

# Output configuration
OUTPUT_CONFIG = {
    "output_dir": "transcripts",
    "temp_dir": "temp_extraction",
    "create_subdirs": True,
    "preserve_input_structure": False,
}

# Progress and logging configuration
PROGRESS_CONFIG = {
    "show_progress": True,
    "show_whisper_output": True,
    "colored_output": True,
    "log_errors": True,
    "summary_report": True,
}

class WhisperConfig:
    """Configuration management for Whisper transcription"""
    
    def __init__(self, config_file=None):
        self.config = DEFAULT_WHISPER_CONFIG.copy()
        self.output_config = OUTPUT_CONFIG.copy()
        self.progress_config = PROGRESS_CONFIG.copy()
        
        # Load from config file if provided
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            
            # Update configs with file values
            if 'whisper' in file_config:
                self.config.update(file_config['whisper'])
            if 'output' in file_config:
                self.output_config.update(file_config['output'])
            if 'progress' in file_config:
                self.progress_config.update(file_config['progress'])
                
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def update_from_args(self, args):
        """Update configuration from command line arguments"""
        # Update Whisper settings
        if hasattr(args, 'model') and args.model:
            self.config['model'] = args.model
        if hasattr(args, 'language') and args.language:
            self.config['language'] = args.language
        if hasattr(args, 'compression_ratio_threshold') and args.compression_ratio_threshold is not None:
            self.config['compression_ratio_threshold'] = args.compression_ratio_threshold
        if hasattr(args, 'condition_on_previous_text') and args.condition_on_previous_text is not None:
            self.config['condition_on_previous_text'] = args.condition_on_previous_text
        if hasattr(args, 'fp16') and args.fp16 is not None:
            self.config['fp16'] = args.fp16
        if hasattr(args, 'temperature') and args.temperature is not None:
            self.config['temperature'] = args.temperature
        
        # Update output settings
        if hasattr(args, 'output_dir') and args.output_dir:
            self.output_config['output_dir'] = args.output_dir
        if hasattr(args, 'verbose') and args.verbose is not None:
            self.progress_config['show_whisper_output'] = args.verbose
    
    def get_whisper_args(self):
        """Get arguments dictionary for Whisper transcribe function"""
        return self.config.copy()
    
    def get_output_config(self):
        """Get output configuration"""
        return self.output_config.copy()
    
    def get_progress_config(self):
        """Get progress configuration"""
        return self.progress_config.copy()
    
    def save_to_file(self, config_file):
        """Save current configuration to JSON file"""
        config_dict = {
            'whisper': self.config,
            'output': self.output_config,
            'progress': self.progress_config
        }
        
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def create_default_config_file(self, config_file):
        """Create a default configuration file for user customization"""
        default_config = {
            'whisper': {
                'model': 'turbo',
                'condition_on_previous_text': False,
                'compression_ratio_threshold': 1.8,
                'fp16': True,
                'language': 'en',
                'temperature': 0.0,
                'no_speech_threshold': 0.6,
                'initial_prompt': None
            },
            'output': {
                'output_dir': 'transcripts',
                'create_subdirs': True,
                'preserve_input_structure': False
            },
            'progress': {
                'show_progress': True,
                'show_whisper_output': True,
                'colored_output': True,
                'summary_report': True
            }
        }
        
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        return config_file

def get_available_models():
    """Return list of available Whisper models"""
    return ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3", "turbo"]

def validate_model(model_name):
    """Validate if model name is available"""
    return model_name in get_available_models()