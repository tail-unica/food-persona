import csv

# extracts the bio and user id from the TXT file

file_input = "UTENTI HUMMUS.txt"
file_output = "dati_estratti.csv"

# Counter to know how many rows we processed
utenti_estratti = 0

print(f"Starting script... Reading file '{file_input}'")

try:
    with open(file_input, encoding="utf-8") as f_in:
        with open(file_output, mode="w", encoding="utf-8", newline="") as f_out:
            lettore_tsv = csv.reader(f_in, delimiter="\t")

            scrittore_csv = csv.writer(f_out)

            scrittore_csv.writerow(["ID", "Bio"])

            for riga in lettore_tsv:
                try:
                    id_utente = riga[0]
                    bio_utente = riga[3]

                    scrittore_csv.writerow([id_utente, bio_utente])
                    utenti_estratti += 1

                except IndexError:
                    # This block is used to skip empty
                    # or malformed rows that don't have at least 4 columns
                    print("Warning: a row was skipped because it's empty or malformed.")

    print("\nExtraction completed successfully!")
    print(f"{utenti_estratti} users were extracted.")
    print(f"Data saved to '{file_output}'.")

except FileNotFoundError:
    print(f"ERROR: Unable to find file '{file_input}'.")
    print("Make sure the 'estrai.py' script is in the same folder as the .txt file")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
