import argparse
import ast
import re
import sys

import pandas as pd

# def clean_fcq_manual(input_file, output_file):
#     print(f"--> Lettura manuale file: {input_file}...")

#     cleaned_rows = []

#     try:
#         with open(input_file, 'r', encoding='utf-8') as f:
#             lines = f.readlines()
#     except Exception as e:
#         print(f"Errore apertura file: {e}")
#         sys.exit(1)

#     print(f"--> Righe totali trovate: {len(lines)}")

#     # Header: Saltiamo la prima riga se contiene "user_id"
#     start_index = 0
#     if "user_id" in lines[0].lower():
#         start_index = 1
#         print("--> Header rilevato e saltato.")

#     success_count = 0
#     skip_count = 0

#     for i in range(start_index, len(lines)):
#         line = lines[i].strip()
#         if not line: continue

#         # --- LOGICA CHIRURGICA ---
#         # Il file è: ID, "JSON", BOOL
#         # 1. Troviamo la prima virgola
#         first_comma = line.find(',')
#         # 2. Troviamo l'ultima virgola
#         last_comma = line.rfind(',')

#         # Se non troviamo le virgole o sono la stessa, la riga è rotta
#         if first_comma == -1 or last_comma == -1 or first_comma == last_comma:
#             print(f"Riga {i+1} malformata (separatori non trovati). Salto.")
#             skip_count += 1
#             continue

#         # ESTRAZIONE DATI
#         user_id = line[:first_comma].strip()
#         attention_check = line[last_comma+1:].strip()

#         # Il JSON è tutto quello che c'è nel mezzo
#         raw_questions = line[first_comma+1:last_comma].strip()

#         # PULIZIA PRELIMINARE JSON
#         # Se il JSON è avvolto da virgolette extra (comune nei CSV), togliamole
#         if raw_questions.startswith('"') and raw_questions.endswith('"'):
#             raw_questions = raw_questions[1:-1]

#         # Sostituiamo le virgolette doppie escape ("") con una singola (")
#         raw_questions = raw_questions.replace('""', '"')

#         # 1. FILTRO: Se attention check è FALSE, saltiamo
#         # if attention_check.lower() != 'true':
#         #     continue

#         try:
#             # Parsing del JSON
#             questions_list = ast.literal_eval(raw_questions)

#             user_text_parts = []
#             for q in questions_list:
#                 q_id = q.get('id')

#                 # 2. RIMUOVI ID 10
#                 if q_id == 10:
#                     continue

#                 text = q.get('text', '').strip()
#                 answer = q.get('answer', '').strip()

#                 if text and answer:
#                     user_text_parts.append(f"{text}: {answer}")

#             full_context = " | ".join(user_text_parts)

#             cleaned_rows.append({
#                 'user_id': user_id,
#                 'fcq_cleaned': full_context
#             })
#             success_count += 1

#         except Exception as e:
#             # Se fallisce qui, probabilmente il JSON è tagliato o corrotto
#             skip_count += 1
#             continue

#     print(f"Parsing completato.")
#     print(f" Utenti validi processati: {success_count}")
#     print(f"  Righe saltate/errori: {skip_count}")

#     # Creazione DataFrame e salvataggio
#     df_final = pd.DataFrame(cleaned_rows)

#     # Salvataggio CSV standard (virgolette automatiche)
#     df_final.to_csv(output_file, index=False)

#     print(f"--> File salvato correttamente in: {output_file}")
#     if not df_final.empty:
#         print(f" Esempio dati: {df_final.iloc[0]['fcq_cleaned'][:50]}...")


# def clean_fcq_manual(input_file, output_file):
#     print(f"--> Starting 'BULLDOZER' mode on file: {input_file}...")

#     cleaned_rows = []

#     try:
#         with open(input_file, encoding="utf-8") as f:
#             lines = f.readlines()
#     except Exception as e:
#         print(f"File opening error: {e}")
#         sys.exit(1)

#     # Header check
#     start_index = 0
#     if lines and "user_id" in lines[0].lower():
#         start_index = 1
#         print("--> Header skipped.")

#     count_ok = 0
#     count_forced = 0
#     count_fail = 0

#     for i in range(start_index, len(lines)):
#         line = lines[i].strip()
#         if not line:
#             continue

#         # 1. IDENTIFICAZIONE USER ID
#         # Prende tutto fino alla prima virgola
#         first_comma = line.find(",")
#         last_comma = line.rfind(",")

