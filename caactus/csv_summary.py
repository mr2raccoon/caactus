# -*- coding: utf-8 -*-
"""
Created on Thu May 16 10:09:45 2024

@author: q243js
"""

from pathlib import Path  # For handling file system paths
import pandas as pd  # For data manipulation
import numpy as np  # For numerical operations
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
    return input("Enter the directory path of the summary-csv-files to be saved to: ")

def get_pixel_size():
    """
    Prompt the user to enter the pixel size from the microscopy software.

    Returns:
    float: The pixel size entered by the user.
    """
    while True:
        try:
            pixel_size = float(input("Enter the pixel size you read out from the microscopy software: "))  # example: 0.454 
            return pixel_size
        except ValueError:
            print("Please enter a valid number for the pixel size.")

def process_csv_files(input_dir, output_dir, pixel_size):
    """
    Process all .csv files in the input directory and save the summary to the output directory.

    Parameters:
    input_dir (str): Path to the directory containing .csv files.
    output_dir (str): Path to the directory where summary .csv files will be saved.
    pixel_size (float): The pixel size from the microscopy software.
    """
    # Ensure the input directory is a valid path
    input_path = Path(input_dir)
    files = input_path.glob('*.csv')  # Use .rglob to include subdirectories if needed

    dfs = list()
    for f in files:
        data = pd.read_csv(f, usecols=["Predicted Class", "Size in pixels"])
        # .stem is method for pathlib objects to get the filename without the extension
        data['file'] = f.stem
        dfs.append(data)

    df = pd.concat(dfs, ignore_index=True)

    # Split the file column, then delete it, transform pixel size to size in µm
 #%%  splits the file column, then deletes it, transforms pixel size to size in µm (info based on microscopy metadata) 
    df['strain'] = df['file'].str.split('_').str[1].replace("strain-", "")
    df['storage'] = df['file'].str.split('_').str[2].replace("storage-", "")
    df['time'] = df['file'].str.split('_').str[3].replace("time-", "")
    df['parallel'] = df['file'].str.split('_').str[4].replace("parallel-", "")
   
    #df = df.drop(columns="file")
     
    df["size_µm"] =  df["Size in pixels"] ** pixel_size

    # Save the cleaned dataframe
    print(df.info())
    print(df.head())

    df_clean = df

    print(df_clean.info())

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    df_clean.to_csv(os.path.join(output_dir, 'df_clean.csv'), index=False)

def main():
    input_dir = get_input_directory()
    output_dir = get_output_directory()
    pixel_size = get_pixel_size()
    process_csv_files(input_dir, output_dir, pixel_size)

if __name__ == "__main__":
    main()








