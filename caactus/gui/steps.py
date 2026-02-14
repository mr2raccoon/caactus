import re
from dataclasses import dataclass, field
from typing import Callable

from caactus import background_processing, csv_summary, renaming, tif2h5py


def replace_single_newline(text, replacement=""):
    return re.sub(r"(?<!\n)\n(?!\n)", replacement, text)


@dataclass
class CaactusStep:
    name: str
    func: Callable | None = None
    config_key: str | None = None
    description: str = ""
    stages: list[str] = field(default_factory=list)


STEPS = [
    CaactusStep(
        name="Renaming",
        func=renaming.run,
        description=replace_single_newline(renaming.DESCRIPTION),
        config_key="renaming",
    ),
    CaactusStep(
        name="Tif to h5",
        func=tif2h5py.convert_tif_to_h5,
        config_key="tif2h5py",
        description=replace_single_newline(tif2h5py.DESCRIPTION),
        stages=["batch", "training"],
    ),
    CaactusStep(
        name="Pixel classification",
        func=None,
        description="Train a pixel classification model in ilastik.",
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
        config_key="background_processing",
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="Object classification",
        func=None,
        description="Perform object classification in ilastik.",
        config_key=None,
    ),
    CaactusStep(
        name="CSV summary",
        func=csv_summary.process_csv_files,
        config_key="csv_summary",
        description=csv_summary.DESCRIPTION,
    ),
]


def run_step(step: Callable, params: dict):
    step(**params)
