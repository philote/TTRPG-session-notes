# config.py

import os

# Configurable parameters

# Session name and part are folder names for storing your recordings
SESSION_NAME = "COS Session 4" # This is the main folder name for the session
PART = 'Part 1' # If your recordings are split into different folder parts, change this to the appropriate part


# Base path configuration for the file directory
BASE_PATH = os.path.join('C:\\', 'Users', 'brand', 'DND', '_ Curse of Strahd', '0. Craig Recordings', SESSION_NAME, PART)

# Name mappings - change these to your player's craig discord names 
# and map them to their character names
NAME_MAPPINGS = {
    'gradels': 'Izzy',
    'blue': 'DM'
}

# Text length settings
SHORT_DUPLICATE_TEXT_LENGTH = 4  # Maximum text length for duplicates to be considered
MERGE_THRESHOLD = 0.01     # Threshold for merging text based on 'end' and 'start'
SHORT_TEXT_LENGTH = 1      # Maximum text length to be removed

# Silence-related gibberish removal (optional cleanup step)
REMOVE_SILENCE_GIBBERISH = True  # Enable/disable silence gibberish removal
SILENCE_GIBBERISH_PATTERNS = [
    "you", "You", "Thank you", "Thank You", "thank you.", "Thank you.", 
    "Hmm", "hmm", "Uh", "uh", "Oh", "oh", "Ah", "ah", "Um", "um",
    "Mm", "mm", "Mm-hmm", "mm-hmm", "Uh-huh", "uh-huh", "Yeah", "yeah",
    "Yep", "yep", "Yes", "yes", "No", "no", "Okay", "okay", "OK", "ok",
    "Alright", "alright", "All right", "all right", "Right", "right",
    "Well", "well", "So", "so", "I mean", "i mean", "Like", "like"
]  # Common gibberish patterns that Whisper generates during silence

# CSV output filenames
PROCESSED_CSV_SUFFIX = '_processed.csv'
COMBINED_CSV_FILENAME = f'{SESSION_NAME}_{PART}_processed.csv'
MERGED_CSV_FILENAME = f'{SESSION_NAME}_{PART}_merged.csv'
FINAL_TXT_FILENAME = f'{SESSION_NAME}_{PART}_final.txt'
REPLACEMENTS_FILE = 'merge_replacements.json'  # Path to replacements JSON file

# Overlap Splitting
MAX_LENGTH = 50000 # Maximum length of one part of the transcript in characters
OVERLAP = 3000 # Number of characters to overlap between parts