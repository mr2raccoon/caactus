#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from typing import Optional, Tuple

import h5py
import tifffile
import vigra

from caactus.utils import load_config

DESCRIPTION = """
## Tif to H5

Converts all `.tif` files in the input folder to `.h5` format.

The **H5 format** allows for significantly better performance when working with ilastik. Use it for both training and batch images.

Use the **Mode** selector in Global Settings to switch between `training` and `batch`.

For more information, see the ilastik performance tips at https://www.ilastik.org/documentation/basics/performance_tips.
"""


def _infer_axes_from_tif(tiff: tifffile.TiffFile) -> Optional[str]:
    """
    Try to get axis string from tifffile metadata (OME or series axes).
    Returns something like 'YX', 'ZYX', 'TZYX', 'ZYXC', 'TCZYX', etc.
    """
    try:
        if tiff.series and len(tiff.series) > 0:
            axes = getattr(tiff.series[0], "axes", None)
            if isinstance(axes, str) and axes:
                return axes
    except Exception:
        pass
    return None


def _to_tzyxc(image_data, axes: Optional[str]) -> Tuple[object, str]:
    """
    Convert image_data to 5D array shaped (t, z, y, x, c) and return axis tag string 'tzyxc'.

    Uses provided axes when available; otherwise uses heuristics.

    Axis mapping:
      - T: time
      - Z: z-stack
      - Y/X: spatial
      - C: channels
      - S: samples (treated as channels)
    """
    import numpy as np

    arr = image_data
    nd = arr.ndim

    # --- Use axes metadata if available and sane ---
    if axes:
        ax = axes.upper().replace("S", "C")  # treat samples as channels

        target = "TZYXC"
        allowed = set(target)

        if all(a in allowed for a in ax):
            # Reorder existing axes into target order (keeping only present axes)
            present = [a for a in target if a in ax]
            perm = [ax.index(a) for a in present]
            arr2 = np.transpose(arr, axes=perm) if perm != list(range(len(perm))) else arr

            # If Y/X are missing, metadata is not usable for ilastik
            if "Y" in present and "X" in present:
                # Insert missing singleton axes at the right positions to reach 5D in TZYXC order
                arr5 = arr2
                current_axes = present[:]  # axes order of arr5 currently

                for i, a in enumerate(target):
                    if a not in current_axes:
                        arr5 = np.expand_dims(arr5, axis=i)
                        current_axes.insert(i, a)

                if arr5.ndim == 5 and current_axes == list(target):
                    return arr5, "tzyxc"

    # --- Heuristic fallback ---
    # Goal: avoid misclassifying (T,Y,X) as (Z,Y,X), which can break ilastik feature scales.
    if nd == 2:
        # (Y, X) -> (1,1,Y,X,1)
        arr5 = arr[None, None, :, :, None]
        warn = "Heuristic: assumed 2D grayscale (YX)."

    elif nd == 3:
        a, b, c = arr.shape

        # If last axis looks like channels (RGB/RGBA), assume (Y,X,C)
        if c in (3, 4):
            arr5 = arr[None, None, :, :, :]
            warn = "Heuristic: assumed 3D is (Y,X,C) (RGB/RGBA)."
        else:
            # Ambiguous: could be (Z,Y,X) or (T,Y,X).
            # If first axis is small and images are reasonably large, treat as time.
            if a <= 10 and b >= 64 and c >= 64:
                arr5 = arr[:, None, :, :, None]  # (T,Y,X) -> (T,1,Y,X,1)
                warn = "Heuristic: assumed 3D is (T,Y,X) (small first axis)."
            else:
                arr5 = arr[None, :, :, :, None]  # (Z,Y,X) -> (1,Z,Y,X,1)
                warn = "Heuristic: assumed 3D is (Z,Y,X)."

    elif nd == 4:
        a, b, c, d = arr.shape

        # If last dim looks like channels, assume (Z,Y,X,C)
        if d in (1, 3, 4):
            arr5 = arr[None, :, :, :, :]  # (Z,Y,X,C) -> (1,Z,Y,X,C)
            warn = "Heuristic: assumed 4D is (Z,Y,X,C)."
        else:
            # Most likely (T,Z,Y,X) (common for time series stacks)
            arr5 = arr[:, :, :, :, None]  # (T,Z,Y,X) -> (T,Z,Y,X,1)
            warn = "Heuristic: assumed 4D is (T,Z,Y,X)."

    elif nd == 5:
        arr5 = arr
        warn = "Assumed 5D already (T,Z,Y,X,C)."

    else:
        raise ValueError(f"Unexpected image shape: {arr.shape}")

    print(f"[WARN] {warn} Input shape={arr.shape} -> output shape={arr5.shape}")
    return arr5, "tzyxc"


def convert_tif_to_h5(main_folder: str, input_path: str, output_path: str) -> None:
    """Convert all .tif files in input_dir to .h5 format in output_dir."""
    input_dir = os.path.join(main_folder, input_path)
    output_dir = os.path.join(main_folder, output_path)
    os.makedirs(output_dir, exist_ok=True)

    tif_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".tif")]
    if not tif_files:
        print("No .tif files found in input directory.")
        return

    for tif_file in tif_files:
        tif_path = os.path.join(input_dir, tif_file)

        with tifffile.TiffFile(tif_path) as tiff:
            axes = _infer_axes_from_tif(tiff)
            image_data = tiff.asarray()
            print(
                f"{tif_file} - image data shape: {image_data.shape}, "
                f"dtype: {image_data.dtype}, axes: {axes}"
            )

            image_data_5d, _ = _to_tzyxc(image_data, axes)
            data_shape = image_data_5d.shape

            # VIGRA axistags for ilastik
            axistags = vigra.defaultAxistags("tzyxc")

            h5_file = os.path.splitext(tif_file)[0] + ".h5"
            h5_path = os.path.join(output_dir, h5_file)

            # Chunking (safe; avoid exceeding dimension sizes)
            # data_shape is always (t,z,y,x,c) here
            _, _, y, x, c = data_shape
            chunks = (1, 1, min(256, y), min(256, x), max(1, c))

            with h5py.File(h5_path, "w") as h5:
                ds = h5.create_dataset(
                    name="data",
                    data=image_data_5d,
                    chunks=chunks,
                )
                ds.attrs["axistags"] = axistags.toJSON()
                ds.attrs["data_shape"] = data_shape

        print(f"Converted {tif_file} -> {h5_file}")
    print("Tif2h5 conversion completed.", file=sys.stderr, flush=True)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("-c", "--config", required=True, help="Path to config file")
    parser.add_argument(
        "-m",
        "--mode",
        required=True,
        choices=["training", "batch"],
        help="Define if training or batch mode",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    script_key = "tif2h5py"

    if script_key not in config or args.mode not in config[script_key]:
        print(f"Missing configuration for [{script_key}.{args.mode}]")
        sys.exit(1)

    section = config[script_key][args.mode]
    main_folder = config["main_folder"]

    convert_tif_to_h5(main_folder, section["input_path"], section["output_path"])
    
    
if __name__ == "__main__":
    main()