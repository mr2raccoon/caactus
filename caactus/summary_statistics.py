#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os  # For path operations
import sys  # For exit handling
import pandas as pd  # For data handling
import seaborn.objects as so  # For plotting
import argparse  # For CLI args
from caactus.utils import load_config, parse_if_needed

DESCRIPTION = """
## Summary Statistics

Generates summary statistics and a **stacked bar plot** from the cleaned cell classification data.

### How it works
- Groups data by the two **Variable Names** (set in Global Settings)
- Computes average count and percentage of each predicted class across technical and biological replicates
- The **first variable** appears on the x-axis; the **second variable** is used for faceting (subplots)

### Configuration (set in Global Settings)
- **Variable Names** — two grouping variables, e.g. `['strain', 'timepoint']`
- **Class Order** — morphotype names in display order
- **Color Mapping** — HEX color per class (default: IBM color-blind-friendly palette)

### Output (saved to `9_data_analysis`)
- `df_summary_complete.csv` — full summary including "not usable" category
- `df_refined_complete.csv` — summary without "not usable" category
- `counts.csv` — count table for PLN Modelling
- `barchart.png` — stacked bar plot
"""


def process_cleaned_data(
    main_folder,
    input_path,
    output_path,
    variable_names,
    color_mapping,
    class_order,
):
    color_mapping = parse_if_needed(color_mapping)

    if not isinstance(color_mapping, dict):
        raise TypeError(
            f"color_mapping must be dict after parsing, got {type(color_mapping)}"
        )
    input_dir = os.path.join(main_folder, input_path)
    output_dir = os.path.join(main_folder, output_path)

    if not os.path.isdir(input_dir):
        print(
            f"Error: Input directory does not exist: {input_dir}\n"
            "Please enter a full (absolute) path to the '9_data_analysis' folder.",
            flush=True,
        )
        return
    if not os.path.isdir(output_dir):
        print(
            f"Error: Output directory does not exist: {output_dir}\n"
            "Please enter a full (absolute) path to the '9_data_analysis' folder.",
            flush=True,
        )
        return

    variable_names = parse_if_needed(variable_names)
    class_order = parse_if_needed(class_order)
    # (color_mapping already parsed above, no need to parse twice)

    df_clean = pd.read_csv(
        os.path.join(input_dir, "df_clean.csv"), index_col=0
    )

    missing_cols = [v for v in variable_names if v not in df_clean.columns]
    if missing_cols:
        print(
            f"Error: The following variable_names columns are missing from df_clean.csv: {missing_cols}\n"
            f"Available columns: {list(df_clean.columns)}\n"
            "Make sure your filenames contain 'variable-value' parts matching the configured variable_names "
            "(e.g. 'strain-WT_timepoint-4h_biorep-1_techrep-1_table.csv').",
            flush=True,
        )
        return

    counts = df_clean.groupby([
        'filename', 'Predicted Class'
    ]).size().reset_index(name='count')

    filename_meta = df_clean.drop_duplicates('filename')[['filename'] + variable_names]
    counts = counts.merge(filename_meta, on='filename', how='left')

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
    
    print("Summary Statistics completed.", flush=True)



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
