# TTRPG Session Notes Automation

## Originally from
- https://medium.com/@brandonharris_12357/automating-d-d-notetaking-with-ai-89ecd36e8b0e
- https://github.com/VCDragoon/dnd-transcript-cleanup

A complete system for processing Discord voice recordings into organized TTRPG session summaries and campaign management materials.

## Overview

This system provides a complete workflow:
1. **Audio Transcription** (`transcribe/`) - Convert audio files to text using OpenAI Whisper
2. **Transcript Processing** (`transcript_cleanup/`) - Clean and organize transcripts
3. **AI-Powered Documentation** (`AI_Prompts/`) - Generate campaign notes, NPC profiles, and summaries

The workflow involves recording sessions with Craig bot, transcribing with Whisper, processing the transcripts, then using AI prompts to generate comprehensive campaign documentation.

## Quick Start

### 1. Audio Transcription
Convert audio files to TSV transcripts:
```bash
cd transcribe
python whisper_transcribe.py /path/to/audio/files/ --output-dir transcripts
```

### 2. Transcript Processing  
Clean and organize transcripts:
```bash
cd transcript_cleanup
# Configure settings in config.py first
python transcript_cleanup.py
```

### 3. AI Documentation
Use prompts in `AI_Prompts/` with ChatGPT or Claude to generate campaign documentation.

## Setup

1. **Directory Structure**: Place the Whisper-generated transcripts in a directory named after the session (e.g., `SESSION_NAME`). If the session has multiple parts, create subdirectories (e.g., `SESSION_NAME/PART`). For example, sometimes I have 5 hour sessions - I stop and start Craig halfway through the session, so I have two "parts" to process separately.

    **Note:** This script does not combine session parts. This is purely organizational. The script will treat "parts" of a session as completely independent, by design.
    
This is a bit outdated. Right now I no longer have "Parts" and I just leave that variable blank.  Probably some room to update that, but whatever.  Feel free to just point it directly to your session transcript folder.

2. **Transcript Files**: I built this to work with the default .tsv output from Whisper. Each file should be a TSV file (tab-separated values) with the following columns:
    
    - `start`: Start timestamp of the dialogue line.
    - `end`: End timestamp of the dialogue line.
    - `text`: The transcribed dialogue.
    - `speaker`: The speaker's identifier.
    
    Ensure one file per speaker, containing their respective dialogue lines.

    The script will loop through and look for *all* .tsv files in the session/part directory, process them all, then merge them together.
    
3. **Replacement File**: Create a JSON file (`merge_replacements.json`) for any custom word replacements you want. This file will help correct common misinterpretations by Whisper. An example format:
    
    json
    
    Copy code
    
    `{     "Valtor": ["volatore", "walter"],     "Orla": ["ola"] }`
    
    **Note:** The script will look for config.py and merge_replacements.json in the same directory as the script. If they aren't found on the first run, they will be copied from the defaults with default values.

4. **Configuration**: The script uses a few configuration parameters to adjust the cleanup process. These include:
        
        - 'NAME_MAPPING': A dictionary to map Discord speaker names to their respective character names.
        - `DUPLICATE_TEXT_LENGTH`: The maximum length of duplicate lines to remove.
        - `SHORT_TEXT_LENGTH`: The minimum length of lines to keep.
        - `SPLIT_THRESHOLD`: The maximum number of lines in the final transcript before splitting.
        
        You can see all the configuration options in the `config.py` file.

## Usage 
Just about everything should happen automatically, but here's a quick breakdown of the process:


1. **Remove Short Form Duplicates**: Lines of dialogue that are identical and shorter than `DUPLICATE_TEXT_LENGTH` are removed, except for the first occurrence. These duplicates typically include fillers like “yeah” or “okay” and other artifacts.
    
    I found it important to keep this separate from the full duplicate check, because of how we merge the speaker lines later. This removes a lot of the "noise" from the transcript, while preserving more important, meaningful "duplicates" (e.g., "Nat 20!")
    
2. **Merge Close Lines**: Consecutive dialogue lines by the same speaker with less than 0.01 seconds between them are merged, creating a more cohesive dialogue flow.
    
3. **Remove Short Lines**: Lines shorter than `SHORT_TEXT_LENGTH` (like “uh huh” or “oh”) are removed if they don’t add value. Adjust this threshold if you wish.
    
4. **Secondary Duplicate Check**: A second duplicate check is performed on the cleaned dialogue to catch additional redundancies, especially longer, repetitive phrases.
    
5. **Compile All Speakers**: The individual cleaned transcripts are then merged into a single file, sorted by timestamp, ensuring the conversational flow reflects all participants in proper order.
    
6. **Final Merge for Consecutive Dialogue**: Consecutive dialogue from the same speaker are combined to further condense the transcript, making it easier to follow.
    
7. **Word Replacement Pass**: Using the provided replacement file (`merge_replacements.json`), the tool corrects common misinterpretations of specific words or names. This can be useful for unique terms or proper nouns often misinterpreted by Whisper.

    **Note:** The merge_replacements.json file has a key for each "true" word, followed by a list of possible "incorrect" words. The script will replace any "incorrect" words with the "true" word. This is useful for correcting common misinterpretations by Whisper. It does NOT care about capitalization from the incorrect words (e.g,. "Chorus" and "chorus" are treated as the same word).
    
8. **Splitting the Transcript**: If the final transcript is too large, it can be divided into parts for ease of processing in models with input limitations. (This step is optional if not needed).
    

## Running the Script

1. Ensure you have the necessary files in place:
    
    - Whisper-generated TSV transcripts for each speaker.
    - A `merge_replacements.json` file with any required word replacements.
2. Run the script. Console output will display details of the cleanup process, including which duplicates and lines were removed or merged.
    
3. The output will be multiple intermediate files for troubleshooting/evaluation purposes, and a final, cleaned transcript file, ready for review or input into other tools.