#         if first_comma == -1:
#             count_fail += 1
#             continue

#         user_id = line[:first_comma].strip()

#         # Isola la parte centrale (il contenuto sporco)
#         # Se non trova l'ultima virgola, prende tutto fino alla fine
#         if last_comma != -1 and last_comma > first_comma:
#             raw_content = line[first_comma + 1 : last_comma]
#         else:
#             raw_content = line[first_comma + 1 :]

#         # Pulizia base
#         raw_content = raw_content.strip()
#         if raw_content.startswith('"') and raw_content.endswith('"'):
#             raw_content = raw_content[1:-1]

#         # Sostituzioni per aiutare il parsing standard
#         clean_content = raw_content.replace('""', '"')
#         clean_content = clean_content.replace(" null", " None").replace(
#             ":null", ":None"
#         )
#         clean_content = clean_content.replace(" true", " True").replace(
#             ":true", ":True"
#         )
#         clean_content = clean_content.replace(" false", " False").replace(
#             ":false", ":False"
#         )

#         questions_list = []
#         parsing_method = "standard"

#         # CLEAN PARSING
#         try:
#             questions_list = ast.literal_eval(clean_content)
#             # If it's an empty list or None, force an error to go to Attempt 2
#             if not questions_list:
#                 raise ValueError("Empty list")
#         except Exception as e:
#             print(f" Standard parsing failed for {user_id}: {e}")
#             # --- ATTEMPT 2: FORCED EXTRACTION (REGEX) ---
#             # If parsing fails, we use regular expressions to "steal" the data
#             parsing_method = "forced"

#             # This pattern searches for:
#             # 1. 'id': (number)
#             # 2. anything in between
#             # 3. 'text': '(text)'
#             # 4. anything in between
#             # 5. 'answer': '(answer)'
#             # The DOTALL flag is not needed here because we work line by line, but we use non-greedy logic

#             # Robust pattern that searches for text/answer pairs ignoring structure
#             pattern = r"'id':\s*(\d+).*?'text':\s*'(.*?)'.*?'answer':\s*'(.*?)'"
#             matches = re.findall(pattern, clean_content)

#             for match in matches:
#                 try:
#                     q_id = int(match[0])
#                     text = match[1]
#                     answer = match[2]
#                     questions_list.append({"id": q_id, "text": text, "answer": answer})
#                 except Exception as e:
#                     print(f"Error processing match {match}: {e}")
#                     continue

#         # RESULT FORMATTING
#         user_text_parts = []
#         for q in questions_list:
#             q_id = q.get("id")

#             # Always skip question ID 10
#             if q_id == 10:
#                 continue

#             text = str(q.get("text", "")).strip()
#             answer = str(q.get("answer", "")).strip()

#             if text and answer:
#                 user_text_parts.append(f"{text}: {answer}")

#         # Se abbiamo estratto qualcosa, salviamo la riga
#         if user_text_parts:
#             full_context = " | ".join(user_text_parts)
#             cleaned_rows.append({"user_id": user_id, "fcq_cleaned": full_context})

#             if parsing_method == "standard":
#                 count_ok += 1
#             else:
#                 count_forced += 1
#         else:
#             # If we couldn't extract anything even with bulldozer
#             # (happens only if the row is empty or has no questions)
#             print(f" No questions found for {user_id}")
#             count_fail += 1

#     print("\nSUMMARY:")
#     print(f"Read perfectly: {count_ok}")
#     print(f"Recovered (that previously failed): {count_forced}")
#     print(f"Empty/Impossible: {count_fail}")

#     # Saving
#     df_final = pd.DataFrame(cleaned_rows)
#     df_final.to_csv(output_file, index=False)
#     print(f"File saved: {output_file} (Total rows: {len(df_final)})")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--input", type=str, required=True)
#     parser.add_argument("--output", type=str, default="fcq_cleaned.csv")
#     args = parser.parse_args()

#     clean_fcq_manual(args.input, args.output)


import pandas as pd
import ast
import re
import sys
import argparse

# 1. DEFINIZIONE DELLE DOMANDE ORIGINALI (GOLD STANDARD)
# Questo garantisce che tutte le domande con lo stesso ID abbiano lo stesso testo
STANDARD_QUESTIONS = {
    1: "I choose foods because they keep me healthy",
    2: "I choose foods that help me control my weight",
    3: "I choose foods that are convenient to prepare",
    4: "I choose foods for their taste",
    5: "I choose foods for ecological/sustainability reasons",
    6: "I choose foods for ethical or religious reasons",
    7: "I choose foods that are familiar/traditional",
    8: "I choose foods based on price",
    9: "I choose foods that improve my mood"
}

