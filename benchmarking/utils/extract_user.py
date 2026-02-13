import os
import zipfile

import pandas as pd

# extracts users with most reviews
# def user_extract(percorso_zip, top_n=10, save_csv=True):
#     with zipfile.ZipFile(percorso_zip, 'r') as z:
#         # Cerca automaticamente il file .inter
#         inter_file = [f for f in z.namelist() if f.endswith(".inter")][0]
#         print("File .inter trovato:", inter_file)

#         # Legge il file (tab-separated, con intestazione)
#         with z.open(inter_file) as f:
#             df = pd.read_csv(f, sep='\t', header=0)

#     # Pulisce i nomi delle colonne (toglie ":token", ":float" ecc.)
#     df.columns = [c.split(':')[0].strip() for c in df.columns]
#     print("Colonne pulite:", df.columns.tolist())

#     #Conta le review per ogni utente
#     conteggio = df['member_id'].value_counts().reset_index()
#     conteggio.columns = ['member_id', 'numero_review']

#     # Ordina in ordine decrescente
#     conteggio = conteggio.sort_values(by='numero_review', ascending=False)


#     #print(f"\nTop {top_n} utenti con più recensioni:\n")
#     #print(conteggio.head(top_n))

#     if save_csv:
#         os.makedirs("output", exist_ok=True)
#         csv_path = os.path.join("output", "top_user.csv")
#         #conteggio.to_csv(csv_path, index=False)
#         conteggio.head(top_n).to_csv(csv_path, index=False)
#         print(f"\nRisultati salvati in: {csv_path}")

#     return conteggio


# extracts a sample of 1000 users
def user_extract(percorso_zip, file_con_ids_da_cercare, top_n=1000, save_csv=True):
    with zipfile.ZipFile(percorso_zip, "r") as z:
        try:
            user_file = [f for f in z.namelist() if f.endswith(".user")][0]
            print("File .user found:", user_file)
        except IndexError:
            print("Error: No .user file found in the zip.")
            return None

        with z.open(user_file) as f:
            print("Reading database in progress...")
            df = pd.read_csv(f, sep="\t", header=0, on_bad_lines="skip")

    # Clean column names (removes ":token", etc.)
    df.columns = [c.split(":")[0].strip() for c in df.columns]
    print("Clean columns:", df.columns.tolist())

    # Load the list of IDs to search for
    if os.path.exists(file_con_ids_da_cercare):
        df_ids = pd.read_csv(file_con_ids_da_cercare)
        # Take the first available column as ID
        col_id_input = df_ids.columns[0]
        target_ids = df_ids[col_id_input].astype(str).tolist()
        print(f"IDs to search loaded: {len(target_ids)}")
    else:
        print(f"Error: ID file {file_con_ids_da_cercare} not found.")
        return None

    col_bio = "member_description"

    if "member_id" in df.columns:
        df["member_id"] = df["member_id"].astype(str)
        df_filtrato = df[df["member_id"].isin(target_ids)]
        print("Users found in .user with requested IDs:", len(df_filtrato))

        # Filter only those with non-empty biography
        # df_filtrato = df_filtrato[df_filtrato[col_bio].fillna("").str.strip() != ""]
        # print("Users found with non-empty bio (after filter):", len(df_filtrato))

        if col_bio in df.columns:
            risultato = df_filtrato[["member_id", col_bio]].copy()
            risultato.columns = ["user_id", "biography"]
        else:
            print("Description column not found, keeping all columns.")
            risultato = df_filtrato.copy()

    else:
        print("Error: Column 'member_id' not found in .user file")
        return None

    # Saving
    if save_csv and not risultato.empty:
        os.makedirs("output", exist_ok=True)
        csv_path = os.path.join("output", "users_hummus.csv")

        # Apply top_n limit if requested
        risultato_finale = risultato.head(top_n)
        # print("DEBUG → effective top_n received by function:", top_n)

        risultato_finale.to_csv(csv_path, index=False)
        print(
            f"\nResults saved to: {csv_path} (Extracted {len(risultato_finale)} users)"
        )
        return risultato_finale

    elif risultato.empty:
        print("\nNo users found crossing the data.")
        return None

    return risultato


# allinea il file precedente delle bio con i nuovi utenti filtrati
# def sync_users_biography(zip_path, file_lista_utenti, file_output_bio, top_n=1000):

#     print(f"Inizio Sincronizzazione ")

#     if not os.path.exists(file_lista_utenti):
#         print(f"Errore: File lista utenti {file_lista_utenti} non trovato.")
#         return

#     # Leggiamo il file di riferimento user_ratings_filtered
#     df_ref = pd.read_csv(file_lista_utenti)

