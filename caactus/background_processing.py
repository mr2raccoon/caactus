#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
try:
    import tomllib as tomli  # Python 3.11+
except ModuleNotFoundError:
    import tomli  # Python 3.10

DESCRIPTION = """
## Background Processing (Training)

Removes the **background** from multicut segmentation files.

The largest region (background) is set to `0`, making it transparent in the subsequent **Object Classification** step in ilastik.

This operation runs **in-place** on all `*_Multicut Segmentation.h5` files in the `3_multicut` folder.

If your folder structure is different, you can use **Advanced mode** to enter the **full path** to the folder.

Click **Run**.
"""

def load_config(path="config.toml"):
    """Load TOML configuration file."""
    with open(path, "rb") as f:
        return tomli.load(f)


def process_image(image_path):
    """
    Process a single HDF5 file by zeroing the largest ID in 'exported_data'.

    Parameters:
        image_path (str): Path to the HDF5 file.
    """
    import h5py
    import numpy as np
    try:
        with h5py.File(image_path, 'r+') as img:
            if 'exported_data' not in img:
                raise KeyError(f"'exported_data' dataset not found in {image_path}")

            image = np.array(img['exported_data'])

            ids, counts = np.unique(image, return_counts=True)
            largest_id = ids[counts.argmax()]
            image[image == largest_id] = 0

            img['exported_data'][:] = image
    except Exception as e:
        print(f"Error processing file {image_path}: {e}")


def batch_process_images(main_folder, input_path):
    """
    Process all matching HDF5 segmentation files in the given directory.

    Parameters:
        input_directory (str): Folder containing .h5 files to process.
    """

    input_dir = os.path.join(main_folder, input_path)
    print(f"Input directory: {input_dir}")
    if not os.path.isdir(input_dir):
        print(
            f"Error: Input directory does not exist: {input_dir}\n"
            "Please enter a full (absolute) path to the '7_batch_multicut' folder.",
            flush=True,
        )
        return
    for filename in os.listdir(input_dir):
        if filename.endswith("Segmentation.h5"):
            input_path = os.path.join(input_dir, filename)
            print(f"Processing: {input_path}")
            process_image(input_path)
            print(f"Finished:   {filename}")
    print("Background processing completed.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to configuration file"
    )
    parser.add_argument(
        "-m", "--mode",
        required=True,
        choices=["training", "batch"],
        help="Mode of operation: training or batch"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    script_key = "background_processing"

    if script_key not in config or args.mode not in config[script_key]:
        print(f"Missing configuration section: [{script_key}.{args.mode}]")
        sys.exit(1)

    section = config[script_key][args.mode]
    main_folder = config.get("main_folder", ".")

    batch_process_images(main_folder, section["input_path"])
    


if __name__ == "__main__":
    main()
