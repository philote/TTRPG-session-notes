#!/usr/bin/env python3
"""
Whisper Transcription Script for TTRPG Session Notes
Automatically transcribes FLAC audio files using OpenAI Whisper

Supports:
- Zip files containing FLAC files
- Directories containing FLAC files  
- Individual FLAC files or lists of files
- Configuration files and command-line overrides
- Progress tracking and comprehensive error reporting

Usage:
    python whisper_transcribe.py <input> [options]
    python whisper_transcribe.py audio_files.zip --output-dir transcripts
    python whisper_transcribe.py /path/to/flac/files/ --model large-v2
    python whisper_transcribe.py file1.flac file2.flac --config my_config.json
"""

import argparse
import os
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json

# Import colorama for colored output (already used in existing code)
from colorama import Fore, Style, init

# Import whisper_config
from .whisper_config import WhisperConfig, get_available_models, validate_model

# Initialize colorama
init()

class TranscriptionError(Exception):
    """Custom exception for transcription errors"""
    pass

class WhisperTranscriber:
    """Main class for handling Whisper transcription workflow"""
    
    def __init__(self, config: WhisperConfig):
        self.config = config
        self.whisper = None
        self.successful_files = []
        self.failed_files = []
        self.temp_dirs = []
        
        # Try to import and initialize Whisper
        self._initialize_whisper()
    
    def _initialize_whisper(self):
        """Initialize Whisper model with error handling"""
        try:
            import whisper
            self.whisper = whisper
            
            # Test if we can load the model
            model_name = self.config.config['model']
            if self.config.progress_config['colored_output']:
                print(f"{Fore.CYAN}Loading Whisper model '{model_name}'...{Style.RESET_ALL}")
            else:
                print(f"Loading Whisper model '{model_name}'...")
                
            self.model = whisper.load_model(model_name)
            
            if self.config.progress_config['colored_output']:
                print(f"{Fore.GREEN}Model loaded successfully!{Style.RESET_ALL}")
            else:
                print("Model loaded successfully!")
                
        except ImportError:
            raise TranscriptionError(
                "OpenAI Whisper is not installed. Please install it with: pip install openai-whisper"
            )
        except Exception as e:
            raise TranscriptionError(f"Failed to load Whisper model: {e}")
    
    def detect_input_type(self, input_path: str) -> str:
        """Detect whether input is a zip file, directory, or file"""
        if not os.path.exists(input_path):
            raise TranscriptionError(f"Input path does not exist: {input_path}")
        
        if os.path.isfile(input_path):
            if input_path.lower().endswith('.zip'):
                return 'zip'
            elif input_path.lower().endswith(('.flac', '.wav', '.mp3', '.m4a')):
                return 'file'
            else:
                raise TranscriptionError(f"Unsupported file type: {input_path}")
        elif os.path.isdir(input_path):
            return 'directory'
        else:
            raise TranscriptionError(f"Unknown input type: {input_path}")
    
    def extract_zip(self, zip_path: str) -> str:
        """Extract zip file to temporary directory and return path"""
        temp_dir = tempfile.mkdtemp(prefix="whisper_transcribe_")
        self.temp_dirs.append(temp_dir)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            if self.config.progress_config['show_progress']:
                if self.config.progress_config['colored_output']:
                    print(f"{Fore.YELLOW}Extracted {zip_path} to {temp_dir}{Style.RESET_ALL}")
                else:
                    print(f"Extracted {zip_path} to {temp_dir}")
            
            return temp_dir
            
        except Exception as e:
            raise TranscriptionError(f"Failed to extract zip file {zip_path}: {e}")
    
    def find_audio_files(self, directory: str) -> List[str]:
        """Find all supported audio files in directory"""
        audio_extensions = {'.flac', '.wav', '.mp3', '.m4a', '.ogg', '.opus'}
        audio_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in audio_extensions:
                    audio_files.append(os.path.join(root, file))
        
        return sorted(audio_files)
    
    def prepare_file_list(self, inputs: List[str]) -> List[str]:
        """Process all inputs and return list of audio files to transcribe"""
        all_files = []
        
        for input_item in inputs:
            input_type = self.detect_input_type(input_item)
            
            if input_type == 'zip':
                extracted_dir = self.extract_zip(input_item)
                zip_files = self.find_audio_files(extracted_dir)
                all_files.extend(zip_files)
                
            elif input_type == 'directory':
                dir_files = self.find_audio_files(input_item)
                all_files.extend(dir_files)
                
            elif input_type == 'file':
                all_files.append(input_item)
        
        if not all_files:
            raise TranscriptionError("No supported audio files found in input(s)")
        
        return all_files
    
    def create_output_path(self, audio_file: str, output_dir: str) -> str:
        """Create output path for transcription file"""
        audio_path = Path(audio_file)
        base_name = audio_path.stem
        output_file = f"{base_name}.tsv"
        return os.path.join(output_dir, output_file)
    
    def transcribe_file(self, audio_file: str, output_file: str) -> bool:
        """Transcribe a single audio file"""
        try:
            # Get Whisper configuration
            whisper_args = self.config.get_whisper_args()
            
            if self.config.progress_config['show_progress']:
                if self.config.progress_config['colored_output']:
                    print(f"{Fore.BLUE}Transcribing: {os.path.basename(audio_file)}{Style.RESET_ALL}")
                else:
                    print(f"Transcribing: {os.path.basename(audio_file)}")
            
            # Remove model, output_format, and other args that aren't transcribe() parameters
            transcribe_args = {k: v for k, v in whisper_args.items() 
                             if k not in ['model', 'output_format', 'verbose']}
            
            # Perform transcription
            result = self.model.transcribe(
                audio_file,
                verbose=self.config.progress_config['show_whisper_output'],
                **transcribe_args
            )
            
            # Write TSV output
            self._write_tsv_output(result, output_file)
            
            self.successful_files.append((audio_file, output_file))
            return True
            
        except Exception as e:
            error_msg = f"Failed to transcribe {audio_file}: {e}"
            if self.config.progress_config['colored_output']:
                print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            else:
                print(error_msg)
            
            self.failed_files.append((audio_file, str(e)))
            return False
    
    def _write_tsv_output(self, result: dict, output_file: str):
        """Write Whisper result to TSV file in format compatible with transcript_cleanup.py"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            # Write TSV header
            f.write("start\tend\ttext\n")
            
            # Write segments - convert to milliseconds as integers to match existing format
            for segment in result['segments']:
                start = int(segment['start'] * 1000)  # Convert seconds to milliseconds
                end = int(segment['end'] * 1000)      # Convert seconds to milliseconds
                text = segment['text'].strip()
                f.write(f"{start}\t{end}\t{text}\n")
    
    def run_transcription(self, inputs: List[str], output_dir: str):
        """Main transcription workflow"""
        # Prepare file list
        if self.config.progress_config['show_progress']:
            if self.config.progress_config['colored_output']:
                print(f"{Fore.CYAN}Preparing file list...{Style.RESET_ALL}")
            else:
                print("Preparing file list...")
        
        try:
            audio_files = self.prepare_file_list(inputs)
        except TranscriptionError as e:
            if self.config.progress_config['colored_output']:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            else:
                print(f"Error: {e}")
            return False
        
        total_files = len(audio_files)
        
        if self.config.progress_config['show_progress']:
            if self.config.progress_config['colored_output']:
                print(f"{Fore.CYAN}Found {total_files} audio files to transcribe{Style.RESET_ALL}")
            else:
                print(f"Found {total_files} audio files to transcribe")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Transcribe each file
        for i, audio_file in enumerate(audio_files, 1):
            if self.config.progress_config['show_progress']:
                progress_msg = f"[{i}/{total_files}] Processing: {os.path.basename(audio_file)}"
                if self.config.progress_config['colored_output']:
                    print(f"{Fore.MAGENTA}{progress_msg}{Style.RESET_ALL}")
                else:
                    print(progress_msg)
            
            output_file = self.create_output_path(audio_file, output_dir)
            self.transcribe_file(audio_file, output_file)
        
        # Generate summary report
        if self.config.progress_config['summary_report']:
            self._print_summary_report()
        
        # Cleanup temporary directories
        self._cleanup()
        
        return len(self.failed_files) == 0
    
    def _print_summary_report(self):
        """Print summary of transcription results"""
        total = len(self.successful_files) + len(self.failed_files)
        successful = len(self.successful_files)
        failed = len(self.failed_files)
        
        if self.config.progress_config['colored_output']:
            print(f"\\n{Fore.CYAN}=== Transcription Summary ==={Style.RESET_ALL}")
            print(f"{Fore.GREEN}Successful: {successful}/{total}{Style.RESET_ALL}")
            if failed > 0:
                print(f"{Fore.RED}Failed: {failed}/{total}{Style.RESET_ALL}")
        else:
            print("\\n=== Transcription Summary ===")
            print(f"Successful: {successful}/{total}")
            if failed > 0:
                print(f"Failed: {failed}/{total}")
        
        if self.successful_files:
            print("\\nSuccessful transcriptions:")
            for audio_file, output_file in self.successful_files:
                print(f"  ✓ {os.path.basename(audio_file)} -> {os.path.basename(output_file)}")
        
        if self.failed_files:
            print("\\nFailed transcriptions:")
            for audio_file, error in self.failed_files:
                print(f"  ✗ {os.path.basename(audio_file)}: {error}")
    
    def _cleanup(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Could not clean up temporary directory {temp_dir}: {e}")

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using OpenAI Whisper",
        epilog="Examples:\\n"
               "  %(prog)s audio_files.zip\\n"
               "  %(prog)s /path/to/audio/files/\\n"
               "  %(prog)s file1.flac file2.flac --model large-v2\\n"
               "  %(prog)s session.zip --output-dir transcripts --config custom.json",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Input arguments
    parser.add_argument(
        'inputs',
        nargs='+',
        help='Input files or directories (zip files, directories, or individual audio files)'
    )
    
    # Output options
    parser.add_argument(
        '--output-dir', '-o',
        default='transcripts',
        help='Output directory for transcription files (default: transcripts)'
    )
    
    # Configuration
    parser.add_argument(
        '--config', '-c',
        help='Configuration file (JSON format)'
    )
    
    # Whisper model options
    parser.add_argument(
        '--model', '-m',
        choices=get_available_models(),
        help='Whisper model to use (default: turbo)'
    )
    
    parser.add_argument(
        '--language', '-l',
        help='Language code (default: en)'
    )
    
    parser.add_argument(
        '--compression-ratio-threshold',
        type=float,
        help='Compression ratio threshold (default: 1.8)'
    )
    
    parser.add_argument(
        '--condition-on-previous-text',
        action='store_true',
        help='Condition on previous text (default: False)'
    )
    
    parser.add_argument(
        '--no-fp16',
        action='store_true',
        help='Disable FP16 (useful for CPU-only systems)'
    )
    
    parser.add_argument(
        '--temperature',
        type=float,
        help='Temperature for sampling (default: 0.0)'
    )
    
    # Progress and output options
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Reduce output verbosity'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--create-config',
        help='Create a default configuration file at specified path'
    )
    
    return parser

def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Handle config file creation
    if args.create_config:
        config = WhisperConfig()
        config.create_default_config_file(args.create_config)
        print(f"Created default configuration file: {args.create_config}")
        return 0
    
    try:
        # Initialize configuration
        config = WhisperConfig(args.config)
        
        # Update configuration with command line arguments
        if args.no_fp16:
            args.fp16 = False
        else:
            args.fp16 = None  # Use default
            
        if args.quiet:
            args.verbose = False
        else:
            args.verbose = None  # Use default
            
        if args.no_color:
            config.progress_config['colored_output'] = False
        
        config.update_from_args(args)
        
        # Create transcriber and run
        transcriber = WhisperTranscriber(config)
        success = transcriber.run_transcription(args.inputs, args.output_dir)
        
        return 0 if success else 1
        
    except TranscriptionError as e:
        if config.progress_config.get('colored_output', True):
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        else:
            print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\\nTranscription cancelled by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())