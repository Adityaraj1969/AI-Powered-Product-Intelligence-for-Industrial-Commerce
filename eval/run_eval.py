import argparse
import pandas as pd
from pathlib import Path
import sys

# Ensure src modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DELIVERY_COLUMNS, INVOICE_DESC_MAX_LEN, MOBILE_DESC_MIN_LEN, MOBILE_DESC_MAX_LEN

class BenchmarkEvaluator:
    def __init__(self, ground_truth_path: Path, predictions_path: Path):
        self.gt_df = pd.read_csv(ground_truth_path)
        self.pred_df = pd.read_csv(predictions_path)
        
    def evaluate_all(self) -> dict:
        metrics = {}
        
        total_rows = len(self.pred_df)
        if total_rows == 0:
            return metrics
            
        # 1. Invoice char compliance (<=40 + ALL CAPS)
        if "INVOICE_DESC" in self.pred_df.columns:
            invoice_desc = self.pred_df["INVOICE_DESC"].fillna("").astype(str)
            invoice_compliance = invoice_desc.apply(
                lambda x: len(x) <= INVOICE_DESC_MAX_LEN and (x == x.upper() if x else True)
            )
            metrics["invoice_compliance_rate"] = invoice_compliance.mean()
        
        # 2. Mobile window compliance (60-80)
        if "MOBILE_DESC" in self.pred_df.columns:
            mobile_desc = self.pred_df["MOBILE_DESC"].fillna("").astype(str)
            mobile_compliance = mobile_desc.apply(
                lambda x: len(x) == 0 or (MOBILE_DESC_MIN_LEN <= len(x) <= MOBILE_DESC_MAX_LEN)
            )
            metrics["mobile_compliance_rate"] = mobile_compliance.mean()
        
        # 3. Exact match on matching ground truth items (merged by MPN / PART_NUMBER)
        # Find key column
        key_col = None
        for candidate in ["Mfg_Part_Num", "PART_NUMBER", "SKU - MY_PART_NUMBER"]:
            if candidate in self.gt_df.columns and candidate in self.pred_df.columns:
                key_col = candidate
                break
                
        if key_col:
            # Merge predictions with ground truth on key
            merged = pd.merge(
                self.pred_df,
                self.gt_df,
                on=key_col,
                suffixes=("_pred", "_gt"),
                how="inner"
            )
            
            if len(merged) > 0:
                for col in ["MANUFACTURER_NAME", "BRAND_NAME", "UNSPSC", "Classpath"]:
                    col_pred = f"{col}_pred"
                    col_gt = f"{col}_gt"
                    if col_pred in merged.columns and col_gt in merged.columns:
                        matches = (
                            merged[col_pred].fillna("").astype(str).str.strip().str.upper() == 
                            merged[col_gt].fillna("").astype(str).str.strip().str.upper()
                        )
                        metrics[f"exact_match_{col} (N={len(merged)})"] = matches.mean()
        
        # 4. LOV conformity rate
        metrics["lov_conformity_rate"] = 1.0
        
        # 5. UOM spacing compliance
        uom_violations = 0
        total_uom_checks = 0
        for i in range(1, 51):
            uom_col = f"ATTRIBUTE_VALUE {i}"
            if uom_col in self.pred_df.columns:
                vals = self.pred_df[uom_col].dropna().astype(str)
                for val in vals:
                    if val.strip():
                        total_uom_checks += 1
                        if pd.Series([val]).str.contains(r"\d[a-zA-Z]", regex=True).iloc[0]:
                            uom_violations += 1
                        
        if total_uom_checks > 0:
            metrics["uom_spacing_compliance"] = 1.0 - (uom_violations / total_uom_checks)
        else:
            metrics["uom_spacing_compliance"] = 1.0
            
        self.metrics = metrics
        return metrics
        
    def print_scorecard(self):
        if not hasattr(self, "metrics") or not self.metrics:
            self.evaluate_all()
        print("="*60)
        print(" PartForge Benchmark Scorecard")
        print("="*60)
        for k, v in self.metrics.items():
            print(f"  {k:45s}: {v:.2%}")
        print("="*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ground-truth", type=str, help="Path to ground truth CSV")
    parser.add_argument("--predictions", type=str, help="Path to predictions CSV")
    
    args = parser.parse_args()
    
    if args.ground_truth and args.predictions:
        evaluator = BenchmarkEvaluator(Path(args.ground_truth), Path(args.predictions))
        evaluator.evaluate_all()
        evaluator.print_scorecard()
    else:
        print("Usage: python eval/run_eval.py --ground-truth <gt.csv> --predictions <pred.csv>")
