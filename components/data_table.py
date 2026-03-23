"""
Interactive Data Table Component.

Renders a sortable, filtered data table with shortage highlighting
and CSV/report export capabilities.
"""

import streamlit as st
import pandas as pd


# Display-friendly column mapping
DISPLAY_COLUMNS = {
    "var.orno": "Order Number",
    "addr.line1": "Company",
    "bom.item1": "Item Code",
    "bom.dsca1": "Description",
    "bom.qty1": "BOM Qty",
    "on.hand1": "On-Hand",
    "shortage_amt": "Shortage",
    "fulfillment_pct": "Fulfillment %",
}


def render_data_table(df: pd.DataFrame):
    """Render an interactive data table with export buttons.

    Args:
        df: Filtered DataFrame with shortage columns.
    """
    if df.empty:
        st.info("No data matches the current filters.")
        return

    # Prepare display DataFrame
    display_cols = [c for c in DISPLAY_COLUMNS if c in df.columns]
    display_df = df[display_cols].copy()
    display_df.columns = [DISPLAY_COLUMNS[c] for c in display_cols]

    # ── Header row ──
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.html(
            f"<p style='color:#8899aa; font-size:0.8rem; margin:0;'>"
            f"Showing <b style='color:#fff;'>{len(display_df):,}</b> items</p>"
        )
    with header_col2:
        csv_data = _convert_to_csv(display_df)
        st.download_button(
            label="📥 Export to CSV",
            data=csv_data,
            file_name="inventory_filtered_export.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── Styled dataframe ──
    st.dataframe(
        display_df,
        width="stretch",
        height=min(600, len(display_df) * 38 + 50),
        column_config={
            "BOM Qty": st.column_config.NumberColumn(format="%,.0f"),
            "On-Hand": st.column_config.NumberColumn(format="%,.0f"),
            "Shortage": st.column_config.NumberColumn(format="%,.0f"),
            "Fulfillment %": st.column_config.ProgressColumn(
                min_value=0,
                max_value=100,
                format="%.1f%%",
            ),
        },
        hide_index=True,
    )


def generate_shortage_report(df: pd.DataFrame):
    """Generate and display a downloadable shortage-only report.

    Args:
        df: Full processed DataFrame.
    """
    shortage_df = df[df["is_shortage"]].copy()

    if shortage_df.empty:
        st.toast("✅ No shortages found — nothing to report!", icon="🎉")
        return

    # Build report DataFrame
    report_cols = [
        "var.orno", "addr.line1", "bom.item1", "bom.dsca1",
        "bom.qty1", "on.hand1", "shortage_amt",
    ]
    report_cols = [c for c in report_cols if c in shortage_df.columns]
    report_df = shortage_df[report_cols].sort_values("shortage_amt", ascending=False)

    # Summary stats
    total_shortage_items = len(report_df)
    total_shortage_qty = report_df["shortage_amt"].sum()
    affected_orders = report_df["var.orno"].nunique()

    # Display summary
    st.html(
        f"""
        <div style="
            background: linear-gradient(135deg, #2a1a1a, #1a1f2e);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            border-left: 4px solid #ff5252;
            margin-bottom: 1rem;
        ">
            <h4 style="color:#ff5252; margin:0 0 0.5rem;">📊 Shortage Report Summary</h4>
            <div style="display:flex; gap:2rem; color:#c0c8d4; font-size:0.85rem;">
                <span><b>{total_shortage_items}</b> items in shortage</span>
                <span><b>{total_shortage_qty:,.0f}</b> total shortage qty</span>
                <span><b>{affected_orders}</b> affected orders</span>
            </div>
        </div>
        """
    )

    # Download button
    csv = _convert_to_csv(report_df)
    st.download_button(
        label="📥 Download Shortage Report (CSV)",
        data=csv,
        file_name="shortage_report.csv",
        mime="text/csv",
        use_container_width=True,
        key="shortage_report_download",
    )

    # Show the report table
    st.dataframe(
        report_df,
        width="stretch",
        height=min(400, len(report_df) * 38 + 50),
        hide_index=True,
    )


def _convert_to_csv(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")
