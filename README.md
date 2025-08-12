# TTRPG Session Notes Automation

Turn your Discord TTRPG sessions into organized campaign notes automatically.

## What You Get

Transform hours of audio recordings into comprehensive campaign documentation:

- **One command**: audio files → clean transcripts → campaign documents
- **AI-powered**: Generate NPC profiles, location notes, story summaries  
- **Flexible**: Works with any audio format, customizable processing
- **Complete**: From recording to campaign documentation in minutes

## Get Started in 2 Minutes

### Quick Install
```bash
pip install -r requirements.txt
```

### Try It Now
```bash
# With your own audio files (recommended)
python main.py process your_session_audio/ --output-dir session_01 --all-steps

# Or with existing transcript files
python main.py process your_transcripts/ --output-dir session_01 --cleanup-only

# View your results
ls session_01/
# Session_complete_Final_COMPLETE.txt  ← Your clean transcript
# *.csv files                          ← Processed data files
```

### What Happens
1. **Audio → Text**: Whisper AI transcribes each player's audio separately
2. **Clean & Organize**: Remove duplicates, fix timing, merge speakers chronologically  
3. **Smart Corrections**: Apply name mappings (fix "Gandolf" → "Gandalf")
4. **Campaign Notes**: Use AI prompts to generate NPC profiles, location docs, story summaries

### Real Example Output
**Input**: 45 minutes of Discord audio with 6 players  
**Output**: Clean 8-page transcript + AI-ready prompts for campaign management

## Essential Commands

### Complete Automation (Recommended)
```bash
# Everything: transcribe → clean → organize
python main.py process session_audio/ --output-dir campaign_session_01 --all-steps

# Customize session info
python main.py process audio/ --output-dir session --session-name "Curse of Strahd" --session-part "Episode_3"
```

### Individual Operations
```bash
# Just transcribe audio files
python main.py transcribe audio.flac --output-dir transcripts

# Just clean existing transcripts  
python main.py cleanup --base-path transcripts --session-name "My Campaign"

# Just apply text corrections
python main.py replace --input transcript.txt --replacements corrections.json

# Get help for any command
python main.py --help
python main.py process --help
```

## Common Workflow Patterns

### Weekly Campaign Sessions
```bash
# 1. Record with Craig Discord bot → download audio files
# 2. One command processing
python main.py process session_audio/ --output-dir "session_12" --all-steps --session-name "Waterdeep" --session-part "episode_12"

# 3. Create name corrections (optional but recommended)
echo '{"Voldemort": ["voldamort", "boltimore"], "Hermione": ["hermione", "her mine"]}' > session_12/merge_replacements.json

# 4. Re-run to apply corrections
python main.py process session_12 --output-dir session_12 --cleanup-only

# 5. Use transcript with AI prompts from AI_Prompts/ folder
```

### One-shot Adventure Processing  
```bash
# Quick processing for single session
python main.py process oneshot_audio/ --output-dir "halloween_oneshot" --all-steps

# Generate story summary using AI_Prompts/dm_simple_story_summarizer.txt
```

### Campaign Catch-up Documentation
```bash
# Process multiple old sessions
for session in session_*_audio/; do
    python main.py process "$session" --output-dir "${session%_audio}" --all-steps
done
```

## Generate Campaign Notes

The system includes specialized AI prompts for campaign management:

### Available Templates
- **Story Summaries**: NY Times-style short stories (10+ pages, Stephen King/Neil Gaiman style)
- **NPC Profiles**: Comprehensive character analysis with motivations, relationships, roleplaying notes
- **Location Documentation**: Detailed location docs with history, secrets, plot hooks  
- **Character Tracking**: Individual player analysis with quotes and development tracking
- **Encounter Documentation**: Structured encounter breakdowns

### Usage with ChatGPT/Claude
1. Process your session: `python main.py process audio/ --output-dir session --all-steps`
2. Copy content from `Session_*_Final_COMPLETE.txt`
3. Use with prompts from `AI_Prompts/` directory
4. For longer transcripts, Claude is recommended (larger context window)

## Customize Your Workflow

### Essential Configuration
Create `config.json` for your campaign:
```json
{
  "cleanup": {
    "session_name": "curse_of_strahd",
    "base_path": "/path/to/sessions"
  },
  "name_mappings": {
    "discord_user123": "Player: Sarah (Character: Elara)",
    "gamer_dude": "Player: Mike (Character: Thorin)"
  }
}
```

### Environment Variables (Alternative)
```bash
export TTRPG_SESSION_NAME="my_campaign"
export TTRPG_BASE_PATH="/path/to/sessions"
export TTRPG_WHISPER_MODEL="turbo"
```

### Advanced Processing Control
```json
{
  "cleanup": {
    "enable_remove_duplicates": true,
    "enable_merge_segments": true,
    "enable_remove_short": false,
    "short_duplicate_text_length": 4,
    "merge_threshold": 0.01
  }
}
```

### Command Line Overrides
```bash
# Skip specific processing steps
python main.py cleanup --skip-duplicates --skip-merge

# Use different Whisper model
python main.py transcribe audio.flac --model large-v2 --no-fp16
```

## Testing Your Setup

### Run All Tests
```bash
# Verify installation
pytest tests/ -v

# Test the CLI interface
python main.py --help
python main.py process --help
```

### Integration Test
```bash
# Test with your own data
python main.py process your_audio_files/ --output-dir test_output --all-steps

# Or test cleanup on existing transcripts
python main.py cleanup --base-path your_transcripts/ --session-name "test_session"
```

