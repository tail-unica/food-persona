import math
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns


def plot_mae_vs_alignment(results, folder):
    if not results:
        return

    os.makedirs(folder, exist_ok=True)

    model_groups = {}
    for item in results:
        m_name = item["model"]
        if m_name not in model_groups:
            model_groups[m_name] = []
        model_groups[m_name].append(item)

    print(f"MAE vs Alignment Plot Generation divided by model into:{folder}")

    for model_name, group_items in model_groups.items():
        n_plots = len(group_items)
        if n_plots == 0:
            continue

        # Configurazione Griglia
        # cols = 2
        # rows = math.ceil(n_plots / cols)

        # fig, axes = plt.subplots(
        #     rows, cols, figsize=(15, 5 * rows), constrained_layout=True, sharey=True
        # )

        # # Gestione assi
        # axes = axes.flatten() if n_plots > 1 else [axes]

        # Configurazione Griglia
        cols = 2
        rows = math.ceil(n_plots / cols)

        fig, axes = plt.subplots(
            rows, cols, figsize=(15, 5 * rows), constrained_layout=True, sharey=True
        )

        # Gestione assi - converti sempre in array 1D
        import numpy as np
        if not isinstance(axes, np.ndarray):
            axes = np.array([axes])
        else:
            axes = axes.flatten()

        # Titolo Generale del File
        fig.suptitle(f"Semantic Alignment Analysis: {model_name}", fontsize=16)

        for i, item in enumerate(group_items):
            df = item["df"].copy()
            source_name = item["source"]

            # Title of the individual subplot
            sub_title = f"{source_name}"

            # Get the current axis
            if i >= len(axes):
                break
            ax = axes[i]

            # Data cleaning: we need both values
            if "mae" not in df.columns or "avg_sim" not in df.columns:
                continue

            df = df.dropna(subset=["mae", "avg_sim"])

            if df.empty:
                ax.text(0.5, 0.5, "insufficient data", ha="center")
                ax.set_title(sub_title)
                continue

            sns.regplot(
                data=df,
                x="avg_sim",
                y="mae",
                ax=ax,
                scatter_kws={"alpha": 0.4, "s": 20, "color": "tab:blue"},
                line_kws={"color": "tab:red", "linewidth": 2},
            )

            ax.set_title(sub_title, fontweight="bold", fontsize=12)
            ax.set_xlabel("Semantic Similarity (Cosine)")

            if i % cols == 0:
                ax.set_ylabel("MAE")
            else:
                ax.set_ylabel("")

            ax.set_xlim(0, 1)  # The cosine always goes from 0 to 1

            ax.grid(True, alpha=0.3)

        # Hide empty boxes
        for j in range(n_plots, len(axes)):
            axes[j].axis("off")

        # Dynamic filename based on model
        safe_name = model_name.replace(" ", "_").replace("/", "-")
        filename = f"Dashboard_Mae_vs_Alignment_{safe_name}.png"
        save_path = os.path.join(folder, filename)

        fig.savefig(save_path, dpi=300)
        plt.close(fig)

        print(f"Saved: {filename}")

    print("All alignment plots have been generated.")


def plot_mae_vs_completeness_strip_line(results, folder, draw_line=False, jitter=True):
    if not results:
        return

    os.makedirs(folder, exist_ok=True)

    # group by model
    model_groups = {}
    for item in results:
        m_name = item["model"]
        if m_name not in model_groups:
            model_groups[m_name] = []
        model_groups[m_name].append(item)

    print(f"Generation of plots divided by model in: {folder}")

    for model_name, group_items in model_groups.items():
        n_plots = len(group_items)
        if n_plots == 0:
            continue

        # Dynamic row and column calculation for THIS model
        cols = 2
        rows = math.ceil(n_plots / cols)

        # create the figure dedicated only to this model
        fig, axes = plt.subplots(
            rows, cols, figsize=(15, 5 * rows), constrained_layout=True, sharey=True
        )

        # Flatten axes for easy iteration
        axes = axes.flatten() if n_plots > 1 else [axes]

        # Overall title for the figure
        fig.suptitle(f"Completeness Analysis: {model_name}", fontsize=16)

        # Add general title to the file
        fig.suptitle(f"Completeness Analysis: {model_name}", fontsize=16)

        for i, item in enumerate(group_items):
            df = item["df"].copy()
            # specific name subplot (es. "questionnaires")
            source_name = item["source"]
            full_title = f"{model_name} ({source_name})"

            if "completeness" not in df.columns or "mae" not in df.columns:
                continue

            df = df.dropna(subset=["mae", "completeness"])

            #
            if i < len(axes):
                ax = axes[i]
            else:
                continue

            # Manage insufficient data
            if df.empty or len(df) < 5:
                ax.text(0.5, 0.5, "insufficient data", ha="center")
                ax.set_title(full_title, fontsize=10, fontweight="bold")
                continue

            df["completeness_pct"] = df["completeness"] * 100

            # paint
            if jitter:
                sns.stripplot(
                    data=df,
                    x="completeness_pct",
                    y="mae",
                    ax=ax,
                    jitter=3,
                    alpha=0.35,
                    size=4,
                    color="tab:blue",
                )
            else:
                sns.scatterplot(
                    data=df,
                    x="completeness_pct",
                    y="mae",
                    ax=ax,
                    alpha=0.35,
                    s=20,
                    color="tab:blue",
                )

            if draw_line:
                sns.lineplot(
                    data=df,
                    x="completeness_pct",
                    y="mae",
                    ax=ax,
                    estimator="mean",
                    errorbar=None,
                    marker="o",
                    linewidth=2,
                    color="red",
                )

            # format axes
            ax.set_title(full_title, fontsize=10, fontweight="bold")
            ax.set_xlabel("Profile Completeness (%)")
            ax.set_ylabel("MAE")
            ax.grid(True, alpha=0.3)

            # tick limit
            ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=12))
            # format as integers
            ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f"))
            # Rotate the labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Hide empty axes if there are free slots in the grid
        for j in range(n_plots, len(axes)):
            axes[j].axis("off")

        # Dynamic filename based on model
        safe_name = model_name.replace(" ", "_").replace("/", "-")
        filename = f"Dashboard_Completeness_{safe_name}.png"
        save_path = os.path.join(folder, filename)

        fig.savefig(save_path, dpi=300)
        plt.close(fig)  # Close the figure to free memory

        print(f"Saved: {filename}")

    print("All saving operations completed.")
