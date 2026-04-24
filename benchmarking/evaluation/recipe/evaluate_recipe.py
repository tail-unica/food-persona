import json

from ollama import ChatResponse, chat

from prompts.prompt_R import format_user_content, prompt_recipe


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
    prompt_r = prompt_recipe.get(context_type)
    if not prompt_r:
        raise ValueError(f"Type of context unknown: {context_type}")

    prompt_text = prompt_r.get("prompt", "")
    if not prompt_text:
        raise ValueError(f"Empty prompt for context type: {context_type}")

    # build the user/recipe specific content
    user_content = format_user_content(
        user_id, context_text, recipe_id, title, ingredients, instructions
    )

    # send to model
    response: ChatResponse = chat(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "Follow the instructions exactly. Output ONLY valid JSON, no extra text.",
            },
            {"role": "user", "content": prompt_text},
            {"role": "user", "content": user_content},
        ],
        options={"temperature": 0.5},
    )

    response_text = response["message"]["content"]

    # check for empty response
    if not response_text or not response_text.strip():
        raise ValueError("Empty response received from the model.")

    # parsing JSON with manual fallback
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        start_index = response_text.find("{")
        end_index = response_text.rfind("}") + 1
        if start_index != -1 and end_index > start_index:
            json_str = response_text[start_index:end_index]
            return json.loads(json_str)
        else:
            raise ValueError(
                f"JSON not found in response. Original response: {response_text}"
            )