def clean_fcq_manual(input_file, output_file):
    print(f"Starting 'BULLDOZER' mode on file: {input_file}...")

    cleaned_rows = []

    try:
        with open(input_file, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"File opening error: {e}")
        sys.exit(1)

    # Header check
    start_index = 0
    if lines and "user_id" in lines[0].lower():
        start_index = 1
        print("--> Header skipped.")

    count_ok = 0
    count_forced = 0
    count_fail = 0

    for i in range(start_index, len(lines)):
        line = lines[i].strip()
        if not line:
            continue

        # ESTRAZIONE USER_ID ---
        first_comma = line.find(",")
        if first_comma == -1:
            count_fail += 1
            continue
        user_id = line[:first_comma].strip()

        # FASE 2: PULIZIA DEL CONTENUTO ---
        # Prendiamo tutto ciò che sta dopo la prima virgola
        raw_content = line[first_comma + 1 :].strip()
        
        # Rimuoviamo virgolette esterne se presenti
        if raw_content.startswith('"') and raw_content.endswith('"'):
            raw_content = raw_content[1:-1]

        # Fix comuni per la sintassi Python/JSON
        clean_content = raw_content.replace('""', '"')
        clean_content = clean_content.replace("null", "None").replace("true", "True").replace("false", "False")

        questions_list = []
        parsing_method = "standard"

        # FASE 3: PARSING (Standard -> Forced) ---
        try:
            # Proviamo il parsing standard
            questions_list = ast.literal_eval(clean_content)
            if not isinstance(questions_list, list):
                raise ValueError("Not a list")
        except:
            # Se fallisce (es. unterminated string), usiamo la Regex "Bulldozer"
            parsing_method = "forced"
            # Cerchiamo i blocchi {'id': ..., 'text': ..., 'answer': ...} anche se rotti
            # Questa regex è più robusta contro le virgolette mancanti alla fine
            pattern = r"'id':\s*(\d+).*?'text':\s*'(.*?)'.*?'answer':\s*'(.*?)'"
            matches = re.findall(pattern, clean_content)

            for match in matches:
                try:
                    questions_list.append({
                        "id": int(match[0]),
                        "text": match[1],
                        "answer": match[2]
                    })
                except:
                    continue

        # UNIFORMITÀ E FILTRO ---
        user_results = []
        # Ordiniamo per ID per avere un output consistente
        if isinstance(questions_list, list):
            # Rimuoviamo duplicati e filtriamo ID 10
            seen_ids = set()
            
            for q in questions_list:
                try:
                    q_id = int(q.get("id", 0))
                    if q_id == 10 or q_id == 0 or q_id in seen_ids:
                        continue
                    
                    # SOSTITUZIONE TESTO: Usiamo il testo standard se l'ID esiste nella nostra mappa
                    final_text = STANDARD_QUESTIONS.get(q_id, q.get("text", "Unknown Question"))
                    answer = str(q.get("answer", "")).strip()

                    if answer:
                        user_results.append((q_id, f"{final_text}: {answer}"))
                        seen_ids.add(q_id)
                except:
                    continue

        # 
        if user_results:
            # Ordiniamo per ID (1, 2, 3...) prima di unire in stringa
            user_results.sort(key=lambda x: x[0])
            full_context = " | ".join([item[1] for item in user_results])
            
            cleaned_rows.append({
                "user_id": user_id,
                "fcq_cleaned": full_context
            })

            if parsing_method == "standard":
                count_ok += 1
            else:
                print(f" Recovered {user_id} via Regex.")
                count_forced += 1
        else:
            print(f" Failed to extract any data for {user_id}")
            count_fail += 1

    # Riepilogo finale
    print("\n--- SUMMARY ---")
    print(f"Parsed perfectly: {count_ok}")
    print(f"Recovered via Bulldozer: {count_forced}")
    print(f"Total failures: {count_fail}")

    df_final = pd.DataFrame(cleaned_rows)
    df_final.to_csv(output_file, index=False)
    print(f"File saved: {output_file} (Total rows: {len(df_final)})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, default="fcq_cleaned.csv")
    args = parser.parse_args()

    clean_fcq_manual(args.input, args.output)