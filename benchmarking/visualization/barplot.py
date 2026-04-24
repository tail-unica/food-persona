import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def barplot_categories(csv_file, save_path):
    if not os.path.exists(csv_file):
        print(f"Error: File not found {csv_file}")
        return

    df = pd.read_csv(csv_file)

    # column cleanup
    df.columns = df.columns.str.strip()

    # filtering for relevant data
    df = df[df["Category"] != "Overall"]
    df = df[df["Questionnaire"] == "FCQ"]

    # Data cleaning
    df["Category"] = df["Category"].astype(str).str.strip()
    df["Model"] = df["Model"].astype(str).str.strip()

    # Manage comma as decimal separator
    df["Category MAE"] = df["Category MAE"].astype(str).str.replace(",", ".")
    df["Category MAE"] = pd.to_numeric(df["Category MAE"], errors="coerce")

    # remove NaN categories
    df = df[df["Category"].str.lower() != "nan"]

    if df.empty:
        print("No valid data found.")
        return

    all_categories = df["Category"].unique()
    all_models = df["Model"].unique()

    full_index = pd.MultiIndex.from_product(
        [all_categories, all_models], names=["Category", "Model"]
    )

    # Reindex to ensure all combinations are present
    df = df.set_index(["Category", "Model"]).reindex(full_index).reset_index()

    # plotting
    plt.figure(figsize=(14, 8))  # Leggermente più grande per far stare tutto
    sns.set_theme(style="whitegrid")

    # Barplot
    ax = sns.barplot(
        data=df,
        x="Category",
        y="Category MAE",
        hue="Model",
        palette="viridis",
        edgecolor="black",
        linewidth=1,  # More visible border
        alpha=0.9,
    )

    # label bars
    for container in ax.containers:
        labels = []
        for val in container.datavalues:
            if np.isnan(val):
                labels.append("N/A")  # Missing data in CSV
            elif val == 0:
                labels.append("0.00")  # Data present and is 0
            else:
                labels.append(f"{val:.2f}")  # Normal data

        ax.bar_label(container, labels=labels, padding=3, fontsize=9, rotation=90)

    # axes labels and title
    plt.xlabel("Categoria", fontsize=12, fontweight="bold")
    plt.ylabel("Category MAE", fontsize=12, fontweight="bold")
    plt.title("Confronto MAE per Categoria e Modello (FCQ)", fontsize=15, pad=20)

    plt.xticks(rotation=45, ha="right")

    # legend outside the plot
    plt.legend(
        title="Modello", bbox_to_anchor=(1.01, 1), loc="upper left", borderaxespad=0
    )

    # y-axis limit
    max_val = df["Category MAE"].max()
    if pd.notna(max_val):
        plt.ylim(0, max_val * 1.15)

    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Barplot saved in '{save_path}'")
