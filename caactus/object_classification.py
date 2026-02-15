DESCRIPTION = """
1. When first training a Object classification model in ilastik, open ilastik.

2. Create a new project and select "Object Classification [Inputs: Raw, Data, Pixel Prediction Map]" as the workflow.

3. Save it as 3_object_classification.ilp inside the main project directory.

4. Under Raw Data, add the .h5 files from 1_images folder.

5. Under Prediction Maps, add the data_Multicut Segmentation.h5 files from 3_multicut folder.

6. Define your cell types plus an additional category for "not-usuable" objects, e.g. cell debris and cut-off objects on the side of the images.

<images/watershed.png>

7. Annotate the edges by clicking on the edges between cells.
 Annotate the background by clicking on the background.

8. Export the Object_Predictions.

<images/export_objectclassification.JPG>

9. Export the Object data_table.csv-files

<images/object_tableexport.JPG>


"""