import argparse
import os

import pandas as pd


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script for filtered ratings CSV on Top 100 users"
    )

    parser.add_argument(
        "--ranking_file",
        type=str,
        required=True,
        help="Path of CSV file with user ranking",
    )
    parser.add_argument(
        "--ratings_file",
        type=str,
        required=True,
        help="Path of CSV file with ALL original ratings",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="Path where to save the new filtered CSV",
    )
    parser.add_argument(
        "--limit", type=int, default=100, help="How many users to extract"
    )

    return parser.parse_args()


def find_id_column(df):
    candidates = ["user_id", "User ID"]
    for col in candidates:
        if col in df.columns:
            return col
    return None


def main():
    args = parse_arguments()

    if not os.path.exists(args.ranking_file):
        print(f"Error: Ranking file not found: {args.ranking_file}")
        return

    print(f"1. Reading ranking from: {args.ranking_file}")
    df_rank = pd.read_csv(args.ranking_file)

    rank_id_col = find_id_column(df_rank)
    if not rank_id_col:
        print("Error: Unable to find ID column (user_id/member_id) in ranking.")
        return

    top_users = df_rank[rank_id_col].unique()[: args.limit]
    print(f"   > Users extracted: {len(top_users)}")

    if not os.path.exists(args.ratings_file):
        print(f"Error: Ratings file not found: {args.ratings_file}")
        return

    df_ratings = pd.read_csv(args.ratings_file)

    ratings_col = find_id_column(df_ratings)
    if not ratings_col:
        print("Error: Unable to find ID column (user_id/member_id) in ratings file.")
        return

    df_filtered = df_ratings[df_ratings[ratings_col].isin(top_users)]

    # rows_count = len(df_filtered)
    users_found_count = df_filtered[ratings_col].nunique()

    if users_found_count < len(top_users):
        print(
            "   WARNING: Some users from the Top list have no reviews in the provided ratings file."
        )

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    df_filtered.to_csv(args.output_file, index=False)
    print(f"File saved successfully to:\n   {args.output_file}")


if __name__ == "__main__":
    main()
