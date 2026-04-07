DESCRIPTION = """
## Training: Pixel Classification

1. Open **ilastik**.

2. Create a new project and select **Pixel Classification** as the workflow.

3. Save it as `1_pixel_classification.ilp` inside the main project directory.

4. Under **Raw Data**, add the `.h5` files from the `1_images` folder.

5. Under **Feature Selection**, select all features (recommended).

6. Create **three classes** for neighbouring/touching cells:
- `0` = interior
- `1` = background
- `2` = boundary
(Follows Python's 0-indexing.)

<images/pixel_classification_classes.JPG>

7. Annotate each class by drawing on the images.

8. Under **4. Prediction Export**, click **Choose Export Image Settings**, configure the settings below and then click `OK`:
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- `File`: `{dataset_dir}/../2_probabilities/{nickname}_{result_type}.h5`

<images/export_probabilities.JPG>

9. Click **Export All**.

10. The output will be saved as `*_Probabilities.h5` files in the `2_probabilities` folder.
"""