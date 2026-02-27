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
        description={"training": tif2h5py.DESCRIPTION, "batch": """
Convert all .tif files in input_dir to .h5 format in output_dir.

Select training or batch from the drop down menu above to specify the input and 
output directories correctly.

 The `.h5-format` allows for better performance when working with ilastik.
 
 Fore more information, please consult https://www.ilastik.org/documentation/basics/performance_tips. 
"""
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

        2. Open your trained ilastik pixel classification project (e.g. `1_pixel_classification.ilp`).

        CAVE: DO NOT CHANGE anything in 1. Input Data, 2. Feature Selection and 3. Training when running Batch Processing!

        3. Under `4. Prediction Export`, select `Export predictions` and name the folder for the output at `File`:
        {dataset_dir}/../6_batch_probabilities/{nickname}_{result_type}.h5

        <images/batch_pixel.png>

        4. Go to `5. Batch processing` tab

        5. Under `Raw data`, add the .h5 files from `5_batch_images` folder.                                                                  
                                                                                    
        6. Now click `Process all files`.

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

        2. Open your trained ilastik boundary-Segmentation project (e.g. open the `2_boundary_segmentation.ilp` project file).
        CAVE: DO NOT CHANGE anything in 1. Input Data, 2. DT Watershed, and 3. Training and Multicut, when running Batch Processing!

        3.  Under `4. Data Export`, select `Choose Export Image Settings` and choose a folder for the output (e.g. 7_batch_multicut).
        - under `Choose Export Image Settings` change the export directory to `File`:
        {dataset_dir}/../7_batch_multicut/{nickname}_{result_type}.h5
                                                                                             
        4. Go to `5. Batch processing`.

        5. Under,`Raw data`, add the .h5 files from `5_batch_images` folder.
                                                                                                                                                                          
        6. Under `Probabilities`, add the data_Probabilities.h5 files from `6_batch_probabilities` folder.

        <images/batch_multicut.png>

        7. Go to `5. Batch Processing` and click `Process all files`.

        8. The output will be saved as _Multicut Segmentation.h5 files in the output folder.
    """)},
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="Background processing",
        func=background_processing.batch_process_images,
        config_key="background_processing",
        description={"training": background_processing.DESCRIPTION, "batch": """This script processes HDF5 segmentation files by zeroing the largest ID in the 'exported_data' dataset.

For futher processing in the object classification, the background needs to eliminated from the multicut data sets.

 For this the next script will set the numerical value of the largest region to 0. 
 
 It will thus be shown as transpartent in the next step of the workflow. 
 
 This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/7_batch_multicut/`.
"""},
        stages=["training", "batch"],
    ),
    CaactusStep(
        name="Object classification",
        func=None,
        description={"training": object_classification.DESCRIPTION, "batch": textwrap.dedent("""
        1. Switch back to ilastik.

        2. Open your trained ilastik object classification project (`3_object_classification.ilp`).
        CAVE: DO NOT CHANGE anything in 1. Input Data, 2. Object Feature Selection, 3. Object Classification, when running Batch Processing!

        3. Under `4. Object Information Export`, choose  `Export Image Settings` change the export directory to `File`:
        {dataset_dir}/../8_batch_objectclassification/{nickname}_{result_type}.h5
        <images/batch_object_image.png>
        
        4. Under "4. Object Information Export", choose "Configure Feature Table Export" with the following settings:
        <images/feature_table_export.png>
                                                                        
        5. In `Configure Feature Table Export General` choose format `.csv` and change output directory to:
        {dataset_dir}/../8_batch_objectclassification/{nickname}.csv

        Choose  `Features` to choose the Feature you are interested in exporting

        <images/features_of_featuretable.png>

        6. Go to 5. `Batch Processing` tab

        7. Under  `Raw data`, add the .h5 files from `5_batch_images` folder.

        8. Under `Segmentation Image`, add the data_Multicut Segmentation.h5 files from `7_batch_multicut` folder.

        9. Go to `5. Batch Processing` and click `Process all files`.  

        10. The output will be saved as data_Object Predictions.h5 files and data_table.csv in the output folder.

        11. Now you have performed all steps in ilastik. You can close ilastik.
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
        name="EUCAST Summary statistics",
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
