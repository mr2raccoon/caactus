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
### Image acquisition
In your respective microscopy software environment, save the images of interest to `.tif-format`. From the metadata note the pixel size and magnification used. 

### Data Preparation
Rename the `.tif-files` so that the provide information about your cells and experimental conditions. Inside the filename, seperate the information with `_`,  e.g. `strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-i`

For portability of the ilastik projects create the directory in the following structure:

project_directory
├── 1_pixel_classification.ilp
├── 2_boundary_segmentation.ilp
├── 3_object_classification.ilp
├── 1_images
│   ├── image-0001.h5
│   ├── image-0001.h5
|   ...
└── results
    ├── image-0001_Probabilities.h5
    ├── image-0002_Probabilities.h5
    ...



### Background processing

### Merging data tables
### Summary statistics
### Data modelling 

### Examplary Worklfow




