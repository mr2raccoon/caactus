# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 13:43:02 2024

@author: q243js
"""

from pathlib import Path  # For handling file system paths
import pandas as pd  # For data manipulation
import matplotlib.pyplot as plt  # For plotting
import os  # For interacting with the operating system

def get_input_directory():
    """
    Prompt the user to enter the directory path of the cleaned .csv table to be imported.

    Returns:
    str: The input directory path entered by the user.
    """
    return input("Enter the directory path of the cleaned .csv-table to be imported: ")

def get_output_directory():
    """
    Prompt the user to enter the directory path where the summary .csv files and figures should be saved.

    Returns:
    str: The output directory path entered by the user.
    """
    return input("Enter the directory path of the summary-csv-files and figure to be saved to: ")

def process_summary_statistics(input_dir, output_dir):
    """
    Process the cleaned CSV file to generate summary statistics and plots.

    Parameters:
    input_dir (str): Path to the directory containing the cleaned CSV file.
    output_dir (str): Path to the directory where summary CSV files and plots will be saved.
    """
    # Ensure the input directory is a valid path
    input_path = Path(input_dir)
    df_clean = pd.read_csv(os.path.join(input_dir, 'df_clean.csv'), index_col=0)

    # Summary aggregation
    # Prepare counts dataframe for further processing in PLN module
    # Group by "storage", "time", and "Predicted Class" and count the occurrences of "Predicted Class"
    counts = df_clean.groupby(['file', 'Predicted Class']).size().reset_index(name='count')
    counts['storage'] = counts['file'].str.split('_').str[2]
    counts['time'] = counts['file'].str.split('_').str[3]

    # Factor level renaming
    time_mapping = {
        '4h': '4 h',
        '6h': '6 h'
    }
    storage_mapping = {
        'a': 'frozen',
        'b': '4 °C',
        'c': 'fresh'
    }

    # Replace the factor levels
    counts['time'] = counts['time'].replace(time_mapping)
    counts['storage'] = counts['storage'].replace(storage_mapping)

    counts["storage"] = counts["storage"].astype("category")
    counts["storage"] = counts["storage"].cat.reorder_categories(["frozen", "4 °C", "fresh"])

    counts["Predicted Class"] = counts["Predicted Class"].astype("category")
    counts["Predicted Class"] = counts["Predicted Class"].cat.reorder_categories(["not usuable", "resting", "swollen", "germling", "hyphae"])
    counts = counts[["file", "storage", "time", "Predicted Class", "count"]]
    print(counts)

    # Export counts_df
    counts.to_csv(os.path.join(output_dir, 'counts_df.csv'))

    # Calculate percentages per group
    # Number of experiments
    unique_experiments = df_clean.groupby(["storage", "time"])["experiment"].nunique()
    print(unique_experiments)

    # Number of parallels
    unique_parallels = df_clean.groupby(["storage", "time"])["parallel"].nunique()
    print(unique_parallels)

    merged_df = counts.groupby(["storage", "time", "Predicted Class"])["count"].sum().reset_index(name="count")

    # Merge counts with unique parallels and experiments per group
    merged_df = merged_df.merge(unique_experiments, on=["storage", "time"], how="left")
    print(merged_df)

    merged_df = merged_df.merge(unique_parallels, on=["storage", "time"], how="left")
    print(merged_df)

    # Calculate the average counts by dividing by the number of unique "parallels" and "experiments"
    merged_df["average_count"] = round(merged_df["count"] / (merged_df["parallel"] * merged_df["experiment"]), 2)

    # Calculate percentages
    merged_df['%'] = round(100 * merged_df["average_count"] / merged_df.groupby(["storage", "time"])["average_count"].transform('sum'), 2)

    # Calculate the average size
    avg_size = df_clean.groupby(["storage", "time", "Predicted Class"])["size_µm"].mean().round(2)
    print(avg_size)

    merged_complete_df = merged_df.merge(avg_size, on=["storage", "time", "Predicted Class"], how="left")
    print(merged_complete_df)

    merged_complete_df.to_csv(os.path.join(output_dir, 'df_summary_complete.csv'))

    # DataFrame with no "not usable"
    counts_df2 = counts.drop(counts[counts["Predicted Class"] == "not usuable"].index)
    counts_df2 = counts_df2.groupby(["storage", "time", "Predicted Class"])["count"].sum().reset_index(name="count")

    # Merge counts with unique parallels per group
    counts_df2 = counts_df2.merge(unique_parallels, on=["storage", "time"], how="left")
    print(counts_df2)

    # Calculate the average counts by dividing by the number of unique "parallels"
    counts_df2["average_count"] = round(counts_df2["count"] / counts_df2["parallel"], 2)

    # Calculate percentages
    counts_df2["%"] = round(100 * counts_df2["count"] / counts_df2.groupby(["storage", "time"])["count"].transform('sum'), 2)
    print(counts_df2)

    counts_df2_complete_df = counts_df2.merge(avg_size, on=["storage", "time", "Predicted Class"], how="left")
    print(counts_df2_complete_df)

    counts_df2_complete_df.to_csv(os.path.join(output_dir, 'df_refined_complete.csv'))

    # Stacked bar plot
    counts2_reduced_df = counts_df2.drop(["count", "parallel"], axis=1)

    # Define your custom order
    class_order = ['resting', 'swollen', 'germling', 'hyphae']
    counts2_reduced_df['Predicted Class'] = pd.Categorical(counts2_reduced_df['Predicted Class'], categories=class_order, ordered=True)

    counts2_pivot_df = counts2_reduced_df.pivot_table(index=["storage", "time"], columns="Predicted Class", values="%", aggfunc="sum")
    counts2_pivot_df = counts2_pivot_df.replace(0, float('nan'))

    color_mapping = {
        'resting': 'yellow',
        'swollen': 'blue',
        'germling': 'red',
        'hyphae': 'cyan',
    }
    colors = [color_mapping[class_name] for class_name in class_order]  # Ensure colors follow the same order

    ab = counts2_pivot_df.plot(kind='bar', stacked=True, color=colors, figsize=(8, 6), rot=0, xlabel='Storage Condition and Time after Inoculation', ylabel='Percentage (%)')
    plt.legend(title='Predicted Class')
    ab.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # Dictionary to keep track of the last used y position for labels on the right of each bar
    last_used_y_position = {}

    # Iterate over each container (group of bars) in the plot
    for c in ab.containers:
        for v in c:
            height = v.get_height()
            idx = v.get_x()  # Index as x position of the bar
            base_y = v.get_y() + height  # Base y is the top of the current bar segment

            if height > 0.9:
                # Labels inside the bar
                label = f'{height:.2f}'
                x = v.get_x() + v.get_width() / 2
                y = v.get_y() + height / 2
                ha = 'center'
                va = 'center'
            elif 0 < height <= 0.9:
                # Labels to the right of the bar
                label = f'{height:.2f}'
                x = v.get_x() + v.get_width() + 0.02  # Offset to the right
                y = last_used_y_position.get(idx, base_y) + 0.02  # Start slightly above the base_y or last used y
                ha = 'left'
                va = 'center'
                last_used_y_position[idx] = y  # Update the last used y position for the next label
            else:
                # No label for zero height
                label = ''

            if label:
                ab.annotate(label, xy=(x, y), ha=ha, va=va, fontsize=8, color='black', fontweight='bold')

    plt.savefig(os.path.join(output_dir, 'barchart.png'), bbox_inches='tight')
    plt.show()

def main():
    input_dir = get_input_directory()
    output_dir = get_output_directory()
    process_summary_statistics(input_dir, output_dir)

if __name__ == "__main__":
    main()