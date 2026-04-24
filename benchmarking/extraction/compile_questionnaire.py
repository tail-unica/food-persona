import re

import langextract as lx
from langextract.core.exceptions import InferenceRuntimeError


def compile_questionnaire(
    user_id, biography_text, prompt, examples, model_name, specific_question=None
):
    biography_text = biography_text.replace(
        '"', "'"
    )  # sostitute double quotes with single quotes
    biography_text = re.sub(r"\s+", " ", biography_text.strip())  # remove extra spaces
    biography_text = biography_text.encode("utf-8", errors="ignore").decode(
        "utf-8"
    )  # remove non-utf8 characters

    input_text = f"user_id: {user_id} | biography_text: {biography_text}"

    # if a specific question is provided, modify the prompt accordingly
    prompt_question = prompt

    if specific_question:
        # add the specific question to the input text
        input_text += f" | QUESTION_TO_ANSWER: {specific_question}"

        # Chain the original prompt with the focus statement
        prompt_question = (
            f"{prompt}\n\n"
            f"IMPORTANT TASK: Focus ONLY on the question: '{specific_question}'. "
            "Extract the answer following the rules above. "
            "Ignore other questionnaire fields."
        )

    try:
        result = lx.extract(
            text_or_documents=input_text,
            prompt_description=prompt_question,
            examples=examples,
            model_id=model_name,
            fence_output=False,
            use_schema_constraints=True,
            language_model_params={"temperature": 0.0, "format": "json"},
            # show_progress=True
        )
    except InferenceRuntimeError as e:
        if "Ollama Model timed out" in str(e):
            print("Timeout rilevato. Ritento con timeout=300...")

            return lx.extract(
                text_or_documents=input_text,
                prompt_description=prompt_question,
                examples=examples,
                model_id=model_name,
                fence_output=False,
                use_schema_constraints=True,
                language_model_params={
                    "temperature": 0.0,
                    "format": "json",
                    "timeout": 300,
                },
            )
        else:
            raise e

    return result
