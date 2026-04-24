import pandas as pd

from utils.text_utils import normalize_text


# Funzione per leggere CSV come dizionario
def read_data_as_map(filepath: str, q_type: str) -> dict:
    try:
        df = pd.read_csv(filepath, dtype=str, keep_default_na=False)

        # data cleaning
        if "user_id" in df.columns:
            df["user_id"] = df["user_id"].str.strip()  # Removes invisible spaces
        else:
            df["user_id"] = "all"

        if q_type == "FCQ":
            df["category"] = df["category"].str.strip()
            df["question"] = df["questions"].str.strip().apply(normalize_text)
            df["score"] = df["score"].str.strip()
            # df["user_id"] = df.get("user_id", "all")  # se non c'è user_id
            return df[["user_id", "category", "questions", "score"]].to_dict(
                orient="records"
            )

        elif q_type == "JC":
            df["question"] = df["questions"].str.strip().apply(normalize_text)
            df["answer"] = df["answer"].str.strip()
            df["answer_other"] = df["answer_other"].str.strip()
            # df["user_id"] = df.get("user_id", "all")
            return df[["user_id", "questions", "answer", "answer_other"]].to_dict(
                orient="records"
            )

        else:
            print(f"Tipo questionario sconosciuto: {q_type}")
            return None

    except Exception as e:
        print(f"ERROR reading {filepath}: {e}")
        return None

