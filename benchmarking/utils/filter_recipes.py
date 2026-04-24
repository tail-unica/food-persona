import os
import zipfile

import pandas as pd


def estrai_utenti_con_bio(percorso_zip):
    with zipfile.ZipFile(percorso_zip, "r") as z:
        user_file = [f for f in z.namelist() if f.endswith(".user")][0]
        # print("File .user trovato:", user_file)

        with z.open(user_file) as f:
            df_user = pd.read_csv(f, sep="\t", header=0, on_bad_lines="skip")

    df_user.columns = [c.split(":")[0].strip() for c in df_user.columns]

    # Filtra bio non vuote e con almeno tot caratteri
    df_user["member_description"] = df_user["member_description"].astype(str)

    df_user_filtrati = df_user[df_user["member_description"].str.strip() != ""]
    df_user_filtrati = df_user_filtrati[
        df_user_filtrati["member_description"].str.len() >= 100
    ]

    # print("Utenti con biografia non vuota:", len(df_user_non_vuoti))

    return df_user_filtrati["member_id"].tolist()


def extract_user_recipes(percorso_csv, save_csv=True):
    try:
        df = pd.read_csv(percorso_csv)
        # print(f"File letto come CSV (separatore virgola): {percorso_csv}")
    except Exception:
        try:
            # If it fails, try as TSV (tab separator)
            df = pd.read_csv(percorso_csv, sep="\t")
            print(f"File read as TSV (tab separator): {percorso_csv}")
        except Exception as e:
            print(f"Error: Unable to read file {percorso_csv}.")
            print(f"Detail: {e}")
            return None

    # Clean column names
    df.columns = [c.split(":")[0].strip() for c in df.columns]
    # print("Clean columns:", df.columns.tolist())

    # List of users to consider
    user_ids = estrai_utenti_con_bio("data.zip")

    filtered = df[df["member_id"].isin(user_ids)][
        ["member_id", "recipe_id", "rating", "text"]
    ]

    # discard recipes where review is not present
    filtered = filtered[filtered["text"].notna() & (filtered["text"].str.strip() != "")]

    # Sort by user and then by recipe
    filtered = filtered.sort_values(["member_id", "recipe_id"]).reset_index(drop=True)

    # Count how many valid reviews each user has
    reviews_per_user = filtered["member_id"].value_counts()

    # filter users with at least 10 recipes and reviews
    users_over_10 = reviews_per_user[reviews_per_user >= 10].index.tolist()

    # Apply the cut
    filtered = filtered[filtered["member_id"].isin(users_over_10)]

    print(f"Reviews remaining (users with >10 reviews): {len(filtered)}")
    print(f"Unique users remaining: {filtered['member_id'].nunique()}")

    # Show results
    # print("\nRatings found")
    if filtered.empty:
        print("No ratings found for the specified users.")
    # else:
    #     for uid in user_ids:
    #         user_data = filtered[filtered["member_id"] == uid]
    #         # if not user_data.empty:
    #         # print(f"\nUtente {uid}:")
    #         # for _, row in user_data.iterrows():
    #         # print(f"  Ricetta {row['recipe_id']}, rating {row['rating']}, testo: {row['text'][:30]}...")
    #         # else:
    #         # print(f"\nUtente {uid}: nessuna valutazione trovata.")

    if save_csv:
        os.makedirs("output", exist_ok=True)
        csv_path = os.path.join("output", "user_ratings_filtered.csv")
        filtered.to_csv(csv_path, index=False)
        print(f"\nResults saved to: {csv_path}")

    return filtered


if __name__ == "__main__":
    # zip_path = "data.zip"
    # df_result = extract_user_recipes(zip_path, save_csv=True)

    csv_file_path = "pp_reviews.csv"
    df_result = extract_user_recipes(csv_file_path, save_csv=True)
