import argparse
import glob
import os
import sys

import pandas as pd

GT_RENAME_MAP = {
    "user_id": "user_id",
    "recipe_id": "recipe_id",
    "score": "rating ground truth",
    "review": "review ground truth",
}

PRED_RENAME_MAP = {
    "member_id": "user_id",
    "recipe_id": "recipe_id",
    "score": "rating predicted",
    "short_review": "review predicted",
    "review": "review predicted",
}

KNOWN_CONTEXTS = [
    "unstructured_context",
    "questionnaires",
    "both",
    "only_fcq",
    "only_jc",
]


def parse_filename(filepath):
    basename = os.path.basename(filepath).replace(".csv", "")
    if basename.startswith("evaluated_recipes_"):
        basename = basename.replace("evaluated_recipes_", "")

    contesto = "unknown"
    modello = basename

    sorted_contexts = sorted(KNOWN_CONTEXTS, key=len, reverse=True)

    for ctx in sorted_contexts:
        if ctx in basename:
            contesto = ctx
            modello = basename.replace(ctx, "")
            modello = modello.replace("__", "_").strip("_")
            break

    return modello, contesto


def main():
    parser = argparse.ArgumentParser(
        description="Merge Predictions and GT with specific columns."
    )
    parser.add_argument(
        "--gt", required=True, help="Ground Truth file"
    )  # user_ratings.csv
    parser.add_argument(
        "--pred", required=True, help="Predictions file"
    )  # (evaluated_*.csv)
    parser.add_argument("--output", default="dataset_finale.csv", help="File di output")

    args = parser.parse_args()

    print(f"Loading Ground Truth: {args.gt}...")
    try:
        #df_gt = pd.read_csv(args.gt, engine='python', on_bad_lines='warn')
        try:
            df_gt = pd.read_csv(args.gt, engine='python', on_bad_lines='warn')
        except TypeError:
            df_gt = pd.read_csv(args.gt, engine='python', error_bad_lines=False, warn_bad_lines=True)
        # Rename GT columns immediately
        df_gt = df_gt.rename(columns=GT_RENAME_MAP)

        # Verify that join keys exist
        if "user_id" not in df_gt.columns or "recipe_id" not in df_gt.columns:
            print("Error: GT file does not contain correct 'user_id' or 'recipe_id'.")
            sys.exit(1)


    except Exception as e:
        print(f"Critical GT error: {e}")
        return

    all_data = []
    final_cols_order = [
        "model",
        "context used",
        "user_id",
        "recipe_id",
        "rating ground truth",
        "rating predicted",
        "review ground truth",
        "review predicted",
    ]

    if not os.path.isdir(args.pred):
        print(f"Error: {args.pred} is not a valid folder.")
        return

    # Search for all files starting with evaluated_recipes_ inside the folder
    search_path = os.path.join(args.pred, "evaluated_recipes_*.csv")
    pred_files = glob.glob(search_path)

    if not pred_files:
        print(f"No files found in {args.pred}")
        sys.exit(1)

    print(f"Found {len(pred_files)} files to process.")

    for pred_file in pred_files:
        try:
            #df_pred = pd.read_csv(pred_file,  engine='python', on_bad_lines='warn')
            try:
                df_pred = pd.read_csv(pred_file, engine='python', on_bad_lines='warn')
            except TypeError:
                df_pred = pd.read_csv(pred_file, engine='python', error_bad_lines=False, warn_bad_lines=True)

            df_pred = df_pred.rename(columns=PRED_RENAME_MAP)

            # Verify keys
            if "user_id" not in df_pred.columns or "recipe_id" not in df_pred.columns:
                print(f"File skipped {pred_file}: missing 'user_id' or 'recipe_id'.")
                continue

            # Extract info from filename
            model, context = parse_filename(pred_file)

            # Join the two DFs where 'user_id' and 'recipe_id' are equal
            merged = pd.merge(df_pred, df_gt, on=["user_id", "recipe_id"], how="inner")

            if merged.empty:
                print(
                    f"No match found for {os.path.basename(pred_file)} (Check the IDs!)"
                )
                continue

            # Add model and context columns
            merged["model"] = model
            merged["context used"] = context

            for col in final_cols_order:
                if col not in merged.columns:
                    merged[col] = None

            final_subset = merged[final_cols_order]
            all_data.append(final_subset)

            print(f" Merged: {model} ({context}) -> {len(final_subset)} reviews.")

        except Exception as e:
            print(f" Error on {pred_file}: {e}")

    if all_data:
        df_totale = pd.concat(all_data, ignore_index=True)
        df_totale = df_totale.sort_values(by=["model", "context used"])
        df_totale.to_csv(args.output, index=False, encoding="utf-8")
        print(f"\nCOMPLETED! File saved to: {args.output}")
        print(f"Total rows merged: {len(df_totale)}")
    else:
        print("\n No data generated.")


if __name__ == "__main__":
    main()
