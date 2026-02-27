#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import os
import sys
import argparse
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (no X11 windows)
import matplotlib.pyplot as plt
import matplotlib as mpl


from caactus.utils import load_config, parse_if_needed


DESCRIPTION = """
This script runs ZIPln modelling on input data with dynamic design and generates PCA visualizations and a correlation circle plot.

The two grouping variables you enter will be used in the model formula and for visualizing the PCA results.

The will be combined into a single factor for the model, and the PCA plot will show the latent variable projections colored by this combined category.

The correlation circle plot will show how the original variables relate to the latent dimensions, helping you interpret the PCA results in terms of the original grouping variables.


"""



def modelling(main_folder, input_path, output_path, variable_names, class_order):
    """Run ZIPln modelling on input data with dynamic design."""
    input_dir = os.path.join(main_folder, input_path)
    output_dir = os.path.join(main_folder, output_path)

    variable_names = parse_if_needed(variable_names)
    class_order = parse_if_needed(class_order)

    from pyPLNmodels import ZIPln  # For statistical modeling
    # Load counts data
    counts = pd.read_csv(
        os.path.join(input_dir, 'counts_df.csv'),
        index_col=0
    )
    counts = counts[counts["Predicted Class"].notna()]
    # Pivot data: shape is [filename + grouping vars] x [Predicted Classes]
    pivot_df = counts.reset_index().pivot_table(
        index=["filename"] + variable_names,
        columns="Predicted Class",
        values="count",
        fill_value=0
    ).reset_index()

    print(pivot_df)

    # Remove unwanted class if present
    if 'not usuable' in pivot_df.columns:
        pivot_df = pivot_df.drop(columns=["not usuable"])

    # Combine category levels into a single factor
    pivot_df['combined_category'] = (
        pivot_df[variable_names[0]].astype(str) +
        ' & ' +
        pivot_df[variable_names[1]].astype(str)
    )

    # Extract data for model
    combined_dict = {
        variable_names[0]: pivot_df[variable_names[0]].to_numpy(),
        variable_names[1]: pivot_df[variable_names[1]].to_numpy(),
        "combined_category": pivot_df["combined_category"].to_numpy(),
        "counts": pivot_df[class_order].to_numpy()
    }

    print("Counts dataframe for dictionary:")
    print(combined_dict["counts"])

    # Fit ZIPln model
    formula = f"counts ~ {variable_names[0]} * {variable_names[1]}"
    zipln = ZIPln.from_formula(formula, data=combined_dict)
    zipln.fit()

    print(zipln)


    # PCA visualization with legend labels (with font sizes + legend outside)
    fig, ax = plt.subplots(figsize=(10, 6))

    for cat in sorted(set(combined_dict["combined_category"])):
        mask = combined_dict["combined_category"] == cat
        ax.scatter(
            zipln.latent_variables[mask, 0],
            zipln.latent_variables[mask, 1],
            label=cat,
        )

    ax.set_xlabel("Latent Dimension 1", fontsize=22)
    ax.set_ylabel("Latent Dimension 2", fontsize=22)
    ax.set_title("ZIPln PCA Projection", fontsize=22)

    ax.tick_params(axis="both", labelsize=20)

    # Legend outside
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])
    leg = ax.legend(
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        title="Combined Category",
    )

    if leg:
        leg.set_title(leg.get_title().get_text(), prop={"size": 20})
        for t in leg.get_texts():
            t.set_fontsize(18)

    fig.savefig(os.path.join(output_dir, "pca_plot.png"), bbox_inches="tight", dpi=300)
    plt.close(fig)


    # Correlation circle
    with mpl.rc_context({
        "font.size": 20,        # helps arrow labels if they’re matplotlib text
        "axes.titlesize": 22,
        "axes.labelsize": 22,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
    }):
        zipln.plot_correlation_circle(
            column_names=[variable_names[0], variable_names[1]],
            column_index=[0, 2],
        )

        plt.savefig(os.path.join(output_dir, "correlation_circle.png"), bbox_inches="tight", dpi=300)
        plt.close(plt.gcf())

    print("PLN Modelling completed.", flush=True)



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
    script_key = "pln_modelling"

    if script_key not in config:
        print(f"Missing configuration section: [{script_key}]")
        sys.exit(1)

    section = config[script_key]
    main_folder = config["main_folder"]
    variable_names = section["variable_names"]
    class_order = section["class_order"]

    modelling(
        main_folder,
        section["input_path"],
        section["output_path"],
        variable_names,
        class_order,
    )


if __name__ == "__main__":
    main()
