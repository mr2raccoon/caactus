DESCRIPTION = """
1. When first training a boundary-based Segmentation model in ilastik, open ilastik.

2. Create a new project and select "Boundary-based Segmentation with Multicut" as the workflow.

3. Save it as 2_boundary_segmentation.ilp inside the main project directory.

4. Under Raw Data, add the .h5 files from 1_images folder.

5. Under Probabilities, add the data_Probabilities.h5 files from 2_probabilites folder.

6. in DT Watershed,  use the input channel the corresponds to the order you used under project setup (in this case input channel = 2).

<images/watershed.png>

7. Annotate the edges by clicking on the edges between cells.
 Annotate the background by clicking on the background.

8. Export the Multicut Segmentation.

<images/export_multicut.JPG>

"""