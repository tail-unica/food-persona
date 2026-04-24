import argparse
import csv
import os

from evaluation.recipe.evaluate_recipe import evaluate_recipe
from evaluation.recipe.load_recipes import load_recipes_from_zip
from utils.extract_text_recipes import get_recipe_text
from utils.smart_load_data import smart_load_data


def main():
    parser = argparse.ArgumentParser(
        description="Rate recipes per user based on their bio or questionnaire or both."
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=[
            "unstructured_context",
            "questionnaires",
            "both",
            "only_fcq",
            "only_jc",
        ],
    )
    parser.add_argument("--ratings", type=str, required=True)
    parser.add_argument("--uc_file", type=str)
    parser.add_argument("--questionaire_FCQ", type=str)
    parser.add_argument("--questionaire_JC", type=str)
    parser.add_argument("--recipes_zip", type=str, required=True, default="./data.zip")
    parser.add_argument(
        "--model",
        type=str,
        default="qwen2.5:32b",
        choices=[
            "deepseek-r1:32b",
            "deepseek-r1:70b",
            "qwen2.5:32b",
            "qwen3:32b",
            "llama3.1:8b",
        ],
    )
    parser.add_argument(
        "--ranking_file", type=str, help="File CSV con la classifica degli utenti"
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=100,
        help="Numero di utenti da estrarre dalla classifica",
    )
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num_recipes", type=int, default=10)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    output_file = os.path.join(
        args.out_dir,
        f"evaluated_recipes_{args.type.lower()}_{args.model.replace(':', '_')}.csv",
    )

    # load recipes
    recipes_df = load_recipes_from_zip(args.recipes_zip)

    # validate args
    if args.type == "unstructured_context" and not args.uc_file:
        raise ValueError("Devi passare --uc_file per 'unstructured_context'")
    if args.type == "questionnaires" and (
        not args.questionaire_FCQ or not args.questionaire_JC
    ):
        raise ValueError(
            "Devi passare sia --questionaire_FCQ che --questionaire_JC per 'questionnaires'"
        )
    if args.type == "both" and (
        not args.uc_file or not args.questionaire_FCQ or not args.questionaire_JC
    ):
        raise ValueError("Devi passare tutti e tre i file per 'both'")
    if args.type == "only_fcq" and not args.questionaire_FCQ:
        raise ValueError("Devi passare --questionaire_FCQ per la modalità 'only_fcq'")
    if args.type == "only_jc" and not args.questionaire_JC:
        raise ValueError("Devi passare --questionaire_JC per la modalità 'only_jc'")

    # load user data
    # all_user_ids = set()

    uc_data, fcq_data, jc_data = {}, {}, {}
    ids_uc, ids_fcq, ids_jc = set(), set(), set()

    # Bio (UC)
    if args.uc_file and args.type in ["unstructured_context", "both"]:
        print(f"Caricamento UC da {args.uc_file}...")
        with open(args.uc_file, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                user_id = row["user_id"]
                text = row.get("biography_text") or row.get("context_text") or "N/A"
                uc_data[user_id] = text
                ids_uc.add(user_id)
    # FCQ
    if args.questionaire_FCQ and args.type in ["questionnaires", "both", "only_fcq"]:
        print("Caricamento FCQ...")
        fcq_data, ids_fcq = smart_load_data(args.questionaire_FCQ)
    # JC
    if args.questionaire_JC and args.type in ["questionnaires", "both", "only_jc"]:
        print("Caricamento JC...")
        jc_data, ids_jc = smart_load_data(args.questionaire_JC)

    all_available_users = ids_uc | ids_fcq | ids_jc

    # ranking filter
    ranked_users_ids = set()
    if args.ranking_file:
        print(f"Reading ranking from: {args.ranking_file} (Top {args.top_k})")
        try:
            with open(args.ranking_file, encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    if count >= args.top_k:
                        break
                    # Handling common column names for user ID
                    uid = (
                        row.get("User ID") or row.get("user_id") or row.get("member_id")
                    )
                    if uid:
                        ranked_users_ids.add(str(uid).strip())
                        count += 1
            print(f"Extract {len(ranked_users_ids)}users from the ranking.")
        except Exception as e:
            print(f"Errore nella lettura del file classifica: {e}")
            return

    # I only take users who are in the top 100 rankings
    if args.ranking_file:
        # Hummus: Filter using ranking
        target_users_ids = all_available_users.intersection(ranked_users_ids)
    else:
        # Prolific: Get ALL found users
        target_users_ids = all_available_users
    print(
        f"End users to be processed (data cross-referencing/ranking): {len(target_users_ids)}"
    )

    # User list construction
    users = []
    for user_id in target_users_ids:
        # Retrieve the biography text and answers lists
        bio_text = uc_data.get(user_id, "N/A")
        fcq_list = fcq_data.get(user_id, [])
        jc_list = jc_data.get(user_id, [])

        # FCQ
        if isinstance(fcq_list, list):
            # HUMMUS
            fcq_text = " | ".join(fcq_list)
        elif fcq_list:
            # PROLIFIC
            fcq_text = str(fcq_list).strip()
        else:
            # if is empty or None
            fcq_text = "N/A"

        # JC Check
        if isinstance(jc_list, list):
            # HUMMUS
            jc_text = " | ".join(jc_list)
        elif jc_list:
            # PROLIFIC
            jc_text = str(jc_list).strip()
        else:
            # if is empty or None
            jc_text = "N/A"
        # Final union
        questionnaire_text = f"FCQ: {fcq_text} | JC: {jc_text}"

        if args.type == "unstructured_context" and user_id in uc_data:
            users.append({"user_id": user_id, "context_text": bio_text})
        elif args.type == "questionnaires" and (
            user_id in fcq_data or user_id in jc_data
        ):
            users.append({"user_id": user_id, "context_text": questionnaire_text})
        elif (
            args.type == "both"
            and user_id in uc_data
            and (user_id in fcq_data or user_id in jc_data)
        ):
            combined_context = (
                f"biography_text: {bio_text} | questionnaire: {questionnaire_text}"
            )
            users.append({"user_id": user_id, "context_text": combined_context})
        elif args.type == "only_fcq" and fcq_text != "N/A":
            users.append({"user_id": user_id, "context_text": f"FCQ: {fcq_text}"})
        elif args.type == "only_jc" and jc_text != "N/A":
            users.append({"user_id": user_id, "context_text": f"JC: {jc_text}"})

    print(f"Caricati {len(users)} utenti idonei per la modalità '{args.type}'.")

    # load user recipes from ratings file
    user_recipes = {}
    with open(args.ratings, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            member_id = str(row["user_id"]).strip()
            recipe_id = int(row["recipe_id"])
            user_recipes.setdefault(member_id, set()).add(recipe_id)
    for member_id in user_recipes:
        user_recipes[member_id] = sorted(list(user_recipes[member_id]))

    # Csv output
    with open(output_file, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["user_id", "recipe_id", "score", "review"])

        for user in users:
            user_id = str(user["user_id"]).strip()

            context_text = user["context_text"]
            recipes_to_rate = sorted(user_recipes.get(user_id, []))[: args.num_recipes]

            if not recipes_to_rate:
                print(f"No recipe to evaluate for{user_id}")
                continue

            successful_recipes_count = 0
            print(f"\nUser {user_id}: Start evaluation (Objective: {args.num_recipes})")

            for recipe_id in recipes_to_rate:
                if successful_recipes_count >= args.num_recipes:
                    break
                try:
                    title, ingredients_str, instructions_str = get_recipe_text(
                        recipes_df, recipe_id
                    )
                    print(f"Recipe development {recipe_id}", end=" ", flush=True)

                    if args.type in ["only_fcq", "only_jc"]:
                        type_to_pass = "questionnaires"
                    else:
                        type_to_pass = args.type

                    result = evaluate_recipe(
                        user_id,
                        context_text,
                        type_to_pass,
                        recipe_id,
                        title,
                        ingredients_str,
                        instructions_str,
                        args.model,
                    )
                    score = result.get("score", "Unknown")
                    short_review = result.get("short_review", "Unknown")
                    writer.writerow([user_id, recipe_id, score, short_review])
                    successful_recipes_count += 1
                    print(
                        f"User {user_id}: Recipe {recipe_id} evaluated ({successful_recipes_count}/{args.num_recipes})"
                    )
                except Exception as e:
                    print(f"Error {user_id}/{recipe_id}: {e}")
                    continue

    print(f"\nAll evaluations completed. File saved in: {output_file}")


if __name__ == "__main__":
    main()
