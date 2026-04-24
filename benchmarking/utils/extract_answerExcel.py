import itertools
import os

import pandas as pd


def load_question_mapping(
    file_mappatura: str, colonna_domanda: str, colonna_categoria: str
) -> dict[str, str]:
    """
    Loads the mapping file and creates a dictionary {Question Text: Category}.
    """
    try:
        if file_mappatura.endswith(".csv"):
            df_map = pd.read_csv(file_mappatura)
        else:
            # Assumiamo il primo foglio se è Excel
            df_map = pd.read_excel(file_mappatura)
    except Exception as e:
        # Raise the error to handle it in the calling block
        raise FileNotFoundError(f"Error loading mapping file {file_mappatura}: {e}")

    # Crea il dizionario {Testo Domanda: Categoria}
    df_map = df_map.rename(
        columns={colonna_domanda: "question", colonna_categoria: "category"}
    )
    mappatura = dict(
        zip(
            df_map["question"].astype(str).str.strip(),
            df_map["category"].astype(str).str.strip(),
        )
    )

    return mappatura


# cleans the excel file
def clean_header(testo: str) -> str:
    if not isinstance(testo, str):
        return str(testo)

    # Cut at the first newline
    testo = testo.split("\n")[0]
    # Cut at the first open parenthesis
    testo = testo.split("(")[0]
    # Remove trailing/leading spaces
    return testo.strip()


def process_questionnaire(
    file_dati: str,
    nome_foglio: str,
    colonne_domande: list[str],
    output_filename: str,
    output_dir: str,
    mappatura: dict[str, str],
    is_jc: bool,
):
    print(f"\nStarting processing: {output_filename} from {file_dati}")

    try:
        if file_dati.endswith(".csv"):
            df_full = pd.read_csv(file_dati)
        else:
            df_full = pd.read_excel(file_dati, sheet_name=nome_foglio)
    except Exception as e:
        print(
            f"ERROR: Unable to load sheet '{nome_foglio}' from file '{file_dati}'. Details: {e}"
        )
        return

    col_id_reale = None
    # Search for a column that resembles "userid" ignoring case and symbols
    for col in df_full.columns:
        if str(col).lower().strip().replace("_", "").replace(" ", "") == "userid":
            col_id_reale = col
            break

    if not col_id_reale:
        print(
            f"CRITICAL ERROR: Column 'user_id' not found. Columns present: {list(df_full.columns)}"
        )
        return

    # Standard rename
    df_full = df_full.rename(columns={col_id_reale: "user_id"})
    utenti_trovati = df_full["user_id"].unique()

    mapping_rinomina = {}

    def clean_excel_header(testo):
        t = str(testo)
        t = t.split("\n")[
            0
        ]  # Removes everything after a newline (e.g., "\n(Options...)")
        t = t.split("(")[
            0
        ]  # Removes everything after an open parenthesis (e.g., "(score 1-4)")
        return t.strip()

    print("   Analyzing and matching columns...")

    for col_excel in df_full.columns:
        if col_excel == "user_id":
            continue

        # Cleaned version of the Excel header
        header_clean = clean_excel_header(col_excel)

        # Caso A: Match Esatto dopo pulizia
        if header_clean in colonne_domande:
            mapping_rinomina[col_excel] = header_clean
        else:
            # Caso B: Match "Fuzzy" (spazi doppi, minuscole/maiuscole)
            for target in colonne_domande:
                # Confronta rimuovendo tutti gli spazi e mettendo in minuscolo
                if (
                    header_clean.replace(" ", "").lower()
                    == target.replace(" ", "").lower()
                ):
                    mapping_rinomina[col_excel] = target
                    break

    # Rename columns in DataFrame using ONLY the names from your original list
    if mapping_rinomina:
        df_full = df_full.rename(columns=mapping_rinomina)
        print(f"Matched {len(mapping_rinomina)} questions.")

    # DATA EXTRACTION
    # Take only the columns we managed to match
    cols_to_select = [col for col in colonne_domande if col in df_full.columns]

    # Warning if something is still missing
    mancanti = set(colonne_domande) - set(cols_to_select)
    if mancanti:
        print(
            f"WARNING: {len(mancanti)} questions from the list not found in Excel (e.g., {list(mancanti)[:2]})."
        )

    df_flat = df_full[["user_id"] + cols_to_select]

    # Unpivoting
    value_name = "answer" if is_jc else "score"

    df_melted = df_flat.melt(
        id_vars="user_id",
        value_vars=cols_to_select,
        var_name="question",
        value_name=value_name,
    )

    # This step ensures that if a user hasn't answered, the row still exists
    grid = list(itertools.product(utenti_trovati, colonne_domande))
    df_grid = pd.DataFrame(grid, columns=["user_id", "question"])

    # Join the data to the perfect grid
    df_final = pd.merge(df_grid, df_melted, on=["user_id", "question"], how="left")

    df_final["category"] = df_final["question"].map(mappatura)
    df_final["category"] = df_final["category"].fillna("Unknown")

    if is_jc:
        if "answer_other" not in df_final.columns:
            df_final["answer_other"] = ""
        df_final = df_final[
            ["user_id", "category", "question", "answer", "answer_other"]
        ]
    # else:
    # df_final = df_final[['user_id', 'category', 'question', 'score']]

    # Strict sorting based on your list
    df_final["question"] = pd.Categorical(
        df_final["question"], categories=colonne_domande, ordered=True
    )
    df_final = df_final.sort_values(by=["user_id", "question"])

    # Final check for empty rows
    righe_vuote = df_final[df_final[value_name].isna()]
    if not righe_vuote.empty:
        print(
            f"   Note: {len(righe_vuote)} answers are empty (or missing in the source file)."
        )

    output_file = os.path.join(output_dir, output_filename)
    df_final.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Data extracted and saved to: {output_file} ({len(df_final)} total rows)")


