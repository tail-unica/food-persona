import argparse
import ast
import csv
import os
import random
import textwrap
import zipfile

import langextract as lx
import polars as pl


def load_recipes_from_zip(zip_path):
    """Apre lo ZIP, trova il file Parquet e lo carica in un DataFrame Polars."""
    with zipfile.ZipFile(zip_path, "r") as z:
        parquet_files = [f for f in z.namelist() if f.endswith(".parquet")]
        if not parquet_files:
            raise FileNotFoundError("Nessun file .parquet trovato dentro lo ZIP.")
        parquet_file = parquet_files[0]
        print(f"File Parquet trovato: {parquet_file}")
        df = pl.read_parquet(z.open(parquet_file))
    print(f"Caricate {df.shape[0]} ricette dal Parquet.")

    return df


# estrae il testo della ricetta dal DataFrame
def get_recipe_text(df, recipe_id):
    row_df = df.filter(pl.col("id") == int(recipe_id))

    if row_df.is_empty():
        raise ValueError(f"Ricetta {recipe_id} non trovata nel Parquet.")

    try:
        title = row_df.item(0, "name") or f"Ricetta {recipe_id}"
    except pl.exceptions.ColumnNotFoundError:
        title = f"Ricetta {recipe_id}"

    try:
        ingredients_data = row_df.item(0, "parsed_ingredients")

        if ingredients_data is None or (
            isinstance(ingredients_data, str) and not ingredients_data.strip()
        ):
            raise ValueError("Lista 'parsed_ingredients' vuota o nullo")

        # Se è stringa, prova a convertire
        if isinstance(ingredients_data, str):
            try:
                ingredients_list = ast.literal_eval(ingredients_data)
            except Exception:
                ingredients_list = [ingredients_data]
        elif isinstance(ingredients_data, list):
            ingredients_list = ingredients_data
        else:
            # Se arriva come Series o altra struttura, convertila in lista
            ingredients_list = list(ingredients_data)

        ingredients_str = ", ".join(map(str, ingredients_list))

    except Exception as e:
        raise ValueError(
            f"Ricetta {recipe_id} ('{title}'): Impossibile parsare 'parsed_ingredients' - {e}"
        )

    try:
        directions_data = row_df.item(0, "directions")

        if directions_data is None or (
            isinstance(directions_data, str) and not directions_data.strip()
        ):
            raise ValueError("Stringa 'directions' vuota o nullo")

        if isinstance(directions_data, str):
            try:
                directions_list = ast.literal_eval(directions_data)
            except Exception:
                directions_list = [directions_data]
        elif isinstance(directions_data, list):
            directions_list = directions_data
        else:
            directions_list = list(directions_data)

        instructions_str = ". ".join([step for step in directions_list if step])

    except Exception as e:
        raise ValueError(
            f"Ricetta {recipe_id} ('{title}'): Impossibile parsare 'directions' - {e}"
        )

    if not ingredients_str or not instructions_str:
        raise ValueError(
            f"Ricetta {recipe_id} ('{title}') ha ingredienti o istruzioni mancanti dopo il parsing."
        )

    return title, ingredients_str, instructions_str