## Common Issues & Solutions

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Audio Transcription Issues
```bash
# Use CPU-optimized model
python main.py transcribe audio.flac --model base --no-fp16

# For low-quality audio
python main.py transcribe audio.flac --model large-v2
```

### Configuration Problems
```bash
# Verify your setup
python main.py --help

# Check specific command options
python main.py cleanup --help
```

### Path Issues
```bash
# Always use absolute paths for reliability
python main.py process /full/path/to/audio/ --output-dir /full/path/to/output/
```

### Text Replacement Not Working
```bash
# Verify your replacements file format
echo '{"CorrectName": ["mishear1", "mishear2"]}' > merge_replacements.json

# Check file location (should be in output directory)
python main.py replace --replacements /full/path/to/merge_replacements.json
```

## Complete Command Reference

### Main Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `process` | Full automation pipeline | `python main.py process audio/ --output-dir session --all-steps` |
| `transcribe` | Audio to text conversion | `python main.py transcribe audio.flac --output-dir transcripts` |
| `cleanup` | Process transcript files | `python main.py cleanup --base-path transcripts` |
| `replace` | Apply text corrections | `python main.py replace --input transcript.txt` |

### Process Command Options
```bash
python main.py process INPUT_PATH --output-dir OUTPUT_DIR [options]

Options:
  --all-steps              Run transcribe → cleanup → replace
  --transcribe-only        Only convert audio to text
  --cleanup-only           Only process existing transcripts
  --session-name NAME      Campaign/session identifier  
  --session-part PART      Episode/part identifier
  --model MODEL            Whisper model (tiny to turbo)
  --no-fp16               Use CPU-only processing
```

### Transcribe Command Options
```bash
python main.py transcribe INPUT_PATH --output-dir OUTPUT_DIR [options]

Options:
  --model MODEL           Whisper model: tiny, base, small, medium, large, large-v2, turbo
  --no-fp16              Disable fp16 (required for CPU-only)
  --language LANG        Audio language (default: en)
  --config-file FILE     Custom Whisper configuration
```

### Cleanup Command Options
```bash
python main.py cleanup --base-path PATH [options]

Options:
  --session-name NAME     Override session name
  --part PART            Override session part  
  --skip-duplicates      Disable duplicate removal
  --skip-merge           Disable segment merging
  --skip-short           Disable short text removal
  --skip-gibberish       Disable silence/gibberish removal
```

## File Formats

### Input Files
- **Audio**: `.flac`, `.wav`, `.mp3` (Craig Discord bot output recommended)
- **Transcripts**: `.tsv` files with `start`, `end`, `text` columns (from Whisper)

### Configuration Files
- **Main Config**: `config.json` with cleanup settings and name mappings
- **Text Corrections**: `merge_replacements.json` for fixing misheard terms
  ```json
  {
    "Gandalf": ["gandolf", "gandulf", "gand off"],
    "PlayerName": ["playername", "player name"]  
  }
  ```

### Output Files
- **Individual CSVs**: `*_processed.csv` (cleaned per-speaker data)
- **Combined CSV**: `*_merged.csv` (chronological speaker data)
- **Final Transcript**: `Session_*_Final_COMPLETE.txt` (readable transcript)
- **Split Parts**: `Session_*_part_N.txt` (if transcript is very long)

## Architecture Overview

### Processing Pipeline
1. **Input**: Audio files or TSV transcripts (one per speaker)
2. **Individual Processing**: Remove duplicates, merge adjacent segments, clean short text
3. **Merge**: Combine all speakers in chronological order
4. **Text Replacement**: Apply name/term corrections from JSON file
5. **Output**: Generate readable transcripts and organized data files

### Directory Structure
```
project/
├── main.py                 # Main CLI entry point
├── cli/                    # Command implementations
├── transcribe/             # Audio transcription (Whisper)
├── transcript_cleanup/     # Text processing and cleanup
├── shared_utils/           # Common configuration and utilities
├── AI_Prompts/             # Campaign management templates
└── tests/                  # Test suite
```

### Technology Stack
- **Audio Processing**: OpenAI Whisper for transcription
- **Text Processing**: pandas for data manipulation
- **Configuration**: JSON files + environment variables
- **Logging**: Structured, colored output for progress tracking
- **Testing**: pytest with comprehensive unit tests

## Legacy Interface

For users who prefer the original scripts:

```bash
# Audio transcription
python transcribe/whisper_transcribe.py audio.flac --output-dir transcripts

# Transcript processing  
python transcript_cleanup/transcript_cleanup_v2.py --base-path transcripts

# Text replacement
python transcript_cleanup/json_text_replace_v2.py --input transcript.txt
```

## Development & Contributing

### Running Tests
```bash
pytest tests/ -v
python tests/run_tests.py
```

### Project Structure
- Phase 1: Shared utilities, professional logging, unified configuration
- Phase 2: CLI interface, pipeline automation, configurable processing
- Maintained with KISS principles: simple, maintainable improvements without over-engineering

### Future Roadmap
- Docker containerization for consistent deployments
- Enhanced error recovery and resume capabilities
- Performance optimizations for large audio files
- Extended AI prompt templates and automation

---

**Originally inspired by**: [Automating D&D Notetaking with AI](https://medium.com/@brandonharris_12357/automating-d-d-notetaking-with-ai-89ecd36e8b0e)

This system has been modernized with Phase 1 & 2 improvements following KISS principles. The unified CLI interface provides streamlined automation while maintaining full backward compatibility.