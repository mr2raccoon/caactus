#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pathlib import Path  # For handling file system paths
import pandas as pd  # For data manipulation
import os  # For file I/O operations
import argparse  # For command-line argument parsing
import sys  # For exit handling

from caactus.utils import load_config


DESCRIPTION = """Process CSV files and generate a cleaned summary CSV.

This script reads all .csv files in the specified input directory, extracts metadata from filenames.
Also, it compiles a cleaned summary CSV with computed cell sizes in microm2.

The expected filename format is: var1-value1_var2-value2_table.csv
"""


def parse_filename(filename):
    """
    Parse a filename into variable names and values, ignoring '_table' part.

    Parameters:
        filename (str): Filename without the extension.

    Returns:
        dict: Variable-value pairs parsed from the filename.
    """
    filename = filename.replace('_table', '')
    parts = filename.split('_')
    file_metadata = {}
    for part in parts:
        try:
            var_name, var_value = part.split('-')
            file_metadata[var_name] = var_value
        except ValueError:
            raise ValueError(
                f"Filename part '{part}' is not in expected format."
            )
    return file_metadata


def process_csv_files(main_folder, input_path, output_path, pixel_size):
    """
    Process all .csv files in the input directory and output a cleaned CSV.

    Parameters:
        input_dir (str): Directory containing .csv files.
        output_dir (str): Directory to save cleaned summary CSV.
        pixel_size (float): Size of a pixel (used to compute microm size).
    """
    input_path = os.path.join(main_folder, input_path)
    output_path = os.path.join(main_folder, output_path)
    pixel_size = float(pixel_size)

    input_path = Path(input_path)
    files = input_path.glob('*.csv')

    dfs = []
    for f in files:
        data = pd.read_csv(f, usecols=["Predicted Class", "Size in pixels"])
        file_metadata = parse_filename(f.stem)

        for var_name, var_value in file_metadata.items():
            data[var_name] = var_value

        data['filename'] = f.stem
        dfs.append(data)

    if len(dfs) == 0:
        print("No .csv files found in the input directory.")
        return

    df = pd.concat(dfs, ignore_index=True)
    df["size_microm2"] = df["Size in pixels"] * pixel_size ** 2

    os.makedirs(output_path, exist_ok=True)
    df.to_csv(os.path.join(output_path, "df_clean.csv"), index=False)

    print(df.info())
    print(df.head())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        required=True,
        default="config.toml",
        help="Path to config file"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    script_key = "csv_summary"

    if script_key not in config:
        print(f"Missing configuration section: [{script_key}]")
        sys.exit(1)

    section = config[script_key]
    main_folder = config["main_folder"]
    input_path = section["input_path"]
    output_path = section["output_path"]
    pixel_size = float(section["pixel_size"])

    process_csv_files(main_folder, input_path, output_path, pixel_size)


if __name__ == "__main__":
    main()