def extract_and_save_complete_data(  # file_excel_fcq: str, foglio_fcq: str,
    file_excel_jc: str,
    foglio_jc: str,
    # colonne_fcq_lista: List[str],
    colonne_jc_lista: list[str],
    # file_mappatura_fcq: str,
    file_mappatura_jc: str,
    col_domanda_map: str,
    col_categoria_map: str,
    output_dir: str,
):
    os.makedirs(output_dir, exist_ok=True)

    # Loading Mappings
    # mappatura_fcq = {}
    mappatura_jc = {}

    try:
        # mappatura_fcq = load_question_mapping(file_mappatura_fcq, col_domanda_map, col_categoria_map)
        # print(f"FCQ mapping loaded: {len(mappatura_fcq)} entries.")
        mappatura_jc = load_question_mapping(
            file_mappatura_jc, col_domanda_map, col_categoria_map
        )
        print(f"JC mapping loaded: {len(mappatura_jc)} entries.")
    except Exception as e:
        print(f"ERROR: Unable to load mapping files. Details: {e}")
        return

    # Processo FCQ
    # processa_questionario(
    #     file_dati=file_excel_fcq,
    #     nome_foglio=foglio_fcq,
    #     colonne_domande=colonne_fcq_lista,
    #     output_filename="questionnaire_Risposte_fcq.csv",
    #     output_dir=output_dir,
    #     mappatura=mappatura_fcq,
    #     is_jc=False
    # )

    # Process JC
    process_questionnaire(
        file_dati=file_excel_jc,
        nome_foglio=foglio_jc,
        colonne_domande=colonne_jc_lista,
        output_filename="questionnaire_risposte_jc.csv",
        output_dir=output_dir,
        mappatura=mappatura_jc,
        is_jc=True,
    )


if __name__ == "__main__":
    # FILE_EXCEL_FCQ = "./quest_fileExcel/questionari_FCQ_per_utentiHummus.xlsx"
    # FOGLIO_DATI_FCQ = "FCQ"

    FILE_EXCEL_JC = "./quest_fileExcel/questionari_JC_per_utentiHummus.xlsx"
    FOGLIO_DATI_JC = "JC"

    # FILE_MAPPATURA_FCQ = "questionnaire_FCQ.csv"
    FILE_MAPPATURA_JC = "./questionnaires/questionnaire_JC.csv"

    OUTPUT_DIRECTORY = "./output"

    COLONNA_TESTO_DOMANDA_MAP = "questions"
    COLONNA_CATEGORIA_MAP = "category"

    COLONNE_FCQ_REALI = [
        "Contains a lot of vitamins and minerals",
        "Keeps me healthy",
        "Is nutritious",
        "Is high in protein",
        "Is good for my skin/teeth/hair/nails etc.",
        "Is high in fibre and roughage",
        "Helps me cope with stress",
        "Helps me to cope with life",
        "Helps me relax",
        "Keeps me awake/alert",
        "Cheers me up",
        "Makes me feel good",
        "Is easy to prepare",
        "Can be cooked very simply",
        "Takes no time to prepare",
        "Can be bought in shops close to where I live or work",
        "Is easily available in shops and supermarkets",
        "Smells nice",
        "Looks nice",
        "Has a pleasant texture",
        "Tastes good",
        "Contains no additives",
        "Contains natural ingredients",
        "Contains no artificial ingredients",
        "Is not expensive",
        "Is cheap",
        "Is good value for money",
        "Is low in calories",
        "Helps me control my weight",
        "Is low in fat",
        "Is what I usually eat",
        "Is familiar",
        "Is like the food I ate when I was a child",
        "Comes from countries I approve of politically",
        "Has the country of origin clearly marked",
        "Is packaged in an environmentally friendly way",
    ]

    COLONNE_JC_REALI = [
        "Age",
        "Gender",
        "Country of birth",
        "Region of birth",
        "Country of residence",
        "Region of residence",
        "Diagnosed pathologies",
        "Drugs in use",
        "Supplements taken",
        "Known food allergies",
        "Intolerances",
        "Foods not liked/avoided",
        "Religious or ethical restrictions",
        "Work activity",
        "Working hours",
        "Lunch break",
        "Snack during the day",
        "Sport practiced",
        "Weekly frequency",
        "Level",
        "Daily time spent walking",
        "Number of main meals",
        "Fruit and vegetables",
        "Meat",
        "Fish",
        "Eggs",
        "Legumes",
        "Dairy products",
        "Industrial sweets/snacks",
        "Alcohol",
        "Coffee/Tea",
        "Sugary drinks",
        "Breakfast",
        "Particular habits",
        "Motivation for change",
        "Personal goals",
        "After a night of poor sleep, what do you prefer for breakfast?",
        "If you're on vacation, what do you order for lunch?",
        "If you only have 15 minutes, what do you cook or eat?",
        "When you're stressed, what foods do you crave?",
    ]

    extract_and_save_complete_data(
        # file_excel_fcq=FILE_EXCEL_FCQ,
        # foglio_fcq=FOGLIO_DATI_FCQ,
        file_excel_jc=FILE_EXCEL_JC,
        foglio_jc=FOGLIO_DATI_JC,
        # colonne_fcq_lista=COLONNE_FCQ_REALI,
        colonne_jc_lista=COLONNE_JC_REALI,
        # file_mappatura_fcq=FILE_MAPPATURA_FCQ,
        file_mappatura_jc=FILE_MAPPATURA_JC,
        col_domanda_map=COLONNA_TESTO_DOMANDA_MAP,
        col_categoria_map=COLONNA_CATEGORIA_MAP,
        output_dir=OUTPUT_DIRECTORY,
    )
