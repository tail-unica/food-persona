import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import torch
from sklearn.metrics import confusion_matrix as sklearn_confusion_matrix

matplotlib.use("Agg")  # Non-interactive mode, for scripts


# Calculate MSE, MAE and RMSE between FCQ questionnaire scores
def calculate_metrics(comparison_df: pd.DataFrame):
    if comparison_df.empty:
        return float("nan"), float("nan"), float("nan"), 0

    try:
        # convert to PyTorch tensors
        y_true = torch.tensor(comparison_df["true"].values, dtype=torch.float32)
        y_pred = torch.tensor(comparison_df["pred"].values, dtype=torch.float32)

        # calculate MAE, MSE and RMSE
        mae = torch.nn.functional.l1_loss(y_pred, y_true).item()
        mse = torch.nn.functional.mse_loss(y_pred, y_true).item()
        mse_tensor = torch.nn.functional.mse_loss(y_pred, y_true)
        mse = mse_tensor.item()
        rmse = torch.sqrt(mse_tensor).item()
        total = len(y_true)  # total number of compared answers

        return mae, mse, rmse, total

    except Exception as e:
        print(f"Error during metrics calculation: {e}")
        return float("nan"), float("nan"), float("nan"), 0


def confusion_matrix(comparison_df: pd.DataFrame, labels=[1, 2, 3, 4, 5]):
    y_true = comparison_df["true"].astype(int)
    y_pred = comparison_df["pred"].astype(int)

    cm = sklearn_confusion_matrix(y_true, y_pred, labels=labels)

    return cm


# def save_confusion_matrix_plot(cm_data, labels, plot_path, title):

#     plt.figure(figsize=(10, 7))

#     # Crea la heatmap usando Seaborn
#     ax = sns.heatmap(cm_data,
#                         annot=True,     # Mostra i numeri in ogni cella
#                         fmt='d',        # Formatta i numeri come interi
#                         cmap='Blues',   # Schema di colori
#                         xticklabels=labels,
#                         yticklabels=labels)

#     ax.set(xlabel='Predicted Label', ylabel='True Label', title=title)

#     # Salva il file
#     plt.savefig(plot_path, bbox_inches='tight')
#     plt.close() # Chiude la figura per liberare memoria

# Salva più matrici di confusione nella stessa figura con scala colori condivisa
# def save_confusion_matrix_plot(cm_dict, labels, plot_path):

#     n_matrices = len(cm_dict)

#     # Calcola il valore massimo globale tra tutte le matrici per uniformare la scala colori
#     max_val = max(cm.max() for cm in cm_dict.values())

#     # Crea i subplots con sharey=True (asse Y condiviso)
#     fig, axes = plt.subplots(1, n_matrices, figsize=(6 * n_matrices, 6), sharey=True)

#     # Se c'è una sola matrice, 'axes' non è una lista, lo rendiamo tale per coerenza
#     if n_matrices == 1:
#         axes = [axes]

#     # Spazio per la colorbar a destra (cbar_ax)
#     # [left, bottom, width, height] in percentuali della figura
#     cbar_ax = fig.add_axes([.91, .15, .02, .7])

#     for ax, (title, cm_data) in zip(axes, cm_dict.items()):
#         sns.heatmap(cm_data,
#                     annot=True,
#                     fmt='d',
#                     cmap='Blues',
#                     xticklabels=labels,
#                     yticklabels=labels,
#                     vmin=0,         # Minimo scala colori fisso a 0
#                     vmax=max_val,   # Massimo scala colori fisso al max globale
#                     cbar=True,      # Attiva la colorbar...
#                     cbar_ax=cbar_ax,# ...ma disegnala nell'asse dedicato (condiviso)
#                     ax=ax)          # Disegna la matrice nell'asse corrente del subplot

#         ax.set_title(title)
#         ax.set_xlabel('Predicted Label')

#         # Mostra la label Y solo sul primo grafico per pulizia (grazie a sharey)
#         if ax == axes[0]:
#             ax.set_ylabel('True Label')
#         else:
#             ax.set_ylabel('')

#     # Regola gli spazi
#     plt.subplots_adjust(right=0.9, wspace=0.1)

#     # Salva
#     plt.savefig(plot_path, bbox_inches='tight')
#     plt.close()


def save_confusion_matrix_plot(cm_dict, labels, model_name, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filename = f"CM_{model_name}.png"
    plot_path = os.path.join(output_folder, filename)

    n_matrices = len(cm_dict)

    # If dictionary is empty, exit
    if n_matrices == 0:
        print(f"No matrix to print for {model_name}")
        return

    # Calculate global maximum to standardize color scale (vmax)
    max_val = max(cm.max() for cm in cm_dict.values())

    # 4. Create figure with N side-by-side subplots
    fig, axes = plt.subplots(1, n_matrices, figsize=(5 * n_matrices, 6), sharey=True)

    # Handle special case: if there's only one matrix, 'axes' is not a list
    if n_matrices == 1:
        axes = [axes]

    # 5. Create dedicated axis for shared Colorbar on the right
    #    [left, bottom, width, height] relative to figure
    cbar_ax = fig.add_axes([0.91, 0.2, 0.02, 0.6])

    for i, (ax, (source_name, cm_data)) in enumerate(zip(axes, cm_dict.items())):
        sns.heatmap(
            cm_data,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            vmin=0,
            vmax=max_val,
            cbar=True,  # Attiva la colorbar.
            cbar_ax=cbar_ax,  # disegna nell'asse laterale condiviso
            ax=ax,
            annot_kws={"size": 14},
        )  # Grandezza numeri

        # Titolo del singolo grafico
        ax.set_title(source_name, fontsize=14, pad=10)
        ax.set_xlabel("Predicted Label")

        # Gestione etichette asse Y (True Label)
        if i == 0:
            ax.set_ylabel("True Label")
        else:
            ax.set_ylabel("")
            ax.tick_params(left=False)  # Nasconde i trattini sull'asse Y

    # header generale per l'intera figura
    plt.suptitle(f"Analisi Modello: {model_name}", fontsize=20, y=1.02)

    plt.subplots_adjust(wspace=0.1, right=0.9)

    print(f"Saving aggregated chart to: {plot_path}")
    plt.savefig(plot_path, bbox_inches="tight", dpi=300)
    plt.close()