#     # tagliamo ai primi top_n
#     df_ref = df_ref.head(top_n)

#     # Cerchiamo la colonna ID corretta nel file di riferimento
#     col_id_ref = next((c for c in df_ref.columns if c in ['member_id', 'user_id', 'id']), None)
#     if not col_id_ref:
#         print("Errore: Colonna ID non trovata nel file di riferimento.")
#         return

#     # Creiamo il SET degli ID che VOGLIAMO avere alla fine
#     target_ids = set(df_ref[col_id_ref].astype(str).str.strip().tolist())
#     print(f"Target: Vogliamo avere i dati per {len(target_ids)} utenti.")

#     # CARICHIAMO IL FILE DELLE BIOGRAFIE ATTUALE
#     if os.path.exists(file_output_bio):
#         print(f"Lettura file biografie esistente: {file_output_bio}")
#         df_bio = pd.read_csv(file_output_bio)

#         # Normalizziamo ID
#         df_bio['user_id'] = df_bio['user_id'].astype(str).str.strip()
#         current_ids = set(df_bio['user_id'].tolist())
#     else:
#         print("File biografie non esistente. Verrà creato nuovo.")
#         df_bio = pd.DataFrame(columns=['user_id', 'biography'])
#         current_ids = set()

#     # CALCOLO DELLE DIFFERENZE
#     ids_da_aggiungere = target_ids - current_ids
#     ids_da_rimuovere = current_ids - target_ids

#     print(f" -> Utenti già presenti: {len(current_ids)}")
#     print(f" -> Utenti da rimuovere (obsoleti): {len(ids_da_rimuovere)}")
#     print(f" -> Utenti da aggiungere (nuovi): {len(ids_da_aggiungere)}")

#     # RIMOZIONE utenti
#     if ids_da_rimuovere:
#         df_bio = df_bio[~df_bio['user_id'].isin(ids_da_rimuovere)]
#         print("Rimozione completata.")

#     # AGGIUNTA utenti
#     if ids_da_aggiungere:
#         print("Estrazione dati mancanti dal file ZIP...")

#         with zipfile.ZipFile(zip_path, 'r') as z:
#             try:
#                 user_file_name = [f for f in z.namelist() if f.endswith(".user")][0]
#             except IndexError:
#                 print("Errore: Nessun file .user trovato nello zip.")
#                 return

#             with z.open(user_file_name) as f:
#                 # Leggiamo il raw data
#                 df_raw = pd.read_csv(f, sep='\t', header=0, on_bad_lines='skip')

#         # Pulizia colonne raw
#         df_raw.columns = [c.split(':')[0].strip() for c in df_raw.columns]
#         df_raw['member_id'] = df_raw['member_id'].astype(str).str.strip()

#         # Prendiamo SOLO le righe degli utenti nuovi che ci servono
#         df_new_data = df_raw[df_raw['member_id'].isin(ids_da_aggiungere)].copy()

#         if not df_new_data.empty:
#             # Formattiamo come il nostro file output (user_id, biography)
#             col_desc = 'member_description' if 'member_description' in df_new_data.columns else None

#             if col_desc:
#                 df_to_append = df_new_data[['member_id', col_desc]].copy()
#                 df_to_append.columns = ['user_id', 'biography']

#                 # Pulizia valori nulli nelle nuove bio
#                 df_to_append['biography'] = df_to_append['biography'].fillna("")

#                 # Unione
#                 df_bio = pd.concat([df_bio, df_to_append], ignore_index=True)
#                 print(f"Aggiunti {len(df_to_append)} nuovi utenti.")
#             else:
#                 print("Attenzione: Colonna descrizione non trovata nel file ZIP.")
#         else:
#             print("Attenzione: Gli ID mancanti non sono stati trovati nemmeno nel file ZIP.")
#     else:
#         print("Nessun nuovo utente da aggiungere.")

#     # SALVATAGGIO FINALE
#     os.makedirs(os.path.dirname(file_output_bio), exist_ok=True)

#     df_bio.to_csv(file_output_bio, index=False)
#     print(f"\nSincronizzazione completata.")
#     print(f"File salvato: {file_output_bio}")
#     print(f"Totale utenti nel file: {len(df_bio)}")

if __name__ == "__main__":
    # user_extract("data.zip", top_n=1000)
    user_extract("data.zip", "./output/user_ratings_filtered.csv", top_n=1000)
    # sync_users_biography(
    #     zip_path="data.zip",
    #     file_lista_utenti="output/user_ratings_filtered.csv",
    #     file_output_bio="./data/hummus/unstructured_context2.csv", top_n=1000)
