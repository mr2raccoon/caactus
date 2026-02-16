from dataclasses import dataclass, field
from typing import Callable

from caactus import (
    background_processing,
    boundary_segmentation,
    csv_summary,
    object_classification,
    pixel_classification,
    pln_modelling,
    renaming,
    summary_statistics,
    summary_statistics_eucast,
    tif2h5py,
)


@dataclass
class CaactusStep:
    name: str
    func: Callable | None = None
    config_key: str | None = None
    description: str | dict[str, str] = ""
    stages: list[str] = field(default_factory=list)


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
        config_key="tif2h5py",
        description={"training": tif2h5py.DESCRIPTION, "batch": "batch lala"},
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="Pixel classification",
        func=None,
        config_key="pixel_classification",
        description={"training": pixel_classification.DESCRIPTION, "batch": "batch lala"},
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="Boundary segmentation",
        func=None,
        config_key="boundary_segmentation",
        description={"training": boundary_segmentation.DESCRIPTION, "batch": "batch lala"},
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="Background processing",
        func=background_processing.batch_process_images,
        config_key="background_processing",
        description={"training": background_processing.DESCRIPTION, "batch": "batch lala"},
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="Object classification",
        func=None,
        description={"training": object_classification.DESCRIPTION, "batch": "batch lala"},
        config_key="object_classification",
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="CSV summary",
        func=csv_summary.process_csv_files,
        config_key="csv_summary",
        description=csv_summary.DESCRIPTION,
    ),
    CaactusStep(
        name="Summary statistics",
        func=summary_statistics.process_cleaned_data,
        config_key="summary_statistics",
        description=summary_statistics.DESCRIPTION,
    ),
    CaactusStep(
        name="Summary statistics EUCAST",
        func=summary_statistics_eucast.process_eucast_data,
        config_key="summary_statistics_eucast",
        description=summary_statistics_eucast.DESCRIPTION,
    ),
    CaactusStep(
        name="PLN modelling",
        func=pln_modelling.modelling,
        config_key="pln_modelling",
        description=pln_modelling.DESCRIPTION,
    ),
]


def run_step(step: Callable, params: dict):
    step(**params)
