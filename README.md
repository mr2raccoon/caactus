# monkey-worker
 A collection of python scripts to help with data preparation, processing and analysis for [ilastik-software](https://www.ilastik.org/)  
 

## Introduction
The goal of this scrip collection is to provide an easy-to-use completion for the [Boundary-based segmentation with Multicut-workflow](https://www.ilastik.org/documentation/multicut/multicut) in [ilastik](https://www.ilastik.org/).
This worklow allwows for the automatization of cell-counting from messy microscopic images with different (touching) cell types for biological research. 

## Installation
### Install python
- [Download and install python](https://www.python.org/downloads/) for your respective operating system
- Make sure that the `pip-installer` was installed along the `python`-installation by typing `pip help` in the command prompt.


### Install ilastik
- [Download and install ilastik](https://www.ilastik.org/download) for your respective operating system.

### Install monkey-worker

- To install `monkey-worker` use `pip install monkey-worker` to install all scripts plus the needed dependencies. 

## Workflow
### 1. Image acquisition
- In your respective microscopy software environment, save the images of interest to `.tif-format`.
- From the metadata note the pixel size and magnification used. 

### 2. Data Preparation
#### 2.1 Rename Files
- Rename the `.tif-files` so that the provide information about your cells and experimental conditions. Inside the filename, seperate the information with `_`,  e.g. `strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-i.tif`
 

#### 2.2 Create Project Directory

- For portability of the ilastik projects create the directory in the following structure:\
(Please note: the below example already includes examples of resulting files in each sub-directory)

```
project_directory  
├── 1_pixel_classification.ilp  
├── 2_boundary_segmentation.ilp  
├── 3_object_classification.ilp
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
```

### 3. Batch Conversion and Selection of Training data
#### 3.1 Batch Conversion
- Use the `batch-conversion` script to transform all `.tif-files` to `.h5-format`. The `.h5-format` allows for better [performance when working with ilastik](https://www.ilastik.org/documentation/basics/performance_tips). 
- Copy the file path where the `.tif-files` are stored and use it as `input directory`
- for storing all converted files use the `project_directory/5_bacth_images` folder, copy the filepath and enter it as the output directory. 
#### 3.2 Selection of Training data
- select a set of images the represantes the different experimental conditions best
- copy the `.h5-files` of those images to `project_directory/1_images`
### 4. Pixel Classification
#### 4.1 Project setup
- Follow the the [documentation for pixel classification with ilastik](https://www.ilastik.org/documentation/pixelclassification/pixelclassification). 
- Create the `1_pixel_classification.ilp`-project file inside the project directory.  
- For working with neighbouring / touching cells, it is suggested to create three classes: 0 = interior, 1 = background, 2 = boundary (This follows python's 0-indexing logic where counting is started at 0).

![pixel_classes](https://github.com/mr2raccoon/monkey-worker/blob/main/pixel_classification_classes.JPG)

#### 4.2 Export Probabilties
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- File: `{dataset_dir}/../2_probabilties/{nickname}_{result_type}.h5`

![export_prob](https://github.com/mr2raccoon/monkey-worker/blob/main/export_probabilities.JPG)


### 5. Boundary-based Segmentation with Multicut
#### 5.1 Project setup
- Follow the the [documentation for boundary-based segmentation with Multicut](https://www.ilastik.org/documentation/multicut/multicut).  
- Create the `2_boundary_segmentation.ilp`-project file inside the project directory.
- In `DT Watershed` use the input channel the corresponds to the order you used under project setup ( in this case input channel = 2).

#### 5.2 Export Multicut Segmentation
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- File: `{dataset_dir}/../3_multicut/{nickname}_{result_type}.h5`

![export_multicut](https://github.com/mr2raccoon/monkey-worker/blob/main/export_multicut.JPG)


### 6. Background Processing
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will this be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
- call the `background-processing` script from the cmd prompt
- enter your respective `project_directory/3_multicut/` directory by copying the filepath. 

### 7. Object Classification
#### 7.1 Project setup
- Follow the the [documentation for object classification](https://www.ilastik.org/documentation/objects/objects).
- define your cell types plus an additional category for "non-usuable" objects, e.g. cell debris and cut-off objects on the side of the images
#### 7.2 Export Object Information
- in `Configure Feature Table Export General` choose `{dataset_dir}/../4_objectclassification/{nickname}.csv` as the output directory and format `.csv`
- select your feautres of interest for exporting

  
![export_prob](https://github.com/mr2raccoon/monkey-worker/blob/main/object_tableexport.JPG)

  
### 8. Batch Processing
- Follow the [documentation for batch processing](https://www.ilastik.org/documentation/basics/batch)
  
#### 8.1 Batch Processing Pixel Classification
- open the `1_pixel_classification.ilp` project file
- under `Prediction Export` change the export directory to `File`: `{dataset_dir}/../6_batch_probabilties/{nickname}_{result_type}.h5`
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`

#### 8.2 Batch Processing Multicut Segmentation
- open the `2_boundary_segmentation.ilp` project file
- under `Choose Export Image Settings` change the export directory to `File`: `{dataset_dir}/../7_batch_multicut/{nickname}_{result_type}.h5`
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`
- under `Batch Processing` `Probabilities` select all files from  `6_batch_probabilities`

#### 8.3 Background Processing
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will this be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
- call the `background-processing` script from the cmd prompt
- enter your respective `project_directory/7_batch_multicut/` directory by copying the filepath. 


#### 8.4 Batch processing Object classification

### 9. Merging Data Tables and Table Export

### 10. Creating Summary Statistics

### 11. Data Modelling 

### Examplary Worklfow




