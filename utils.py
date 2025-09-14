import pandas as pd, json
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "gourmet.csv"

def load_df():
    if DATA.exists():
        df = pd.read_csv(DATA, dtype=str).fillna("")
        return df
    return pd.DataFrame(columns=["id","prefecture_ja","prefecture_en","dish_ja","dish_en","category_en","description_en","image_path","source","region"])
