import textwrap

# FOR FCQ
config = {
    "JSON_rules": textwrap.dedent("""
        CRITICAL JSON RULES:
        1. Output ONLY valid JSON. No markdown, no <think> tags.
        2. The "attributes" key MUST be a nested JSON Object { "Key": "Value" }.
        3. NEVER output "attributes" as a string.
        CORRECT: "attributes": { "Keeps me healthy": "4" }
        WRONG: "attributes": "Keeps me healthy: 4"
        4. You MUST return a key for EVERY question.
    """),
    "FCQ": {
        "prompt": textwrap.dedent(r"""\ Extract the user_id, the biography_text for every user. Then compile the questionnaire,
            relying only on the information included into the biography_text provided.
            Compile every aswer for every user, with value from 1 to 4, the values correspond to
                "1":Not at all important,
                "2":Not very important,
                "3":Somewhat important,
                "4":Very important.
            You must provide an answer for EVERY single question in the questionnaire.
            Answer every question in the exact order provided. Do NOT reorder or skip questions.
            If in the biography there isn't the necessary information to answer the question, insert "Unknown" in the answer,
            instead of making up a value. The attributes must correspond only to the questions in the questionnaire.
        """),
        "examples": [
            {
                "text": textwrap.dedent(r"""\ user_id: new2healthyeating_291860 | biography_text: I am looking for Gluten-free, organice recipes
                    that are vegetarian based and free of fats. I know it sounds really restricted, but my family is feeling
                    better and healthier than we have in years. This is our chance to 'start over'. I can't believe how excited
                    I am about cooking, now. I LOVE IT! """),
                "extractions": [
                    {
                        "extraction_class": "user",
                        "extraction_text": "new2healthyeating_291860",
                        "attributes": {"field": "user_id"},
                    },
                    {
                        "extraction_class": "biography",
                        "extraction_text": "I am looking for Gluten-free, organice recipes that are vegetarian based and free of fats. I know it sounds really restricted, but my family is feeling better and healthier than we have in years. This is our chance to 'start over'. I can't believe how excited I am about cooking, now. I LOVE IT!",
                        "attributes": {"field": "biography_text"},
                    },
                    {
                        "extraction_class": "questionnaire",
                        "extraction_text": "but my family is feeling better and healthier than we have in years.",
                        "attributes": {
                            "Keeps me healthy": "4",
                        },
                    },
                    {
                        "extraction_class": "questionnaire",
                        "extraction_text": "but my family is feeling better and healthier than we have in years.",
                        "attributes": {
                            "Makes me feel good": "4",
                        },
                    },
                    {
                        "extraction_class": "questionnaire",
                        "extraction_text": "",
                        "attributes": {
                            "Is easy to prepare": "Unknown",
                        },
                    },
                    {
                        "extraction_class": "questionnaire",
                        "extraction_text": "",
                        "attributes": {
                            "Is convenient": "Unknown",
                        },
                    },
                ],
            }
        ],
    },
    # FOR JC
    "JC": {
        "prompt": textwrap.dedent(r"""\ Extract the user_id, the biography_text for every user. Then compile the questionnaire,
            relying only on the information included into the biography_text provided.
            Some questions have open-ended answers, while others require you to choose an option. Fill in each answer to the questions
            for each user, but do not explain why they chose one of the available options.
            If in the biography there isn't the neccesary information to compile the question, insert "Unknown" in the answer.
            When there is partial information that allows you to deduce the answer, indicate the part of the biography text from
            which it was deduced. The attributes must correspond only to the questions in the questionnaire.
            You must complete all the questions, without skipping any."""),
        "examples": [
            {
                "text": textwrap.dedent(r"""\ user_id: erinl228_1342735 | biography_text: I am a stay at home mom who loves to cook and bake!
                    I am always looking for new recipes and a lot of the time I whip up my own version, altering the recipe! It's so
                    much fun and the satisfaction you get from everyone enjoying your food and baked goods so much is so rewarding!
                    I live in Upstate NY with my amazing daughter, my fiance and our cat and goldfish! """),
                "extractions": [
                    {
                        "extraction_class": "user",
                        "extraction_text": "erinl228_1342735",
                        "attributes": {"field": "user_id"},
                    },
                    {
                        "extraction_class": "biography",
                        "extraction_text": "I am a stay at home mom who loves to cook and bake! I am always looking for new recipes and a lot of the time I whip up my own version, altering the recipe! It's so much fun and the satisfaction you get from everyone enjoying your food and baked goods so much is so rewarding! I live in Upstate NY with my amazing daughter, my fiance and our cat and goldfish!",
                        "attributes": {"field": "biography_text"},
                    },
                    {
                        "extraction_class": "questionnaire",
                        "extraction_text": "I am a stay at home mom who loves to cook and bake!",
                        "attributes": {
                            "Gender": "F",
                        },
                    },
                    {
                        "extraction_class": "questionnaire",
                        "extraction_text": "I live in Upstate NY ",
                        "attributes": {
                            "City of residence": "Upstate NY",
                        },
                    },
                    {
                        "extraction_class": "questionnaire",
                        "extraction_text": "",
                        "attributes": {
                            "Intolerances": "Unknown",
                        },
                    },
                    {
                        "extraction_class": "questionnaire",
                        "extraction_text": "",
                        "attributes": {
                            "Diagnosed pathologies": "Unknown",
                        },
                    },
                ],
            },
            {
                "text": textwrap.dedent(r"""\ user_id: new2healthyeating_291860 | biography_text: I am looking for Gluten-free, organice recipes
                    that are vegetarian based and free of fats. I know it sounds really restricted, but my family is feeling
                    better and healthier than we have in years. This is our chance to 'start over'. I can't believe how excited
                    I am about cooking, now. I LOVE IT! """),
                "extractions": [
                    {
                        "extraction_class": "user",
                        "extraction_text": "new2healthyeating_291860",
                        "attributes": {"field": "user_id"},
                    },
                    {
                        "extraction_class": "biography",
                        "extraction_text": "I am looking for Gluten-free, organice recipes that are vegetarian based and free of fats. I know it sounds really restricted, but my family is feeling better and healthier than we have in years. This is our chance to 'start over'. I can't believe how excited I am about cooking, now. I LOVE IT!",
                        "attributes": {"field": "biography_text"},
                    },
                    {
                        "extraction_class": "questionnaire",
                        "extraction_text": "I am looking for Gluten-free, organice recipes that are vegetarian based and free of fats.",
                        "attributes": {
                            "Religious or ethical restrictions": "Other",
                            "Religious or ethical restrictions_other": "Vegetarian, Gluten-free, organic, free of fats",
                        },
                    },
                ],
            },
        ],
        "option_prompt": "Option: {option}. Choose one.\n",
        "option_other_prompt": "If you choose 'Other', please write your own answer instead of copying 'Other'.\n",
    },
}
