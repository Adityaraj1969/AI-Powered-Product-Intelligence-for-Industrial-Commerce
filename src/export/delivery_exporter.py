import pandas as pd
from pathlib import Path
from typing import List

from src.models import EnrichedProductRecord
from src.config import DELIVERY_COLUMNS

class DeliveryExporter:
    def export_to_csv(self, records: List[EnrichedProductRecord], output_path: Path):
        data = [record.to_delivery_row() for record in records]
        df = pd.DataFrame(data, columns=DELIVERY_COLUMNS)
        df.to_csv(output_path, index=False)
        print(f"Exported {len(records)} records to CSV at {output_path}")

    def export_to_excel(self, records: List[EnrichedProductRecord], output_path: Path):
        data = [record.to_delivery_row() for record in records]
        df = pd.DataFrame(data, columns=DELIVERY_COLUMNS)
        
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Delivery Format")
        print(f"Exported {len(records)} records to Excel at {output_path}")

if __name__ == "__main__":
    from src.models import RawProductInput
    
    records = [
        EnrichedProductRecord(sku="SKU-1", raw_input=RawProductInput(mfg_part_num="111", part_desc="Desc 1")),
        EnrichedProductRecord(sku="SKU-2", raw_input=RawProductInput(mfg_part_num="222", part_desc="Desc 2")),
    ]
    
    exporter = DeliveryExporter()
    test_csv = Path("test_delivery.csv")
    exporter.export_to_csv(records, test_csv)
    test_excel = Path("test_delivery.xlsx")
    exporter.export_to_excel(records, test_excel)
    
    # Clean up
    if test_csv.exists(): test_csv.unlink()
    if test_excel.exists(): test_excel.unlink()
