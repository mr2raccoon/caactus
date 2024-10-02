# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 16:46:19 2024

@author: q243js
"""

from pyPLNmodels import ZIPln  # Import ZIPln for statistical modeling
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

def get_dynamic_columns():
    """
    Prompt the user to enter the column names to include in the analysis (e.g., 'germling,hyphae,resting').
    
    Returns:
    list: A list of column names to include in the analysis.
    """
    columns = input("Enter the Predicted Class column names to include in the analysis (comma-separated, e.g., 'germling,hyphae,resting'): ")
    return columns.split(',')

def get_variable_names():
    """
    Prompt the user to enter the variable names from the data (e.g., 'storage,time').
    
    Returns:
    list: A list of variable names to extract (e.g., 'storage,time').
    """
    variables = input("Enter the variable names to use from the data (comma-separated, e.g., 'storage,time'): ")
    return variables.split(',')

def main():
    # Get the input and output directories from the user
    input_dir = get_input_directory()
    output_dir = get_output_directory()

    # Get the dynamic columns and variable names from the user
    dynamic_columns = get_dynamic_columns()  # Columns like 'germling, hyphae, etc.'
    variable_names = get_variable_names()  # Variables like 'storage, time'

    # Read the counts data from the input directory
    counts = pd.read_csv(os.path.join(input_dir, 'counts_df.csv'), index_col=0)

    # Pivot the data based on user-specified variables
    pivot_df = counts.reset_index().pivot_table(
        index=["filename"] + variable_names,
        columns="Predicted Class",
        values="count",
        fill_value=0
    ).reset_index()

    print(pivot_df)  # Show the pivoted DataFrame for debugging

    # Remove the 'not usuable' column if it exists
    if 'not usuable' in pivot_df.columns:
        pivot_df = pivot_df.drop(columns=["not usuable"])

    # Create a new combined category column using the user-specified variables
    pivot_df['combined_category'] = pivot_df[variable_names[0]] + ' & ' + pivot_df[variable_names[1]].astype(str)

    # Extract the combined category and selected variables as numpy arrays
    combined_category = pivot_df["combined_category"].to_numpy()
    var1 = pivot_df[variable_names[0]].to_numpy()
    var2 = pivot_df[variable_names[1]].to_numpy()

    # Convert the dynamic columns (e.g., 'germling', 'hyphae') to a NumPy array for the model
    counts_df = pivot_df[dynamic_columns].to_numpy()

    print("Counts dataframe for dictionary:")
    print(counts_df)

    # Prepare the dictionary for pyPLNmodels
    combined_dict = {
        variable_names[0]: var1,
        variable_names[1]: var2,
        "counts": counts_df,
        "combined_category": combined_category
    }

    # Fit the ZIPln model using the dynamic variables and columns
    formula = f"counts ~ {variable_names[0]} * {variable_names[1]}"
    inflation = ZIPln.from_formula(formula, data=combined_dict)
    inflation.fit()

    print(inflation)

    # Summarize the results for each selected dynamic column
    for i, col in enumerate(dynamic_columns):
        print(f"Summary for {col}:")
        print(inflation.summary(variable_number=i))

    # Plotting the PCA analysis
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
