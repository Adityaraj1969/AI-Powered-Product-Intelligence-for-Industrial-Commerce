"""
PartForge Delivery Exporter Engine.

Supports dual export formats:
  1. Full 252-Column Master Delivery Standard (Official Unilog Submission Format)
  2. Compact / Polished Commerce Feed (Clean, Trimmed — drops 100% empty columns for easy spreadsheet viewing)
"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple

from src.models import EnrichedProductRecord
from src.config import DELIVERY_COLUMNS


class DeliveryExporter:
    """Exports enriched catalog records to CSV and Excel."""

    def get_full_dataframe(self, records: List[EnrichedProductRecord]) -> pd.DataFrame:
        """Returns the full 252-column DataFrame."""
        data = [record.to_delivery_row() for record in records]
        return pd.DataFrame(data, columns=DELIVERY_COLUMNS)

    def get_compact_dataframe(self, records: List[EnrichedProductRecord]) -> pd.DataFrame:
        """
        Returns a compact DataFrame that trims out all 100% empty columns
        across the entire dataset, creating a clean, polished, readable spreadsheet.
        """
        df_full = self.get_full_dataframe(records)
        
        # Keep columns that have at least one non-empty value
        non_empty_cols = []
        for col in df_full.columns:
            series = df_full[col].fillna("").astype(str).str.strip()
            if not (series == "").all():
                non_empty_cols.append(col)
                
        return df_full[non_empty_cols]

    def export_to_csv(self, records: List[EnrichedProductRecord], output_path: Path, compact: bool = False):
        """Exports records to CSV file."""
        if compact:
            df = self.get_compact_dataframe(records)
        else:
            df = self.get_full_dataframe(records)
            
        df.to_csv(output_path, index=False)
        print(f"Exported {len(records)} records ({len(df.columns)} columns) to CSV at {output_path}")

    def export_to_excel(self, records: List[EnrichedProductRecord], output_path: Path, compact: bool = False):
        """Exports records to styled Excel file."""
        df_full = self.get_full_dataframe(records)
        df_compact = self.get_compact_dataframe(records)
        
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df_compact.to_excel(writer, index=False, sheet_name="Clean Compact Feed")
            df_full.to_excel(writer, index=False, sheet_name="252-Col Master Standard")
            
        print(f"Exported {len(records)} records to Excel at {output_path}")


if __name__ == "__main__":
    from src.models import RawProductInput
    from src.ingestion.pipeline import enrich_single_item

    raw = RawProductInput(
        mfg_part_num="DCB518ASTS06G",
        part_desc="DCB518ASTS06G Diablo 1/2\"x18\" - Sanding Belt 6pc",
        e1_brand="-- Unbranded --",
        part_manuf="Freud Inc (2435)"
    )
    rec = enrich_single_item(raw)
    
    exporter = DeliveryExporter()
    df_c = exporter.get_compact_dataframe([rec])
    df_f = exporter.get_full_dataframe([rec])
    print(f"Full columns:    {len(df_f.columns)}")
    print(f"Compact columns: {len(df_c.columns)}")
    print("Columns kept in compact feed:", list(df_c.columns))
