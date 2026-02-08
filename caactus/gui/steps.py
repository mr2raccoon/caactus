from typing import Callable

from caactus import background_processing, renaming, tif2h5py

STEPS = [
    {
        "name": "Renaming",
        "func": renaming.run,
        "description": renaming.DESCRIPTION,
        "config_key": "renaming",
    },
    {
        "name": "Tif to h5",
        "func": tif2h5py.convert_tif_to_h5,
        "config_key": "tif2h5py.batch",
    },
    {
        "name": "Pixel classification",
        "func": None,
        "description": "Train a pixel classification model in ilastik.",
        "config_key": None,
    },
    {
        "name": "Boundary segmentation",
        "func": None,
        "description": "Perform boundary segmentation in ilastik.",
        "config_key": None,
    },
    {
        "name": "Background processing",
        "func": background_processing.batch_process_images,
        "config_key": "background_processing.batch",
    },
    {
        "name": "Object classification",
        "func": None,
        "description": "Perform object classification in ilastik.",
        "config_key": None,
    },
]


def run_step(step: Callable, params: dict):
    step(**params)
