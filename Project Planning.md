# Notes on this Project

## Links
- guide part 1: https://medium.com/@brandonharris_12357/automating-d-d-notetaking-with-ai-89ecd36e8b0e
- guide part 2: https://medium.com/@brandonharris_12357/level-up-your-d-d-session-notes-useful-ai-prompts-cleanup-scripts-ca959de9a541
- Repo for part 2: https://github.com/VCDragoon/dnd-transcript-cleanup

## Project Goal
Create a system to track complex and dynamic storyline, character information, world building, sessions feedback, scheduling chat. Ideally something will record and transcript the voice chat into a script then that script will be used to to create a summary of the gaming session. These games will be played online using Discord.

### future goals
- automated process (give audio files -> summary doc)
- create & update location, NPC, Special Items, Players documents

## Tools
- Discord
- Discord Bot [Craig](https://craig.chat/) to record sessions with
    - will create multiple files, one for each player
- [Whisper](https://github.com/openai/whisper) Transcribing AI tool
- [Obsidian](https://obsidian.md/) used as the game note store

## Process to create a POC
1. Record a session on Discord using the Craig bot
2. Transcribe the recordings using Whisper
3. Merge, sort, organize, and clean
4. use the cleaned up script to create a summary with an LLM API
5. save the info in markdown files for Obsidian

## Whisper notes
- Whisper does some funky things when filling the gaps in between silencing. These two parameters may help with this a LOT:
    - `condition_on_previous_text` False
    - `compression_ration_threshold` `1.8` (or something lower than the default `2.4`)

### Sample bash command to start Whisper transcribing a file
```bash
whisper --model large-v2 --language en --condition_on_previous_text False --compression_ratio_threshold 1.8 audio-tests/craig-b9CjgsrXsinn-Bj-4whxZg8Ob0zHa1CZxV504QpbuBB.flac/1-ephson.flac
```

## Merge, sort, organize, and clean up the transcriptions Notes
Things that need fixed:
- Each file contains the transcript for just one speaker — to get a FULL session transcript, not only will we need to merge all the speaker files, but they also need to be sorted in speaking order
- Whisper seems to randomly split lines of dialogue, these need to be "unsplit"
- Fix Incorrect Words: Whisper can miss some of the most important proper nouns, like PC names. We need to automate fixing as many of those as possible
- The raw transcriptions tend to include spoken idiosyncrasies. For example: “I think” said a lot, “um”s, “uh”s, repeating lot of words, etc. We want to clean these out as they will not be helpful for creating the session notes.

We will work with the Whisper .tsv files.