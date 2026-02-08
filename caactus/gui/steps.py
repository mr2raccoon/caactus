from typing import Callable

from caactus import background_processing, renaming, tif2h5py

STEPS = [
    {
        "name": "Renaming",
        "func": renaming.run,
        "config_key": "renaming",
    },
    {
        "name": "Tif to h5",
        "func": tif2h5py.convert_tif_to_h5,
        "config_key": "tif2h5py.batch",
    },
    {
        "name": "Background processing",
        "func": background_processing.batch_process_images,
        "config_key": "background_processing.batch",
    },
]


def run_step(step: Callable, params: dict):
    step(**params)
