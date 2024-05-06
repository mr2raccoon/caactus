# monkey-worker
 A collection of python scripts to help with data preparation, processing and analysis for [ilastik-software](https://www.ilastik.org/)  
 

## Introduction
The goal of this scrip collection is to provide an easy-to-use completion for the [Boundary-based segmentation with Multicut-workflow](https://www.ilastik.org/documentation/multicut/multicut) in [ilastik](https://www.ilastik.org/).
This worklow allwows for the automatization of cell-counting from messy microscopic images with different (touching) cell types for biological research. 

## Installation
### Install python
 [Download and install python](https://www.python.org/downloads/) for your respective operating system.

### Install ilastik
[Download and install ilastik]([https://www.python.org/downloads/](https://www.ilastik.org/download) for your respective operating system.
Make sure that the `pip-installer` was installed along the `python`-installation by typing `pip help` in the command prompt.

### Install monkey-worker

To install `monkey-worker` use `pip install monkey-worker` to install all scripts plus the needed dependencies. 

## Workflow
### 1. Image acquisition
In your respective microscopy software environment, save the images of interest to `.tif-format`. From the metadata note the pixel size and magnification used. 

### 2. Data Preparation
#### 2.1 Rename Files
Rename the `.tif-files` so that the provide information about your cells and experimental conditions. Inside the filename, seperate the information with `_`,  e.g. `strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-i.tif`

#### 2.2 Create Project Directory

For portability of the ilastik projects create the directory in the following structure:\
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
```

### 3. Batch Conversion
Use the `batch-conversion` script to transform all `.tif-files` to `.h5-format`. The `.h5-format` allows for better [performance when working with ilastik](https://www.ilastik.org/documentation/basics/performance_tips). 
Use `project_directory/1_images/` as the output directory. 

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
### 7. Object Classification
### 8. Merging Data Tables and Table Export
### 9. Creating Summary Statistics
### 10. Data Modelling 

### Examplary Worklfow




