import pandas as pd
import os
import re
import csv
import json
from colorama import Fore, Style, init


# first check to see if there is a config.py file in the same directory as this script
# if there is not, then copy the default_config.py file to config.py
# check just for the file name, not the full path
# if not os.path.isfile('config.py'):
#     import shutil
#     shutil.copyfile('default_config.py', 'config.py')
    
# # do the same for the merge_replacements.json
# if not os.path.isfile('merge_replacements.json'):
#     import shutil
#     shutil.copyfile('default_merge_replacements.json', 'merge_replacements.json')

import config as config  # Import configuration

# Initialize colorama
init()

# Set variables from config
part_name = config.PART
session_name = config.SESSION_NAME
base_path = config.BASE_PATH
name_mapping = config.NAME_MAPPINGS
max_length = config.MAX_LENGTH
overlap = config.OVERLAP

# Function to load replacements from JSON file
def load_replacements(file_path):
    script_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(script_dir, file_path)
    with open(abs_file_path, 'r') as file:
        return json.load(file)
    
# Apply replacements to text
def apply_replacements(text, replacement_map):
    for primary_name, aliases in replacement_map.items():
        for alias in aliases:
            pattern = re.compile(re.escape(alias), re.IGNORECASE)
            text = pattern.sub(primary_name, text)
    return text

# Processing TSV files
def process_tsv_to_csv(file_path):
    # Load the TSV file to a pandas DataFrame
    df = pd.read_csv(file_path, delimiter='\t')

    # Find and remove duplicate 'text' values with a length threshold from config
    short_texts = df[df['text'].str.len() <= config.SHORT_DUPLICATE_TEXT_LENGTH]
    duplicate_texts = short_texts[short_texts.duplicated(subset='text', keep=False)]
    duplicate_count = duplicate_texts['text'].value_counts()
    
    # Print duplicate information
    print("\n" + f"{Fore.CYAN}Duplicate Short Text Info:{Style.RESET_ALL}")
    for text, count in duplicate_count.items():
        print(f"\ttext: '{Fore.YELLOW}{text}{Style.RESET_ALL}' occurrences: {Fore.GREEN}{count}{Fore.RED}{Style.RESET_ALL}")
    print("\r")

    # Remove duplicates based on the length configuration
    df = df[~((df['text'].str.len() <= config.SHORT_DUPLICATE_TEXT_LENGTH) & df.duplicated(subset='text', keep='first'))]
    removed_duplicates_count = len(short_texts) - len(df[df['text'].str.len() <= config.SHORT_DUPLICATE_TEXT_LENGTH])

    print(f"{Fore.CYAN}Total duplicate rows of texts with {config.SHORT_DUPLICATE_TEXT_LENGTH} characters or less removed: {Fore.GREEN}{removed_duplicates_count}{Style.RESET_ALL}\n")

    # Merge rows based on 'end' and 'start' values
    merged_count = 0
    i = 0
    while i < len(df) - 1:
        if abs(df.iloc[i]['end'] - df.iloc[i + 1]['start']) <= config.MERGE_THRESHOLD:
            end_val = df.iloc[i + 1]['end']
            combined_text = str(df.iloc[i]['text']) + " " + str(df.iloc[i + 1]['text'])
            df.loc[df.index[i], 'end'] = end_val
            df.loc[df.index[i], 'text'] = combined_text
            df = df.drop(df.index[i + 1])
            df = df.reset_index(drop=True)
            merged_count += 1
        else:
            i += 1
    print(f"Total rows merged: {merged_count}")

    # Remove rows with short text based on config length
    short_text_count = df[df['text'].apply(lambda x: len(x) if isinstance(x, str) else 0) <= config.SHORT_TEXT_LENGTH].shape[0]
    df = df[df['text'].apply(lambda x: len(x) > config.SHORT_TEXT_LENGTH if isinstance(x, str) else False)]
    print(f"Rows removed with short text: {short_text_count}")

    # Second duplicate check
    duplicate_texts = df[df.duplicated(subset='text', keep=False)]
    duplicate_count = duplicate_texts.groupby('text').size()
    print("\n" + f"{Fore.CYAN}Remaining Duplicate Text Info:{Style.RESET_ALL}")
    for text, count in duplicate_count.items():
        print(f"\ttext: '{Fore.YELLOW}{text}{Style.RESET_ALL}' occurrences: {Fore.GREEN}{count}{Fore.RED}{Style.RESET_ALL}")
    print("\r")
    df = df.drop_duplicates(subset='text', keep='first')
    print(f"{Fore.CYAN}Total duplicate rows removed (pass 2): {Fore.GREEN}{duplicate_texts.shape[0]}{Style.RESET_ALL}\n")    

    # Determine name based on file_path using config mapping
    name = 'Unknown'
    for key in name_mapping:
        if key in file_path:
            name = name_mapping[key]
            break

    # Add 'name' column to DataFrame
    df['name'] = name

    # Save to new CSV file with configurable suffix
    df.to_csv(f'{file_path}{config.PROCESSED_CSV_SUFFIX}', index=False)
    return df

