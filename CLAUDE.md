# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a TTRPG (Tabletop RPG) session note automation system that processes Discord voice recordings into organized session summaries and campaign management materials. The workflow involves recording sessions with Craig bot, transcribing with Whisper, processing the transcripts, then using AI prompts to generate comprehensive campaign documentation.

The system produces both cleaned transcripts and uses AI models (ChatGPT/Claude) to create structured campaign notes including NPC profiles, location documentation, character tracking, and narrative summaries.

## Key Scripts and Commands

### Main Processing Script
```bash
# Run the transcript cleanup pipeline
cd transcript_cleanup
python transcript_cleanup.py
```

### Whisper Transcription
```bash
# Sample command for transcribing audio files
whisper --model large-v2 --language en --condition_on_previous_text False --compression_ratio_threshold 1.8 [audio_file.flac]
```

### Text Replacement Tool
```bash
# Apply name/term replacements to transcripts
cd transcript_cleanup  
python json_text_replace.py
```

## Configuration

### Main Config (`transcript_cleanup/config.py`)
- `SESSION_NAME`: Main folder name for session recordings
- `PART`: Sub-folder for session parts 
- `BASE_PATH`: Full path to session files
- `NAME_MAPPINGS`: Maps Discord usernames to character names
- Processing thresholds for text merging and cleanup

### Replacements (`merge_replacements.json`)
- JSON mapping for correcting misheard proper nouns (character names, locations, etc.)
- Format: `{"CorrectName": ["mishear1", "mishear2"]}`

## Architecture

### Processing Pipeline
1. **Input**: TSV files from Whisper transcription (one per speaker)
2. **Individual Processing**: Remove duplicates, merge adjacent segments, clean short text
3. **Merge**: Combine all speakers into chronological order
4. **Text Replacement**: Apply name/term corrections
5. **Output**: Generate session summary parts and complete transcript

### Key Functions
- `process_tsv_to_csv()`: Cleans individual speaker files
- `merge_speaker_texts()`: Combines speakers chronologically  
- `apply_replacements()`: Fixes misheard terms
- `split_text()`: Breaks large transcripts into manageable parts

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

## Setup Instructions

Based on the README, initial setup requires:

1. **Copy Configuration Files**:
   ```bash
   cd transcript_cleanup
   cp default_config.py config.py
   cp default_merge_replacements.json merge_replacements.json
   ```

2. **Configure Settings**: Edit `config.py` and `merge_replacements.json` with your session details and name mappings

3. **Directory Structure**: Organize Whisper TSV files in session folders (e.g., `sessions/session_name/`)

## File Structure
```
/
├── sessions/[session_name]/        # Processed session data
│   ├── *.tsv                       # Whisper transcription files
│   ├── *_processed.csv             # Cleaned individual files  
│   ├── sessions_*_merged.csv       # Combined speaker data
│   └── Session * Final *.txt       # Output transcripts
├── audio-tests/                    # Test recordings
├── AI_Prompts/                     # Campaign management prompts
│   ├── dm_simple_story_summarizer.txt
│   ├── NPC_template.txt
│   ├── LOCATIONS_template.txt
│   ├── PC_tracker.txt
│   └── [other prompt templates]
└── transcript_cleanup/             # Processing scripts
    ├── transcript_cleanup.py       # Main processing pipeline
    ├── json_text_replace.py        # Batch text replacement
    ├── config.py                   # Session configuration
    └── merge_replacements.json     # Name/term corrections
```

## Dependencies
- pandas, colorama (for data processing and colored output)
- Whisper (OpenAI) for audio transcription
- Craig Discord bot for recording sessions