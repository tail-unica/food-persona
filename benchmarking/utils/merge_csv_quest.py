import argparse
import os

import pandas as pd


# merges the questions from the two prolific files
def merge_csv_files(file1_path, file2_path, output_path):
    # Verify file existence
    if not os.path.exists(file1_path):
        print(f"ERROR: File {file1_path} does not exist.")
        return
    if not os.path.exists(file2_path):
        print(f"ERROR: File {file2_path} does not exist.")
        return

    print("Loading files...")

    # Load CSV
    df1 = pd.read_csv(file1_path, dtype={"user_id": str})
    df2 = pd.read_csv(file2_path, dtype={"user_id": str})

    # Remove whitespace from column names for safety
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    # Remove whitespace from IDs
    df1["user_id"] = df1["user_id"].str.strip()
    df2["user_id"] = df2["user_id"].str.strip()

    print(f"File 1: {len(df1)} rows found.")
    print(f"File 2: {len(df2)} rows found.")

    # merge
    merged_df = pd.merge(df1, df2, on="user_id", how="outer")

    merged_df = merged_df.fillna("")

    # Reorder columns putting user_id first (optional but useful)
    cols = ["user_id"] + [c for c in merged_df.columns if c != "user_id"]
    merged_df = merged_df[cols]

    print(f"Merged file: {len(merged_df)} total rows.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    merged_df.to_csv(output_path, index=False)
    print(f"Save completed to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merges two questionnaire CSVs based on user_id"
    )
    parser.add_argument(
        "--file1",
        required=True,
        help="Path of the first CSV file (e.g., demographic data)",
    )
    parser.add_argument(
        "--file2",
        required=True,
        help="Path of the second CSV file (e.g., food frequencies)",
    )
    parser.add_argument(
        "--out", required=True, help="Path where to save the merged file"
    )

    args = parser.parse_args()

    merge_csv_files(args.file1, args.file2, args.out)
