import pandas as pd
import torch


def calculate_metrics_by_category(df: pd.DataFrame, gt_known_total: int):
    if df.empty:
        return {}

    results = {}
    categories = df["category"].unique()

    for cat in categories:
        cat_df = df[df["category"] == cat]
        if cat_df.empty:
            continue

        y_true = torch.tensor(cat_df["true"].values, dtype=torch.float32)
        y_pred = torch.tensor(cat_df["pred"].values, dtype=torch.float32)

        mae = torch.nn.functional.l1_loss(y_pred, y_true).item()
        mse_tensor = torch.nn.functional.mse_loss(y_pred, y_true)
        mse = mse_tensor.item()
        rmse = torch.sqrt(mse_tensor).item()
        total = len(y_true)

        llm_known_percent_categ = (
            (total / gt_known_total * 100) if gt_known_total else 0
        )

        results[cat] = {
            "Count": total,
            "MAE": mae,
            "MSE": mse,
            "RMSE": rmse,
            "LLM known representation Categ": llm_known_percent_categ,
        }

    return results
