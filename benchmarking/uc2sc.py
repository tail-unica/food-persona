import argparse
import logging
import os

import langextract as lx
import pandas as pd

from extraction.compile_questionnaire import compile_questionnaire
from preprocessing.preprocess_questionnaire import preprocess_questionnaire
from utils.text_utils import normalize_text

# logging.basicConfig(level=logging.DEBUG)


def main():
    parser = argparse.ArgumentParser(
        description="Compile questionnaire from unstructured context."
    )
    parser.add_argument("--type", choices=["FCQ", "JC"], required=True)
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
    parser.add_argument("--uc_file", type=str, default="./data/hummus/unstructured_context.csv")
    parser.add_argument("--out_dir", type=str, default="./data/hummus/structured_context_output/")
    parser.add_argument("--overwrite", action="store_true", help="Se attivo, sovrascrive il file di output esistente.")
    parser.add_argument("--dataset", type=str, choices=["hummus", "prolific"])
    args = parser.parse_args()

    output_file = os.path.join(
        args.out_dir,
        f"structured_context_{args.type.lower()}_{args.model.replace(':', '_')}.csv",
    )
    jsonl_output_file = os.path.join(
        args.out_dir,
        f"structured_context_{args.type.lower()}_{args.model.replace(':', '_')}.jsonl",
    )
    html_output_file = os.path.join(
        args.out_dir,
        f"visualization_{args.type.lower()}_{args.model.replace(':', '_')}.html",
    )

    # List to contain the results for jsonl display
    all_processed_documents = []
    all_users_json_data = {}

    unstructured_context = pd.read_csv(args.uc_file)
    if os.path.exists(output_file) and not args.overwrite:
        sc_output = pd.read_csv(output_file)
        unstructured_context = unstructured_context[
            ~unstructured_context["user_id"].isin(sc_output["user_id"])
        ]
    else:
        if args.type == "FCQ":
            columns = ["user_id", "category", "questions", "score"]
        else:
            columns = [
                "user_id",
                "category",
                "questions",
                "options",
                "answer",
                "answer_other",
            ]
        sc_output = pd.DataFrame(columns=columns)

    if unstructured_context.empty:
        print("All users have already been processed!")
        return

    already_processed = len(sc_output["user_id"].unique())
    to_process = len(unstructured_context["user_id"].unique())

    print(f"Users already processed: {already_processed}")
    print(f"Users to process: {to_process}")

    prompt, examples, questionnaire_df = preprocess_questionnaire(args.type, dataset_source=args.dataset)

    # iterates the users to process
    for _, user_context_row in unstructured_context.iterrows():
        user_id = user_context_row["user_id"]
        biography_text = user_context_row["context_text"]

        logging.info(f"START USER PROCESSING: {user_id}")

        user_answers = {}

        # process one question at a time
        for question in questionnaire_df["questions"]:
            try:
                compile_csv = compile_questionnaire(
                    user_id,
                    biography_text,
                    prompt,
                    examples,
                    args.model,
                    specific_question=question,
                )

                if not compile_csv.extractions:
                    logging.warning(f"No extraction for {user_id}, skipping.")
                    continue

                # updates user response dictionary
                for extraction in compile_csv.extractions:
                    if (
                        extraction.extraction_class == "questionnaire"
                        and extraction.attributes
                    ):
                        normalized_attrs = {
                            normalize_text(k): v
                            for k, v in extraction.attributes.items()
                        }
                        user_answers.update(normalized_attrs)

            except Exception as e:
                print(f"Error with user {user_id}: {e}")
                logging.error(f"Error user {user_id}: {e}", exc_info=True)
                continue

        # Show all collected responses for debugging
        print(f"\n Extracted answers for user {user_id}")
        print(user_answers)

        logging.info(f"Success for user: {user_id}")
        all_processed_documents.append(compile_csv)  # for visualization

        all_attributes = user_answers

        current_user_json_data = {}

        compiled_questionnaire = questionnaire_df.copy(deep=True)
        compiled_questionnaire["user_id"] = user_id
        if args.type == "FCQ":
            compiled_questionnaire["score"] = compiled_questionnaire["questions"].map(
                lambda q: all_attributes.get(q, None)
            )
        else:
            compiled_questionnaire["answer"] = compiled_questionnaire["questions"].map(
                lambda q: all_attributes.get(q, None)
            )
            compiled_questionnaire["answer_other"] = compiled_questionnaire[
                "questions"
            ].map(lambda q: all_attributes.get(f"{q}_other", None))

        # Adds the user's JSON data to the main dictionary
        if args.type == "JC" and current_user_json_data:
            all_users_json_data[user_id] = current_user_json_data

        sc_output = pd.concat([sc_output, compiled_questionnaire], ignore_index=True)
        # Save partial output file after each user
        sc_output.to_csv(output_file, index=False)
        print(f"Success with user {user_id}")

    print(f"\nAll compilations completed. Saved to {output_file}")
    # Write the json file and create the HTML view
    if all_processed_documents:
        print("\nSaving annotated documents for viewing")
        # Save file .jsonl
        lx.io.save_annotated_documents(
            all_processed_documents, output_name=jsonl_output_file, output_dir="."
        )

        # Generate the HTML view
        print(f"Saving view in{html_output_file}...")
        html_content = lx.visualize(jsonl_output_file)

        with open(html_output_file, "w", encoding="utf-8") as f:
            if hasattr(html_content, "data"):
                f.write(html_content.data)
            else:
                f.write(str(html_content))
        print(f"Interactive view saved in {html_output_file}")


if __name__ == "__main__":
    main()
