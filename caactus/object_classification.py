DESCRIPTION = """
## Training: Object Classification

1. Open **ilastik**.

2. Create a new project and select **Object Classification [Inputs: Raw Data, Pixel Prediction Map]** as the workflow.

3. Save it as `3_object_classification.ilp` inside the main project directory.

4. Under **Raw Data**, add the `.h5` files from the `1_images` folder.

5. Under **Segmentation Image**, add the `*_Multicut Segmentation.h5` files from the `3_multicut` folder.

6. Define your cell classes plus a **"not-usable"** category (for debris and cells cut off at image borders).
Default class names: `resting`, `swollen`, `germling`, `hyphae`, `notusable` (and `mycelium` for EUCAST workflow). 
You are welcome to change the names. 
Make sure to also change the names in the caactus GUI when performing analysis steps below.

<images/watershed.png>

7. Annotate objects by clicking on them in each class.

8. Under **4. Object Information Export**, click **Choose Export Image Settings** and set the output path to `File`:
`{dataset_dir}/../4_objectclassification/{nickname}_{result_type}.h5`

<images/export_objectclassification.JPG>

9. Click **Configure Feature Table Export**, set format to `.csv` and output path to:
`{dataset_dir}/../4_objectclassification/{nickname}.csv`

<images/object_tableexport.JPG>

10. Click **OK**.

11. Click **Export All**.

12. The output will be saved as `*_Object Predictions.h5` files and `*_table.csv` in the `4_objectclassification` folder.
"""