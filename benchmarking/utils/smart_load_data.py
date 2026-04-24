import csv
import os

import pandas as pd


def smart_load_data(filepath):
    user_data = {}
    all_ids = set()

    if not filepath or not os.path.exists(filepath):
        print(f"Skipping: File not found {filepath}")
        return user_data, all_ids

    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            return user_data, all_ids

        # Map to normalized column names (case-insensitive)
        headers_map = {h.strip().lower(): h for h in reader.fieldnames}
        clean_headers = list(headers_map.keys())

        # find ID
        found_id_key = next(
            (k for k in ["user_id", "user ID", "member_id"] if k in clean_headers), None
        )
        if not found_id_key:
            print(f"ERROR: ID not found in {filepath}")
            return user_data, all_ids
        id_col = headers_map[found_id_key]

        # format detection
        found_q_key = next((k for k in clean_headers if "questions" in k), None)
        quest_col = headers_map[found_q_key] if found_q_key else None

        # 'score' or 'answer'
        found_score_key = next((k for k in clean_headers if k == "score"), None)
        found_answer_key = next((k for k in clean_headers if k == "answer"), None)

        # category'
        found_cat_key = next((k for k in clean_headers if "category" in k), None)
        cat_col = headers_map[found_cat_key] if found_cat_key else None

        # 'answer_other' (Only JC)
        found_other_key = next((k for k in clean_headers if "answer_other" in k), None)
        other_col = headers_map[found_other_key] if found_other_key else None

        # if there are 'questions' and ('score' O 'answer'), then is HUMMUS format
        is_hummus_format = (quest_col is not None) and (
            (found_score_key is not None) or (found_answer_key is not None)
        )

        # PARSING
        for row in reader:
            raw_uid = row.get(id_col)
            if not raw_uid:
                continue

            uid = str(raw_uid).strip()

            if uid not in user_data:
                user_data[uid] = []

            # hummus
            if is_hummus_format:
                # Recover Category and question
                cat = row.get(cat_col, "").strip() if cat_col else ""
                q = row.get(quest_col, "").strip()

                # recovery answer
                val = ""
                if found_score_key:
                    val = row.get(headers_map[found_score_key], "").strip()
                elif found_answer_key:
                    val = row.get(headers_map[found_answer_key], "").strip()

                # Management 'answer_other'
                if other_col:
                    other_val = (row.get(other_col) or "").strip()
                    if other_val:
                        val += f" ({other_val})"

                # Formattazione stringa
                if q:
                    entry = f"{cat}, {q}: {val}" if cat else f"{q}: {val}"
                    user_data[uid].append(entry)

            # Prolific
            else:
                for key, val in row.items():
                    # skip ID and empty values
                    if key != id_col and val and val.strip():
                        clean_key = key.replace("_", " ").title()
                        user_data[uid].append(f"{clean_key}: {val.strip()}")

    final_data = {}
    for uid, info_list in user_data.items():
        if info_list:
            final_data[uid] = " | ".join(info_list)
            all_ids.add(uid)

    return final_data, all_ids


# read the completeness CSV and transform it into a map
def load_completeness_from_csv(csv_path, csv_path_bio):
    stats = {}
    # Check file existence
    if not os.path.exists(csv_path):
        print(f"Warning: File not found: {csv_path}")
        return {}
    if not os.path.exists(csv_path_bio):
        print(f"Warning: File bio not found: {csv_path_bio}")
        return {}

    try:
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()  # remove leading/trailing spaces
        df_bio = pd.read_csv(csv_path_bio)
        df_bio.columns = df_bio.columns.str.strip()

        # Logic to compute unstructured context completeness based on bio length
        id_col = "user_id"
        bio_col = "context_text"

        if bio_col in df_bio.columns:
            # Calculate number of words
            word_counts = (
                df_bio[bio_col].fillna("").apply(lambda x: len(str(x).split()))
            )
            max_words = word_counts.max()
            if max_words == 0:
                max_words = 1

            # temporary map {User ID: normalized_percentage}
            df_bio["unstructured_val"] = word_counts / max_words
            bio_map = pd.Series(
                df_bio.unstructured_val.values, index=df_bio[id_col].astype(str)
            ).to_dict()
        else:
            print(f"Warning: Column '{bio_col}' not found in {csv_path_bio}")
            bio_map = {}

        for _, row in df.iterrows():
            # User ID as clean string
            uid = str(int(row.get("User ID", 0)))

            # Read percentages and convert to decimals (0.0 - 1.0)
            val_fcq = float(row.get("FCQ %", 0)) / 100.0
            val_jc = float(row.get("JC %", 0)) / 100.0
            val_global = float(row.get("Global %", 0)) / 100.0
            val_unstructured = bio_map.get(uid, 0.0)

            entry = {
                "only_fcq": val_fcq,  # Asse X to only_fcq
                "only_jc": val_jc,  # Asse X to only_jc
                "questionnaires": val_global,  # Asse X to questionnaires
                "both": val_global,  # Asse X to both (usa % globale questionari)
                "unstructured_context": val_unstructured,
                "unknown": 0.0,
            }
            stats[uid] = entry

        print(f"Loaded completeness data for {len(stats)} users.")
        return stats
    except Exception as e:
        print(f"Error reading completeness CSV: {e}")
        return {}
