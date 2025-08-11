# TTRPG Session Notes Automation

A complete system for processing Discord voice recordings into organized TTRPG session summaries and campaign management materials.

## Originally From
- https://medium.com/@brandonharris_12357/automating-d-d-notetaking-with-ai-89ecd36e8b0e
- https://github.com/VCDragoon/dnd-transcript-cleanup

## Overview

This modernized system provides a complete workflow with professional tooling:

1. **Audio Transcription** (`transcribe/`) - Convert audio files to text using OpenAI Whisper
2. **Transcript Processing** (`transcript_cleanup/`) - Clean and organize transcripts with Phase 1 improvements
3. **AI-Powered Documentation** (`AI_Prompts/`) - Generate campaign notes, NPC profiles, and summaries
4. **Shared Utilities** (`shared_utils/`) - Common configuration, logging, and processing functions
5. **Testing Suite** (`tests/`) - Comprehensive unit tests for reliability

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### 1. Audio Transcription
Convert audio files to TSV transcripts:
```bash
# Transcribe a single file
python transcribe/whisper_transcribe.py audio_file.flac --output-dir transcripts

# Transcribe a directory of files
python transcribe/whisper_transcribe.py /path/to/audio/files/ --output-dir transcripts

# Transcribe with custom settings
python transcribe/whisper_transcribe.py audio_files.zip --model large-v2 --no-fp16
```

### 2. Transcript Processing (Phase 1 Improved)
Clean and organize transcripts with modern tooling:
```bash
# Using v2 improved script with JSON configuration
python transcript_cleanup/transcript_cleanup_v2.py --config my_config.json

# Using environment variables for configuration
export TTRPG_SESSION_NAME="my_session"
export TTRPG_BASE_PATH="/path/to/transcripts"
python transcript_cleanup/transcript_cleanup_v2.py

# Quick test with existing data (run from project root)
python transcript_cleanup/transcript_cleanup_v2.py --base-path transcripts-test-data --log-level INFO
```

### 3. Text Replacement (Phase 1 Improved)
Apply name/term corrections:
```bash
# Auto-detect input files
python transcript_cleanup/json_text_replace_v2.py

# Specify files explicitly
python transcript_cleanup/json_text_replace_v2.py \
  --input transcript.txt \
  --replacements replacements.json \
  --output transcript_corrected.txt
```

### 4. AI Documentation
Use prompts in `AI_Prompts/` with ChatGPT or Claude to generate campaign documentation.

## 🏗️ Architecture

### Phase 1 Improvements (Completed)
- ✅ **Dependency Management**: `requirements.txt` for consistent environments
- ✅ **Shared Configuration**: JSON configs with environment variable support  
- ✅ **Professional Logging**: Colored, structured logging instead of print statements
- ✅ **Shared Utilities**: Common text processing and file operations
- ✅ **Unit Testing**: 23 comprehensive tests with 100% pass rate
- ✅ **Backward Compatibility**: Migration tools for existing setups

### Processing Pipeline
1. **Input**: TSV files from Whisper transcription (one per speaker)
2. **Individual Processing**: Remove duplicates, merge adjacent segments, clean short text
3. **Merge**: Combine all speakers into chronological order
4. **Text Replacement**: Apply name/term corrections
5. **Output**: Generate session summary parts and complete transcript

### Directory Structure
```
/
├── transcribe/                     # Audio transcription tools
│   ├── whisper_transcribe.py       # Main transcription script (Phase 1)
│   ├── whisper_config.py           # Configuration management
│   └── README.md                   # Transcription usage guide
├── transcript_cleanup/             # Text processing scripts (Phase 1 improved)
│   ├── transcript_cleanup_v2.py    # Main processing pipeline (v2)
│   ├── json_text_replace_v2.py     # Text replacement tool (v2)
│   ├── README.md                   # Detailed usage documentation
│   └── OLD/                        # Legacy scripts (archived)
├── shared_utils/                   # Phase 1 shared utilities
│   ├── config.py                   # Unified configuration system
│   ├── logging_config.py           # Professional logging
│   ├── text_processing.py          # Text processing utilities
│   └── file_operations.py          # File I/O utilities
├── tests/                          # Test suite
│   ├── test_config.py              # Configuration tests
│   ├── test_text_processing.py     # Text processing tests
│   ├── test_file_operations.py     # File operations tests
│   └── run_tests.py                # Test runner
├── AI_Prompts/                     # Campaign management prompts
│   ├── dm_simple_story_summarizer.txt
│   ├── NPC_template.txt
│   ├── LOCATIONS_template.txt
│   └── [other templates]
├── TEST-DATA/                      # Test audio and transcript files
└── requirements.txt                # Python dependencies
```

