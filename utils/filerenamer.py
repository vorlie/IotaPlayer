import os
import re

"""
File Renamer Utility

This script is designed to clean and rename files within a specified directory. 
It is particularly useful for standardizing file names and removing unwanted characters or trailing numbers.

Features:
- Replaces special characters (like arrows) with hyphens.
- Retains only standard US keyboard characters and common symbols.
- Removes extra spaces from file names.
- Strips trailing numbers before file extensions.

Usage:
1. Set the `directory` variable to the path of the directory containing the files you want to rename.
2. Run the script to process and rename all `.mp3` files in that directory.

Customization:
- The `clean_text` function currently retains standard US keyboard characters and common symbols. If you need to allow additional special characters, modify the regular expression in `clean_text` function accordingly.
- For example, to include more symbols, add them to the character class `[^A-Za-z0-9\s!@#$%^&*()_+=\-\[\]{}|\\;:\'",.<>/?`~]` in the `re.sub()` function.

Note: 
Ensure that you have proper backups of your files before running this script as it will rename files in the specified directory.
"""

def clean_text(text):
    """
    Clean and normalize the text by:
    - Replacing special characters (like arrows) with hyphens.
    - Removing characters that are not part of a standard US keyboard set.
    - Stripping extra spaces to avoid formatting issues.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned and normalized text.
    """
    # Replace arrows with "-"
    text = text.replace("⧸", "+")
    text = text.replace("｜", "+")
    text = text.replace("⧹", "+")
    text = text.replace("【Dubstep】", "")
    text = text.replace("Melodic Dubstep", "")
    # Remove special characters, keeping only those usable on a US keyboard
    text = re.sub(r'[^A-Za-z0-9\s!@#$%^&*()_+=\-\[\]{}|\\;:\'",.<>/?`~]', '', text)

    # Strip extra spaces
    text = ' '.join(text.split())

    return text

def remove_trailing_number(filename):
    """
    Remove any trailing numbers from the filename, which are followed by spaces before the file extension.

    Args:
        filename (str): The original filename.

    Returns:
        str: The filename with trailing numbers removed.
    """
    base, extension = os.path.splitext(filename)
    # Remove trailing numbers followed by space before the extension
    base = re.sub(r'\s+\d+$', '', base)
    return base + extension

def clean_filenames(directory):
    """
    Iterate through files in the specified directory, cleaning and renaming `.mp3` files.

    Args:
        directory (str): The path to the directory containing the files to be cleaned and renamed.
    """
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

            # Rename the file only if the new name is different
            if old_path != new_path:
                os.rename(old_path, new_path)
                print(f'Renamed: {filename} -> {new_filename}')

# Specify the directory containing your .mp3 files
directory = 'C:\\Users\\karol\\Music\\Dubstep2'

clean_filenames(directory)