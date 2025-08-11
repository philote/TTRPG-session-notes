import json
import re
from collections import defaultdict
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Load the JSON mapping
with open('merge_replacements.json', 'r', encoding='utf-8') as file:
    mapping = json.load(file)

# Read the transcript file
with open('COS ALL SESSIONS.txt', 'r', encoding='utf-8') as file:
    transcript = file.read()

# Perform replacement (ignoring capitalization)
def replace_terms(text, mapping):
    replacement_counts = defaultdict(lambda: defaultdict(int))
    
    for key, values in mapping.items():
        for value in values:
            # Count occurrences before replacement
            matches = re.findall(re.escape(value), text, flags=re.IGNORECASE)
            replacement_counts[key][value] += len(matches)
            # Perform the replacement
            text = re.sub(re.escape(value), key, text, flags=re.IGNORECASE)
    
    # Sort by total replacements per key
    sorted_counts = sorted(replacement_counts.items(), key=lambda x: sum(x[1].values()), reverse=True)
    
    for key, terms in sorted_counts:
        total_replacements = sum(terms.values())
        print(Fore.CYAN + f"{key}:")
        for term, count in terms.items():
            print(Fore.GREEN + f"\t{term}: " + Fore.RED + f"{count}" + Fore.GREEN + " occurrences replaced")
        print(Fore.YELLOW + f"\tTotal replacements for {key}: " + Fore.RED + f"{total_replacements}\n")
    
    return text

# Run the replacement
updated_transcript = replace_terms(transcript, mapping)

# Save the updated transcript
with open('COS ALL TRANSCRIPTS_UPDATED.txt', 'w', encoding='utf-8') as file:
    file.write(updated_transcript)

print(Fore.MAGENTA + "Replacement complete. The updated transcript is saved as 'COS ALL TRANSCRIPTS_UPDATED.txt'")
