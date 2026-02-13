import os

import langextract as lx
import pandas as pd

from prompts.prompt_Q import config
from utils.text_utils import normalize_text


def preprocess_questionnaire(questionnaire_type, dataset_source):
    # load file in base to type
    #PER HUMMUS
    #questionnaire_file = os.path.join("questionnaires", f"./questionnaire_{questionnaire_type}.csv")
    #PER PROLIFIC 
    #questionnaire_file = os.path.join("questionnaires", f"./questionnaire_{questionnaire_type}_revisited.csv")

    
    filename = f"questionnaire_{questionnaire_type}"
    # only for prolific FCQ
    if dataset_source == "prolific" and questionnaire_type == "FCQ":
        filename += "_revisited"
    # add file extension
    filename += ".csv"

    questionnaire_file = os.path.join("questionnaires", filename)

    questionnaire = pd.read_csv(questionnaire_file)

    questionnaire["questions"] = questionnaire["questions"].map(normalize_text)

    prompt_text = config[questionnaire_type]["prompt"]
    for _, row in questionnaire.iterrows():
        options = row.get("options")
        # JC
        if questionnaire_type == "JC" and "options" in row and row["options"]:
            if pd.notna(options) and options:
                prompt_text += config["JC"]["option_prompt"].format(
                    option=row["options"]
                )
                if "Altro" in row["options"]:
                    prompt_text += config["JC"]["option_other_prompt"]

    prompt_text += config["JSON_rules"]

    examples = config[questionnaire_type]["examples"]
    for i in range(len(examples)):
        for j in range(len(examples[i]["extractions"])):
            examples[i]["extractions"][j] = lx.data.Extraction(
                **examples[i]["extractions"][j]
            )
        examples[i] = lx.data.ExampleData(**examples[i])

    return prompt_text, examples, questionnaire
