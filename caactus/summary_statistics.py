#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os  # For path operations
import sys  # For exit handling
import pandas as pd  # For data handling
import seaborn.objects as so  # For plotting
import argparse  # For CLI args
import tomli

from caactus.utils import load_config, parse_if_needed

DESCRIPTION = """
This script processes cleaned data to generate summary statistics and a stacked bar plot of predicted classes.

For the stacked bar plot, it groups data by the two variables that you enter.

It computes the average count and percentage of each predicted class, across replicates (technical and biological), for each combination of the two grouping variables.


It visualizes the distribution in stacked bar plots of classes across different conditions.

The first variable you enter will be displayed on the x-axis (e.g. incubation temperature), and the second variable will be used for faceting (e.g. timepoint).

This will create separate subplots for each level of that variable.

The plot will show the percentage distribution of predicted classes for each condition, allowing you to compare how the classes are distributed across different experimental conditions defined by the two grouping variables.

 The colors of the bars will correspond to the predicted classes, as defined in your color mapping.

 By default the IBM coloor-blind friendly palette is used, but you can customize the colors by providing the HEX color code.
 """

def parse_filename(filename, variable_names):
    filename = filename.replace('_table', '')
    parts = filename.split('_')
    metadata = {}
    for part in parts:
        var_name, var_value = part.split('-')
        if var_name in variable_names:
            metadata[var_name] = var_value
    print(f"Parsed metadata: {filename} -> {metadata}")
    return metadata


def process_cleaned_data(
    main_folder,
    input_path,
    output_path,
    variable_names,
    color_mapping,
    class_order,
):
    input_dir = os.path.join(main_folder, input_path)
    output_dir = os.path.join(main_folder, output_path)
    variable_names = parse_if_needed(variable_names)
    color_mapping = parse_if_needed(color_mapping)
    class_order = parse_if_needed(class_order)

    df_clean = pd.read_csv(
        os.path.join(input_dir, 'df_clean.csv'), index_col=0
    )

    counts = df_clean.groupby([
        'filename', 'Predicted Class'
    ]).size().reset_index(name='count')

    for i, row in counts.iterrows():
        file_metadata = parse_filename(row['filename'], variable_names)
        for var in variable_names:
            counts.at[i, var] = file_metadata.get(var, None)

    counts.to_csv(os.path.join(output_dir, 'counts_df.csv'))

    group_cols = variable_names.copy()
    unique_bioreps = df_clean.groupby(group_cols)["biorep"].nunique()
    unique_techreps = df_clean.groupby(group_cols)["techrep"].nunique()

    merged_df = counts.groupby(group_cols + ["Predicted Class"])[
        "count"
    ].sum().reset_index(name="count")

    merged_df = merged_df.merge(
        unique_bioreps, on=group_cols, how="left"
    ).merge(
        unique_techreps, on=group_cols, how="left"
    )

    merged_df["average_count"] = round(
        merged_df["count"] /
        (merged_df["techrep"] * merged_df["biorep"]), 2
    )

    merged_df['%'] = round(
        100 * merged_df["average_count"] /
        merged_df.groupby(group_cols)["average_count"].transform('sum'), 2
    )

    avg_size = df_clean.groupby(group_cols + ["Predicted Class"])[
        "size_microm2"
    ].mean().round(2)

    merged_complete_df = merged_df.merge(
        avg_size, on=group_cols + ["Predicted Class"], how="left"
    )

    merged_complete_df.to_csv(
        os.path.join(output_dir, 'df_summary_complete.csv')
    )

    counts_df2 = counts[
        counts["Predicted Class"] != "not usuable"
    ]
    counts_df2 = counts_df2.groupby(
        group_cols + ["Predicted Class"]
    )["count"].sum().reset_index(name="count")

    counts_df2 = counts_df2.merge(
        unique_techreps, on=group_cols, how="left"
    ).merge(
        unique_bioreps, on=group_cols, how="left"
    )

    counts_df2["average_count"] = round(
        counts_df2["count"] /
        (counts_df2["techrep"] * counts_df2["biorep"]), 2
    )

    counts_df2["%"] = round(
        100 * counts_df2["count"] /
        counts_df2.groupby(group_cols)["count"].transform('sum'), 2
    )

    counts_df2_complete_df = counts_df2.merge(
        avg_size, on=group_cols + ["Predicted Class"], how="left"
    )

    counts_df2_complete_df.to_csv(
        os.path.join(output_dir, 'df_refined_complete.csv')
    )

    counts2_reduced_df = counts_df2.drop([
        "count", "techrep", "biorep"
    ], axis=1)

    counts2_reduced_df['Predicted Class'] = pd.Categorical(
        counts2_reduced_df['Predicted Class'],
        categories=class_order,
        ordered=True
    )

    counts2_pivot_df = counts2_reduced_df.pivot_table(
        index=group_cols,
        columns="Predicted Class",
        values="%",
        aggfunc="sum",
        observed=False
    ).replace(0, float('nan')).reset_index()

    counts2_melted_df = counts2_pivot_df.melt(
        id_vars=group_cols,
        value_vars=class_order,
        var_name='Predicted Class',
        value_name='%'
    ).dropna()

    counts2_melted_df['Predicted Class'] = pd.Categorical(
        counts2_melted_df['Predicted Class'],
        categories=class_order,
        ordered=True
    )

    color_palette = [color_mapping[class_name] for class_name in class_order]

    plot = so.Plot(
        counts2_melted_df,
        x=group_cols[0],
        y="%",
        color="Predicted Class",
        text="%"
    ).facet(
        row=group_cols[1]
    ).layout(
        size=(8, 4)
    ).add(
        so.Bar(), so.Stack()
    ).scale(
        color=color_palette
    ).theme({
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
        "axes.labelsize": 22,
        "axes.titlesize": 22,
        "legend.fontsize": 20,
        "legend.title_fontsize": 22,
    })

    plot.plot()
    plot.save(os.path.join(output_dir, 'barchart.png'), bbox_inches="tight")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        required=True,
        default="config.toml",
        help="Path to config file"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    script_key = "summary_statistics"

    if script_key not in config:
        print(f"Missing configuration section: [{script_key}]")
        sys.exit(1)

    section = config[script_key]
    main_folder = config["main_folder"]
    input_path = section["input_path"]
    output_path = section["output_path"]
    variable_names = section["variable_names"]
    class_order = section["class_order"]
    color_mapping = section["color_mapping"]


    process_cleaned_data(
        main_folder, input_path, output_path, variable_names, color_mapping, class_order
    )


if __name__ == "__main__":
    main()