## 🔧 Configuration

### Modern Configuration (Phase 1)
The system now supports multiple configuration methods:

#### 1. JSON Configuration Files
```json
{
  "cleanup": {
    "session_name": "my_campaign",
    "part": "session_01",
    "base_path": "/path/to/transcripts",
    "short_duplicate_text_length": 4,
    "merge_threshold": 0.01
  },
  "name_mappings": {
    "discord_user": "Player: Name (Character: Name)"
  }
}
```

#### 2. Environment Variables
```bash
export TTRPG_SESSION_NAME="my_campaign"
export TTRPG_BASE_PATH="/path/to/transcripts"
export TTRPG_WHISPER_MODEL="turbo"
export TTRPG_LOG_LEVEL="INFO"
```


## 🧪 Testing

### Run All Tests
```bash
# Using pytest (recommended)
pytest tests/ -v

# Using custom test runner
python tests/run_tests.py

# Using unittest
python -m unittest discover tests/ -v
```

### Integration Testing
```bash
# Test with real transcript data (run from project root)
python transcript_cleanup/transcript_cleanup_v2.py --base-path transcripts-test-data
```

## 📁 File Formats

### Input Files
- **Audio**: `.flac`, `.wav`, `.mp3` (for Whisper transcription)
- **Transcripts**: `.tsv` files with columns: `start`, `end`, `text` (from Whisper)

### Configuration Files  
- **Replacements**: `merge_replacements.json` - JSON mapping for correcting misheard terms
  ```json
  {
    "CorrectName": ["mishear1", "mishear2"],
    "Gandalf": ["gandolf", "gandulf"]
  }
  ```

### Output Files
- **Processed CSVs**: Individual cleaned speaker files (`*_processed.csv`)
- **Merged CSV**: Combined chronological transcript (`*_merged.csv`)
- **Final Transcript**: Clean, readable session transcript (`.txt`)

## 🛠️ Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration Errors**
   ```bash
   # Verify your configuration
   python transcript_cleanup/transcript_cleanup_v2.py --help
   ```

3. **Transcription Issues**
   ```bash
   # Use fallback model
   python transcribe/whisper_transcribe.py audio.flac --model base --no-fp16
   ```

4. **Path Issues**
   ```bash
   # Use absolute paths
   python transcript_cleanup/transcript_cleanup_v2.py --base-path /full/path/to/files
   ```

### Getting Help
- Check the `transcript_cleanup/README.md` for detailed processing information
- Review test files in `tests/` for usage examples
- See `CLAUDE.md` for development guidance
- Check `Project Planning.md` for architectural details

## 🎯 Workflow Example

```bash
# 1. Transcribe audio files
python transcribe/whisper_transcribe.py session_audio/ --output-dir my_session

# 2. Create replacements file
echo '{"PlayerName": ["playername", "player name"]}' > my_session/merge_replacements.json

# 3. Process transcripts  
python transcript_cleanup/transcript_cleanup_v2.py --base-path my_session

# 4. Apply additional corrections if needed
python transcript_cleanup/json_text_replace_v2.py --input my_session/Session_complete_Final_COMPLETE.txt

# 5. Use AI prompts for campaign documentation
# (Copy transcript content to ChatGPT/Claude with prompts from AI_Prompts/)
```

## 🚀 Future Roadmap

### Phase 2: Architectural Improvements (Planned)
- Plugin architecture for cleanup steps
- Pipeline orchestrator for automated file flow
- Data models with Pydantic for type safety
- CLI framework (Click/Typer) for better UX
- Factory patterns for different input types

### Phase 3: Production Readiness (Planned)
- Docker containerization
- Monitoring/metrics collection
- Graceful error recovery
- API layer for web interface
- Comprehensive documentation site

---

**Note**: This system has been modernized with Phase 1 improvements for better reliability, maintainability, and user experience. Legacy scripts are preserved in `transcript_cleanup/OLD/` for backward compatibility.