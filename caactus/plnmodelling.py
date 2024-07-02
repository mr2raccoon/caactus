# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:59:09 2024

@author: q243js
"""

# -*- coding: utf-8 -*-
"""
Created on Tue May 28 10:36:06 2024

@author: q243js
"""

from pyPLNmodels import ZIPln  # Import ZIPln from pyPLNmodels for statistical modeling
import pandas as pd  # For data manipulation
import numpy as np  # For numerical operations
import os  # For interacting with the operating system
import matplotlib.pyplot as plt  # For plotting

def get_input_directory():
    """
    Prompt the user to enter the directory path of the .csv files to be imported.

    Returns:
    str: The input directory path entered by the user.
    """
    return input("Enter the directory path of the .csv-files to be imported: ")

def get_output_directory():
    """
    Prompt the user to enter the directory path where the summary .csv files and figure should be saved.

    Returns:
    str: The output directory path entered by the user.
    """
    return input("Enter the directory path of the summary-csv-files and figure to be saved to: ")

def main():
    # Get the input and output directories from the user
    input_dir = get_input_directory()
    output_dir = get_output_directory()

    # Read the counts data from the input directory
    counts = pd.read_csv(os.path.join(input_dir, 'counts_df.csv'), index_col=0)

    # Prepare data for pyPLNmodels after import
    pivot_df = counts.reset_index().pivot_table(
        index=["file", "storage", "time"],
        columns="Predicted Class",
        values="count",
        fill_value=0
    ).reset_index()

    # Print the resulting pivoted DataFrame
    print(pivot_df)

    pivot_df2 = pivot_df.drop(columns=["not usuable"])

    # Create a new combined category column
    pivot_df2['combined_category'] = pivot_df2['storage'] + ' & ' + pivot_df2['time'].astype(str)

    combined_category = pivot_df2["combined_category"].to_numpy()
    print(combined_category)

    storage = pivot_df2["storage"].to_numpy()
    print(storage)

    time = pivot_df2["time"].to_numpy()
    print(time)

    # Specify the columns to convert
    columns_to_convert = ["germling", "hyphae", "resting", "swollen"]

    # Extract column names
    column_names = columns_to_convert

    labels = np.array(columns_to_convert).reshape(1, -1)

    # Convert to NumPy array
    counts_df = pivot_df2.drop(columns=["file", "storage", "time", "combined_category"])

    print("Counts dataframe for dictionary:")
    print(counts_df)
    print("\nColumn Names:")
    print(column_names)

    combined_dict = {
        "storage": storage,
        "time": time,
        "counts": counts_df,
        "labels": labels,
        "combined_category": combined_category
    }

    # Fit the ZIPln model and summarize the results
    inflation = ZIPln.from_formula("counts ~ storage*time", data=combined_dict)
    inflation.fit()
    print(inflation)
    for i in range(len(column_names)):
        print(inflation.summary(variable_number=i))
    
    # Create a figure and axis for the plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size if needed
    inflation.viz(ax=ax, colors=combined_dict["combined_category"][~inflation.samples_only_zeros.numpy()])

    # Adjust the layout to make room for the legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])  # Shrink the plot area to make room for the legend
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Combined Category')

    # Save and show the plot
    plt.savefig(os.path.join(output_dir, 'pca_plot.png'), bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
