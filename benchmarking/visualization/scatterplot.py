import os

import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# scatterplot based on category for FCQ
def plot_scatter_categories(csv_file, save_path):
    df = pd.read_csv(csv_file)
    df = df[df["Category"] != "Overall"]
    # filter only FCQ rows
    df = df[df["Questionnaire"] == "FCQ"]
    # remove rows with missing category
    df = df[df["Category"].notna()]
    df["Category"] = df["Category"].astype(str)

    if df.empty:
        print("No FCQ rows with category present in CSV.")
        return

    # cleanup model names
    df["Model"] = df["Model"].str.replace("_FCQ", "")

    # Models → Colors
    models = sorted(df["Model"].unique())
    palette = sns.color_palette("tab10", len(models))
    model_color_map = dict(zip(models, palette))

    # Categories → Markers
    categories = sorted(df["Category"].unique())
    markers = ["o", "s", "D", "^", "P", "X", "*", "v", "<"]
    category_marker_map = dict(zip(categories, markers))

    plt.figure(figsize=(12, 7))
    plt.subplots_adjust(right=0.70)

    #  scatterplot
    for model in models:
        df_m = df[df["Model"] == model]
        for cat in categories:
            df_mc = df_m[df_m["Category"] == cat]
            if df_mc.empty:
                continue
            plt.scatter(
                df_mc["LLM known representation Categ"],
                df_mc["Category MAE"],
                color=model_color_map.get(model, "black"),  # modello
                marker=category_marker_map.get(cat, "o"),  # categoria
                s=120,
                # label=f"{model} - {cat}"
            )

    # Legend
    color_handles = [
        mpatches.Patch(color=model_color_map[model], label=model) for model in models
    ]

    # legend categ
    marker_handles = [
        mlines.Line2D(
            [],
            [],
            color="black",
            marker=category_marker_map[cat],
            linestyle="None",
            markersize=8,
            label=cat,
        )
        for cat in categories
    ]

    # add color legend
    leg1 = plt.legend(
        handles=color_handles,
        title="Modello",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )
    plt.gca().add_artist(leg1)
    plt.legend(
        handles=marker_handles,
        title="Category",
        bbox_to_anchor=(1.05, 0.5),
        loc="upper left",
    )

    plt.xlabel("LLM Known Representation Categ (%)")
    plt.ylabel("MAE")
    plt.title("Scatterplot MAE by Category and Model (FCQ)")
    plt.grid(True, linestyle="--", alpha=0.4)
    # plt.tight_layout()

    # Save PNG if requested
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Scatterplot saved to '{save_path}'")


def scatterplot_general(csv_file, save_path):
    df = pd.read_csv(csv_file)

    df = df[df["Questionnaire"] == "FCQ"]

    plt.figure(figsize=(10, 7))

    sns.scatterplot(
        data=df,
        x="LLM known representation",
        y="MAE",
        hue="Questionnaire",
        style="Model",
        s=120,
    )

    plt.xlabel("LLM Known Representation (%)")
    plt.ylabel("MAE")
    plt.title("Scatterplot MAE by Questionnaire and Model")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    # Save PNG if requested
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Scatterplot saved to '{save_path}'")

    plt.close()
