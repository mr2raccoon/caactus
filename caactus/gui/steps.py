from dataclasses import dataclass
from typing import Callable

from caactus import background_processing, renaming, tif2h5py


@dataclass
class CaactusStep:
    name: str
    func: Callable | None = None
    config_key: str | None = None
    description: str = ""


STEPS = [
    CaactusStep(
        name="Renaming",
        func=renaming.run,
        description=renaming.DESCRIPTION,
        config_key="renaming",
    ),
    CaactusStep(
        name="Tif to h5",
        func=tif2h5py.convert_tif_to_h5,
        config_key="tif2h5py.batch",
    ),
    CaactusStep(
        name="Pixel classification",
        func=None,
        description="Train a pixel classification model in ilastik.",
        config_key=None,
    ),
    CaactusStep(
        name="Boundary segmentation",
        func=None,
        description="Perform boundary segmentation in ilastik.",
        config_key=None,
    ),
    CaactusStep(
        name="Background processing",
        func=background_processing.batch_process_images,
        config_key="background_processing.batch",
    ),
    CaactusStep(
        name="Object classification",
        func=None,
        description="Perform object classification in ilastik.",
        config_key=None,
    ),
]


def run_step(step: Callable, params: dict):
    step(**params)
