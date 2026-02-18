from dataclasses import dataclass, field
from typing import Callable
import textwrap

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
    introduction,
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
        name="Introduction",
        func=None,
        description=introduction.DESCRIPTION,
        config_key=None,
    ),
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
        description={"training": tif2h5py.DESCRIPTION, "batch": """lala"""
    },
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="Pixel classification",
        func=None,
        config_key="pixel_classification",
        description={"training": pixel_classification.DESCRIPTION, "batch": textwrap.dedent("""
        Select training or batch from the drop down menu above to specify the input and 
        output directories correctly.
                                                                                            
        1. Open ilastik.

        2. Open your trained ilastik pixel classification project (1_pixel_classification.ilp).

        3. Go to "5. Batch processing" tab.6_batch_predictions

        4. Under "1.Input Data","Raw data", add the .h5 files from 5_batch_images folder.                                                                  

        5. Under "4. Prediction Export", select "Export predictions" and choose a folder for the output (e.g. 6_batch_probabilities).
        <images/batch_pixel.png>
                                                                                            
        6. Go to "5. Batch Processing" and click "Process all files".
        
        7. The output will be saved as _Probabilities.h5 files in the output folder.
    """)},
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="Boundary segmentation",
        func=None,
        config_key="boundary_segmentation",
        description={"training": boundary_segmentation.DESCRIPTION, "batch": textwrap.dedent("""
        Select training or batch from the drop down menu above to specify the input and 
        output directories correctly.
        1. Open ilastik.

        2. Open your trained ilastik boundary-Segmentation project (2_boundary_segmentation.ilp).

        3. Go to "5. Batch processing" tab.

        4. Under "1.Input Data","Raw data", add the .h5 files from 5_batch_images folder.
                                                                                                                                                                                  
        5. Under "1.Input Data","Probabilities", add the data_Probabilities.h5 files from 6_batch_probabilities folder.

        6. Under "4. Data Export", select "Choose Export Image Settings" and choose a folder for the output (e.g. 7_batch_multicut).
        <images/batch_multicut.png>

        7. Go to "5. Batch Processing" and click "Process all files".
        
        8. The output will be saved as _Multicut Segmentation.h5 files in the output folder.
    """)},
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
        description={"training": object_classification.DESCRIPTION, "batch": textwrap.dedent("""
        1. Open ilastik.

        2. Open your trained ilastik object classification project (3_object_classification.ilp).

        3. Go to "5. Batch processing" tab.

        4. Under "1.Input Data", "Raw data", add the .h5 files from 5_batch_images folder.
                                                                                                                                                                                  
        5. Under "1.Input Data","Segmentation Image", add the data_Multicut Segmentation.h5 files from 7_batch_multicut folder.

        6. Under "4. Object Information Export", choose "Export Image Settings" with the following settings:
        <images/batch_object_image.png>

        7. Under "4. Object Information Export", choose "Configure Feature Table Export" with the following settings:
        <images/feature_table_export.png>
                                                                               
        8. Under "Configure Feature Table Export", choose " Features" to choose the Feature you are interested in exporting for each object.
        <images/features_of_featuretable.png>

        9. Go to "5. Batch Processing" and click "Process all files".
                                                                                             
        10. The output will be saved as data_Object Predictions.h5 files and data_table.csv in the output folder.
    """)},
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
