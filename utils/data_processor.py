"""
Data Processing Module for Inventory Dashboard.

Handles Excel file loading, column validation, shortage calculations,
and filter application.
"""

import pandas as pd
import numpy as np
import streamlit as st

# Required columns in the uploaded Excel file
REQUIRED_COLUMNS = [
    "var.orno",    # Order Number
    "addr.line1",  # Company Name
    "bom.item1",   # Item Code
    "bom.dsca1",   # Item Description
    "bom.qty1",    # Required BOM Quantity
    "on.hand1",    # Current Inventory On-Hand
]

COLUMN_LABELS = {
    "var.orno": "Order Number",
    "addr.line1": "Company Name",
    "bom.item1": "Item Code",
    "bom.dsca1": "Item Description",
    "bom.qty1": "BOM Quantity",
    "on.hand1": "On-Hand",
    "shortage_amt": "Shortage Amount",
    "is_shortage": "Has Shortage",
    "fulfillment_pct": "Fulfillment %",
}


@st.cache_data(show_spinner=False)
def load_excel(uploaded_file) -> pd.DataFrame:
    """Load an Excel file and return a DataFrame.

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        pd.DataFrame with original data.

    Raises:
        ValueError: If the file is empty or cannot be parsed.
    """
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {e}")

    if df.empty:
        raise ValueError("The uploaded file contains no data.")

    return df


def validate_columns(df: pd.DataFrame) -> list[str]:
    """Check that all required columns are present.

    Returns a list of missing column names (empty list = all valid).
    """
    # Normalize column names: strip whitespace and lowercase
    df.columns = df.columns.str.strip().str.lower()
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing


def compute_shortage(df: pd.DataFrame) -> pd.DataFrame:
    """Add shortage-related calculated columns.

    New columns:
        - shortage_amt: bom.qty1 - on.hand1 (negative = surplus)
        - is_shortage: True when on.hand1 < bom.qty1
        - fulfillment_pct: min(on.hand1 / bom.qty1, 1.0) * 100
    """
    df = df.copy()

    # Always normalize columns (cached objects may lose in-place changes)
    df.columns = df.columns.str.strip().str.lower()

    # Coerce numeric columns
    df["bom.qty1"] = pd.to_numeric(df["bom.qty1"], errors="coerce").fillna(0)
    df["on.hand1"] = pd.to_numeric(df["on.hand1"], errors="coerce").fillna(0)

    df["shortage_amt"] = df["bom.qty1"] - df["on.hand1"]
    df["is_shortage"] = df["on.hand1"] < df["bom.qty1"]

    # Fulfillment percentage (cap at 100%)
    with np.errstate(divide="ignore", invalid="ignore"):
        pct = np.where(
            df["bom.qty1"] > 0,
            np.minimum(df["on.hand1"] / df["bom.qty1"], 1.0) * 100,
            100.0,  # If BOM qty is 0, consider it fulfilled
        )
    df["fulfillment_pct"] = np.round(pct, 1)

    return df


def apply_filters(
    df: pd.DataFrame,
    selected_orders: list[str] | None = None,
    selected_items: list[str] | None = None,
    shortage_only: bool = False,
    exclude_prefixes: list[str] | None = None,
    search_text: str = "",
) -> pd.DataFrame:
    """Apply user-selected filters to the DataFrame.

    Args:
        df: DataFrame with shortage columns already computed.
        selected_orders: List of order numbers to include (None = all).
        selected_items: List of item codes to include (None = all).
        shortage_only: If True, only show rows where is_shortage is True.
        exclude_prefixes: Item code prefixes to exclude (e.g. ["DRFB", "DRFI"]).
        search_text: Free-text search across item descriptions and company names.

    Returns:
        Filtered DataFrame.
    """
    filtered = df.copy()

    # Order filter
    if selected_orders:
        filtered = filtered[filtered["var.orno"].astype(str).isin(selected_orders)]

    # Item filter
    if selected_items:
        filtered = filtered[filtered["bom.item1"].astype(str).isin(selected_items)]

    # Shortage toggle
    if shortage_only:
        filtered = filtered[filtered["is_shortage"]]

    # Exclude item prefixes
    if exclude_prefixes:
        mask = filtered["bom.item1"].astype(str).str.startswith(tuple(exclude_prefixes))
        filtered = filtered[~mask]

    # Global search
    if search_text.strip():
        search_lower = search_text.strip().lower()
        mask = (
            filtered["bom.dsca1"].astype(str).str.lower().str.contains(search_lower, na=False)
            | filtered["addr.line1"].astype(str).str.lower().str.contains(search_lower, na=False)
        )
        filtered = filtered[mask]

    return filtered.reset_index(drop=True)


def get_kpi_metrics(df: pd.DataFrame) -> dict:
    """Compute summary KPI metrics from the processed DataFrame.

    On-hand quantity is a per-item inventory snapshot (not additive
    across orders), so we take one value per item before summing.

    Returns:
        Dictionary with keys:
            - total_items: number of rows
            - total_orders: unique order count
            - items_in_shortage: rows where is_shortage is True
            - fulfillment_pct: overall order fulfillment percentage
            - total_bom_qty: sum of all BOM quantities
            - total_on_hand: sum of deduplicated per-item on-hand
            - total_shortage: sum of positive shortage amounts
    """
    total_items = len(df)
    total_orders = df["var.orno"].nunique()
    items_in_shortage = int(df["is_shortage"].sum())

    total_bom = df["bom.qty1"].sum()

    # On-hand is per-item inventory; take one value per item (max)
    per_item_on_hand = df.groupby("bom.item1")["on.hand1"].max()
    total_on_hand = per_item_on_hand.sum()

    total_shortage = df.loc[df["is_shortage"], "shortage_amt"].sum()

    fulfillment = (
        min(total_on_hand / total_bom, 1.0) * 100 if total_bom > 0 else 100.0
    )

    return {
        "total_items": total_items,
        "total_orders": total_orders,
        "items_in_shortage": items_in_shortage,
        "fulfillment_pct": round(fulfillment, 1),
        "total_bom_qty": total_bom,
        "total_on_hand": total_on_hand,
        "total_shortage": total_shortage,
    }
