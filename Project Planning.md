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

## Process to create a POC
1. [DONE] Record a session on Discord using the Craig bot
    - [DONE] then clip them to under 10 mins for easy testing
2. [DONE] Transcribe the recordings using Whisper
    - [TODO] create a script to take in a folder of flac files, trascribe them, then output a folder of tsv files. Whisper python usage info: https://github.com/openai/whisper?tab=readme-ov-file#python-usage
        - no translations, only supporting english
    - [DONE] run some tests to see how the different Whisper models work with the test files (would be nice if we could use a faster model and still get good results, large-v2 takes a very long time)
3. [TODO] Merge, sort, organize, and clean the tsv files
    - [TODO] review the existing scripts, see if there are improvements to be made
4. [TODO] use the cleaned up script to create a summary with an LLM API
    - [TODO] Review options to do locally or over a cheap/free API
    - [TODO] create templates for different types of data
5. [TODO] save the info in markdown files for Obsidian
    - [TODO] create rules for how and where to save them

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

## Proposed Improvements

### Phase 1: Foundation (Quick Wins)
- **Add dependency management** (requirements.txt)
- **Create shared config system** with environment variable support
- **Add logging framework** (replace colorama prints)
- **Extract common utilities** into shared module
- **Add basic unit tests** for core functions

### Phase 2: Architectural Improvements
- **Implement plugin architecture** for cleanup steps
- **Add pipeline orchestrator** to automate file flow
- **Create data models** with Pydantic for type safety
- **Add CLI framework** (Click/Typer) for better UX
- **Implement factory patterns** for different input types

### Phase 3: Production Readiness
- **Add comprehensive testing** (pytest with fixtures)
- **Create Docker containerization**
- **Add monitoring/metrics** collection
- **Implement graceful error recovery**
- **Add API layer** for future web interface

This approach prioritizes immediate stability improvements while building toward the headless server goal with minimal breaking changes.

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