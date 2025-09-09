# caactus
caactus (**c**ell **a**nalysis **a**nd **c**ounting **t**ool using ila**stik** software) is a collection of python scripts to provide a streamlined workflow for [ilastik-software](https://www.ilastik.org/), including data preparation, processing and analysis. It aims to provide biologist with an easy-to-use tool for counting and analyzing cells from a large number of microscopy pictures. 

 ![workflow](https://github.com/mr2raccoon/caactus/blob/main/images/caactus-workflow(1).png)
 

# Introduction
The goal of this script collection is to provide an easy-to-use completion for the [Boundary-based segmentation with Multicut-workflow](https://www.ilastik.org/documentation/multicut/multicut) in [ilastik](https://www.ilastik.org/).
This worklow allwows for the automatization of cell-counting from messy microscopic images with different (touching) cell types for biological research. 
For easy copy & paste, commands are provided in `grey code boxes` with one-click C&P

# Installation
## Install miniconda, create an environment and install Python and vigra
- [Download and install miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install#windows-installation) for your respective operating system according to the instructions.
  - Miniconda provides a lightweight package and environment manager. It allows you to create isolated environments so that Python versions and package dependencies required by caactus do not interfere with your system Python or other projects.
- Once installed, create an environment for using `caactus` with the following command from your cmd-line
  ```bash
  conda create -n caactus-env -c conda-forge "python>=3.10.12" vigra 

## Install caactus
- Activate the `caactus-env` from the cmd-line with
  ```bash
  conda activate caactus-env
- To install `caactus` plus the needed dependencies inside your environment, use
  ```bash
  pip install caactus
- During the below described steps that call the `caactus-scripts`, make sure to have the `caactus-env` activated.


## Install ilastik
- [Download and install ilastik](https://www.ilastik.org/download) for your respective operating system.


# Workflow
## A Culturing
- Culture your cells in a flat bottom plate of your choice and according to the needs of the organims being researched.
## B Image acquisition
- In your respective microscopy software environment, save the images of interest to `.tif-format`.
- From the image metadata, copy the pixel size and magnification used. 

## C Data Preparation
### C.1 Create Project Directory

- For portability of the ilastik projects create the directory in the following structure:\
(Please note: the below example already includes examples of resulting files in each sub-directory)

```
project_directory  
├── 1_pixel_classification.ilp  
├── 2_boundary_segmentation.ilp  
├── 3_object_classification.ilp
├── renaming.csv
├── conif.toml
├── 0_1_original_tif_training_images
  ├── training-1.tif
  ├── training-2.tif
  ├── ...
├── 0_2_original_tif_batch_images
  ├── image-1.tif
  ├── image-2.tif
  ├── ..
├── 0_3_batch_tif_renamed
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1.tif
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2.tif
  ├── ..
├── 1_images
  ├── training-1.h5
  ├── training-2.h5
  ├── ...
├── 2_probabilities
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Probabilities.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Probabilities.h5
  ├── ...
├── 3_multicut
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Multicut Segmentation.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Multicut Segmentation.h5
  ├── ...
├── 4_objectclassification
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Object Predictions.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_table.csv
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Object Predictions.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_table.csv
  ├── ...
├── 5_batch_images
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2.h5
  ├── ...
├── 6_batch_probabilities
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Probabilities.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Probabilities.h5
  ├── ...
├── 7_batch_multicut
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Multicut Segmentation.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Multicut Segmentation.h5
  ├── ...
├── 8_batch_objectclassification
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Object Predictions.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_table.csv
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Object Predictions.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_table.csv
  ├── ...
├── 9_data_analysis

```
### C.1 Setup config.toml-file
- copy config/config.toml to your working directory and modify it as needed.
- the caactus scripts are setup for pulling the information needed for running from the file

## D Training
### D.1. Selection of Training Images and Conversion
#### D.1.1 Selection of Training data
- select a set of images that represant the different experimental conditions best
- store them in 0_1_original_tif_training_images

#### D.1.2 Conversion
- call the `tif2h5py` script from the cmd prompt to transform all `.tif-files` to `.h5-format`. 
 The `.h5-format` allows for better [performance when working with ilastik](https://www.ilastik.org/documentation/basics/performance_tips). 
- select "-c" and enter path to config.toml
- select "-m" and choose "training"
- whole command
  ```bash
  tif2hpy -c \path\to\config.toml -m training

### D.2. Pixel Classification
#### D.2.1 Project setup
- Follow the the [documentation for pixel classification with ilastik](https://www.ilastik.org/documentation/pixelclassification/pixelclassification). 
- Create the `1_pixel_classification.ilp`-project file inside the project directory.  
- For working with neighbouring / touching cells, it is suggested to create three classes: 0 = interior, 1 = background, 2 = boundary (This follows python's 0-indexing logic where counting is started at 0).

![pixel_classes](https://github.com/mr2raccoon/caactus/blob/main/images/pixel_classification_classes.JPG)

#### D.2.2 Export Probabilties
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- File:
  ```bash
  {dataset_dir}/../2_probabilties/{nickname}_{result_type}.h5

![export_prob](https://github.com/mr2raccoon/caactus/blob/main/images/export_probabilities.JPG)


### D.3 Boundary-based Segmentation with Multicut
#### D.3.1 Project setup
- Follow the the [documentation for boundary-based segmentation with Multicut](https://www.ilastik.org/documentation/multicut/multicut).  
- Create the `2_boundary_segmentation.ilp`-project file inside the project directory.
- In `DT Watershed` use the input channel the corresponds to the order you used under project setup (in this case input channel = 2).

![watershed](https://github.com/mr2raccoon/caactus/blob/main/images/watershed.png)


#### D.3.2 Export Multicut Segmentation
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- File:
  ```bash
  {dataset_dir}/../3_multicut/{nickname}_{result_type}.h5

![export_multicut](https://github.com/mr2raccoon/caactus/blob/main/images/export_multicut.JPG)


### D.4 Background Processing
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will thus be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
- call the `background-processing` script from the cmd prompt
- select "-c" and enter path to config.toml
- enter "-m training" for training mode
- whole command
  ```bash
  background-processing -c \path\to\config.toml -m training

### D.5. Object Classification
#### D.5.1 Project setup
- Follow the the [documentation for object classification](https://github.com/mr2raccoon/caactus/blob/main/images/export_objectclassification.JPG).
- define your cell types plus an additional category for "not-usuable" objects, e.g. cell debris and cut-off objects on the side of the images
#### D.5.2 Export Object Information
In `Choose Export Imager Settings` change settings to
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- File:
  ```bash
  {dataset_dir}/../4_objectclassification/{nickname}_{result_type}.h5

![export_multicut](https://github.com/mr2raccoon/caactus/blob/main/images/export_multicut.JPG)
  
In `Configure Feature Table Export General` change seetings to
- format `.csv` and output directory File:
  ```bash
  {dataset_dir}/../4_objectclassification/{nickname}.csv`
- select your feautres of interest for exporting

  
![export_prob](https://github.com/mr2raccoon/caactus/blob/main/images/object_tableexport.JPG)

  
## E Batch Processing
- Follow the [documentation for batch processing](https://www.ilastik.org/documentation/basics/batch)
- store the images you want to process in the 0_2_original_tif_batch_images directory
- Perform steps D.2 to D.5 in batch mode, as explained in detail below (E.2 to E.5)
  
### E.1 Rename Files
- Rename the `.tif-files` so that they contain information about your cells and experimental conditions
- Create a csv-file that contains the information you need in columns. Each row corresponds to one image. Follow the same order as the sequence of image acquisition.
- the only hardcoded columns that have to be added are `biorep` for "biological replicate" and `techrep` for "technical replicate". They are needed for downstream analysis for calculating the averages
- The script will rename your files in the following format ```columnA-value1_columnB-value2_columnC_etc.tif ``` eg. as seen in the example below picture 1 (well A1 from our plate) will be named ```strain-ATCC11559_date-20241707_timepoint-6h_biorep-A_techrep-1.tif ```
- Call the `rename` script from the cmd prompt to rename all your original `.tif-files` to their new name.
- whole command:
  ```bash
  rename -c \path\to\config.toml

 ![96-well-plate](https://github.com/mr2raccoon/caactus/blob/main/images/96_well_setup.png)

### E.2 Batch Processing Pixel Classification
- open the `1_pixel_classification.ilp` project file
- under `Prediction Export` change the export directory to `File`:
  ```bash
  {dataset_dir}/../6_batch_probabilities/{nickname}_{result_type}.h5
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`

### E.3 Batch Processing Multicut Segmentation
- open the `2_boundary_segmentation.ilp` project file
- under `Choose Export Image Settings` change the export directory to `File`:
  ```bash
  {dataset_dir}/../7_batch_multicut/{nickname}_{result_type}.h5
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`
- under `Batch Processing` `Probabilities` select all files from  `6_batch_probabilities`

### E.4 Background Processing 
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will thus be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
- call the `background-processing.py` script from the cmd prompt
- enter "-m batch" for batch mode
- whole command:
  ```bash
  background-processing -c \path\to\config.toml -m batch


### E.5 Batch processing Object classification 
- under `Choose Export Image Settings` change the export directory to `File`:
  ```bash
  {dataset_dir}/../8_batch_objectclassification/{nickname}_{result_type}.h5
- in `Configure Feature Table Export General` choose format `.csv` and change output directory to:
  ```bash
  {dataset_dir}/../8_batch_objectclassification/{nickname}.csv
- select your feautres of interest for exporting
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`
- under `Batch Processing` `Segmentation Image` select all files from  `7_batch_multicut`

## F Post-Processing and Data Analysis
- Please be aware, the last two scripts, `summary_statisitcs.py` and `pln_modelling.py` at this stage are written for the analysis and visualization of two independent variables.
### F.1 Merging Data Tables and Table Export
The next script will combine all tables from all images into one global table for further analysis. Additionally, the information stored in the file name will be added as columns to the dataset. 
- call the `csv_summary.py` script from the cmd prompt
- whole command:
   ```bash
  python csv_summary.py
- Technically from this point on, you can continue to use whatever software / workflow your that is easiest for use for subsequent data analysis. 

### F.2 Creating Summary Statistics
- call the `summary_statistics.py` script from the cmd prompt
- whole command:
   ```bash
  summary_statistics
- if working with EUCAST antifungal susceptibility testing, call `summary_statistics_eucast`


### F.3 PLN Modelling 
- call the `pln_modelling.py` script from the cmd prompt`
- whole command:
   ```bash
  pln_modelling
- please note: the limit of categories for display in the PCA-plot is n=15






