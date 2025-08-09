# Whisper Transcription Script

This script automates the transcription of FLAC audio files using OpenAI Whisper, producing TSV files compatible with the existing `transcript_cleanup.py` pipeline.

## Features

- ✅ Support for zip files, directories, or individual audio files
- ✅ Configurable Whisper settings with sensible defaults
- ✅ Command-line interface with progress tracking
- ✅ Compatible TSV output format (integer millisecond timestamps)
- ✅ Comprehensive error handling and reporting
- ✅ Integration with existing transcript cleanup pipeline

## Requirements

- Python 3.7+
- OpenAI Whisper: `pip install openai-whisper`
- Dependencies: pandas, colorama (already used in project)

## Basic Usage

### Transcribe a directory of FLAC files:
```bash
python whisper_transcribe.py /path/to/audio/files/ --output-dir transcripts
```

### Transcribe a zip file:
```bash
python whisper_transcribe.py session_audio.zip --output-dir transcripts
```

### Transcribe specific files:
```bash
python whisper_transcribe.py file1.flac file2.flac --output-dir transcripts
```

### Use different Whisper model:
```bash
python whisper_transcribe.py audio_files/ --model large-v2 --output-dir transcripts
```

## Configuration

### Default Settings (as per Project Planning.md requirements):
- Model: turbo
- Language: en
- condition_on_previous_text: False  
- compression_ratio_threshold: 1.8
- output_format: tsv
- fp16: True (auto-disabled on CPU)

### Command Line Options:
```bash
python whisper_transcribe.py --help
```

Key options:
- `--model`: Choose Whisper model (tiny, base, small, medium, large, large-v2, large-v3, turbo)
- `--output-dir`: Output directory for TSV files
- `--no-fp16`: Disable FP16 for CPU-only systems
- `--language`: Language code (default: en)
- `--compression-ratio-threshold`: Adjust compression ratio
- `--quiet`: Reduce output verbosity
- `--no-color`: Disable colored output

### Configuration File:
Create a default config file:
```bash
python whisper_transcribe.py --create-config my_config.json
```

Use custom config:
```bash
python whisper_transcribe.py audio/ --config my_config.json
```

## Integration with Existing Pipeline

The script produces TSV files that work seamlessly with the existing `transcript_cleanup.py`:

1. Run transcription:
```bash
cd transcribe
python whisper_transcribe.py session_audio/ --output-dir session_transcripts
```

2. Move TSV files to session directory:
```bash
cp session_transcripts/*.tsv ../sessions/session_name/
```

3. Run existing cleanup pipeline:
```bash
cd ../sessions/session_name/
python ../../transcript_cleanup/transcript_cleanup.py
```

## Testing

Test with provided audio files:
```bash
cd transcribe
python whisper_transcribe.py ../audio-tests/session-zero-cuts/ --output-dir test-output --no-fp16
```

## Output Format

The script produces TSV files with the format expected by `transcript_cleanup.py`:
- Timestamps in integer milliseconds
- Three columns: start, end, text
- Compatible with existing processing pipeline

## Performance Notes

- Turbo model is fastest but may be less accurate for complex audio
- large-v2 model is more accurate but slower
- Use `--no-fp16` on CPU-only systems to avoid warnings
- Processing time scales with audio length and model size

## Error Handling

The script provides detailed error reporting:
- Missing dependencies (Whisper installation)
- Unsupported file formats
- Processing failures with specific error messages
- Summary report showing successful vs failed transcriptions

## Example Workflow

Complete workflow from audio to processed transcripts:

```bash
# 1. Transcribe audio files
cd transcribe
python whisper_transcribe.py session_audio.zip --output-dir session_1_transcripts

# 2. Setup session directory (if needed)
mkdir -p ../sessions/session_1

# 3. Copy TSV files to session directory  
cp session_1_transcripts/*.tsv ../sessions/session_1/

# 4. Update config.py for the session
# Edit transcript_cleanup/config.py:
# SESSION_NAME = "sessions"
# PART = "session_1"

# 5. Run cleanup pipeline
cd ../sessions/session_1
python ../../transcript_cleanup/transcript_cleanup.py
```

This will produce the final processed transcript files ready for AI prompt processing.