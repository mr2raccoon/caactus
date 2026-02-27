# caactus
caactus (**c**ell **a**nalysis **a**nd **c**ounting **t**ool **u**sing ilastik **s**oftware) is a collection of python scripts to provide a streamlined workflow for [ilastik-software](https://www.ilastik.org/), including data preparation, processing and analysis. It aims to provide biologist with an easy-to-use tool for counting and analyzing cells from a large number of microscopy pictures.

 ![workflow](caactus/gui/assets/images/caactus-workflow(1).png)
 

# Introduction
The goal of this script collection is to provide an easy-to-use completion for the [Boundary-based segmentation with Multicut-workflow](https://www.ilastik.org/documentation/multicut/multicut) in [ilastik](https://www.ilastik.org/).
This workflow allows for the automatization of cell-counting from messy microscopic images with different (touching) cell types for biological research. 
For easy copy & paste, commands are provided in `grey code boxes` with one-click copy & paste.

# Installation
## Install miniconda, create an environment and install Python and vigra
- [Download and install miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install#windows-installation) for your respective operating system according to the instructions.
  - Miniconda provides a lightweight package and environment manager. It allows you to create isolated environments so that Python versions and package dependencies required by caactus do not interfere with your system Python or other projects.
- Once installed, create an environment for using `caactus` with the following command from your cmd-line
  ```bash
conda create -n caactus-env -c conda-forge python=3.12 vigra
  ```

## Install caactus
- Activate the `caactus-env` from the cmd-line with
  ```bash
  conda activate caactus-env
  ```
- To install `caactus` plus the needed dependencies inside your environment, use
  ```bash
  pip install caactus
  ```
- During the below described steps that call the `caactus-scripts`, make sure to have the `caactus-env` activated.


## Install ilastik
- [Download and install ilastik](https://www.ilastik.org/download) for your respective operating system.
- Please note, we developed the pipeline on ilastik 1.4.0. For optimal user experience, we recommend installing ilastik 1.4.0. For this, scroll down to "Previous stable versions" on the ilastik download webpage. 

# Quick Overview of the workflow
1. **Culture** organism of interest in 96-well plate
2. **Acquire** images of cells via microscopy.
3. **Create** project directory
4. **Rename** Files with the caactus-script ```renaming```
5. **Convert** files to HDF5 Format with the caactus-script  ```tif2h5py```
6. Train a [pixel classification](https://www.ilastik.org/documentation/pixelclassification/pixelclassification) model in ilastik for and later run it batch-mode.
7. Train a [boundary-based segmentation with Multicut](https://www.ilastik.org/documentation/multicut/multicut) model in ilastik for and later run it batch-mode.
8. **Remove** the background from the images using ```background_processing```
9. Train a [object classification](https://www.ilastik.org/documentation/objects/objects) model in ilastik for  and later run it batch-mode.
10. **Pool** all csv-tables  from the individual images into one global table with ```csv_summary```
- output generated: 
    - "df_clean.csv"
11. **Summarize** the data with  ```summary_statistics```
- output generated:
    - a) "df_summary_complete.csv" = .csv-table containing also "not usable" category,
    - b) "df_refined_complete.csv" = .csv-table without "not usable" category", 
    - c) "counts.csv" dataframe used in PlnModelling
    - d) bar graph ("barchart.png")
12. **Model** the count data with ```pln_modelling```
  - output generated:
    - a) "correlation_circle.png"
    - b) "pca_plot.png"

## Sample Dataset
- a sample dataset to quickly test the workflow can be accessed via  [zenodo](https://doi.org/10.5281/zenodo.18799803)
- to showcase the functionalties, the ilastik steps have been pretrained. Use caactus in batch-modes.



# Detailed Description of the Workflow
## 1. Culturing
- Culture your cells in a flat bottom plate of your choice and according to the needs of the organims being researched.
## 2. Image acquisition
- In your respective microscopy software environment, save the images of interest to `.tif-format`.
- From the image metadata, copy the pixel size. 

## 3. Data Preparation
### 3.1 Create Project Directory

- For portability of the ilastik projects create the directory in the following structure:\
(Please note: the below example already includes examples of resulting files in each sub-directory)
- This allows you to copy an already trained workflow and use it multiple times with new datasets.

```
project_directory = Main folder  
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

## 3.2 Getting started
- open the the caacuts Graphical User Interface (GUI) by opening the command line in Unix or Anaconda Powershell/Prompt in Windows.
- make sure you have the caactus environmnet activated 
```bash
conda activate caactus-env
```
- now simply type `caactus` and hit `enter`to start the graphical user interace
```bash
caactus
```
- On the top, enter the path to your mainfolder.
- For steps where it is relevant, choose between training and batch mode.
- The subdirectories have default naming according to 3.1. You can rename them.
- When all information have been entered, click ```Run```.
- Processing messages will appear on the bottom.
- The output can be accessed by inspecting the respective subdirectory from your main folder. 

## 4. Training

To facilitate cross-platform reusability of the ilastik models, make sure to store Raw Data, Probabilities and Prediction Maps in Relative Links. This allows for portability of the models to other storage locations.

![relative_link](caactus/gui/assets/images/relative_location.png)

In case absolute file path is selected, right click on the location and select `edit properties` under `storage` the path logic can be modified

![relative_storage](caactus/gui/assets/images/relative_storage.png)


### 4.1. Selection of Training Images and Conversion
#### 4.1.1 Selection of Training data
- select a set of images that represant the different experimental conditions best
- store them in `0_1_original_tif_training_images`

#### 4.1.2 Conversion
1. Go to the `tif2h5py` tab. Select `Training` from the dropdown menu.
- The script in the background will convert `.tif-files` to `.h5-format`. 
- The `.h5-format` allows for better [performance when working with ilastik](https://www.ilastik.org/documentation/basics/performance_tips). 
2. When the file path are correct, click ```Run```.

### 4.2. Pixel Classification
1. When first training a pixel classification model in ilastik, open ilastik.

2. Create a new project and select "Pixel Classification" as the workflow.

3. Save it as 1_pixel_classification.ilp inside the main project directory.

4. Under Raw Data, add the .h5 files from 1_images folder.

5. Feature selection. Select the features you want to use for training. It is recommended to use all features.

6. For working with neighbouring / touching cells, it is suggested to create three classes: 
0 = interior, 
1 = background, 
2 = boundary 
(This follows python's 0-indexing logic where counting is started at 0).
![pixel_classes](caactus/gui/assets/images/pixel_classification_classes.JPG)


7. Annotate the classes by drawing on the images.

8. Export the Predictions.
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- File:
  ```bash
  {dataset_dir}/../2_probabilties/{nickname}_{result_type}.h5
  ```

![export_prob](caactus/gui/assets/images/export_probabilities.JPG)


- For more information, consult the [documentation for pixel classification with ilastik](https://www.ilastik.org/documentation/pixelclassification/pixelclassification). 


### 4.3 Boundary-based Segmentation with Multicut
1. When first training a boundary-based Segmentation model in ilastik, open ilastik.

2. Create a new project and select "Boundary-based Segmentation with Multicut" as the workflow.

3. Save it as `2_boundary_segmentation.ilp` inside the main project directory.

4. Under Raw Data, add the .h5 files from `1_images folder`.

5. Under Probabilities, add the data_Probabilities.h5 files from `2_probabilites` folder.

6. in DT Watershed,  use the input channel the corresponds to the order you used under project setup (in this case input channel = 2).

![watershed](caactus/gui/assets/images/watershed.png)


7. Annotate the edges by clicking on the edges between cells. Annotate the background by clicking on the background.

8. Export the Multicut Segmentation.
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- File:
  ```bash
  {dataset_dir}/../3_multicut/{nickname}_{result_type}.h5
  ```

![export_multicut](caactus/gui/assets/images/export_multicut.JPG)


- For more information follow the [documentation for boundary-based segmentation with Multicut](https://www.ilastik.org/documentation/multicut/multicut).  


### 4.4 Background Processing
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will thus be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
1. Select the `background-processing` tab in the GUI.
2. Select `Training` mode from the dropdown menu.
3. When the file path are correct, click ```Run```.


### 4.5. Object Classification
1. When first training a Object classification model in ilastik, open ilastik.

2. Create a new project and select "Object Classification [Inputs: Raw, Data, Pixel Prediction Map]" as the workflow.

3. Save it as 3_object_classification.ilp inside the main project directory.

4. Under "Raw Data", add the .h5 files from 1_images folder.

5. Under "Segmentation Image", add the data_Multicut Segmentation.h5 files from 3_multicut folder.

6. Define your cell types plus an additional category for "not-usable" objects, e.g. cell debris and cut-off objects on the side of the images.
Please note: default settings for the cell names in caactus are `resting`, `swollen`, `germling`, `hyphae`, `notusable` (and `mycelium` for EUCAST steps). You are welcome to change the names. Make sure to also change the names in the caactus GUI when performing analysis steps below.


7. Annotate the edges by clicking on the edges between cells.
 Annotate the background by clicking on the background.

8. Export the Object_Predictions.
In `Choose Export Imager Settings` change settings to
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- File:
  ```bash
  {dataset_dir}/../4_objectclassification/{nickname}_{result_type}.h5
  ```

![export_multicut](caactus/gui/assets/images/export_objectclassification.JPG)


9. Export the Object data_table.csv-files
In `Configure Feature Table Export General` change seetings to
- format `.csv` and output directory File:
  ```bash
  {dataset_dir}/../4_objectclassification/{nickname}.csv
  ```
- select your features of interest for exporting
![export_prob](caactus/gui/assets/images/object_tableexport.JPG)

For more information follow the [documentation for object classification](https://www.ilastik.org/documentation/objects/objects).


## 5. Batch Processing
- Once you have successfully trained all three ilastik models, you are ready to process large image datasets with the caactus pipeline.
1. store the images you want to process in the `0_2_original_tif_batch_images` directory
2. Perform steps 4.1 to 4.5 in batch mode, as explained in detail below (5.1 to 5.5).
3. When relevant select batch in the dropdown menu in the caactus GUI.
- For more information, follow the [documentation for batch processing](https://www.ilastik.org/documentation/basics/batch)
  
### 5.1 Rename Files
- Rename the `.tif-files` so that they contain information about your cells and experimental conditions
1. Create a csv-file that contains the information you need in columns. Each row corresponds to one image. Follow the same order as your images files are stored in the respective directory.

- The script will rename your files in the following format ```columnA-value1_columnB-value2_columnC_etc.tif ``` eg. as seen in the example below picture 1 (well A1 from our plate) will be named ```strain-ATCC11559_date-20241707_timepoint-6h_biorep-A_techrep-1.tif ```

2. Select the Renaming tab in the caactus GUI. When the file path are correct, click ```Run```.
![96_well](caactus/gui/assets/images/96_well_setup.png)

CAVE: Do not use underscores or dashes in the column names or values, as they will be used as delimiters in the new file names.

CAVE: The only hardcoded column names needed are "biorep", and "techrep". They are needed in downstream analysis for calculating averages.

CAVE: After successfully having renamed the files, we recommend deleting the content of 0_2_original_tif_batch_images in order to save disk space.
"""

#### 5.2 Conversion
1. Go to the `tif2h5py` tab. Select `Batch` from the dropdown menu.
- The script in the background will convert `.tif-files` to `.h5-format`. 
- The `.h5-format` allows for better [performance when working with ilastik](https://www.ilastik.org/documentation/basics/performance_tips). 
2. When the file path are correct, click ```Run```.

CAVE: After successfully having converted the files, we recommend deleting the content of 0_3_batch_renamed in order to save disk space.

### 5.3 Batch Processing Pixel Classification

1. Open ilastik.

2. Open your trained ilastik pixel classification project (e.g. `1_pixel_classification.ilp`).

CAVE: DO NOT CHANGE anything in 1. Input Data, 2. Feature Selection and 3. Training when running Batch Processing!

3. Under `4. Prediction Export`, select `Export predictions` and name the folder for the output at `File`:
  ```bash
  {dataset_dir}/../6_batch_probabilities/{nickname}_{result_type}.h5
  ```

![batch_pixel](caactus/gui/assets/images/batch_pixel.png)

4. Go to `5. Batch processing` tab

5. Under `Raw data`, add the .h5 files from `5_batch_images` folder.                                                                  
                                                                                    
6. Now click `Process all files`.

7. The output will be saved as _Probabilities.h5 files in the output folder.

### 5.4 Batch Processing Multicut Segmentation

1. Open ilastik.

2. Open your trained ilastik boundary-Segmentation project (e.g. open the `2_boundary_segmentation.ilp` project file).
CAVE: DO NOT CHANGE anything in 1. Input Data, 2. DT Watershed, and 3. Training and Multicut, when running Batch Processing!

3.  Under `4. Data Export`, select `Choose Export Image Settings` and choose a folder for the output (e.g. 7_batch_multicut).
- under `Choose Export Image Settings` change the export directory to `File`:
  ```bash
  {dataset_dir}/../7_batch_multicut/{nickname}_{result_type}.h5
  ```
4. Go to `5. Batch processing`.

5. Under,`Raw data`, add the .h5 files from `5_batch_images` folder.
                                                                                                                                                                          
6. Under `Probabilities`, add the data_Probabilities.h5 files from `6_batch_probabilities` folder.

![batch_multicut](caactus/gui/assets/images/batch_multicut.png)

7. Go to `5. Batch Processing` and click `Process all files`.

8. The output will be saved as _Multicut Segmentation.h5 files in the output folder.




### 5.5 Background Processing 
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will thus be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
1. Select the `background-processing` tab in the GUI.
2. Select `Batch` mode from the dropdown menu.
3. When the file path are correct, click ```Run```.


### 5.6 Batch processing Object classification 

1. Open ilastik.

2. Open your trained ilastik object classification project (`3_object_classification.ilp`).
CAVE: DO NOT CHANGE anything in 1. Input Data, 2. Object Feature Selection, 3. Object Classification, when running Batch Processing!

3. Under `4. Object Information Export`, choose  `Export Image Settings` change the export directory to `File`:
  ```bash
  {dataset_dir}/../8_batch_objectclassification/{nickname}_{result_type}.h5
  ```
![object_image](caactus/gui/assets/images/batch_object_image.png)

4. Under "4. Object Information Export", choose "Configure Feature Table Export" with the following settings:
![feature_table](caactus/gui/assets/images/feature_table_export.png)
                                                                        
5. In `Configure Feature Table Export General` choose format `.csv` and change output directory to:
  ```bash
  {dataset_dir}/../8_batch_objectclassification/{nickname}.csv
  ```

Choose  `Features` to choose the Feature you are interested in exporting

![feature_features](caactus/gui/assets/images/features_of_featuretable.png)

6. Go to 5. `Batch Processing` tab

7. Under  `Raw data`, add the .h5 files from `5_batch_images` folder.

8. Under `Segmentation Image`, add the data_Multicut Segmentation.h5 files from `7_batch_multicut` folder.

9. Go to `5. Batch Processing` and click `Process all files`.

10. The output will be saved as data_Object Predictions.h5 files and data_table.csv in the output folder.



## 6. Post-Processing and Data Analysis

- Please be aware, the last two scripts, `summary_statisitcs.py` and `pln_modelling.py` at this stage are written for the analysis and visualization of two independent variables.

### 6.1 Merging Data Tables and Table Export

The next script will combine all tables from all images into one global table for further analysis. Additionally, the information stored in the file name will be added as columns to the dataset. 
- Technically from this point on, you can continue to use whatever software / workflow your that is easiest for use for subsequent data analysis. 
1. Go to the `CSV summary` tab in the caactus GUI.
2. Enter the pixel size for cell size calculation.
3. When the file path are correct, click ```Run```.
4. The output generated will be `df_clean.csv`.
5. This spreadsheet now has all feature tables that are the output of 5.6 Object classification united in one spreadsheet.
5. You can use this spreadsheet now, to continue with analysis in the software of your choice.


### 6.2 Creating Summary Statistics

- This script processes EUCAST data and generates summary statistics and a stacked bar plot of predicted classes cell categories.
- If working with EUCAST antifungal susceptibility testing, use the `Summary Statistics EUCAST` tab
- For the stacked bar plot, it groups data by the two variables that you enter.
- It computes the average count and percentage of each predicted class, across replicates (technical and biological), for each combination of the two grouping variables.
- It visualizes the distribution in stacked bar plots of classes across different conditions.
- The first variable you enter will be displayed on the x-axis (e.g. incubation temperature), and the second variable will be used for faceting (e.g. timepoint).
- This will create separate subplots for each level of that variable.
- The plot will show the percentage distribution of predicted classes for each condition, allowing you to compare how the classes are distributed across different experimental conditions defined by the two grouping variables.
- The colors of the bars will correspond to the predicted classes, as defined in your color mapping.
- By default the IBM coloor-blind friendly palette is used, but you can customize the colors by providing the HEX color code.
1. Go to the `Summary Statistics` tab in the caactus GUI.
2. When the file path are correct, click ```Run```.
3. The output generated will be 
    - a) "df_summary_complete.csv" = .csv-table containing also "not usable" category,
    - b) "df_refined_complete.csv" = .csv-table without "not usable" category", 
    - c) "counts.csv" dataframe used in PlnModelling
    - d) bar graph ("barchart.png")
4. CAVE: all fields contain default values. You may change them to your needs. E.g. edit `Variable names`to enter the variables you are interested in for analysis. Edit `Class order` to name it according to your cell morphotype names and ordering. Change the `Color mapping`according to the logic of `Class order`. 

### 6.3 PLN Modelling 

- This script runs ZIPln modelling on input data with dynamic design and generates PCA visualizations and a correlation circle plot.

- The two grouping variables you enter will be used in the model formula and for visualizing the PCA results.

- The will be combined into a single factor for the model, and the PCA plot will show the latent variable projections colored by this combined category.

- The correlation circle plot will show how the original variables relate to the latent dimensions, helping you interpret the PCA results in terms of the original grouping variables.

- CAVE: the limit of categories for display in the PCA-plot is n=15

1. Go to the `PLN modelling` tab in the caactus GUI.
2. When the file path are correct, click ```Run```.
3. The output generated will be 
    - a) "correlation_circle.png"
    - b) "pca_plot.png"
4. CAVE: all fields contain default values. You may change them to your needs. E.g. edit `Variable names`to enter the variables you are interested in for analysis. Edit `Class order` to name it according to your cell morphotype names and ordering.


## 7. Tutorial
### 7.1 Download Sample Data
1. Go to [zenodo](https://doi.org/10.5281/zenodo.18799803) to download the sample data.
2. Unpack the `.zip`-file into your project folder.
3. The path to where you unpacked the sample data will be your main folder.
4. To showcase the functionalties, the ilastik steps have been pretrained. Use caactus in batch-mode for the following steps. Please note, we intentionally left some subdirectories empty for the tutorial. The intend of the the tutorial is that potential users learn how to run the batch mode with pretrained models. The subdirectory `0_1_original_tif_training_images`is empty and will stay empty. The other empty subdirectories will get filled with data once the user follows the below explained steps. 
5. 
- make sure you have caactus installed (see Installation above)
- make sure you have the caactus environmnet activated 
```bash
conda activate caactus-env
```
- now simply type `caactus` and hit `enter`to start the graphical user interace
```bash
caactus
```
6. On the top, enter the path to your mainfolder.

7. We recommend working with two screens. This allows to follow the instructions implemented in the caactus GUI while performing the steps in ilastik and quickly switiching back to the caactus steps for fast completion of the pipeline.

### 7.2 Renaming
1. Inspect the `renaming.csv` spreadsheet, to see how the `renaming.csv` is constucted and filled.
2. Go the renaming tab inside the caactus GUI.
3. Enter the main folder path fro 7.3
4. Click `Run`

## 7.3 Batch Pixel Classification
1. Open ilastik.

2. Open the pre-trained ilastik pixel classification project from the sample data in the main folder (`1_pixel_classification.ilp`).
CAVE: DO NOT CHANGE anything in 1. Input Data, 2. Feature Slection 3. Training when running Batch Processing!

3. Under `4. Prediction Export`, select `Export predictions` and choose a folder for the output to `File`:
  ```bash
  {dataset_dir}/../6_batch_probabilities/{nickname}_{result_type}.h5
  ```

![batch_pixel](caactus/gui/assets/images/batch_pixel.png)

4. Go to `5. Batch processing` tab

5. Under `Raw data`, add the .h5 files from `5_batch_images` folder.                                                                  
                                                                                    
6. Now click `Process all files`.

7. The output will be saved as _Probabilities.h5 files in the output folder.


## 7.4 Batch Processing Multicut Segmentation
1. In ilastik open the next project file.
 
2. Open the pre-trained ilastik boundary-Segmentation project from the sample data in the main folder (`2_boundary_segmentation.ilp` project file).
CAVE: DO NOT CHANGE anything in 1. Input Data, 2. DT Watershed, 3. Training and Multicut, when running Batch Processing!

3.  Under `4. Data Export`, select `Choose Export Image Settings` and choose a folder for the output (e.g. 7_batch_multicut).
- under `Choose Export Image Settings` change the export directory to `File`:
  ```bash
  {dataset_dir}/../7_batch_multicut/{nickname}_{result_type}.h5
  ```
4. Go to `5. Batch processing`.

5. Under,`Raw data`, add the .h5 files from `5_batch_images` folder.

6. Under `Probabilities`, add the data_Probabilities.h5 files from `6_batch_probabilities` folder.

![batch_multicut](caactus/gui/assets/images/batch_multicut.png)

7. Go to `5. Batch Processing` and click `Process all files`.

8. The output will be saved as _Multicut Segmentation.h5 files in the output folder.

9. Close the `2_boundary_segmentation.ilp`project-file in ilastik.


## 7.5 Batch Background Processing
1. Switch back to the caactus GUI.
2. Select the `background-processing` tab in the GUI.
3. Select `Batch` mode from the dropdown menu.
4. When the file paths are correct, click ```Run```.
5. The background now has been deleted and you can continue with object classification in ilastik.


## 7.8 Batch Object classification
1. Switch back to ilastik.

2. Open your trained ilastik object classification project (`3_object_classification.ilp`).
CAVE: DO NOT CHANGE anything in 1. Input Data, 2. Object Feature Selection, 3. Object Classification, when running Batch Processing!

3. Under `4. Object Information Export`, choose  `Export Image Settings` change the export directory to `File`:
  ```bash
  {dataset_dir}/../8_batch_objectclassification/{nickname}_{result_type}.h5
  ```
![object_image](caactus/gui/assets/images/batch_object_image.png)

4. Under "4. Object Information Export", choose "Configure Feature Table Export" with the following settings:
![feature_table](caactus/gui/assets/images/feature_table_export.png)
                                                                        
5. In `Configure Feature Table Export General` choose format `.csv` and change output directory to:
  ```bash
  {dataset_dir}/../8_batch_objectclassification/{nickname}.csv
  ```

Choose  `Features` to choose the Feature you are interested in exporting

![feature_features](caactus/gui/assets/images/features_of_featuretable.png)

6. Go to 5. `Batch Processing` tab

7. Under  `Raw data`, add the .h5 files from `5_batch_images` folder.

8. Under `Segmentation Image`, add the data_Multicut Segmentation.h5 files from `7_batch_multicut` folder.

9. Go to `5. Batch Processing` and click `Process all files`.                                                                                                                               
10. The output will be saved as data_Object Predictions.h5 files and data_table.csv in the output folder.

11. Now you have performed all steps in ilastik. You can close ilastik.

## 7.9 CSV summary
1. Switch back to the caactus GUI.
2. Go to the `CSV summary` tab in the caactus GUI.
2. You can leave the default pixel size for cell size calculation.
3. When the file paths are correct, click ```Run```.
4. Inspect the generated results. The output generated will be `df_clean.csv`.
5. This spreadsheet now has all feature tables that are the output of 5.6 Object classification united in one spreadsheet.
6. You can use this spreadsheet now, to continue with analysis in the software of your choice.

## 7.10 Summary Statistics
1. Go to the `Summary Statistics` tab in the caactus GUI.
2. Change the variable names to `['condition1','condition2']` . 
3. When the file paths are correct, click ```Run```.
4. Inspect the generated results. The output generated will be 
    - a) "df_summary_complete.csv" = .csv-table containing also "not usable" category,
    - b) "df_refined_complete.csv" = .csv-table without "not usable" category", 
    - c) "counts.csv" dataframe used in PlnModelling
    - d) bar graph ("barchart.png") (faceted by condition1 on x-axis, percent of morphotypes "Predicted Class" on the y-axis and condition2 as the facetting variable in rows.) You can play around by putting 'condition2' first and 'condition1' second to see how it changes the plot.
5. You may also change the colors:
 change the default 
`{'resting': '#FE6100', 'swollen': '#648FFF', 'germling': '#785EF0', 'hyphae': '#DC267F'}` <br>
 to <br>
`{'resting': 'yellow', 'swollen': 'cyan', 'germling': 'blue', 'hyphae': 'magenta'}` <br> 

6. Similarly, you my change the morphotype names. Open `df_clean.csv` in a speadsheet software (e.g. Excel). Replace all `resting`with `dormant` (use `Ctrl+F`). Now re-do step `7.10 Summary Statistics`. Before you click `Run`, make sure you replace `resting` with `dormant`in both `Class order`and `Color Mapping` fields.

## 7.11 PLN modelling
1. Go to the `PLN modelling` tab in the caactus GUI.
2. Change the variable names to `['condition1','condition2']` . 
3. When the file path are correct, click ```Run```.
4. Inspect the generated results. The output generated will be 
    - a) "correlation_circle.png". Shows that PCA1, accounting for 57.465% of the variance, primarily separated samples by condition2, whereas  PCA2 accounted for 24.57% of the variance based on condition1.
    - b) "pca_plot.png". The PCA plot shows how the images are grouped together in 2D-space based on combined category of condition1 and condition2 (the categorical levels will be combined).