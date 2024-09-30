# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 08:33:29 2024

@author: q243js
"""

from pathlib import Path  # For handling file system paths
import pandas as pd  # For data manipulation
import os  # For interacting with the operating system

def get_input_directory():
    """
    Prompt the user to enter the directory path of the .csv files to be imported.

    Returns:
    str: The input directory path entered by the user.
    """
    return input("Enter the directory path of the .csv-files to be imported: ")

def get_output_directory():
    """
    Prompt the user to enter the directory path where the summary .csv files should be saved.

    Returns:
    str: The output directory path entered by the user.
    """
    return input("Enter the directory path where summary .csv-files should be saved: ")

def get_pixel_size():
    """
    Prompt the user to enter the pixel size from the microscopy software.

    Returns:
    float: The pixel size entered by the user.
    """
    while True:
        try:
            pixel_size = float(input("Enter the pixel size from the microscopy software: "))  # example: 0.454 
            return pixel_size
        except ValueError:
            print("Please enter a valid number for the pixel size.")

def parse_filename(filename):
    """
    Parse a filename into variable names and their values, ignoring the last '_table' part.

    Parameters:
    filename (str): The name of the file to be parsed (without the extension).

    Returns:
    dict: A dictionary with variable names as keys and the extracted values as values.
    """
    # Remove the '_table' suffix if present
    filename = filename.replace('_table', '')
    
    # Split the filename by underscores into variable-value pairs
    parts = filename.split('_')
    
    # Extract variable names and values from the format 'variable-varvalue'
    file_metadata = {}
    for part in parts:
        try:
            var_name, var_value = part.split('-')
            file_metadata[var_name] = var_value
        except ValueError:
            raise ValueError(f"Filename part '{part}' is not in the expected 'variable-varvalue' format.")
    
    return file_metadata

def process_csv_files(input_dir, output_dir, pixel_size):
    """
    Process all .csv files in the input directory and save the summary to the output directory.

    Parameters:
    input_dir (str): Path to the directory containing .csv files.
    output_dir (str): Path to the directory where summary .csv files will be saved.
    pixel_size (float): The pixel size from the microscopy software.
    """
    input_path = Path(input_dir)
    files = input_path.glob('*.csv')  # Use .rglob to include subdirectories if needed

    dfs = list()
    for f in files:
        data = pd.read_csv(f, usecols=["Predicted Class", "Size in pixels"])
        # Parse the filename into a dictionary (excluding '_table')
        file_metadata = parse_filename(f.stem)
        
        # Add each metadata as a new column to the DataFrame
        for var_name, var_value in file_metadata.items():
            data[var_name] = var_value
        
        dfs.append(data)

    df = pd.concat(dfs, ignore_index=True)

    # Transform pixel size to size in µm
    df["size_µm"] = df["Size in pixels"] * pixel_size ** 2

    # Save the cleaned dataframe
    print(df.info())
    print(df.head())

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, 'df_clean.csv'), index=False)

def main():
    input_dir = get_input_directory()
    output_dir = get_output_directory()
    pixel_size = get_pixel_size()
    
    process_csv_files(input_dir, output_dir, pixel_size)

if __name__ == "__main__":
    main()