def evaluate_recipe(
    user_id,
    context_text,
    context_type,
    recipe_id,
    title,
    ingredients,
    instructions,
    model_name,
):
    if context_type == "unstructured_context":
        prompt = textwrap.dedent("""Extract each user's biographical text. Then rate each recipe based on their biography,
            scoring it from 1 to 6, and enter a short review explaining the reason for that rating.
            If you don't know how to rate a recipe, enter "None." The result should be a single rating per recipe.
        """)

        examples = [
            lx.data.ExampleData(
                text=textwrap.dedent("""
                user_id: 1123 | biography_text: I'm vegan and I love simple, healthy dishes.
                recipe_id: 167 | title: Roasted Brussels Sprouts | ingredients: Brussels sprouts, olive oil, Flaky salt, Pepper  """),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="evaluation",
                        extraction_text="Roasted Brussels Sprouts",
                        attributes={
                            "score": "6",
                            "short_review": "As a vegan who loves healthy dishes, I would rate this recipe highly. It's plant-based and simple to prepare.",
                        },
                    )
                ],
            ),
            lx.data.ExampleData(
                text=textwrap.dedent("""
                user_id: 1123 | biography_text: I'm vegan and I love simple, healthy dishes.
                recipe_id: 238 | title: Lasagna alla Bolognese | ingredients: Meat, milk, butter
                """),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="evaluation",
                        extraction_text="Lasagna alla Bolognese",
                        attributes={
                            "score": "1",
                            "short_review": "As a vegan, I cannot eat meat-based dishes like this lasagna.",
                        },
                    )
                ],
            ),
        ]
    elif context_type == "questionnaires":
        prompt = textwrap.dedent("""Based on the user's answers in the questionnaire, rate each recipe
            on a scale from 1 to 6 and provide a short_review explaining your rating.
            If you cannot rate a recipe, respond with "None." Ensure that there is only one rating per recipe.
        """)

        examples = [
            lx.data.ExampleData(
                text=textwrap.dedent("""
                user_id: 1123 | questionnaire: Convenience, Takes no time to prepare: 4 |
                recipe_id: 167 | title: Avocado Crab Salad | ingredients: Hass avocado, grape tomatoes, about 10, halved,
                crumbled feta cheese (I use an herbed one),black olives, halved,canned black beans, rinsed and drained,
                crabmeat (or however much you like), extra virgin olive oil, to taste", pepper, to taste.
                """),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="evaluation",
                        extraction_text="Avocado Crab Salad",
                        attributes={
                            "score": "5",
                            "short_review": "Based on the user's preference for convenience and quick preparation, this recipe is suitable as it is easy and fast to make.",
                        },
                    )
                ],
            )
        ]
    elif context_type == "both":
        prompt = textwrap.dedent("""Based on the user's answers in the questionnaire and biography rate each recipe
            on a scale from 1 to 6 and provide a short_review explaining your rating.
            If you cannot rate a recipe, respond with "None." Ensure that there is only one rating per recipe.
        """)

        examples = [
            lx.data.ExampleData(
                text=textwrap.dedent("""
                user_id: 2223 | questionnaire: Convenience, Takes no time to prepare: 4 | biography_text: I love anything that
                combines flavor and simplicity. In the kitchen, I look for recipes that are quick to prepare but always
                deliver something special. I enjoy experimenting with fresh, colorful ingredients, creating light, flavorful
                dishes, perfect for those who want to eat well without spending hours in the kitchen.
                recipe_id: 167 | title: Avocado Crab Salad | ingredients: Hass avocado, grape tomatoes, about 10, halved,
                crumbled feta cheese (I use an herbed one),black olives, halved,canned black beans, rinsed and drained,
                crabmeat (or however much you like), extra virgin olive oil, to taste", pepper, to taste.
                """),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="evaluation",
                        extraction_text="Avocado Crab Salad",
                        attributes={
                            "score": "5",
                            "short_review": "Based on the user's preference for convenience and quick preparation, this recipe is suitable as it is easy and fast to make.",
                        },
                    )
                ],
            )
        ]

    if context_type == "unstructured_context":
        input_text = f"user_id: {user_id} | biography_text: {context_text} | recipe_id: {recipe_id} | title: {title} | ingredients: {ingredients} | instructions: {instructions}"
    elif context_type == "questionnaires":
        input_text = f"user_id: {user_id} | questionnaire: {context_text} | recipe_id: {recipe_id} | title: {title} | ingredients: {ingredients} | instructions: {instructions}"
    elif context_type == "both":
        input_text = f"user_id: {user_id} | questionnaire: {context_text} | biography_text: {context_text} | recipe_id: {recipe_id} | title: {title} | ingredients: {ingredients} | instructions: {instructions}"

    result = lx.extract(
        text_or_documents=input_text,
        prompt_description=prompt,
        examples=examples,
        model_id=model_name,
        fence_output=False,
        use_schema_constraints=False,
        # language_model_params={"timeout": 600}
    )
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Rate 10 recipes per user based on their bio or their questionnaire."
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=["unstructured_context", "questionnaires", "both"],
    )
    parser.add_argument(
        "--ratings", type=str, required=True
    )  # nome file:user_ratings_filtered.csv
    parser.add_argument(
        "--uc_file", type=str, help="uncontext file with user biographies"
    )
    parser.add_argument("--questionaire_FCQ", type=str)
    parser.add_argument("--questionaire_JC", type=str)
    parser.add_argument(
        "--recipes_zip",
        type=str,
        required=True,
        help="Archivio ZIP contenente phase_recipes.parquet",
    )

    # parser.add_argument("--model", type=str, default="llama3.1:8b")
    # parser.add_argument("--model", type=str, default="qwen2.5:32b")
    # parser.add_argument("--model", type=str, default="qwen3:32b")
    # parser.add_argument("--model", type=str, default="deepseek-r1:32b")
    parser.add_argument("--model", type=str, default="deepseek-r1:70b")

    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num_recipes", type=int, default=10)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    output_file = os.path.join(
        args.out_dir,
        f"evaluated_recipes_{args.type.lower()}_{args.model.replace(':', '_')}.csv",
    )

    # Carica le ricette dal Parquet
    recipes_df = load_recipes_from_zip(args.recipes_zip)

    if args.type == "unstructured_context" and not args.uc_file:
        raise ValueError("Devi passare --uc_file per il tipo 'unstructured_context'")
    if args.type == "questionnaires" and (
        not args.questionaire_FCQ or not args.questionaire_JC
    ):
        raise ValueError(
            "Devi passare SIA --questionaire_FCQ SIA --questionaire_JC per il tipo 'questionnaires'"
        )
    if args.type == "both" and (
        not args.uc_file or not args.questionaire_FCQ or not args.questionaire_JC
    ):
        raise ValueError(
            "Devi passare TUTTI E TRE i file (--uc_file, --questionaire_FCQ, --questionaire_JC) per il tipo 'both'"
        )

    #
    uc_data = {}
    fcq_data = {}
    jc_data = {}
    all_user_ids = set()

    # Carica biografie se il file è fornito
    if args.uc_file:
        try:
            with open(args.uc_file, encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    user_id = row["user_id"]
                    uc_data[user_id] = row.get("biography_text", "N/A")
                    all_user_ids.add(user_id)
        except FileNotFoundError:
            if args.type == "unstructured_context" or args.type == "both":
                raise FileNotFoundError(
                    f"File biografie richiesto non trovato: {args.uc_file}"
                )
        except Exception as e:
            raise Exception(f"Errore in {args.uc_file}: {e}")

    # Carica FCQ se il file è fornito
    if args.questionaire_FCQ:
        try:
            with open(args.questionaire_FCQ, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user_id = row["user_id"]
                    answer_str = f"{row['category']}, {row['question']}: {row['score']}"
                    fcq_data.setdefault(user_id, []).append(answer_str)
                    all_user_ids.add(user_id)
        except FileNotFoundError:
            if args.type == "questionnaires" or args.type == "both":
                raise FileNotFoundError(
                    f"File FCQ richiesto non trovato: {args.questionaire_FCQ}"
                )
        except Exception as e:
            raise Exception(f"Errore in {args.questionaire_FCQ}: {e}")

    # Carica JC se il file è fornito
    if args.questionaire_JC:
        try:
            with open(args.questionaire_JC, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user_id = row["user_id"]
                    answer_other = row.get("answer_other", "").strip()
                    answer_text = row["answer"]
                    if answer_other:
                        answer_text = f"{answer_text} ({answer_other})"
                    answer_str = f"{row['category']}, {row['question']}: {answer_text}"
                    jc_data.setdefault(user_id, []).append(answer_str)
                    all_user_ids.add(user_id)
        except FileNotFoundError:
            if args.type == "questionnaires" or args.type == "both":
                raise FileNotFoundError(
                    f"File JC richiesto non trovato: {args.questionaire_JC}"
                )
        except Exception as e:
            raise Exception(f"Errore in {args.questionaire_JC}: {e}")

    users = []
    for user_id in all_user_ids:
        bio_text = uc_data.get(user_id, "N/A")
        fcq_list = fcq_data.get(user_id, ["N/A"])
        jc_list = jc_data.get(user_id, ["N/A"])

        # Unisce FCQ e JC in una singola stringa di testo
        fcq_text = " | ".join(fcq_list)
        jc_text = " | ".join(jc_list)
        questionnaire_text = f"FCQ: {fcq_text} | JC: {jc_text}"

        if args.type == "unstructured_context":
            # Aggiungi solo se l'utente HA una biografia
            if user_id in uc_data:
                users.append({"user_id": user_id, "context_text": bio_text})

        elif args.type == "questionnaires":
            # Aggiungi solo se l'utente HA dati da almeno un questionario
            if user_id in fcq_data or user_id in jc_data:
                users.append({"user_id": user_id, "context_text": questionnaire_text})

        elif args.type == "both":
            # Aggiunge solo se l'utente HA SIA bio SIA dati questionari
            if user_id in uc_data and (user_id in fcq_data or user_id in jc_data):
                combined_context = (
                    f"biography_text: {bio_text} | questionnaire: {questionnaire_text}"
                )
                users.append({"user_id": user_id, "context_text": combined_context})

    print(f"Caricati {len(users)} utenti idonei per la modalità '{args.type}'.")

    # Carica lista (utente-ricette)
    user_recipes = {}
    with open(args.ratings, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            member_id = int(row["member_id"])
            recipe_id = int(row["recipe_id"])
            user_recipes.setdefault(member_id, set()).add(recipe_id)

    # Converti i set in liste e mescola l’ordine per varietà
    for member_id in user_recipes:
        recipe_list = list(user_recipes[member_id])
        random.shuffle(recipe_list)
        user_recipes[member_id] = recipe_list

    # Crea CSV output
    with open(output_file, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["member_id", "recipe_id", "score", "short_review"])

        for user in users:
            user_id = int(user["user_id"])

            context_text = user["context_text"]

            recipes_to_rate = user_recipes.get(user_id, [])

            successful_recipes_count = 0

            if not recipes_to_rate:
                print(f"Nessuna ricetta da valutare per {user_id}")
                continue

            print(
                f"\nUtente {user_id}: Inizio valutazione (Obiettivo: {args.num_recipes})"
            )

            for recipe_id in recipes_to_rate:
                if successful_recipes_count >= args.num_recipes:
                    print(
                        f"Utente {user_id}: Obiettivo di {args.num_recipes} ricette raggiunto."
                    )
                    break

                try:
                    title, ingredients_str, instructions_str = get_recipe_text(
                        recipes_df, recipe_id
                    )

                    result = evaluate_recipe(
                        user_id,
                        context_text,
                        args.type,
                        recipe_id,
                        title,
                        ingredients_str,
                        instructions_str,
                        args.model,
                    )

                except Exception as e:
                    print(f"Error {user_id}/{recipe_id}: {e}")
                    continue

                if not result.extractions:
                    print(
                        f"Warn {user_id}/{recipe_id}: No extraction from model. - Recipe skipped."
                    )
                    continue

                extraction = next(
                    (
                        ex
                        for ex in result.extractions
                        if ex and ex.extraction_class == "evaluation"
                    ),
                    None,
                )

                if extraction:
                    score = extraction.attributes.get("score", "None")
                    short_review = extraction.attributes.get("short_review", "None")
                    writer.writerow([user_id, recipe_id, score, short_review])

                    successful_recipes_count += 1
                    print(
                        f"User {user_id}: Recipe {recipe_id} valid. ({successful_recipes_count}/{args.num_recipes})"
                    )

    print(f"\nAll evaluations completed. File saved to: {output_file}")


if __name__ == "__main__":
    main()
