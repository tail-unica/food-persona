import zipfile

import polars as pl


# Open a zip file and load the first parquet file found inside
def load_recipes_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, "r") as z:
        parquet_files = [f for f in z.namelist() if f.endswith(".parquet")]
        if not parquet_files:
            raise FileNotFoundError("No .parquet file found inside the ZIP.")
        parquet_file = parquet_files[0]
        print(f"Parquet file found: {parquet_file}")
        df = pl.read_parquet(z.open(parquet_file))
    print(f"Loaded {df.shape[0]} recipes from Parquet.")

    return df
