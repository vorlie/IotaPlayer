import os
import re

def clean_text(text):
    # Replace arrows with "-"
    text = text.replace("⧸", "-")
    # Remove special characters, keeping only those usable on a US keyboard
    text = re.sub(r'[^A-Za-z0-9\s!@#$%^&*()_+=\-\[\]{}|\\;:\'",.<>/?`~]', '', text)

    # Strip extra spaces
    text = ' '.join(text.split())

    return text

def remove_trailing_number(filename):
    base, extension = os.path.splitext(filename)
    # Remove trailing numbers followed by space before the extension
    base = re.sub(r'\s+\d+$', '', base)
    return base + extension

def clean_filenames(directory):
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".mp3"):
            # Clean the filename
            cleaned_filename = clean_text(filename)
            
            # Remove trailing numbers
            new_filename = remove_trailing_number(cleaned_filename)

            # Construct full file paths
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)

            # Rename the file only if new name is different
            if old_path != new_path:
                os.rename(old_path, new_path)
                print(f'Renamed: {filename} -> {new_filename}')

# Specify the directory containing your .mp3 files
directory = 'C:\\Users\\karol\\Music\\Nightcore'

clean_filenames(directory)