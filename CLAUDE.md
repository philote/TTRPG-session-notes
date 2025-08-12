# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a TTRPG (Tabletop RPG) session note automation system that processes Discord voice recordings into organized session summaries and campaign management materials. The workflow involves recording sessions with Craig bot, transcribing with Whisper, processing the transcripts, then using AI prompts to generate comprehensive campaign documentation.

The system has been modernized with **Phase 1 improvements** including shared utilities, professional logging, unified configuration, and comprehensive testing. It produces both cleaned transcripts and uses AI models (ChatGPT/Claude) to create structured campaign notes including NPC profiles, location documentation, character tracking, and narrative summaries.

## Key Scripts and Commands (Phase 1 Improved)

### 🆕 Phase 2: Unified CLI Interface (Recommended)
```bash
# Full automated pipeline: audio → transcripts → cleaned text
python main.py process audio_files/ --output-dir session_01 --all-steps --session-name "Campaign" --session-part "Episode_1"

# Individual operations with enhanced UX
python main.py transcribe audio.flac --output-dir transcripts --model turbo --no-fp16
python main.py cleanup --base-path transcripts --session-name my_session
python main.py replace --input transcript.txt --replacements corrections.json

# Get comprehensive help for any command
python main.py --help
python main.py process --help
python main.py cleanup --help
```

### Legacy Interface (Still Supported - Phase 1 Improved)
```bash
# Audio Transcription
python transcribe/whisper_transcribe.py /path/to/audio/files/ --output-dir transcripts --model turbo --no-fp16

# Main Processing Script with configurable cleanup steps
python transcript_cleanup/transcript_cleanup_v2.py --config config.json --log-level INFO

# Text Replacement Tool
python transcript_cleanup/json_text_replace_v2.py --input transcript.txt --replacements replacements.json

# Quick test with provided test data (run from project root)
python transcript_cleanup/transcript_cleanup_v2.py --base-path TEST-DATA/transcripts-test-data
```

### Testing (Phase 1)
```bash
# Run all tests
pytest tests/ -v

# Run individual test files
python tests/run_tests.py
```


## Configuration (Phase 1 - Unified System)

### Shared Configuration System (`shared_utils/config.py`)
The modern configuration system supports multiple input methods:

**JSON Configuration Files:**
```json
{
  "cleanup": {
    "session_name": "my_campaign",
    "base_path": "/path/to/transcripts",
    "short_duplicate_text_length": 4,
    "merge_threshold": 0.01
  },
  "name_mappings": {
    "discord_user": "Player: Name (Character: Name)"
  }
}
```

**Environment Variables (prefixed with TTRPG_):**
```bash
export TTRPG_SESSION_NAME="my_campaign"
export TTRPG_BASE_PATH="/path/to/transcripts" 
export TTRPG_WHISPER_MODEL="turbo"
export TTRPG_LOG_LEVEL="INFO"
```

### Replacements (Located in session directories)
- JSON mapping for correcting misheard proper nouns (character names, locations, etc.)
- Format: `{"CorrectName": ["mishear1", "mishear2"]}`
- Place `merge_replacements.json` in the same directory as your TSV files

## Architecture

### Processing Pipeline
1. **Input**: TSV files from Whisper transcription (one per speaker)
2. **Individual Processing**: Remove duplicates, merge adjacent segments, clean short text
3. **Merge**: Combine all speakers into chronological order
4. **Text Replacement**: Apply name/term corrections
5. **Output**: Generate session summary parts and complete transcript

### Key Functions (Phase 1 - Shared Utilities)
**Text Processing (`shared_utils/text_processing.py`):**
- `clean_transcript_dataframe()`: Full cleaning pipeline for DataFrames
- `apply_text_replacements()`: Advanced text replacement with statistics
- `merge_adjacent_segments()`: Combines adjacent speaker segments
- `split_text_with_overlap()`: Intelligent text splitting with overlap

