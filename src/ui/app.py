"""
PartForge Streamlit HITL Dashboard — Interactive Product Intelligence Triage.

Run: streamlit run src/ui/app.py
"""

import sys
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.config import (
    CONFIDENCE_AMBER,
    CONFIDENCE_AUTO_PASS,
    DELIVERY_COLUMNS,
    INPUT_CSV,
)
from src.models import (
    ConfidenceLevel,
    EnrichedProductRecord,
    RawProductInput,
    ValidationStatus,
)


# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="PartForge — Product Intelligence Workbench",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Session State ─────────────────────────────────────────────────────────────

if "records" not in st.session_state:
    st.session_state.records = []
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = 0


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/maintenance.png", width=64)
    st.title("PartForge")
    st.caption("AI-Powered Product Intelligence Pipeline")
    st.markdown("**$0.00 API Cost** · Free Tier & Local-First")
    st.divider()

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Input CSV",
        type=["csv", "xlsx"],
        help="Upload the 6-column input dataset (Mfg_Part_Num, Part_Desc, ...)",
    )

    st.divider()

    # Filter controls
    st.subheader("🎯 Triage Filters")
    show_green = st.checkbox("🟢 Auto-Passed (≥0.95)", value=True)
    show_amber = st.checkbox("🟡 Quick Triage (0.80-0.94)", value=True)
    show_red = st.checkbox("🔴 Manual Review (<0.80)", value=True)

    st.divider()
    st.metric("Total Records", len(st.session_state.records))

    # Count by confidence level
    green_count = sum(
        1 for r in st.session_state.records
        if r.confidence_level == ConfidenceLevel.GREEN
    )
    amber_count = sum(
        1 for r in st.session_state.records
        if r.confidence_level == ConfidenceLevel.AMBER
    )
    red_count = sum(
        1 for r in st.session_state.records
        if r.confidence_level == ConfidenceLevel.RED
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢", green_count)
    col2.metric("🟡", amber_count)
    col3.metric("🔴", red_count)


# ── Data Loading ──────────────────────────────────────────────────────────────

def load_and_process(file_or_path) -> list:
    """Load input CSV and create initial UPIR records."""
    try:
        if hasattr(file_or_path, "read"):
            df = pd.read_csv(file_or_path)
        else:
            df = pd.read_csv(file_or_path)
    except Exception:
        df = pd.read_excel(file_or_path)

    records = []
    for _, row in df.iterrows():
        raw = RawProductInput(
            mfg_part_num=str(row.get("Mfg_Part_Num", "")).strip(),
            part_desc=str(row.get("Part_Desc", "")).strip(),
            e1_brand=str(row.get("E1_Brand", "")) if pd.notna(row.get("E1_Brand")) else None,
            unilog_brand=str(row.get("Unilog_Brand", "")) if pd.notna(row.get("Unilog_Brand")) else None,
            dib_brand=str(row.get("DIB_Brand", "")) if pd.notna(row.get("DIB_Brand")) else None,
            part_manuf=str(row.get("Part_Manuf", "")) if pd.notna(row.get("Part_Manuf")) else None,
        )
        record = EnrichedProductRecord(
            sku=raw.mfg_part_num,
            raw_input=raw,
        )
        records.append(record)
    return records


# ── Main Layout ───────────────────────────────────────────────────────────────

st.title("🔧 PartForge — Product Intelligence Workbench")
st.markdown(
    "**AI-Powered Product Intelligence Pipeline** · "
    "UniHack 2026 · Unilog × Hack2Skill · "
    "**100% Free Tier & Local-First ($0.00 API Cost)**"
)

# Load data
if uploaded_file is not None:
    if not st.session_state.records:
        with st.spinner("Loading and processing input data..."):
            st.session_state.records = load_and_process(uploaded_file)
        st.success(f"Loaded {len(st.session_state.records)} records!")
elif INPUT_CSV.exists() and not st.session_state.records:
    if st.button("📂 Load Default Dataset (1,000 Items)", type="primary"):
        with st.spinner("Loading default dataset..."):
            st.session_state.records = load_and_process(INPUT_CSV)
        st.rerun()

# Display records
records = st.session_state.records

if not records:
    st.info("👆 Upload a CSV file or click 'Load Default Dataset' to begin.")
    st.stop()

# ── KPI Dashboard ─────────────────────────────────────────────────────────────

st.divider()
kpi_cols = st.columns(5)
kpi_cols[0].metric("📦 Total Items", len(records))
kpi_cols[1].metric("🟢 Auto-Pass", green_count)
kpi_cols[2].metric("🟡 Triage", amber_count)
kpi_cols[3].metric("🔴 Review", red_count)

# Enrichment rate
enriched = sum(1 for r in records if r.validation_status != ValidationStatus.PENDING)
kpi_cols[4].metric("✅ Enriched", f"{enriched}/{len(records)}")


# ── Record Browser ────────────────────────────────────────────────────────────

st.divider()
st.subheader("📋 Record Browser")

# Build display dataframe
display_data = []
for i, r in enumerate(records):
    confidence_emoji = {
        ConfidenceLevel.GREEN: "🟢",
        ConfidenceLevel.AMBER: "🟡",
        ConfidenceLevel.RED: "🔴",
    }.get(r.confidence_level, "⚪")

    display_data.append({
        "#": i + 1,
        "Status": confidence_emoji,
        "MPN": r.raw_input.mfg_part_num,
        "Description": r.raw_input.part_desc[:60] + "..." if len(r.raw_input.part_desc) > 60 else r.raw_input.part_desc,
        "Brand": r.brand_profile.brand_name or r.raw_input.e1_brand or "—",
        "Manufacturer": r.brand_profile.manufacturer_name or r.raw_input.part_manuf or "—",
        "Confidence": f"{r.overall_confidence:.0%}",
        "Errors": len(r.validation_errors),
    })

display_df = pd.DataFrame(display_data)

# Apply filters
if not show_green:
    display_df = display_df[display_df["Status"] != "🟢"]
if not show_amber:
    display_df = display_df[display_df["Status"] != "🟡"]
if not show_red:
    display_df = display_df[display_df["Status"] != "🔴"]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=300,
)

