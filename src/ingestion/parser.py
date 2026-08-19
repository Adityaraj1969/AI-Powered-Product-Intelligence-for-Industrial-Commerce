import pandas as pd
from pathlib import Path
from typing import List
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models import RawProductInput

def load_input_csv(path: Path) -> List[RawProductInput]:
    df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
    df = df.replace({np.nan: None})
    
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            
    records = []
    for _, row in df.iterrows():
        records.append(RawProductInput(
            mfg_part_num=str(row.get('Mfg_Part_Num', '')),
            part_desc=str(row.get('Part_Desc', '')),
            e1_brand=row.get('E1_Brand'),
            unilog_brand=row.get('Unilog_Brand'),
            dib_brand=row.get('DIB_Brand'),
            part_manuf=row.get('Part_Manuf')
        ))
    return records

def load_delivery_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding='utf-8')
    return df

if __name__ == "__main__":
    test_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Unihack_ Sample Dataset - Input.csv')))
    if test_path.exists():
        records = load_input_csv(test_path)
        for r in records[:3]:
            print(r)
    else:
        print(f"Test path {test_path} does not exist.")
