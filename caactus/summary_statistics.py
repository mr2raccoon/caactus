# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 09:53:38 2024

@author: q243js
"""

from pathlib import Path
import pandas as pd
import os
import seaborn.objects as so  # For plotting


def get_input_directory():
    return input("Enter the directory path of the cleaned .csv table to be imported: ")

def get_output_directory():
    return input("Enter the directory path where summary CSV files and figures should be saved: ")

def get_variable_names():
    """
    Ask the user which variables to extract from the filenames.
    
    Returns:
    list: A list of variable names to extract from the filenames (e.g., 'media', 'strain').
    """
    return input("Enter the variable names to extract from the filenames (comma-separated, e.g., 'media,strain' (the first variable entered will be on x-axis the second the facetting variable)): ").split(',')

def parse_filename(filename, variable_names):
    """
    Parse a filename into variable names and their values.
    
    Parameters:
    filename (str): The name of the file to be parsed (without the extension).
    variable_names (list): List of variables to extract from the filename.

    Returns:
    dict: A dictionary with variable names as keys and the extracted values as values.
    """
    filename = filename.replace('_table', '')  # Remove '_table' suffix if present
    parts = filename.split('_')
    metadata = {}
    for part in parts:
        var_name, var_value = part.split('-')
        if var_name in variable_names:
            metadata[var_name] = var_value
    
    print(f"Parsed metadata from filename: {filename} -> {metadata}")  # Debugging line
    return metadata

def process_cleaned_data(input_dir, output_dir, variable_names, color_mapping, class_order):
    # Read the cleaned CSV
    df_clean = pd.read_csv(os.path.join(input_dir, 'df_clean.csv'), index_col=0)

    # Group and aggregate counts
    counts = df_clean.groupby(['filename', 'Predicted Class']).size().reset_index(name='count')

    # Parse metadata from the filename and add as columns dynamically based on variable names
    for i, row in counts.iterrows():
        file_metadata = parse_filename(row['filename'], variable_names)
        for var in variable_names:
            counts.at[i, var] = file_metadata.get(var, None)

    # Export counts DataFrame
    counts.to_csv(os.path.join(output_dir, 'counts_df.csv'))

    # Aggregating and calculating metrics
    group_cols = variable_names.copy()  # Use all user-defined variables for grouping
    unique_bioreps = df_clean.groupby(group_cols)["biorep"].nunique()
    unique_techreps = df_clean.groupby(group_cols)["techrep"].nunique()

    merged_df = counts.groupby(group_cols + ["Predicted Class"])["count"].sum().reset_index(name="count")
    merged_df = merged_df.merge(unique_bioreps, on=group_cols, how="left")
    merged_df = merged_df.merge(unique_techreps, on=group_cols, how="left")

    # Calculating averages
    merged_df["average_count"] = round(merged_df["count"] / (merged_df["techrep"] * merged_df["biorep"]), 2)
    merged_df['%'] = round(100 * merged_df["average_count"] / merged_df.groupby(group_cols)["average_count"].transform('sum'), 2)

    # Average size calculation
    avg_size = df_clean.groupby(group_cols + ["Predicted Class"])["size_microm"].mean().round(2)
    merged_complete_df = merged_df.merge(avg_size, on=group_cols + ["Predicted Class"], how="left")

    merged_complete_df.to_csv(os.path.join(output_dir, 'df_summary_complete.csv'))

    # Create a plot with seaborn
    counts_df2 = counts.drop(counts[counts["Predicted Class"] == "not usuable"].index)
    counts_df2 = counts_df2.groupby(group_cols + ["Predicted Class"])["count"].sum().reset_index(name="count")

    counts_df2 = counts_df2.merge(unique_techreps, on=group_cols, how="left")
    counts_df2 = counts_df2.merge(unique_bioreps, on=group_cols, how="left")
    counts_df2["average_count"] = round(counts_df2["count"] / (counts_df2["techrep"] * counts_df2["biorep"]), 2)
    counts_df2["%"] = round(100 * counts_df2["count"] / counts_df2.groupby(group_cols)["count"].transform('sum'), 2)

    counts_df2_complete_df = counts_df2.merge(avg_size, on=group_cols + ["Predicted Class"], how="left")
    counts_df2_complete_df.to_csv(os.path.join(output_dir, 'df_refined_complete.csv'))

    # Plotting
    counts2_reduced_df = counts_df2.drop(["count", "techrep", "biorep"], axis=1)
    counts2_reduced_df['Predicted Class'] = pd.Categorical(counts2_reduced_df['Predicted Class'], categories=class_order, ordered=True)
    counts2_pivot_df = counts2_reduced_df.pivot_table(index=group_cols, columns="Predicted Class", values="%", aggfunc="sum", observed=False)
    counts2_pivot_df = counts2_pivot_df.replace(0, float('nan')).reset_index()

    # Melt the DataFrame for seaborn
    counts2_melted_df = counts2_pivot_df.melt(id_vars=group_cols, value_vars=class_order, var_name='Predicted Class', value_name='%')
    counts2_melted_df = counts2_melted_df.dropna()
    counts2_melted_df['Predicted Class'] = pd.Categorical(counts2_melted_df['Predicted Class'], categories=class_order, ordered=True)

    # Create the color palette
    color_palette = [color_mapping[class_name] for class_name in class_order]

    # Plot with seaborn objects
    plot = so.Plot(counts2_melted_df, x=group_cols[0], y="%", color="Predicted Class", text="%")
    plot = plot.facet(row=group_cols[1]).layout(size=(8, 4))  # Adjust size dynamically based on first two grouping vars
    plot = plot.add(so.Bar(), so.Stack()).scale(color=color_palette)
    plot.plot()
    plot.save(os.path.join(output_dir, 'barchart.png'), bbox_inches="tight")

if __name__ == "__main__":
    input_dir = get_input_directory()
    output_dir = get_output_directory()

    # Get the variable names from the user
    variable_names = get_variable_names()

    # Define the class order and color mapping (you can also make this dynamic if needed)
    class_order = ['resting', 'swollen', 'germling', 'hyphae']
    color_mapping = {
        'resting': 'yellow',
        'swollen': 'blue',
        'germling': 'red',
        'hyphae': 'cyan'
    }

    process_cleaned_data(input_dir, output_dir, variable_names, color_mapping, class_order)