# ── Detail Panel ──────────────────────────────────────────────────────────────

st.divider()
st.subheader("🔍 Record Detail Inspector")

selected_idx = st.number_input(
    "Select Record #",
    min_value=1,
    max_value=len(records),
    value=1,
    step=1,
) - 1

if 0 <= selected_idx < len(records):
    record = records[selected_idx]

    # Two-column detail layout
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("### 📥 Raw Input")
        st.json({
            "Mfg_Part_Num": record.raw_input.mfg_part_num,
            "Part_Desc": record.raw_input.part_desc,
            "E1_Brand": record.raw_input.e1_brand,
            "Unilog_Brand": record.raw_input.unilog_brand,
            "DIB_Brand": record.raw_input.dib_brand,
            "Part_Manuf": record.raw_input.part_manuf,
        })

        st.markdown("### 🏢 Brand Profile")
        st.json({
            "MANUFACTURER_NAME": record.brand_profile.manufacturer_name,
            "BRAND_NAME": record.brand_profile.brand_name,
            "TRADE_NAME": record.brand_profile.trade_name,
            "Confidence": record.brand_profile.confidence,
        })

        st.markdown("### 📂 Taxonomy")
        st.json({
            "Classpath": record.taxonomy.classpath,
            "UNSPSC": record.taxonomy.unspsc_code,
            "Confidence": record.taxonomy.confidence,
        })

    with right_col:
        st.markdown("### 📝 Multi-Channel Descriptions")

        # Invoice
        inv = record.descriptions.invoice_desc
        inv_len = len(inv) if inv else 0
        inv_ok = inv_len <= 40 and (inv == inv.upper() if inv else True)
        st.text_input(
            f"Invoice Desc ({inv_len}/40 chars) {'✅' if inv_ok else '❌'}",
            value=inv,
            key=f"inv_{selected_idx}",
        )

        # Mobile
        mob = record.descriptions.mobile_desc
        mob_len = len(mob) if mob else 0
        mob_ok = 60 <= mob_len <= 80
        st.text_input(
            f"Mobile Desc ({mob_len} chars, target 60-80) {'✅' if mob_ok else '⚠️'}",
            value=mob,
            key=f"mob_{selected_idx}",
        )

        # Short/Title
        short = record.descriptions.short_desc
        short_len = len(short) if short else 0
        st.text_input(
            f"Short Desc / Title ({short_len}/150 chars)",
            value=short,
            key=f"short_{selected_idx}",
        )

        # Long
        st.text_area(
            "Long Description",
            value=record.descriptions.long_desc,
            height=100,
            key=f"long_{selected_idx}",
        )

        st.markdown("### 📊 Attributes")
        if record.attributes:
            attr_data = [
                {
                    "Label": a.normalized_label or a.attribute_label,
                    "Value": a.normalized_value or a.raw_value,
                    "UOM": a.uom or "",
                    "Conf": f"{a.confidence:.0%}",
                }
                for a in record.attributes
            ]
            st.dataframe(pd.DataFrame(attr_data), use_container_width=True, hide_index=True)
        else:
            st.info("No attributes extracted yet.")

    # Validation errors
    if record.validation_errors:
        st.markdown("### ⚠️ Validation Errors")
        err_data = [
            {
                "Tier": e.tier,
                "Code": e.error_code,
                "Severity": e.severity,
                "Field": e.field_name,
                "Message": e.message,
                "Auto-Repaired": "✅" if e.auto_repair_applied else "❌",
            }
            for e in record.validation_errors
        ]
        st.dataframe(pd.DataFrame(err_data), use_container_width=True, hide_index=True)

    # Action buttons
    st.divider()
    btn_cols = st.columns(4)
    with btn_cols[0]:
        if st.button("✅ Approve", type="primary", key=f"approve_{selected_idx}"):
            record.validation_status = ValidationStatus.PASSED
            st.success("Record approved!")
    with btn_cols[1]:
        if st.button("🔄 Re-Enrich", key=f"reenrich_{selected_idx}"):
            st.info("Re-enrichment would be triggered here.")
    with btn_cols[2]:
        if st.button("❌ Reject", key=f"reject_{selected_idx}"):
            record.validation_status = ValidationStatus.FAILED
            st.warning("Record rejected.")
    with btn_cols[3]:
        if st.button("📥 Export 252-Col CSV", key=f"export_{selected_idx}"):
            row = record.to_delivery_row()
            export_df = pd.DataFrame([row], columns=DELIVERY_COLUMNS)
            csv_data = export_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                data=csv_data,
                file_name=f"PartForge_{record.raw_input.mfg_part_num}.csv",
                mime="text/csv",
            )

# ── Footer ────────────────────────────────────────────────────────────────────

st.divider()
st.caption(
    "PartForge v1.0 · UniHack 2026 · Unilog × Hack2Skill · "
    "100% Free Tier & Local-First Architecture ($0.00 API Cost) · "
    "Built with Streamlit"
)
