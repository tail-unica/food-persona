import ast

import polars as pl

from utils.text_utils import clean_text


# extracts the recipe text from the DataFrame
def get_recipe_text(df, recipe_id):
    row_df = df.filter(pl.col("id") == int(recipe_id))

    if row_df.is_empty():
        raise ValueError(f"Recipe {recipe_id} not found in Parquet.")

    try:
        title = row_df.item(0, "name") or f"Recipe {recipe_id}"
    except pl.exceptions.ColumnNotFoundError:
        title = f"Recipe {recipe_id}"

    try:
        ingredients_data = row_df.item(0, "parsed_ingredients")

        if ingredients_data is None or (
            isinstance(ingredients_data, str) and not ingredients_data.strip()
        ):
            raise ValueError("List 'parsed_ingredients' empty or null")

        # if is string, try to eval as list
        if isinstance(ingredients_data, str):
            try:
                ingredients_list = ast.literal_eval(ingredients_data)
            except Exception:
                ingredients_list = [ingredients_data]
        elif isinstance(ingredients_data, list):
            ingredients_list = ingredients_data
        else:
            # if arrives as Series or other structure, convert to list
            ingredients_list = list(ingredients_data)

        ingredients_str = ", ".join(map(str, ingredients_list))
        ingredients_str = clean_text(ingredients_str)

    except Exception as e:
        raise ValueError(
            f"Recipe {recipe_id} ('{title}'): Impossible to parse 'parsed_ingredients' - {e}"
        )

    try:
        directions_data = row_df.item(0, "directions")

        if directions_data is None or (
            isinstance(directions_data, str) and not directions_data.strip()
        ):
            raise ValueError("String 'directions' empty or null")

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
        instructions_str = clean_text(instructions_str)

    except Exception as e:
        raise ValueError(
            f"Recipe {recipe_id} ('{title}'): Impossible to parse 'directions' - {e}"
        )

    title = clean_text(title)

    if not ingredients_str:  # or not instructions_str:
        raise ValueError(
            f"Recipe {recipe_id} ('{title}') has missing ingredients after parsing."
        )

    return title, ingredients_str, instructions_str
