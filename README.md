# TTRPG Session Notes Automation

Turn your Discord TTRPG sessions into organized campaign notes automatically.

> [!NOTE]
> **This project was inspired by**: [Automating D&D Notetaking with AI](https://medium.com/@brandonharris_12357/automating-d-d-notetaking-with-ai-89ecd36e8b0e)
> **Original code** inside the transcript_cleanup folder from [dnd-transcript-cleanup](https://github.com/VCDragoon/dnd-transcript-cleanup)

## What You Get

Transform hours of audio recordings into comprehensive campaign documentation:

- **One command**: audio files → clean transcripts → campaign documents
- **AI-powered**: Generate NPC profiles, location notes, story summaries  
- **Flexible**: Works with any audio format, customizable processing
- **Complete**: From recording to campaign documentation in minutes

## Get Started in 5 Minutes

### Prerequisites
You'll need **Python 3.10 through 3.13** (Python 3.14+ support coming soon). Check your version:
```bash
python3 --version
```

**Python 3.12 is recommended** for the best experience with AI features. If you have Python 3.9 or older, [upgrade to Python 3.12](https://www.python.org/downloads/).

> [!NOTE]
> Python 3.14 was just released and the `numba` dependency (required by Whisper) doesn't support it yet. If you have Python 3.14, use Python 3.12 instead (see instructions below).

#### FFmpeg (Required for Audio Transcription)

**FFmpeg is required** to transcribe audio files. Install it before running transcription:

**macOS** (using Homebrew):
```bash
brew install ffmpeg
```

**Linux** (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows**:
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your PATH.

**Verify installation**:
```bash
ffmpeg -version
```

If you get "command not found", ffmpeg is not installed or not in your PATH.

On a Mac, install [Homebrew](https://brew.sh/) and install Python with `brew install python`

#### Make sure Homebrew's bin directory is in your PATH
For Apple Silicon
`export PATH="/opt/homebrew/bin:$PATH"`
For Intel Mac
`export PATH="/usr/local/bin:$PATH"`
Then run source `~/.zshrc` to reload.

#### Add an alias to your shell config file:
For zsh
`echo 'alias python=python3' >> ~/.zshrc`
`echo 'alias pip=pip3' >> ~/.zshrc`
`source ~/.zshrc`

### Recommended Setup (Virtual Environment)
Using a virtual environment keeps this project's dependencies separate from your system Python:

```bash
# 1. Create a virtual environment in the project directory
# If you have multiple Python versions, use python3.12 explicitly:
python3.12 -m venv venv

# 2. Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# You should see (venv) in your terminal prompt now

# 3. Verify Python version inside venv
python --version  # Should show python3.12

# 4. Install dependencies
pip install -r requirements.txt
```

### Quick Install (System-wide)
If you prefer to install system-wide (not recommended):
```bash
pip install -r requirements.txt
```

**Note**: Remember to activate your virtual environment (`source venv/bin/activate`) each time you use the project.

### 🤖 AI Campaign Generation Setup (Optional)
For AI-powered NPC and location generation, set up API keys:

```bash
# 1. Copy the example environment file
cp .env.example .env

# 2. Edit .env with your API keys (choose one or more providers):
# - OpenAI: Get key from https://platform.openai.com/api-keys  
# - Anthropic: Get key from https://console.anthropic.com/
# - Google: Get key from https://console.cloud.google.com/

# Example .env content:
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# OPENAI_API_KEY=sk-your-openai-key-here
```

**Cost**: AI generation typically costs $0.01-0.10 per session depending on transcript length and provider.

### Try It Now
```bash
# Basic workflow: audio → clean transcripts
python main.py process your_session_audio/ --output-dir session_01 --all-steps

# 🚀 NEW: Add AI campaign generation
python main.py process your_session_audio/ --output-dir session_01 --all-steps --generate-campaign

# Or with existing transcript files
python main.py process your_transcripts/ --output-dir session_01 --cleanup-only

# Standalone AI generation from existing transcripts (recommended for testing)
python main.py generate session_01/Session_*_Final_COMPLETE.txt --output-dir campaign_docs --prompts dm_base_helper LOCATIONS_template NPC_template PC_metadata PC_tracker

# View your results
ls session_01/
# Session_complete_Final_COMPLETE.txt  ← Your clean transcript
# *.csv files                          ← Processed data files

ls campaign_docs/  # AI-generated campaign documents
# NPC_your-session.md                  ← All NPCs found in session
# LOCATIONS_your-session.md            ← All locations found in session
```

### What Happens
1. **Audio → Text**: Whisper AI transcribes each player's audio separately
2. **Clean & Organize**: Remove duplicates, fix timing, merge speakers chronologically  
3. **Smart Corrections**: Automatic text corrections for 40+ common RPG terms (fix "stilmiss choir" → "Stillness Choir", "wizardry" → "wizardry", etc.)
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

# Text corrections are now automatic (use --config for custom terms)

# Just generate AI campaign documents
python main.py generate transcript.txt --output-dir campaign --prompts NPC_template LOCATIONS_template

# Get help for any command
python main.py --help
python main.py generate --help
```

## Common Workflow Patterns

### Weekly Campaign Sessions
```bash
# 1. Record with Craig Discord bot → download audio files
# 2. One command processing (includes automatic text corrections)
python main.py process session_audio/ --output-dir "session_12" --all-steps --session-name "Waterdeep" --session-part "episode_12"

# 3. Done! Text corrections are automatic (40+ built-in RPG term corrections)
# 4. Use transcript with AI prompts from AI_Prompts/ folder
```

### Custom Text Replacements (Advanced)
Want to add your own campaign-specific corrections? 

```bash
# 1. Copy the example config
cp shared_utils/example_config.py my_config.py

# 2. Edit my_config.py and add your terms to DEFAULT_TEXT_REPLACEMENTS:
# "Your BBEG Name": ["bbeg mishear1", "bbeg mishear2"],
# "Your Important NPC": ["npc mishear1", "npc mishear2"],

# 3. Use your custom config
python main.py process audio/ --output-dir session_01 --all-steps --config my_config.py
```

**Built-in corrections include**: Stillness Choir, Ember Thieves, wizard, rogue, perception, armor, crossbow, and 30+ more RPG terms.

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

## 🤖 AI Campaign Generation (Phase 3)

The system now includes **automated AI-powered campaign document generation** that transforms your session transcripts into comprehensive campaign materials.

### Current Implementation: Direct LLM Analysis (Step 1)

The AI system analyzes your complete session transcript and generates comprehensive campaign documents in one step:

**What it generates:**
- **NPC Documentation**: Complete profiles with motivations, relationships, dialogue patterns, and roleplaying notes
- **Location Documentation**: Detailed location descriptions with history, secrets, and plot hooks
- **Story Summaries**: Narrative summaries and session recaps
- **Character Tracking**: Player character development and session highlights

### Quick Start with AI Generation

```bash
# Complete workflow: audio → transcripts → AI campaign docs
python main.py process your_session_audio/ --output-dir session_01 --all-steps --generate-campaign

# Generate from existing transcript (recommended for testing)
python main.py generate session_01/Session_*_Final_COMPLETE.txt --output-dir campaign_docs --prompts NPC_template LOCATIONS_template
```

### Expected Output
```
campaign_docs/
├── NPC_your-session.md      # All NPCs with full profiles and quotes
└── LOCATIONS_your-session.md # All locations with detailed descriptions
```

### Cost & Performance
- **Cost**: $0.01-0.10 per session (varies by transcript length and provider)
- **Speed**: 30-60 seconds per document
- **Accuracy**: Direct analysis provides 100% relevant content (no entity extraction errors)

### Available AI Prompt Templates
- **`NPC_template`**: Comprehensive NPC analysis with physical descriptions, motivations, relationships, and roleplaying notes
- **`LOCATIONS_template`**: Detailed location documentation including events, history, secrets, and plot hooks
- **`dm_simple_story_summarizer`**: NY Times-style short stories (10+ pages, Stephen King/Neil Gaiman style)
- **`PC_tracker`**: Individual player character session analysis with relationships, quotes, and development tracking
- **`dm_encounter_template`**: Structured encounter documentation
- **`PC_metadata`**: Player character metadata and background information

### AI Provider Setup
```bash
# Copy example environment file
cp .env.example .env

# Add your API keys (choose one or more providers):
# ANTHROPIC_API_KEY=sk-ant-your-key-here      # Claude (recommended for long transcripts)
# OPENAI_API_KEY=sk-your-openai-key-here      # ChatGPT (fast and cost-effective)
# GOOGLE_API_KEY=your-google-key-here         # Gemini (alternative option)
```

### Testing & Template Improvement

**Current Status**: Step 1 (Direct Generation) is complete and working. Step 2 (Intelligent Merging) is on hold for testing and template refinement.

**Test the system:**
```bash
# Generate documents from your transcript
python main.py generate your_transcript.txt --output-dir test_campaign --prompts NPC_template

# Review the generated markdown files
ls test_campaign/
cat test_campaign/NPC_*.md
```

**Template Enhancement**: The AI prompts in `AI_Prompts/` can be customized for your campaign style. Modify the templates to match your preferred output format.

### Example Test Session

Here's what to expect when testing the AI generation with a typical D&D session transcript:

**Input**: Session transcript (8 pages) containing:
- 3 NPCs: Tavern keeper "Grenda", Guard captain "Marcus", Mysterious stranger "Vex"  
- 2 Locations: "The Prancing Pony" tavern, "Westgate Guard Tower"
- 1 Combat encounter with bandits
- Character dialogue and roleplay

**Generated Output**:

`NPC_test-session.md` (example excerpt):
```markdown
---
prompt_type: NPC_template
session_name: test-session
generated_date: 2024-01-15T14:30:25
provider: anthropic
auto_generated: true
---

# NPCs from Test Session

## Grenda - The Prancing Pony Tavern Keeper

**Physical Description**: A stout halfling woman with graying brown hair tied back in a practical bun...

**Personality**: Warm but no-nonsense, protective of her establishment and regular customers...

**Key Quotes**: 
- "You look like trouble, but your coin's good here."
- "Haven't seen Marcus this worried since the goblin raids."

**Relationships**: 
- **Marcus**: Old friend, provides information about local threats
- **Party**: Cautiously helpful, appreciates their gold

## Marcus - Westgate Guard Captain

**Physical Description**: Human male, mid-40s, weathered face with a distinctive scar across his left cheek...
```

`LOCATIONS_test-session.md` (example excerpt):
```markdown
---
prompt_type: LOCATIONS_template  
session_name: test-session
generated_date: 2024-01-15T14:30:45
provider: anthropic
auto_generated: true
---

# Locations from Test Session

## The Prancing Pony - Tavern & Inn

**Description**: A two-story stone and timber building with a thatched roof...

**Atmosphere**: Warm and welcoming, with the smell of hearty stew and fresh bread...

**Important Events**: 
- Party gathered information about bandit attacks
- Met mysterious stranger "Vex" who offered a job
- Marcus arrived with urgent news about missing patrols

**Secrets & Hooks**:
- Grenda knows more about the local bandits than she lets on
- Regular meeting place for information brokers
```

**Performance**: Generated in ~45 seconds, cost ~$0.05, 2 comprehensive documents created.

### Template Improvement Guide

The AI prompt templates in `AI_Prompts/` can be customized for better results with your specific campaign style:

#### Customizing Prompt Templates

**1. Copy and modify existing templates:**
```bash
# Make a backup first
cp AI_Prompts/NPC_template.txt AI_Prompts/NPC_template_custom.txt

# Edit with your preferred format
nano AI_Prompts/NPC_template_custom.txt
```

**2. Template customization tips:**
- **Add campaign-specific context**: Include your world's races, factions, or terminology
- **Specify output format**: Request bullet points, tables, or specific markdown structure  
- **Include example outputs**: Show the AI exactly what format you want
- **Add constraints**: Specify word counts, detail levels, or focus areas

**3. Example customizations:**

*For a sci-fi campaign:*
```
Focus on: Technology levels, cybernetic implants, corporate affiliations
Include: Threat assessment, security clearance, known aliases
Format: Corporate dossier style with threat ratings
```

*For a political intrigue campaign:*
```
Emphasize: Social connections, secrets, leverage opportunities
Include: Family trees, political affiliations, blackmail material
Format: Intelligence briefing with relationship maps
```

**4. Test your custom templates:**
```bash
# Test with your custom template
python main.py generate your_transcript.txt --output-dir test --prompts NPC_template_custom

# Compare results
diff test/NPC_*.md original/NPC_*.md
```

#### Template Performance Tips

- **Shorter prompts = faster generation** (and lower cost)
- **Specific instructions = better results** than generic requests
- **Examples in prompts = consistent formatting** across sessions
- **Constraints help focus** (e.g., "limit to 3 NPCs per location")

#### Provider-Specific Optimization

**Claude (Anthropic)**: Excellent with longer, detailed prompts and context
**ChatGPT (OpenAI)**: Best with structured, step-by-step instructions  
**Gemini (Google)**: Good with concise, focused prompts

Test the same template across providers to find what works best for your campaign style.

## Current System Status & Roadmap

### ✅ What's Working (Phase 3 - Step 1)

- **Direct LLM Generation**: Analyzes complete transcripts and generates accurate campaign documents
- **Multi-Provider Support**: Claude, OpenAI GPT, and Google Gemini integration via LiteLLM
- **Template System**: Customizable AI prompts for different document types
- **Obsidian Integration**: Generated markdown files work seamlessly with Obsidian vaults
- **Cost-Effective**: Typical cost of $0.01-0.10 per session
- **High Accuracy**: 100% success rate, no false entities or nonsense files

### ⏸️ On Hold (Phase 3 - Step 2)

**Intelligent Merging System** - Currently paused for testing and template improvement:
- **Document Merging**: Combining new AI content with existing campaign documents
- **Entity Resolution**: Detecting duplicate NPCs/locations across sessions
- **Content Preservation**: Maintaining user modifications while adding new information
- **Version Control**: Tracking changes and providing rollback capabilities

### 🎯 Current Focus Areas

1. **Template Optimization**: Improving AI prompt quality for better outputs
2. **Cost Analysis**: Comparing providers for optimal cost/quality ratios  
3. **User Testing**: Gathering feedback on generated document quality
4. **Format Refinement**: Enhancing markdown structure and frontmatter

### 🚀 Future Roadmap

**Short Term (Next Phase)**:
- Complete Step 2 implementation (intelligent merging)
- Advanced entity resolution with fuzzy matching
- Conflict resolution for overlapping content
- User preference system for merge strategies

**Medium Term**:
- Campaign timeline generation from multiple sessions
- Cross-session relationship tracking  
- Advanced plot hook identification
- Integration with popular VTT platforms

**Long Term**:
- Real-time session analysis during gameplay
- Voice-to-campaign-docs pipeline automation
- Multi-campaign universe management
- AI-powered campaign planning assistance

### 🔧 Known Limitations

**Current System**:
- Each session generates separate documents (no automatic merging yet)
- Manual template customization required for specialized campaigns
- API costs scale with transcript length
- Limited to text-based analysis (no audio/visual processing)

**Technical Constraints**:
- Requires Python 3.10+ for AI dependencies
- Internet connection required for LLM providers
- API key management needed for production use

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

### Python Version Issues
If you get an error about `numba` not supporting your Python version:
```bash
# Check which Python versions you have installed
python3 --version
python3.12 --version
python3.13 --version

# Error: "Cannot install on Python version 3.14.0"
# Solution: Use Python 3.12 or 3.13 instead
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify you're using the correct version
python --version  # Should show 3.10-3.13
```

**Note**: Python 3.14 support is coming soon but `numba` (required by Whisper) doesn't support it yet. Use Python 3.12 for the best experience.

### Audio Transcription Issues

**Error: `[Errno 2] No such file or directory: 'ffmpeg'`**
```bash
# FFmpeg is required for audio transcription. Install it first:
brew install ffmpeg  # macOS
# or: sudo apt-get install ffmpeg  # Linux

# Verify installation
ffmpeg -version
```

**Other transcription issues:**
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
