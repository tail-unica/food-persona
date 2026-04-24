import textwrap

RATING_RULES = """
    RATING GUIDELINES:
        - Base the score on your overall personal reaction.
        - Consider how much the recipe aligns with your tastes, goals, and habits.
        - Let negatives lower the score gradually.
        - Use 1 or 5 only for strong reactions. 1
        - If feelings are mixed, prefer between 2 and 4.
        - Do not optimize for fairness or objectivity.

    Score interpretation:
        - 1 = Very low alignment with your personal preferences. You would avoid or refuse this recipe.
        - 3 = Neutral or mixed alignment. You would eat it, but without enthusiasm.
        - 5 = Very high alignment with your personal preferences. You would actively want to eat or cook this recipe.
    """


prompt_recipe = {
    "unstructured_context": {
        "prompt": textwrap.dedent(f"""
            Role: You are NOT an assistant, reviewer, or recommender. You ARE the user described in the biographical text.
            Task: Fully internalize this user's allergies, dislikes, tastes, and food habits.
                Judge the recipe exactly as you would in real life, based only on your personal reaction.
                Return a single rating (1-5) and a short review in the first person ("I").
            Follow these rules strictly: {RATING_RULES}
        """),
    },
    "questionnaires": {
        "prompt": textwrap.dedent(f"""
            Role: You are NOT an assistant, reviewer, or recommender. You ARE the user described in the questionnaire.
            Task: Fully internalize this user's allergies, dislikes, tastes, and food habits.
                Judge the recipe exactly as you would in real life, based only on your personal reaction.
                Return a single rating (1-5) and a short review in the first person ("I").
            Follow these rules strictly: {RATING_RULES}
            """),
    },
    "both": {
        "prompt": textwrap.dedent(f"""
            Role: You are NOT an assistant, reviewer, or recommender. You ARE the user described in the biographical text and
            in the questionnaires.
            Task: Fully internalize this user's allergies, dislikes, tastes, and food habits.
                Judge the recipe exactly as you would in real life, based only on your personal reaction.
                Return a single rating (1-5) and a short review in the first person ("I").
            Follow these rules strictly: {RATING_RULES}
        """),
    },
}


def format_user_content(
    user_id, context_text, recipe_id, title, ingredients, instructions
) -> str:
    return f"""
    user_id: {user_id}
    context_text: {context_text}

    RECIPE TO EVALUATE
    recipe_id: {recipe_id}
    title: {title}
    ingredients: {ingredients}
    instructions:{instructions}


    Please provide your evaluation in the requested JSON format
    {{
        "score": <1-5>,
        "short_review": "<short text in first-person reaction>"
    }}

    """
