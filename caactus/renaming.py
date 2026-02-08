#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse  # For command-line parsing
import os  # For interacting with the file system
import re  # For natural sorting using regex
import shutil  # For copying and renaming files
import sys  # For error handling and exit

import pandas as pd  # For handling CSV data

from caactus.utils import load_config


DESCRIPTION = """Rename input files to match common naming scheme used in caactus.

More description. Dolor tempor dolore ut aliqua mollit enim Lorem ad culpa laboris
consectetur dolore. Id laboris cillum adipisicing laborum consectetur ex tempor. Eu
occaecat amet laboris ex reprehenderit voluptate qui sit. Laboris consectetur
reprehenderit cillum dolore laborum sunt consectetur quis nisi sint velit.

Fugiat incididunt dolor culpa aute. Aute nisi occaecat id commodo culpa labore ut.
Cillum anim sunt ullamco ex minim.
"""


def natural_sort_key(s):
    """
    Key function for natural sorting of file names.
    Splits strings into parts of digits and non-digits for natural ordering.
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def run(main_folder, input_path, output_path, csv_rename):
    input_dir = os.path.join(main_folder, input_path)
    output_dir = os.path.join(main_folder, output_path)
    csv_file = os.path.join(main_folder, csv_rename)

    # Load new names from the CSV file
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"The file {csv_file} was not found.")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # List and sort files naturally
    files = [f for f in os.listdir(input_dir)
             if os.path.isfile(os.path.join(input_dir, f))
             and not f.startswith('.')]
    files.sort(key=natural_sort_key)

    if len(df) != len(files):
        print("The number of new names does not match the number of files.")
        print(f"Number of files: {len(files)}")
        print(f"Number of new names: {len(df)}")
    else:
        for idx, row in df.iterrows():
            new_file_name = "_".join(
                [f"{col}-{row[col]}" for col in df.columns]) + ".tif"
            current_file_name = files[idx]
            current_file_path = os.path.join(input_dir, current_file_name)
            new_file_path = os.path.join(output_dir, new_file_name)

            shutil.copy(current_file_path, new_file_path)
            print(f"Renamed '{current_file_name}' to '{new_file_name}'")

        print("Batch renaming completed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        default="config.toml",
        help="Path to config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    script_key = "renaming"

    if script_key not in config:
        print(f"Missing configuration section: [{script_key}]")
        sys.exit(1)

    section = config[script_key]
    run(
        config["main_folder"],
        section["input_path"],
        section["output_path"],
        section["csv_rename"],
    )


if __name__ == "__main__":
    main()

