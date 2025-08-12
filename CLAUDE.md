# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a TTRPG (Tabletop RPG) session note automation system that processes Discord voice recordings into organized session summaries and campaign management materials. The workflow involves recording sessions with Craig bot, transcribing with Whisper, processing the transcripts, then using AI prompts to generate comprehensive campaign documentation.

The system has evolved through three phases:
- **Phase 1**: Shared utilities, professional logging, unified configuration, and comprehensive testing
- **Phase 2**: Unified CLI interface with pipeline automation
- **Phase 3**: AI-powered campaign document generation with direct LLM analysis

It produces cleaned transcripts and automatically generates structured campaign documentation including NPC profiles, location documentation, character tracking, and narrative summaries using AI models.

## Key Scripts and Commands (Phase 1 Improved)

### 🆕 Phase 3: AI-Powered Campaign Generation (Current - Step 1 Complete)
```bash
# Complete workflow: audio → transcripts → cleaned text → AI campaign docs
python main.py process audio_files/ --output-dir session_01 --all-steps --generate-campaign

# Standalone AI generation from existing transcripts (recommended for testing)
python main.py generate session_01/Session_*_Final_COMPLETE.txt --output-dir campaign_docs --prompts NPC_template LOCATIONS_template

# Test with specific prompts
python main.py generate transcript.txt --output-dir campaign --prompts NPC_template

# Get help for generate command
python main.py generate --help
```

### Phase 2: Unified CLI Interface 
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

# AI Campaign Generation
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"  
export GOOGLE_API_KEY="your-key"
export TTRPG_AI_PROVIDER="anthropic"
export TTRPG_CAMPAIGN_DIR="campaign_docs"
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

## AI-Powered Campaign Document Generation (Phase 3)

### Current Status: Step 1 Complete - Direct LLM Analysis

The AI system now **automatically generates comprehensive campaign documents** from session transcripts using direct LLM analysis. This approach analyzes the complete transcript in one pass and generates relevant campaign materials.

**Step 2 (Intelligent Merging)** is on hold for testing and template improvement.

### Architecture Overview

**Current Implementation (Step 1):**
- **Direct Analysis**: LLM analyzes the full transcript and identifies all relevant entities
- **Single-pass Generation**: Creates comprehensive documents in one operation
- **No Entity Extraction**: Avoids regex-based entity extraction that caused false positives
- **100% Accuracy**: Only generates content that actually appears in the session

**Future Implementation (Step 2 - On Hold):**
- **Intelligent Merging**: Will merge new content with existing campaign documents
- **Entity Resolution**: Will detect existing NPCs/locations to avoid duplicates
- **Content Preservation**: Will preserve user modifications while adding new information

### Setup Requirements

1. **Install AI dependencies:**
   ```bash
   pip install -r requirements.txt  # Includes litellm, python-frontmatter, python-dotenv
   ```

2. **Configure API keys in .env file:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (choose one or more providers)
   ```

3. **Choose your AI provider:** Claude (Anthropic), GPT (OpenAI), or Gemini (Google)

### Current Features (Step 1)

- **Multi-provider support**: Claude, OpenAI GPT, Google Gemini via LiteLLM
- **Direct generation**: Analyzes complete transcripts without entity extraction
- **Obsidian compatibility**: Generates markdown with YAML frontmatter
- **Template-based**: Uses existing AI_Prompts/ templates for consistent output
- **Cost-effective**: $0.01-0.10 per session depending on length and provider

### Testing Results

- **Success Rate**: 100% (2/2 documents generated successfully in testing)
- **Content Quality**: High relevance, no false entities or nonsense files
- **Output Format**: Clean markdown with proper frontmatter
- **Performance**: 30-60 seconds per document

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
├── shared_utils/                   # Phase 1 shared utilities + Phase 3 AI
│   ├── config.py                   # Unified configuration system
│   ├── logging_config.py           # Professional logging framework
│   ├── text_processing.py          # Text processing utilities
│   ├── file_operations.py          # File I/O utilities
│   ├── llm_client.py               # Multi-provider LLM integration (Phase 3)
│   ├── document_manager.py         # Campaign document management (Phase 3)
│   ├── entity_resolver.py          # Entity resolution (Phase 3 - for Step 2)
│   └── campaign_generator.py       # Main AI orchestrator (Phase 3)  
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
├── cli/                            # Phase 2 CLI commands + Phase 3 AI
│   ├── main.py                     # Main CLI entry point
│   └── commands/                   # Individual command implementations
│       ├── generate_cmd.py         # AI generation command (Phase 3)
│       └── [other commands]
├── requirements.txt                # Python dependencies (Phases 1-3)
├── .env.example                    # Environment variables template (Phase 3)
└── main.py                         # Root CLI entry point (Phase 2)
```

## Dependencies (Phases 1-3)
- **Core**: pandas, colorama, openai-whisper (see `requirements.txt`)
- **AI Integration (Phase 3)**: litellm, python-frontmatter, python-dotenv, fuzzywuzzy
- **Testing**: pytest (for comprehensive test suite)  
- **Audio Recording**: Craig Discord bot
- **AI Processing**: Automated generation via Claude, OpenAI GPT, or Google Gemini

## Current Limitations and Future Plans

### Current System (Step 1 - Direct Generation)
✅ **Working**: Direct LLM analysis generates accurate campaign documents
✅ **Working**: Multi-provider support with automatic API key detection
✅ **Working**: Template-based document generation
✅ **Working**: Obsidian-compatible markdown output

### On Hold (Step 2 - Intelligent Merging)
⏸️ **Pending**: Merging new content with existing campaign documents
⏸️ **Pending**: Entity resolution and duplicate detection
⏸️ **Pending**: Preserving user modifications during updates

### Testing Focus
🔍 **Current Priority**: Template improvement and output refinement
🔍 **Current Priority**: Cost optimization and provider comparison
🔍 **Current Priority**: User feedback on generated document quality