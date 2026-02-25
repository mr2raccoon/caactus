DESCRIPTION = """
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

<images/pixel_classification_classes.JPG>

7. Annotate the classes by drawing on the images.

8. Export the Predictions.

<images/export_probabilities.JPG>

"""