# Merge consecutive rows with the same speaker and save the result
def merge_speaker_texts(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as input_file, \
         open(output_filename, 'w', newline='', encoding='utf-8') as output_file:

        csv_reader = csv.reader(input_file)
        csv_writer = csv.writer(output_file)
        headers = next(csv_reader)
        csv_writer.writerow(headers)

        # Initialize variables to keep track of the merged text and last speaker
        merged_text = ''
        start_point = 0
        end_point = 0
        last_speaker = None
        
        for row in csv_reader:
            start = int(row[0])
            end = int(row[1])
            speaker = row[3]
            text = row[2]
            
            # Check if the current row's speaker is the same as the last row's speaker
            if speaker == last_speaker:
                # Concatenate the text to the merged_text
                merged_text += " " + text

            else:
                # Write the previous speaker's merged text to the output file
                if last_speaker is not None:
                    csv_writer.writerow([start, end, merged_text, last_speaker])
                
                # Reset the merged_text and last_speaker for the current row
                merged_text = text
                last_speaker = speaker

        
        # Write the last speaker's text after the loop ends
        if last_speaker is not None:
            csv_writer.writerow([merged_text, last_speaker])

# Split large text into parts
def split_text(text, max_length=50000, overlap=3000):
    parts, start = [], 0
    while start < len(text):
        end = start + max_length
        if end >= len(text):
            parts.append(text[start:])
            break
        end = text.rfind('\n', start, end) if '\n' in text[start:end] else end
        parts.append(text[start:end])
        start = end - overlap
    return parts

def main():
    dataframes = []
    # Process files in the directory
    for subdir, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.tsv'):
                print("\n" + Fore.LIGHTGREEN_EX + "="*100 + "\n" + Fore.LIGHTGREEN_EX + "="*100 + Style.RESET_ALL + "\n")
                print(f"Processing file: {Fore.LIGHTBLUE_EX}{file}{Style.RESET_ALL}")
                file_path = os.path.join(subdir, file)
                processed_df = process_tsv_to_csv(file_path)
                dataframes.append(processed_df)
                print(f"Processed file: {Fore.LIGHTBLUE_EX}{file}{Style.RESET_ALL}")   

    # Concatenate and save the combined DataFrame
    # if all_data is empty, print a message with the base_path (use a color) and say that probably no files were found ther
    if not dataframes:
        print(f"\n{Fore.LIGHTRED_EX}Error finding files - are you sure this is the right path: {Fore.LIGHTWHITE_EX}'{base_path}'{Style.RESET_ALL}")
    all_data = pd.concat(dataframes).sort_values(by='start')
    combined_csv_path = os.path.join(base_path, config.COMBINED_CSV_FILENAME)
    all_data.to_csv(os.path.join(base_path, config.COMBINED_CSV_FILENAME), index=False)
    print("\n" + f"{Fore.LIGHTMAGENTA_EX}All data combined and saved in: {Fore.LIGHTWHITE_EX}'{config.COMBINED_CSV_FILENAME}'")

    # Merge speaker texts and process replacements
    merged_csv_path = os.path.join(base_path, config.MERGED_CSV_FILENAME)
    merge_speaker_texts(combined_csv_path, merged_csv_path)

    # Load replacements and apply them
    replacements = load_replacements(config.REPLACEMENTS_FILE)
    df = pd.read_csv(merged_csv_path)
    for column in df.columns:
        df[column] = df[column].astype(str).apply(lambda x: apply_replacements(x, replacements))
    concatenated_text = df.apply(lambda row: f"{row['name']}: {row['text']}", axis=1).str.cat(sep='\n')

    # Split text into parts and save
    parts = split_text(concatenated_text, max_length, overlap)
    for i, part in enumerate(parts):
        part_path = os.path.join(base_path, f"Session {config.PART} Final part_{i + 1}.txt")
        with open(part_path, 'w', encoding='utf-8') as file:
            file.write(part)
            
    full_path = os.path.join(base_path, f"Session {config.PART} Final COMPLETE.txt")
    with open(full_path, 'w', encoding='utf-8') as file:
            file.write(concatenated_text)
    print("Consecutive rows with the same speaker have been merged and split into parts.")
    
# run the main function
if __name__ == "__main__":
    main()