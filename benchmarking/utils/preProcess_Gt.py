import pandas as pd
import os
import glob

JC_QUEST = {
    "birth_country": "country of birth", "birth_region": "region of birth",
    "residence_country": "country of residence", "residence_region": "region of residence",
    "meals_per_day": "number of main meals", "sport": "sport practiced",
    "sport_frequency": "weekly frequency", "sport_level": "level",
    "dietary_restrictions": "religious or ethical restrictions",
    "allergies": "known food allergies", "medications": "drugs in use",
    "conditions": "diagnosed pathologies", "meat_frequency": "meat",
    "fish_frequency": "fish", "dairy_frequency": "dairy products",
    "eggs_frequency": "eggs", "legumes_frequency": "legumes",
    "fruits_veggies_frequency": "fruit and vegetables",
    "sweets_frequency": "industrial sweetssnacks", "coffee_frequency": "coffeetea",
    "alcohol_frequency": "alcohol", "motivation_level": "motivation for change scale 1 to 5"
}

FCQ_QUEST = {
    "I choose foods because they keep me healthy": "i choose foods because they keep me healthy",
    "I choose foods that help me control my weight": "i choose foods that help me control my weight",
    "I choose foods that are convenient to prepare": "i choose foods that are convenient to prepare",
    "I choose foods for their taste": "i choose foods for their taste",
    "I choose foods for ecological/sustainability reasons": "i choose foods for ecologicalsustainability reasons",
    "I choose foods for ethical or religious reasons": "i choose foods for ethical or religious reasons",
    "I choose foods that are familiar/traditional": "i choose foods that are familiartraditional",
    "I choose foods based on price": "i choose foods based on price",
    "I choose foods that improve my mood": "i choose foods that improve my mood"
}



# create a dictionary by reading a model files
def build_category_map(model_folder):
    cat_map = {}
    model_files = glob.glob(os.path.join(model_folder, "*.csv"))
    for f in model_files:
        try:
            df = pd.read_csv(f, dtype=str)
            if 'questions' in df.columns and 'category' in df.columns:
                for _, row in df.iterrows():
                    q = row['questions'].strip().lower()
                    cat = row['category'].strip()
                    cat_map[q] = cat
        except: continue
    return cat_map

def transform_gt_to_model_format(input_path, output_path, q_type, category_map):
    if not os.path.exists(input_path): return

    df_raw = pd.read_csv(input_path, dtype=str).fillna("")
    new_rows = []

    if q_type == "FCQ":
        score_map = {"Not important at all": "1", "Slightly important": "2", 
                 "Very important": "3", "Extremely important": "4"}
        
        for _, row in df_raw.iterrows():
            parts = str(row["questions"]).split("|")
            for part in parts:
                if ":" in part:
                    q_raw, val_raw = part.rsplit(":", 1)
                    q_clean = q_raw.strip()
                    
                    
                    q_model_name = FCQ_QUEST.get(q_clean, q_clean.lower())
                    
                    # cerca la CATEGORIA usando il nome del modello
                    category = category_map.get(q_model_name.lower(), "General")
                    score = score_map.get(val_raw.strip(), val_raw.strip())
                    
                    new_rows.append({
                        "user_id": row.get("user_id", "unknown"),
                        "category": category,
                        "questions": q_model_name,
                        "score": score
                    })

    elif q_type == "JC":
        df_melted = df_raw.melt(id_vars=["user_id"], var_name="tech_name", value_name="answer")
        for _, row in df_melted.iterrows():
            q_model_name = JC_QUEST.get(row["tech_name"], row["tech_name"])
            
            # Cerca la CATEGORIA
            category = category_map.get(q_model_name.lower().strip(), "Other")
            
            new_rows.append({
                "user_id": row["user_id"],
                "category": category,
                "questions": q_model_name,
                "answer": row["answer"],
                "answer_other": ""
            })

    pd.DataFrame(new_rows).to_csv(output_path, index=False)
    print(f"File {q_type} creato correttamente in: {output_path}")

if __name__ == "__main__":
    MODEL_FOLDER = "data/prolific/structured_context_output"
    
    print("Estrazione categorie dai file modello...")
    global_category_map = build_category_map(MODEL_FOLDER)
    
    transform_gt_to_model_format("data/prolific/structured_context/structured_context_jc.csv", "data/prolific/structured_context/JC_gt_structured.csv", "JC", global_category_map)
    transform_gt_to_model_format("data/prolific/structured_context/fcq_cleaned.csv", "data/prolific/structured_context/FCQ_gt_structured.csv", "FCQ", global_category_map)