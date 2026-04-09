"""
Sidebar Filters Component.

Premium sidebar with floating card sections, pastel accents,
hover effects, and interactive filter controls.
"""

import streamlit as st
import pandas as pd


def _section_label(icon: str, text: str, color: str) -> str:
    """Generate a styled section label."""
    return f"""
    <p style="
        color: {color};
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        margin: 0 0 0.15rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    "><span style="font-size:0.8rem;">{icon}</span> {text}</p>
    """


def _badge(text: str, color: str) -> str:
    """Generate an inline count badge."""
    return f"""
    <div style="
        display: inline-block;
        background: linear-gradient(135deg, {color}25, {color}15);
        border: 1px solid {color}40;
        border-radius: 20px;
        padding: 0.15rem 0.65rem;
        font-size: 0.62rem;
        color: {color};
        font-weight: 600;
        margin-top: 0.2rem;
        backdrop-filter: blur(4px);
    ">{text}</div>
    """


def render_sidebar_filters(df: pd.DataFrame) -> dict:
    """Render sidebar filter controls and return current filter state."""
    with st.sidebar:
        # ── Branding Header ──
        st.html(
            """
            <div style="
                text-align: center;
                padding: 1rem 0.5rem 0.5rem;
            ">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 52px;
                    height: 52px;
                    border-radius: 18px;
                    background: linear-gradient(135deg, #c4a8e0, #7eb8da);
                    font-size: 1.6rem;
                    margin-bottom: 0.6rem;
                    box-shadow:
                        0 4px 20px rgba(196, 168, 224, 0.3),
                        0 0 40px rgba(126, 184, 218, 0.1);
                ">📦</div>
                <h2 style="
                    margin: 0;
                    background: linear-gradient(135deg, #c4a8e0, #7eb8da);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: 800;
                    font-size: 1.15rem;
                    letter-spacing: -0.3px;
                ">Inventory Dashboard</h2>
                <p style="
                    color: #667788;
                    font-size: 0.65rem;
                    margin: 0.25rem 0 0;
                    letter-spacing: 0.5px;
                ">BOM Requirements vs. Availability</p>
            </div>
            """
        )

        # ═══════════════════════════════════════════
        # SEARCH CARD
        # ═══════════════════════════════════════════
        with st.container(border=True):
            st.html(_section_label("🔍", "Global Search", "#c4a8e0"))
            search_text = st.text_input(
                "Search items & companies",
                placeholder="Search descriptions, companies…",
                label_visibility="collapsed",
                key="global_search",
            )

        # ═══════════════════════════════════════════
        # ORDER NUMBER CARD
        # ═══════════════════════════════════════════
        with st.container(border=True):
            st.html(_section_label("📋", "Order Number", "#7eb8da"))
            order_options = sorted(df["var.orno"].dropna().astype(str).unique().tolist())
            selected_orders = st.multiselect(
                "Filter by Order",
                options=order_options,
                default=[],
                placeholder="All orders",
                label_visibility="collapsed",
                key="order_filter",
            )
            if selected_orders:
                st.html(_badge(
                    f"{len(selected_orders)} order{'s' if len(selected_orders) != 1 else ''} selected",
                    "#7eb8da",
                ))

        # ═══════════════════════════════════════════
        # ITEM CODE CARD
        # ═══════════════════════════════════════════
        with st.container(border=True):
            st.html(_section_label("🏷️", "Item Code", "#81d4a8"))
            item_options = sorted(df["bom.item1"].dropna().astype(str).unique().tolist())
            selected_items = st.multiselect(
                "Filter by Item",
                options=item_options,
                default=[],
                placeholder="All items",
                label_visibility="collapsed",
                key="item_filter",
            )
            if selected_items:
                st.html(_badge(
                    f"{len(selected_items)} item{'s' if len(selected_items) != 1 else ''} selected",
                    "#81d4a8",
                ))

        # ═══════════════════════════════════════════
        # FILTER OPTIONS CARD
        # ═══════════════════════════════════════════
        with st.container(border=True):
            st.html(_section_label("⚙️", "Filter Options", "#f6d983"))

            shortage_only = st.toggle(
                "⚠️ Shortage items only",
                value=False,
                key="shortage_toggle",
            )
            if shortage_only:
                shortage_count = int(df["is_shortage"].sum()) if "is_shortage" in df.columns else 0
                st.html(_badge(f"⚠ {shortage_count} items with shortages", "#f4a0a0"))

            exclude_drfb = st.toggle(
                "🚫 Exclude DRFB",
                value=True,
                key="exclude_drfb",
            )
            exclude_drfi = st.toggle(
                "🚫 Exclude DRFI",
                value=True,
                key="exclude_drfi",
            )
            exclude_patu = st.toggle(
                "🚫 Exclude PATU",
                value=True,
                key="exclude_patu",
            )
            exclude_stcl_chag = st.toggle(
                "🚫 Exclude STCL / CHAG",
                value=False,
                key="exclude_stcl_chag",
            )

            # Show combined exclusion badge
            prefixes_on = []
            if exclude_drfb:
                prefixes_on.append("DRFB")
            if exclude_drfi:
                prefixes_on.append("DRFI")
            if exclude_patu:
                prefixes_on.append("PATU")
            if exclude_stcl_chag:
                prefixes_on.extend(["STCL", "CHAG"])
            if prefixes_on:
                excluded_count = int(
                    df["bom.item1"].astype(str).str.startswith(tuple(prefixes_on)).sum()
                )
                st.html(_badge(f"🚫 {excluded_count} items excluded", "#f5b7a5"))

        # ═══════════════════════════════════════════
        # DATA OVERVIEW CARD
        # ═══════════════════════════════════════════
        total = len(df)
        shortages = int(df["is_shortage"].sum()) if "is_shortage" in df.columns else 0
        pct = round((1 - shortages / total) * 100, 1) if total > 0 else 100
        with st.container(border=True):
            st.html(f"""
                <div style="padding: 0.1rem 0;">
                    {_section_label("📊", "Data Overview", "#80cbc4")}
                    <div style="display:flex; justify-content:space-between; margin: 0.5rem 0 0.35rem;">
                        <span style="color:#778899; font-size:0.72rem;">Total Items</span>
                        <span style="
                            font-weight:700; font-size:0.72rem;
                            background: linear-gradient(135deg, #7eb8da, #c4a8e0);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                        ">{total:,}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.35rem;">
                        <span style="color:#778899; font-size:0.72rem;">Shortages</span>
                        <span style="color:#f4a0a0; font-weight:700; font-size:0.72rem;">{shortages}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:#778899; font-size:0.72rem;">Coverage</span>
                        <span style="color:#81d4a8; font-weight:700; font-size:0.72rem;">{pct}%</span>
                    </div>
                    <div style="
                        margin-top: 0.6rem;
                        background: #1e2535;
                        border-radius: 10px;
                        height: 8px;
                        overflow: hidden;
                        box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
                    ">
                        <div style="
                            width: {pct}%;
                            height: 100%;
                            border-radius: 10px;
                            background: linear-gradient(90deg, #81d4a8, #7eb8da, #c4a8e0);
                            box-shadow: 0 0 8px rgba(129, 212, 168, 0.4);
                            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                        "></div>
                    </div>
                </div>
            """)

        # ═══════════════════════════════════════════
        # ACTION BUTTONS CARD
        # ═══════════════════════════════════════════
        with st.container(border=True):
            st.html(_section_label("⚡", "Quick Actions", "#f6d983"))
            col1, col2 = st.columns(2)
            with col1:
                clear_clicked = st.button("🔄 Clear", use_container_width=True)
            with col2:
                report_clicked = st.button("📊 Report", use_container_width=True)

    return {
        "selected_orders": selected_orders,
        "selected_items": selected_items,
        "shortage_only": shortage_only,
        "exclude_drfb": exclude_drfb,
        "exclude_drfi": exclude_drfi,
        "exclude_patu": exclude_patu,
        "exclude_stcl_chag": exclude_stcl_chag,
        "search_text": search_text,
        "clear_clicked": clear_clicked,
        "report_clicked": report_clicked,
    }


def handle_clear_filters():
    """Reset all filter-related session state keys."""
    keys_to_clear = [
        "global_search",
        "order_filter",
        "item_filter",
        "shortage_toggle",
        "exclude_drfb",
        "exclude_drfi",
        "exclude_patu",
        "exclude_stcl_chag",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
