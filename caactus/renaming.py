# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 10:45:59 2024

@author: q243js
"""

import os
import pandas as pd
import shutil
import re

def get_input_directory():
    """
    Prompt the user to enter the directory path of the original tif-files to be imported.
    Returns:
    str: The input directory path entered by the user.
    """
    return input("Enter the directory path of the .tif files to be imported: ")

def get_output_directory():
    """
    Prompt the user to enter the directory path where the renamed tif-files should be saved.
    Returns:
    str: The output directory path entered by the user.
    """
    return input("Enter the directory path where the renamed .tif files should be saved: ")

def get_csv_file():
    """
    Prompt the user to enter the path of the .csv file to be imported.
    Returns:
    str: The input CSV file path entered by the user.
    """
    return input("Enter the path of the .csv file containing new file names: ")

def natural_sort_key(s):
    """
    Key function for natural sorting of file names.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def main():
    input_dir = get_input_directory()
    output_dir = get_output_directory()
    csv_file = get_csv_file()

    # Load the new names from the CSV file
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"The file {csv_file} was not found.")
        exit()

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # List all files in the directory, excluding hidden/system files
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and not f.startswith('.')]

    # Sort files using natural sort order
    files.sort(key=natural_sort_key)

    # Ensure the number of new names matches the number of files
    if len(df) != len(files):
        print("The number of new names does not match the number of files.")
        print(f"Number of files: {len(files)}")
        print(f"Number of new names: {len(df)}")
    else:
        # Iterate over the DataFrame and rename files
        for idx, row in df.iterrows():
            # Construct the new file name dynamically based on the columns in the DataFrame
            new_file_name = "_".join([f"{col}-{row[col]}" for col in df.columns]) + ".tif"
            
            # Get the current file name
            current_file_name = files[idx]
            
            # Full path to the current and new file
            current_file_path = os.path.join(input_dir, current_file_name)
            new_file_path = os.path.join(output_dir, new_file_name)
            
            # Copy and rename the file to the output directory
            shutil.copy(current_file_path, new_file_path)
            print(f"Renamed '{current_file_name}' to '{new_file_name}'")

        print("Batch renaming completed.")

if __name__ == "__main__":
    main()