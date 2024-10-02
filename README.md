# caactus
 caactus (cell analysis and counting Tool using ilastik software) is a collection of python scripts to provide a streamlined workflow for [ilastik-software](https://www.ilastik.org/), including data preparation, processing and analysis. It aims to provide an easy-to-use tool for counting and analyzing cells from microscopy pictures. 

 ![workflow](https://github.com/mr2raccoon/caactus/blob/main/images/caactus-workflow(1).png)
 

# Introduction
The goal of this script collection is to provide an easy-to-use completion for the [Boundary-based segmentation with Multicut-workflow](https://www.ilastik.org/documentation/multicut/multicut) in [ilastik](https://www.ilastik.org/).
This worklow allwows for the automatization of cell-counting from messy microscopic images with different (touching) cell types for biological research. 

# Installation
## Install python
- [Download and install python](https://www.python.org/downloads/) for your respective operating system
- Make sure that the `pip-installer` was installed along the `python`-installation by typing `pip help` in the command prompt.


## Install ilastik
- [Download and install ilastik](https://www.ilastik.org/download) for your respective operating system.

## Install caactus

- To install `caactus` use `pip install caactus` to install all scripts plus the needed dependencies. 

# Workflow
## 1. Culturing
- Culture your cells in a plate of your choice and according to the needs of the organims being researched.
## 2. Image acquisition
- In your respective microscopy software environment, save the images of interest to `.tif-format`.
- From the metadata note down the pixel size and magnification used. 

## 3. Data Preparation
### 3.1 Create Project Directory

- For portability of the ilastik projects create the directory in the following structure:\
(Please note: the below example already includes examples of resulting files in each sub-directory)

```
project_directory  
├── 1_pixel_classification.ilp  
├── 2_boundary_segmentation.ilp  
├── 3_object_classification.ilp
├── 0_original_tif_images
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1.tif
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2.tif
  ├── ..
├── 1_images
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2.h5
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
## 4. Rename Files
- Rename the `.tif-files` so that they contain information about your cells and experimental conditions. Create a csv-file that contains the information you need in columns. Each row corresponds to one image. Follow the same order as in your plate and sequence of image acquisition.
- The script will rename your files in the following format ```columnA-value1_columnB-value2_columnC_etc.tif ``` eg. as seen in the example below picture 1 (well A1 from our plate) will be named ```strain-ATCC11559_date-20241707_timepoint-6h_biorep-A_techrep-1.tif ```
  
![csv_table](https://github.com/mr2raccoon/caactus/blob/main/images/csv-file_forrenaming.JPG)

- Call the `rename` script from the cmd prompt to rename all your original `.tif-files` to their new name.

## 5. Batch Conversion and Selection of Training data
### 5.1 Batch Conversion
- call the `tif2h5py` script from the cmd prompt to transform all `.tif-files` to `.h5-format`. 
 The `.h5-format` allows for better [performance when working with ilastik](https://www.ilastik.org/documentation/basics/performance_tips). 
- Copy the file path where the `.tif-files` are stored and use it as `input directory`
- for storing all converted files use the `project_directory/5_bacth_images` folder, copy the filepath and enter it as the output directory. 
### 5.2 Selection of Training data
- select a set of images the represantes the different experimental conditions best
- copy the `.h5-files` of those images to `project_directory/1_images`

# Training  
## 6. Pixel Classification
### 6.1 Project setup
- Follow the the [documentation for pixel classification with ilastik](https://www.ilastik.org/documentation/pixelclassification/pixelclassification). 
- Create the `1_pixel_classification.ilp`-project file inside the project directory.  
- For working with neighbouring / touching cells, it is suggested to create three classes: 0 = interior, 1 = background, 2 = boundary (This follows python's 0-indexing logic where counting is started at 0).

![pixel_classes](https://github.com/mr2raccoon/caactus/blob/main/images/pixel_classification_classes.JPG)

### 6.2 Export Probabilties
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- File: `{dataset_dir}/../2_probabilties/{nickname}_{result_type}.h5`

![export_prob](https://github.com/mr2raccoon/caactus/blob/main/images/export_probabilities.JPG)


## 7. Boundary-based Segmentation with Multicut
### 7.1 Project setup
- Follow the the [documentation for boundary-based segmentation with Multicut](https://www.ilastik.org/documentation/multicut/multicut).  
- Create the `2_boundary_segmentation.ilp`-project file inside the project directory.
- In `DT Watershed` use the input channel the corresponds to the order you used under project setup ( in this case input channel = 2).

### 7.2 Export Multicut Segmentation
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- File: `{dataset_dir}/../3_multicut/{nickname}_{result_type}.h5`

![export_multicut](https://github.com/mr2raccoon/caactus/blob/main/images/export_multicut.JPG)


## 8. Background Processing
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will this be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
- call the `background-processing` script from the cmd prompt
- enter your respective `project_directory/3_multicut/` directory by copying the filepath. 

## 9. Object Classification
### 9.1 Project setup
- Follow the the [documentation for object classification](https://github.com/mr2raccoon/caactus/blob/main/images/export_objectclassification.JPG).
- define your cell types plus an additional category for "non-usuable" objects, e.g. cell debris and cut-off objects on the side of the images
### 9.2 Export Object Information
In `Choose Export Imager Settings` change settings to
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- File: `{dataset_dir}/../4_objectclassification/{nickname}_{result_type}.h5`

![export_multicut](https://github.com/mr2raccoon/caactus/blob/main/images/export_multicut.JPG)
  
In `Configure Feature Table Export General` change seetings to
- File:  `{dataset_dir}/../4_objectclassification/{nickname}.csv` as the output directory and format `.csv`
- select your feautres of interest for exporting

  
![export_prob](https://github.com/mr2raccoon/caactus/blob/main/images/object_tableexport.JPG)

  
# Batch Processing
- Follow the [documentation for batch processing](https://www.ilastik.org/documentation/basics/batch).
- Perform steps 6 to 9 in batch mode
  
##  6. Batch Processing Pixel Classification
- open the `1_pixel_classification.ilp` project file
- under `Prediction Export` change the export directory to `File`: `{dataset_dir}/../6_batch_probabilities/{nickname}_{result_type}.h5`
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`

## 7. Batch Processing Multicut Segmentation
- open the `2_boundary_segmentation.ilp` project file
- under `Choose Export Image Settings` change the export directory to `File`: `{dataset_dir}/../7_batch_multicut/{nickname}_{result_type}.h5`
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`
- under `Batch Processing` `Probabilities` select all files from  `6_batch_probabilities`

## 8. Background Processing 
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will this be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
- call the `background-processing` script from the cmd prompt
- enter your respective `project_directory/7_batch_multicut/` directory by copying the filepath. 


## 9. Batch processing Object classification 
- under `Choose Export Image Settings` change the export directory to `File`: `{dataset_dir}/../8_batch_objectclassification/{nickname}_{result_type}.h5`
- in `Configure Feature Table Export General` choose `{dataset_dir}/../8_batch_objectclassification/{nickname}.csv` as the output directory and format `.csv`
- select your feautres of interest for exporting
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`
- under `Batch Processing` `Segmentation Image` select all files from  `7_batch_multicut`

# Post-Processing and Data Analysis
- Please be aware, the last two scripts, "11. Creating Summary Statistics" and "12. Data Modelling" at this stage are written for the analysis and visualization of two independent variables.
## 10. Merging Data Tables and Table Export
The next script will combine all tables from all images into one global table for further analysis. Additionally, the information stored in the file name will be added as columns to the dataset. 
- call the `csv_summary` script from the cmd prompt
- enter your respective `project_directory/8_batch_objectclassification/` directory by copying the filepath
- for saving the global table enter your respective `project_directory/9_data_analysis/` directory by copying the filepath
- Technically from this point on, you can continue to use whatever software / workflow your that is easiest for use for subsequent data analysis. 

## 11. Creating Summary Statistics
- call the `summary_statistics` script from the cmd prompt
- enter your respective `project_directory/9_data_analysis/` directory by copying the filepath
- next enter the path, where youn want the results saved (we use `project_directory/9_data_analysis/` directory as well)
- finally enter the names of your explantory variables used for grouping separated by `,`, e.g. `storage,timepoint`. For the plots, the variable entered first will be on the x-axis, the second variable entered will be used for facetting.

## 12. Data Modelling 
- call the `pln_modelling` script from the cmd prompt
- enter your the filepath where you stored the output of 11., e.g. `project_directory/9_data_analysis/` directory by copying the filepath
- enter the filepath, where you would like to save the graph to
- next enter the Predicted Class column names that you would like to include in the analysis, e.g. `resting,swollen,germling,hyphae`
- finally enter the variable names, e.g. `storage,timepoint`





