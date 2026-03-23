"""
Charts Component.

Renders interactive Plotly charts:
  - Need vs Have (grouped horizontal bar chart)
  - Shortage Heatmap (orders × items)
  - Quantity Treemap (BOM usage distribution)
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st

# ── Pastel palette ──
CHART_TEMPLATE = "plotly_dark"
CHART_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"

# Pastel tones
PASTEL_BLUE = "#7eb8da"
PASTEL_GREEN = "#81d4a8"
PASTEL_RED = "#f4a0a0"
PASTEL_AMBER = "#f6d983"
PASTEL_PURPLE = "#c4a8e0"
PASTEL_CORAL = "#f5b7a5"
PASTEL_TEAL = "#80cbc4"
PASTEL_PINK = "#f3a9c7"

CHART_LAYOUT = dict(
    template=CHART_TEMPLATE,
    plot_bgcolor=CHART_BG,
    paper_bgcolor=PAPER_BG,
    font=dict(family="Inter, sans-serif", color="#c0c8d4"),
    margin=dict(l=20, r=20, t=50, b=20),
)


def render_need_vs_have_chart(df: pd.DataFrame, max_items: int = 25):
    """Grouped horizontal bar chart comparing BOM qty vs on-hand.

    Two side-by-side bars per item so neither is hidden.
    On-Hand bar color: pastel green if covered, pastel red if shortage.
    """
    if df.empty:
        st.info("No data to display for the Need vs. Have chart.")
        return

    # Aggregate by item: sum BOM and on-hand
    # On-hand is a per-item snapshot (not additive), so take max per item
    agg = (
        df.groupby(["bom.item1", "bom.dsca1"], as_index=False)
        .agg({"bom.qty1": "sum", "on.hand1": "max"})
        .sort_values("bom.qty1", ascending=True)
        .tail(max_items)
    )

    # Build compact labels
    labels = agg.apply(
        lambda r: f"{r['bom.item1']}<br><span style='font-size:10px;color:#8899aa'>"
                  f"{str(r['bom.dsca1'])[:30]}</span>",
        axis=1,
    )

    # Per-item on-hand color (pastel green = covered, pastel red = shortage)
    on_hand_colors = [
        PASTEL_GREEN if oh >= bom else PASTEL_RED
        for oh, bom in zip(agg["on.hand1"], agg["bom.qty1"])
    ]

    fig = go.Figure()

    # BOM Required bars
    fig.add_trace(
        go.Bar(
            y=labels,
            x=agg["bom.qty1"],
            name="BOM Required",
            orientation="h",
            marker=dict(
                color=PASTEL_BLUE,
                line=dict(color="#5a9bbf", width=1),
            ),
            opacity=0.9,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Required: <b>%{x:,.0f}</b><extra></extra>"
            ),
        )
    )

    # On-Hand bars
    fig.add_trace(
        go.Bar(
            y=labels,
            x=agg["on.hand1"],
            name="On-Hand",
            orientation="h",
            marker=dict(
                color=on_hand_colors,
                line=dict(color="rgba(255,255,255,0.15)", width=1),
            ),
            opacity=0.9,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "On-Hand: <b>%{x:,.0f}</b><extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(
            text="<b>Need vs. Have</b> — BOM Required vs On-Hand",
            font=dict(size=16),
        ),
        barmode="group",  # Side-by-side, no overlap
        bargap=0.20,
        bargroupgap=0.05,
        height=max(450, len(agg) * 45 + 100),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12),
        ),
        xaxis=dict(
            title="Quantity",
            gridcolor="#1e2738",
            zeroline=False,
        ),
        yaxis=dict(automargin=True),
    )

    st.plotly_chart(fig, width="stretch")


def render_shortage_heatmap(df: pd.DataFrame):
    """Heatmap showing shortage amounts across orders and items."""
    if df.empty:
        st.info("No data to display for the Shortage Heatmap.")
        return

    shortage_df = df[df["is_shortage"]].copy()

    if shortage_df.empty:
        st.success("🎉 No shortages detected — all items are fully stocked!")
        return

    pivot = shortage_df.pivot_table(
        index="var.orno",
        columns="bom.item1",
        values="shortage_amt",
        aggfunc="sum",
        fill_value=0,
    )

    pivot = pivot.loc[:, (pivot > 0).any()]

    if pivot.empty:
        st.success("🎉 No shortages detected in filtered data.")
        return

    # Pastel-warm heatmap scale
    fig = px.imshow(
        pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.astype(str).tolist(),
        color_continuous_scale=[
            [0, "#1a1f2e"],
            [0.25, PASTEL_AMBER],
            [0.55, PASTEL_CORAL],
            [1.0, PASTEL_RED],
        ],
        aspect="auto",
        labels=dict(x="Item Code", y="Order Number", color="Shortage Qty"),
    )

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(
            text="<b>Shortage Heatmap</b> — Critical Parts by Order",
            font=dict(size=16),
        ),
        height=max(350, len(pivot) * 40 + 150),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=11)),
        coloraxis_colorbar=dict(
            title="Shortage",
            thickness=15,
            len=0.7,
        ),
    )

    st.plotly_chart(fig, width="stretch")


def render_quantity_treemap(df: pd.DataFrame):
    """Treemap showing the most-used items across all orders by BOM quantity."""
    if df.empty:
        st.info("No data to display for the Quantity Treemap.")
        return

    agg = (
        df.groupby(["bom.item1", "bom.dsca1"], as_index=False)
        .agg({"bom.qty1": "sum", "var.orno": "nunique"})
        .rename(columns={"var.orno": "order_count"})
        .sort_values("bom.qty1", ascending=False)
    )

    agg["label"] = agg.apply(
        lambda r: f"{r['bom.item1']}<br>{str(r['bom.dsca1'])[:25]}",
        axis=1,
    )

    # On-hand is a per-item snapshot (not additive), so take max per item
    on_hand_agg = (
        df.groupby("bom.item1", as_index=False)["on.hand1"].max()
    )
    agg = agg.merge(on_hand_agg, on="bom.item1", how="left")
    agg["fulfillment"] = (agg["on.hand1"] / agg["bom.qty1"].clip(lower=1) * 100).clip(upper=100).round(1)

    # Pastel treemap scale
    fig = px.treemap(
        agg,
        path=["label"],
        values="bom.qty1",
        color="fulfillment",
        color_continuous_scale=[
            [0, PASTEL_RED],
            [0.5, PASTEL_AMBER],
            [1.0, PASTEL_GREEN],
        ],
        color_continuous_midpoint=50,
        custom_data=["bom.item1", "bom.qty1", "on.hand1", "order_count", "fulfillment"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "BOM Qty: %{customdata[1]:,.0f}<br>"
            "On-Hand: %{customdata[2]:,.0f}<br>"
            "Orders: %{customdata[3]}<br>"
            "Fulfillment: %{customdata[4]:.1f}%<br>"
            "<extra></extra>"
        ),
        textinfo="label+value",
        textfont=dict(size=11),
    )

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(
            text="<b>BOM Quantity Distribution</b> — Most Used Items",
            font=dict(size=16),
        ),
        height=500,
        coloraxis_colorbar=dict(
            title="Fulfillment %",
            thickness=15,
            len=0.7,
        ),
    )

    st.plotly_chart(fig, width="stretch")
