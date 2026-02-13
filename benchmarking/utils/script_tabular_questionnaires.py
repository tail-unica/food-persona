import argparse
import os

import pandas as pd


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Converts a list of questions (Category, Question) into a table (Columns=Categories)."
    )
    parser.add_argument(
        "--input",
        type=str,
        help="The input CSV file with questions (default: fcq_questions.csv)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="fcq_tabular_view.csv",
        help="The output file name (default: fcq_tabular_view.csv)",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        return

    # Read the CSV file
    df = pd.read_csv(args.input, sep=None, engine="python")

    df.columns = df.columns.str.strip().str.lower()

    # Check required columns
    required_cols = {"category", "questions"}
    if not required_cols.issubset(set(df.columns)):
        print(f"Error: Input file must contain the columns: {required_cols}")
        return

    # check if it's JC or FCQ
    has_options = False
    if "options" in df.columns:
        # Pulisce i NaN e controlla se c'è del testo vero
        if df["options"].fillna("").astype(str).str.strip().any():
            has_options = True
    final_data = {}
    # group by category and convert to list
    grouped = df.groupby("category", sort=False)

    if has_options:
        print("Options detected: Generating DOUBLE COLUMN table (Question | Options).")
        for category, group in grouped:
            cat_name = str(category).strip()
            # Question column
            final_data[cat_name] = group["questions"].tolist()
            # Options column
            final_data[f"{cat_name} (Options)"] = group["options"].fillna("").tolist()
    else:
        print("No options detected: Generating SIMPLE table (Questions only).")
        for category, group in grouped:
            cat_name = str(category).strip()
            final_data[cat_name] = group["questions"].tolist()

    # Create a new DataFrame in tabular format
    # tabular_df = pd.DataFrame.from_dict(dict(grouped), orient='index').transpose()
    tabular_df = pd.DataFrame.from_dict(final_data, orient="index").transpose()

    tabular_df.to_csv(args.output, index=False)
    print(f"Table saved to '{args.output}'")


if __name__ == "__main__":
    main()
