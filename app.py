"""
Inventory Requirements Dashboard — Main Application.

A Streamlit dashboard for visualizing BOM requirements vs. inventory availability.
"""

import streamlit as st
import warnings

warnings.filterwarnings("ignore")

from utils.data_processor import (
    load_excel,
    validate_columns,
    compute_shortage,
    apply_filters,
    get_kpi_metrics,
)
from components.filters import render_sidebar_filters, handle_clear_filters
from components.kpi_cards import render_kpi_cards
from components.charts import (
    render_need_vs_have_chart,
    render_shortage_heatmap,
    render_quantity_treemap,
)
from components.data_table import render_data_table, generate_shortage_report


# ── Page Config ──
st.set_page_config(
    page_title="Inventory Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_custom_css():
    """Inject custom CSS for premium dark dashboard styling."""
    st.html(
        """
        <style>
            /* ── Global ── */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif !important;
            }

            .stApp {
                background: linear-gradient(180deg, #0e1117 0%, #0a0d12 100%);
            }

            /* ── Sidebar ── */
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f1318 0%, #0a0d11 100%) !important;
                border-right: 1px solid #1e2738 !important;
            }

            /* ── Sidebar floating cards (bordered containers) ── */
            section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
                background: linear-gradient(145deg, #161b28, #131720) !important;
                border: 1px solid #252d3d !important;
                border-radius: 16px !important;
                box-shadow:
                    0 4px 16px rgba(0, 0, 0, 0.35),
                    0 1px 3px rgba(0, 0, 0, 0.25),
                    inset 0 1px 0 rgba(255, 255, 255, 0.03) !important;
                margin-bottom: 0.55rem !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                overflow: hidden !important;
            }

            section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
                border-color: #354060 !important;
                box-shadow:
                    0 8px 28px rgba(0, 0, 0, 0.45),
                    0 2px 6px rgba(0, 0, 0, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
                transform: translateY(-2px) !important;
            }

            section[data-testid="stSidebar"] .stMultiSelect > div {
                background: #1a1f2e !important;
                border: 1px solid #2a3040 !important;
                border-radius: 14px !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            section[data-testid="stSidebar"] .stMultiSelect > div:hover {
                border-color: #7eb8da !important;
                box-shadow: 0 0 12px rgba(126, 184, 218, 0.15) !important;
            }

            section[data-testid="stSidebar"] .stMultiSelect > div:focus-within {
                border-color: #c4a8e0 !important;
                box-shadow: 0 0 16px rgba(196, 168, 224, 0.2) !important;
            }

            section[data-testid="stSidebar"] .stTextInput > div > div {
                background: #1a1f2e !important;
                border: 1px solid #2a3040 !important;
                border-radius: 14px !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            section[data-testid="stSidebar"] .stTextInput > div > div:hover {
                border-color: #c4a8e0 !important;
                box-shadow: 0 0 12px rgba(196, 168, 224, 0.15) !important;
            }

            section[data-testid="stSidebar"] .stTextInput > div > div:focus-within {
                border-color: #c4a8e0 !important;
                box-shadow: 0 0 16px rgba(196, 168, 224, 0.25) !important;
            }

            /* ── Sidebar toggle switches ── */
            section[data-testid="stSidebar"] [data-testid="stToggle"] {
                padding: 0.35rem 0;
            }

            section[data-testid="stSidebar"] [data-testid="stToggle"] label p {
                font-size: 0.78rem !important;
                color: #9aa8b8 !important;
                transition: color 0.2s ease !important;
            }

            section[data-testid="stSidebar"] [data-testid="stToggle"]:hover label p {
                color: #c0c8d4 !important;
            }

            /* ── Sidebar buttons ── */
            section[data-testid="stSidebar"] .stButton button {
                background: linear-gradient(135deg, #1e2540, #1a2035) !important;
                border: 1px solid #2a3555 !important;
                border-radius: 14px !important;
                color: #c0c8d4 !important;
                font-weight: 600 !important;
                font-size: 0.8rem !important;
                padding: 0.55rem 0.8rem !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
            }

            section[data-testid="stSidebar"] .stButton button:hover {
                background: linear-gradient(135deg, #7eb8da, #c4a8e0) !important;
                color: #0e1117 !important;
                border-color: transparent !important;
                box-shadow: 0 4px 20px rgba(126, 184, 218, 0.35) !important;
                transform: translateY(-2px) !important;
            }

            section[data-testid="stSidebar"] .stButton button:active {
                transform: translateY(0px) !important;
                box-shadow: 0 1px 6px rgba(126, 184, 218, 0.2) !important;
            }

            /* ── File uploader ── */
            [data-testid="stFileUploader"] {
                background: linear-gradient(135deg, #141820, #1a1f2e) !important;
                border: 2px dashed #2a3f5f !important;
                border-radius: 16px !important;
                padding: 2rem !important;
                transition: border-color 0.3s ease;
            }

            [data-testid="stFileUploader"]:hover {
                border-color: #1e88e5 !important;
            }

            /* ── Tabs ── */
            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
                background: transparent;
            }

            .stTabs [data-baseweb="tab"] {
                background: #1a1f2e !important;
                border: 1px solid #2a3040 !important;
                border-radius: 10px 10px 0 0 !important;
                color: #8899aa !important;
                padding: 0.5rem 1.5rem !important;
                font-weight: 600 !important;
            }

            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, #1e88e5, #1565c0) !important;
                color: #ffffff !important;
                border-color: #1e88e5 !important;
            }

            /* ── Dataframe ── */
            [data-testid="stDataFrame"] {
                border-radius: 12px !important;
                overflow: hidden !important;
                border: 1px solid #2a3040 !important;
            }

            /* ── Buttons ── */
            .stDownloadButton button,
            .stButton button {
                background: linear-gradient(135deg, #1e88e5, #1565c0) !important;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                padding: 0.5rem 1rem !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 2px 10px rgba(30, 136, 229, 0.3) !important;
            }

            .stDownloadButton button:hover,
            .stButton button:hover {
                box-shadow: 0 4px 20px rgba(30, 136, 229, 0.5) !important;
                transform: translateY(-1px) !important;
            }

            /* ── Toggle ── */
            [data-testid="stToggle"] label span {
                font-weight: 500 !important;
            }

            /* ── Spinner / Toast ── */
            .stSpinner > div {
                border-top-color: #1e88e5 !important;
            }

            /* ── Section dividers ── */
            hr {
                border-color: #1e2738 !important;
                margin: 1.5rem 0 !important;
            }

            /* ── Info/Success boxes ── */
            [data-testid="stAlert"] {
                background: #1a1f2e !important;
                border-radius: 12px !important;
                border: 1px solid #2a3040 !important;
            }

            /* ── Header animation ── */
            @keyframes shimmer {
                0% { background-position: -200% center; }
                100% { background-position: 200% center; }
            }

            .dashboard-title {
                background: linear-gradient(
                    90deg,
                    #1e88e5 0%,
                    #42a5f5 25%,
                    #90caf9 50%,
                    #42a5f5 75%,
                    #1e88e5 100%
                );
                background-size: 200% auto;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: shimmer 4s linear infinite;
                font-weight: 800;
                font-size: 2rem;
                margin: 0;
            }
        </style>
        """
    )


def render_header():
    """Render the dashboard header."""
    st.html(
        """
        <div style="padding: 0.5rem 0 1rem;">
            <p class="dashboard-title">📦 Inventory Requirements Dashboard</p>
            <p style="color:#667788; font-size:0.85rem; margin:0.25rem 0 0;">
                Upload your BOM Excel file to analyze inventory coverage, identify shortages, and export reports.
            </p>
        </div>
        """
    )


def render_upload_section() -> object | None:
    """Render the file upload section.

    Returns:
        The uploaded file object, or None.
    """
    uploaded_file = st.file_uploader(
        "Upload your inventory Excel file (.xlsx)",
        type=["xlsx"],
        help="Drag and drop or click to browse. File must contain columns: "
             "var.orno, addr.line1, bom.item1, bom.dsca1, bom.qty1, on.hand1",
        key="file_uploader",
    )
    return uploaded_file


def render_empty_state():
    """Show a friendly empty state when no file is uploaded."""
    st.html(
        """
        <div style="
            text-align: center;
            padding: 4rem 2rem;
            color: #556677;
        ">
            <p style="font-size: 4rem; margin: 0;">📂</p>
            <h3 style="color: #8899aa; font-weight: 600; margin: 0.5rem 0;">
                Upload an Excel file to get started
            </h3>
            <p style="font-size: 0.85rem; max-width: 500px; margin: 0.5rem auto;">
                Your file should contain BOM requirements (<code>bom.qty1</code>)
                and inventory on-hand (<code>on.hand1</code>) data organized by
                order number and item code.
            </p>
        </div>
        """
    )


def main():
    """Main application entry point."""
    load_custom_css()
    render_header()

    # ── File Upload ──
    uploaded_file = render_upload_section()

    if uploaded_file is None:
        render_empty_state()
        return

    # ── Load & Validate ──
    try:
        with st.spinner("Loading Excel file…"):
            raw_df = load_excel(uploaded_file)
    except ValueError as e:
        st.error(f"❌ **Upload Error:** {e}")
        return

    missing = validate_columns(raw_df)
    if missing:
        st.error(
            f"❌ **Missing Columns:** The following required columns were not "
            f"found in your file: `{'`, `'.join(missing)}`"
        )
        st.info(
            "Required columns: `var.orno`, `addr.line1`, `bom.item1`, "
            "`bom.dsca1`, `bom.qty1`, `on.hand1`"
        )
        return

    # ── Compute Shortage ──
    processed_df = compute_shortage(raw_df)

    # ── Sidebar Filters ──
    filter_state = render_sidebar_filters(processed_df)

    # Handle clear filters
    if filter_state["clear_clicked"]:
        handle_clear_filters()

    # Build exclusion prefix list from individual toggles
    exclude_prefixes = []
    if filter_state["exclude_drfb"]:
        exclude_prefixes.append("DRFB")
    if filter_state["exclude_drfi"]:
        exclude_prefixes.append("DRFI")
    if filter_state["exclude_patu"]:
        exclude_prefixes.append("PATU")
    if filter_state["exclude_stcl_chag"]:
        exclude_prefixes.extend(["STCL", "CHAG"])

    filtered_df = apply_filters(
        processed_df,
        selected_orders=filter_state["selected_orders"],
        selected_items=filter_state["selected_items"],
        shortage_only=filter_state["shortage_only"],
        exclude_prefixes=exclude_prefixes or None,
        search_text=filter_state["search_text"],
    )

    # ── KPI Cards ──
    metrics = get_kpi_metrics(filtered_df)
    render_kpi_cards(metrics)

    st.divider()

    # ── Charts Section ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Need vs. Have",
        "🔥 Shortage Heatmap",
        "🗺️ Quantity Treemap",
        "📋 Data Table",
    ])

    with tab1:
        render_need_vs_have_chart(filtered_df)

    with tab2:
        render_shortage_heatmap(filtered_df)

    with tab3:
        render_quantity_treemap(filtered_df)

    with tab4:
        render_data_table(filtered_df)

    # ── Shortage Report (triggered from sidebar) ──
    if filter_state["report_clicked"]:
        st.divider()
        st.html("<h3 style='color:#ff5252;'>📊 Shortage Report</h3>")
        generate_shortage_report(filtered_df)


if __name__ == "__main__":
    main()
