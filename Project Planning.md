# Notes on this Project

## Links
- guide part 1: https://medium.com/@brandonharris_12357/automating-d-d-notetaking-with-ai-89ecd36e8b0e
- guide part 2: https://medium.com/@brandonharris_12357/level-up-your-d-d-session-notes-useful-ai-prompts-cleanup-scripts-ca959de9a541
- Repo for part 2: https://github.com/VCDragoon/dnd-transcript-cleanup

## Project Goal
Create a system to track complex and dynamic storyline, character information, world building, sessions feedback, scheduling chat. Ideally something will record and transcript the voice chat into a script then that script will be used to to create a summary of the gaming session. These games will be played online using Discord.
- goal is to run this on a headless server, 1st as a commandline script interface then later with a web interface.

### future goals
- automated process (give audio files -> summary doc)
- create & update location, NPC, Special Items, Players documents

## Tools
- Discord
- Discord Bot [Craig](https://craig.chat/) to record sessions with
    - will create multiple files, one for each player
- [Whisper](https://github.com/openai/whisper) Transcribing AI tool
    - requires the command-line tool [ffmpeg](https://ffmpeg.org/)
- Python scripts for cleanup and collation (in the transcript_cleanup folder)
- [Obsidian](https://obsidian.md/) used as the game note store

## Process to create a POC ✅ **Phase 1 COMPLETED**
1. ✅ [DONE] Record a session on Discord using the Craig bot
    - ✅ [DONE] then clip them to under 10 mins for easy testing
2. ✅ [DONE] Transcribe the recordings using Whisper
    - ✅ [DONE - Phase 1] Created `transcribe/whisper_transcribe.py` - comprehensive script for processing flac files/folders/zip files with proper configuration and progress tracking
        - Supports all input formats (zip, folder, file list)
        - Configurable Whisper settings via JSON config and command line
        - Progress tracking and comprehensive error handling
        - Proper TSV output compatible with cleanup pipeline
    - ✅ [DONE] run some tests to see how the different Whisper models work with the test files
3. ✅ [DONE - Phase 1] Merge, sort, organize, and clean the tsv files
    - ✅ [DONE - Phase 1] **Major improvements made**: Created `transcript_cleanup_v2.py` with shared utilities, professional logging, and modern configuration
    - ✅ Successfully processes individual TSV files → merged chronological transcript → text replacements → final output
    - ✅ Comprehensive testing completed with real session data
4. ✅ [DONE] Use the cleaned up script to create a summary with an LLM API
    - ✅ [DONE] Created comprehensive AI prompt templates in `AI_Prompts/` directory
    - ✅ Templates for: NPC profiles, location documentation, character tracking, story summaries, encounter documentation
    - ✅ Designed for use with ChatGPT custom GPTs or Claude models
5. 🔄 [PARTIAL] Save the info in markdown files for Obsidian
    - ✅ AI prompts generate markdown-compatible output
    - 🔄 Could add automated markdown generation in Phase 2

## Whisper notes
- Whisper does some funky things when filling the gaps in between silencing. These two parameters may help with this a LOT:
    - `condition_on_previous_text` False
    - `compression_ration_threshold` `1.8` (or something lower than the default `2.4`)

### Sample bash command to start Whisper transcribing a file
```bash
whisper --model turbo --language en --condition_on_previous_text False --compression_ratio_threshold 1.8 --output_format tsv --fp16 False 
```

## Merge, sort, organize, and clean up the transcriptions Notes
Things that need fixed (the current scripts in transcript_cleanup should do all this): 
- Each file contains the transcript for just one speaker — to get a FULL session transcript, not only will we need to merge all the speaker files, but they also need to be sorted in speaking order
- Whisper seems to randomly split lines of dialogue, these need to be "unsplit"
- Fix Incorrect Words: Whisper can miss some of the most important proper nouns, like PC names. We need to automate fixing as many of those as possible
- The raw transcriptions tend to include spoken idiosyncrasies. For example: “I think” said a lot, “um”s, “uh”s, repeating lot of words, etc. We want to clean these out as they will not be helpful for creating the session notes.

We will work with the Whisper .tsv files.

# Next steps
- Create a transcoding script with the following requirements
    - take an input of a zip file of flac files, a folder of flac files or a list of flac files.
        - if zip, unzip it into a folder then read in all the flac files for processing
    - uses these defaults:
        - Model: turbo
        - condition_on_previous_text: False
        - compression_ratio_threshold: 1.8
        - output_format: tsv
        - fp16: True
        - language: en
    - have a config file where these can be set/changed
    - also make it were they can be changed on cmd line inputs
    - Create an output folder for the tsv files
    - show the progress of transcribing
        - show which file is being processed, and output from whisper
        - show that you are on x of y files
    - we want good error reporting for when things go wrong as well as telling the user what got processed and what did not

# Implementation Plan for Whisper Transcription Script

## Overview
Create a new Python script `whisper_transcribe.py` in the `transcript_cleanup/` directory that automates the transcription of FLAC audio files using OpenAI Whisper.

## Requirements from Project Planning.md:
- Support input formats: zip file, folder of FLAC files, or list of FLAC files
- Default Whisper settings: turbo model, condition_on_previous_text=False, compression_ratio_threshold=1.8, TSV output, fp16=True, English language
- Configuration file support with command-line overrides
- Progress tracking and error reporting
- Automatic output folder creation

## Implementation Steps:

### 1. Script Architecture
- Create `whisper_transcribe.py` as the main script
- Create `whisper_config.py` for configuration management
- Use argparse for command-line interface
- Integrate with existing project structure

### 2. Core Features
- **Input handling**: Detect and process zip files, directories, or file lists
- **Zip extraction**: Temporary extraction with cleanup
- **Whisper integration**: Use the whisper Python API
- **Progress tracking**: Show current file (x of y) and Whisper output
- **Error handling**: Comprehensive error reporting and recovery
- **Output management**: Organized TSV file output with proper naming

### 3. Configuration System
- Default config matching requirements (turbo, fp16=True, etc.)
- JSON/Python config file support
- Command-line parameter overrides
- Integration with existing config.py pattern

### 4. Testing Strategy
- Test with the provided test files in `/audio-tests/session-zero-cuts/`
- Validate zip file processing
- Verify error handling and progress reporting
- Ensure proper integration with existing transcript cleanup pipeline

### 5. Dependencies
- Uses existing project dependencies: pandas, colorama
- Requires: openai-whisper, zipfile (built-in), argparse (built-in)
- Will check for whisper installation and provide helpful error messages

### 6. Output Structure
- Creates organized output folders
- TSV files named consistently with existing patterns
- Maintains compatibility with existing `transcript_cleanup.py` pipeline

# Code Review & Architecture Improvements

## Current State Analysis ✅

**Strengths:**
- Clear separation of concerns (transcribe → cleanup → AI prompts)
- Good configuration management with defaults
- Comprehensive error handling and progress tracking
- Well-documented with README files
- Functional and tested pipeline

**Pain Points Identified:**

### 🔴 Critical Issues
1. **No Dependency Management** - Missing requirements.txt/pyproject.toml
2. **Hardcoded Paths** - Absolute paths in configs reduce portability
3. **Monolithic Functions** - 100+ line functions in transcript_cleanup.py
4. **Config Inconsistency** - Two different config systems (whisper vs cleanup)
5. **Manual File Management** - No automation for moving files between stages

### 🟡 Medium Issues
6. **Code Duplication** - Text replacement logic exists in multiple places
7. **Limited Testing** - Only manual integration tests
8. **No Logging System** - Only colorama print statements
9. **Import Pollution** - Global imports and config loading
10. **Data Format Coupling** - TSV format assumptions throughout

## Phase 1: Foundation (Quick Wins) ✅ **COMPLETED**

**Implementation Results:**
- ✅ **Dependency Management**: Added `requirements.txt` with core and testing dependencies
- ✅ **Shared Config System**: Created `shared_utils/config.py` with JSON configs + environment variable support (TTRPG_ prefixed)
- ✅ **Logging Framework**: Built `shared_utils/logging_config.py` with colored, structured logging replacing all colorama prints
- ✅ **Common Utilities**: Extracted to `shared_utils/` - text processing, file operations, comprehensive functionality
- ✅ **Unit Testing**: 23 comprehensive tests with 100% pass rate using pytest framework

**New Phase 1 Scripts Created:**
- ✅ `transcript_cleanup/transcript_cleanup_v2.py` - Modernized main processor
- ✅ `transcript_cleanup/json_text_replace_v2.py` - Improved text replacement tool
- ✅ `transcript_cleanup/README.md` - Comprehensive usage documentation
- ✅ Legacy scripts preserved in `transcript_cleanup/OLD/` for reference

**Testing & Validation:**
- ✅ All 23 unit tests pass (config, text processing, file operations)
- ✅ Integration testing completed with `transcripts-test-data/`
- ✅ Successfully processed 6 TSV files (226 → 78 cleaned rows → 51 speaker segments)
- ✅ Applied 17 text replacements and generated final transcripts
- ✅ Comprehensive error handling and progress tracking verified

**Benefits Realized:**
- 🚀 **Professional Logging**: Clear, colored progress information with proper levels
- 🚀 **Unified Configuration**: Environment variables + JSON configs work seamlessly
- 🚀 **Error Resilience**: Graceful handling of missing files and invalid data  
- 🚀 **Performance**: Shared utilities make processing more efficient
- 🚀 **Maintainability**: Code is now modular, well-tested, and documented
- 🚀 **Backward Compatibility**: Legacy systems can migrate gradually

### ✅ Phase 2: KISS-Focused Improvements (COMPLETED)

**Implementation Results:**
- ✅ **Unified CLI Interface**: Created `main.py` with subcommands (transcribe, cleanup, replace, process)
- ✅ **Pipeline Automation**: `ttrpg process` command chains operations automatically
- ✅ **Configurable Cleanup Steps**: Simple enable/disable flags in config (not over-engineered plugins)
- ✅ **Enhanced User Experience**: Better help text, error handling, and progress tracking
- ✅ **KISS Architecture**: Avoided plugin complexity, used simple function lists instead

**New Phase 2 Components:**
- ✅ `main.py` - Main CLI entry point with comprehensive help
- ✅ `cli/commands/` - Individual command modules (transcribe_cmd, cleanup_cmd, replace_cmd, process_cmd)
- ✅ `transcript_cleanup/cleanup_steps.py` - Simple configurable cleanup pipeline
- ✅ Enhanced `shared_utils/config.py` - Added cleanup step enable/disable flags
- ✅ Enhanced `shared_utils/text_processing.py` - Auto-detects new cleanup system

**Testing & Validation:**
- ✅ All CLI subcommands working properly with comprehensive help
- ✅ Pipeline automation successfully tested (cleanup-only mode validated)
- ✅ Configurable cleanup steps process test data correctly (226 → 78 → 51 segments)
- ✅ Backward compatibility maintained - legacy scripts still functional
- ✅ Error handling improved with proper CLI exit codes

**Benefits Realized:**
- 🚀 **Single Command Workflow**: `ttrpg process audio/ --output-dir session --all-steps`
- 🚀 **Better User Experience**: Comprehensive help, clear error messages, progress tracking
- 🚀 **Flexible Processing**: Enable/disable cleanup steps without code changes
- 🚀 **Maintainable Code**: Simple architecture following KISS principles
- 🚀 **Future-Ready**: Foundation for Phase 3 without architectural debt

### Phase 3: Production Readiness (Planned)
- **Enhanced Error Recovery**: Resume interrupted processing workflows
- **Docker Containerization**: Consistent deployment across environments  
- **Performance Optimizations**: Large audio file processing improvements
- **Optional API Layer**: Foundation for potential web interface
- **Extended AI Integration**: More automated prompt application

**Phase 2 successfully delivered practical improvements that add real value while maintaining the KISS philosophy and avoiding over-engineering.**

---

# Notes for someday, ignore for now:
- https://github.com/openai/whisper/discussions/2570

## ideas to improve
- beam_search=5, if processing time is not really a problem.
- ffmpeg pure-silence filtering.
- efficient VAD processing to remove as noise as possible

## ore ideas
if processing time is not a problem for you, here is perhaps the ultimate way to get a good SRT.

    Do all we explained above to get a TXT transcription as clean and accurate as possible, without hallucination:
    a- use VAD to chunk the sound file, removing noise parts.
    b- use ffmpeg to remove silent parts from chunks, and apply a loudness normalization.
    c- use the markers procedure above, possibly doing several processing of some chunks. Certainly you will need different markers for each language, having a native speaker to create it. Use a pertinent initial_prompt to get these markers as well recognized as possible, as explained above.
    d- use Whisper large model, with beam_search=5.

    Do a synchronization of Whisper timestamps over the clean TXT using my WhisperTimeSync tool on the original sound, as explained here:
    https://github.com/EtienneAb3d/WhisperTimeSync

 faster-whisper https://github.com/SYSTRAN/faster-whisper and its integrated VAD (Silero-VAD). Since faster-whisper is 4-10X quicker, we've been able to use the full default set of parameters (beam_size = 5, best_of = 5, temperatures = (0, 0.2, 0.4, etc.) in our pipelines. Using any VAD to remove non-speech segments and then passing the data through the accelerated model with all of the fallback options is almost a foolproof solution. We also tuned the no_speech_threshold and the compression_ratio_threshold.

options = {"task":"transcribe","language":"English","fp16":fp16,'no_speech_threshold':0.1, "condition_on_previous_text": False, "logprob_threshold": -1.00, "without_timestamps":True}
result = whisper.transcribe(wmodel, audio=s['fname'], verbose=False, **options)

- fp16 is boolean, it can be set to true only if running on GPU, otherwise set it to false. It is more to save memory on the gpu if your gpu has little memory. If you set to true and running on CPU, it will still default to fp32 but will throw out some warning message to say that fp16 is only available on GPU.
- no_speech_threshold is to tell whisper that as long as whisper thinks there is 10% chance of no-speech, just treat it as no speech. Too high a value and whisper will think there is speech it cannot figure out and it will just throw some random rubbish. I find it good to set a low value especially if the audio file has music or lots of noise.
- 

----

Look at using 
https://github.com/EtienneAb3d/WhisperHallu
https://github.com/SYSTRAN/faster-whisper
https://github.com/EtienneAb3d/WhisperTimeSync