#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 13:05:10 2025

@author: kuba
"""


import os  # OS operations
import sys  # System exit
import tomli  # For loading TOML config
import h5py  # For HDF5 file handling
import tifffile  # TIFF file I/O
import vigra  # Image metadata and axistags
import argparse  # Command-line parsing
import imagecodecs  # Optional TIFF compression (loaded if needed)


def load_config(path="config.toml"):
    """Load configuration from a TOML file."""
    with open(path, "rb") as f:
        return tomli.load(f)


def convert_tif_to_h5(input_dir, output_dir):
    """
    Convert all .tif files in input_dir to .h5 files in output_dir,
    using 5D structure and vigra axistags (tzyxc).
    """

    # Ensure output folder exists
    os.makedirs(output_dir, exist_ok=True)

    # Collect all TIFF files from the input directory
    tif_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]

    for tif_file in tif_files:
        tif_path = os.path.join(input_dir, tif_file)

        with tifffile.TiffFile(tif_path) as tiff:
            # Load the image stack
            image_data = tiff.asarray()
            shape = image_data.shape
            print(f"Image data shape: {shape}")

            # Reshape to 5D (t, z, y, x, c) format
            if len(shape) == 3:
                image_data_5d = image_data.reshape((1, 1, *shape))
            elif len(shape) == 4:
                image_data_5d = image_data.reshape((1, *shape))
            else:
                raise ValueError(f"Unexpected image shape: {shape}")

            data_shape = image_data_5d.shape
            axistags = vigra.defaultAxistags("tzyxc")

            # Build .h5 path
            h5_file = os.path.splitext(tif_file)[0] + ".h5"
            h5_path = os.path.join(output_dir, h5_file)

            # Save HDF5 with metadata
            with h5py.File(h5_path, "w") as h5:
                ds = h5.create_dataset(
                    name="data",
                    data=image_data_5d,
                    chunks=(1, 1, 256, 256, 1)
                )
                ds.attrs["axistags"] = axistags.toJSON()
                ds.attrs["data_shape"] = data_shape

        print(f"Converted {tif_file} → {h5_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        required=True,
        default="config.toml",
        help="Path to config file"
    )
    parser.add_argument(
        "-m", "--mode",
        required=True,
        choices=["training", "batch"],
        help="Define processing mode: training or batch"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    script_key = "tif2h5py"

    # Ensure proper configuration exists
    if script_key not in config or args.mode not in config[script_key]:
        print(f"Missing configuration for [{script_key}.{args.mode}]")
        sys.exit(1)

    section = config[script_key][args.mode]
    main_folder = config.get("main_folder", ".")

    # Construct full I/O paths
    input_dir = os.path.join(main_folder, section["input_path"])
    output_dir = os.path.join(main_folder, section["output_path"])

    # Run the conversion
    convert_tif_to_h5(input_dir, output_dir)