**File Operations (`shared_utils/file_operations.py`):**
- `load_tsv_file()`: Robust TSV file loading
- `save_dataframe()`: Multi-format DataFrame saving
- `find_files_by_pattern()`: Pattern-based file discovery
- `merge_csv_files()`: Chronological file merging

## AI Prompts for Campaign Management

The `AI_Prompts/` directory contains specialized prompts for generating structured campaign documentation:

### Available Prompts
- **`dm_simple_story_summarizer.txt`**: Creates NY Times-style short stories from session summaries (10+ pages, Stephen King/Neil Gaiman style)
- **`NPC_template.txt`**: Comprehensive NPC analysis template with physical descriptions, motivations, relationships, and roleplaying notes
- **`LOCATIONS_template.txt`**: Detailed location documentation including events, history, secrets, and plot hooks
- **`PC_tracker.txt`**: Individual player character session analysis with relationships, quotes, and development tracking
- **`PC_metadata.txt`**: Player character metadata and background information
- **`dm_base_helper.txt`**: General DM assistance prompts
- **`dm_encounter_template.txt`**: Structured encounter documentation

### Usage
These prompts are designed for use with ChatGPT custom GPTs or Claude models. For longer transcripts, Claude is recommended due to larger context windows.

## Setup Instructions (Phase 1)

### Quick Setup (Recommended)
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Configuration** (choose one method):
   ```bash
   # Option A: Use environment variables
   export TTRPG_BASE_PATH="/path/to/your/transcripts"
   export TTRPG_SESSION_NAME="my_campaign"
   
   # Option B: Create JSON config file
   python transcript_cleanup/config_migration.py --create-v2
   ```

3. **Prepare Session Directory**: Place Whisper TSV files and create replacements file:
   ```bash
   mkdir my_session/
   # Place your *.tsv files in my_session/
   echo '{"PlayerName": ["playername"]}' > my_session/merge_replacements.json
   ```


## File Structure (Phase 1)
```
/
├── transcribe/                     # Audio transcription tools
│   ├── whisper_transcribe.py       # Main transcription script (Phase 1)
│   ├── whisper_config.py           # Configuration management  
│   └── README.md                   # Transcription usage guide
├── transcript_cleanup/             # Text processing (Phase 1 improved)
│   ├── transcript_cleanup_v2.py    # Main processing pipeline (v2)
│   ├── json_text_replace_v2.py     # Text replacement tool (v2)
│   ├── README.md                   # Detailed usage documentation
│   └── OLD/                        # Legacy scripts (archived)
│       ├── transcript_cleanup.py   # Original script
│       ├── json_text_replace.py    # Original replacement tool
│       └── config.py               # Original configuration
├── shared_utils/                   # Phase 1 shared utilities
│   ├── config.py                   # Unified configuration system
│   ├── logging_config.py           # Professional logging framework
│   ├── text_processing.py          # Text processing utilities
│   └── file_operations.py          # File I/O utilities  
├── tests/                          # Test suite (Phase 1)
│   ├── test_config.py              # Configuration tests
│   ├── test_text_processing.py     # Text processing tests
│   ├── test_file_operations.py     # File operations tests
│   └── run_tests.py                # Test runner
├── AI_Prompts/                     # Campaign management prompts
│   ├── dm_simple_story_summarizer.txt
│   ├── NPC_template.txt
│   ├── LOCATIONS_template.txt
│   ├── PC_tracker.txt
│   └── [other templates]
├── TEST-DATA/                      # Test audio and transcript files
│   └── audio-tests/session-zero-cuts/  # Sample audio files
├── transcripts-test-data/          # Sample transcript files for testing
├── requirements.txt                # Python dependencies (Phase 1)
└── test_phase1_improvements.py     # Integration test script
```

## Dependencies (Phase 1)
- **Core**: pandas, colorama, openai-whisper (see `requirements.txt`)
- **Testing**: pytest (for comprehensive test suite)  
- **Audio Recording**: Craig Discord bot
- **AI Processing**: ChatGPT or Claude for campaign documentation