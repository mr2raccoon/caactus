DESCRIPTION = """
## Training: Boundary Segmentation

1. Open **ilastik**.

2. Create a new project and select **Boundary-based Segmentation with Multicut** as the workflow.

3. Save it as `2_boundary_segmentation.ilp` inside the main project directory.

4. Under **Raw Data**, add the `.h5` files from the `1_images` folder.

5. Under **Probabilities**, add the `*_Probabilities.h5` files from the `2_probabilities` folder.

6. In **DT Watershed**, use the input channel that corresponds to the boundary class from Pixel Classification (the number of the channel corresponds to the boundary class (0-indexed)).

<images/watershed.png>

7. Annotate edges between cells and the background region.

8. Under **4. Data Export**, click **Choose Export Image Settings** and configure:
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- `File`: `{dataset_dir}/../3_multicut/{nickname}_{result_type}.h5`

<images/export_multicut.JPG>

9. Click **OK**.

10. Click **Export All**.

11. The output will be saved as `*_Multicut Segmentation.h5` files in the `3_multicut` folder.
"""