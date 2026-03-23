"""
KPI Cards Component.

Renders stylish metric cards for inventory health overview
using a pastel color palette.
"""

import streamlit as st


def render_kpi_cards(metrics: dict):
    """Display four KPI cards in a row.

    Args:
        metrics: Dictionary from data_processor.get_kpi_metrics().
    """
    # Determine fulfillment color (pastel tones)
    fp = metrics["fulfillment_pct"]
    if fp >= 90:
        ful_color = "#81d4a8"
        ful_icon = "✅"
    elif fp >= 70:
        ful_color = "#f6d983"
        ful_icon = "⚡"
    else:
        ful_color = "#f4a0a0"
        ful_icon = "🔴"

    # Shortage severity (pastel tones)
    shortage_count = metrics["items_in_shortage"]
    if shortage_count == 0:
        short_color = "#81d4a8"
        short_icon = "✅"
    elif shortage_count <= 5:
        short_color = "#f6d983"
        short_icon = "⚠️"
    else:
        short_color = "#f4a0a0"
        short_icon = "🚨"

    cards = [
        {
            "title": "Total Items",
            "value": f"{metrics['total_items']:,}",
            "subtitle": f"Across {metrics['total_orders']} orders",
            "icon": "📦",
            "accent": "#7eb8da",
        },
        {
            "title": "Items in Shortage",
            "value": f"{shortage_count:,}",
            "subtitle": f"Qty deficit: {metrics['total_shortage']:,.0f}",
            "icon": short_icon,
            "accent": short_color,
        },
        {
            "title": "Fulfillment Rate",
            "value": f"{fp:.1f}%",
            "subtitle": f"{metrics['total_on_hand']:,.0f} / {metrics['total_bom_qty']:,.0f}",
            "icon": ful_icon,
            "accent": ful_color,
        },
        {
            "title": "Total Orders",
            "value": f"{metrics['total_orders']:,}",
            "subtitle": "Unique order numbers",
            "icon": "📋",
            "accent": "#c4a8e0",
        },
    ]

    card_html = '<div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1.5rem;">'

    for card in cards:
        card_html += f"""
        <div style="
            flex: 1;
            min-width: 200px;
            background: linear-gradient(135deg, #1a1f2e 0%, #141820 100%);
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            border: 1px solid #2a3040;
            border-left: 4px solid {card['accent']};
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <p style="
                        color: #8899aa;
                        font-size: 0.72rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        margin: 0 0 0.5rem;
                    ">{card['title']}</p>
                    <p style="
                        color: #ffffff;
                        font-size: 1.75rem;
                        font-weight: 800;
                        margin: 0;
                        line-height: 1.1;
                    ">{card['value']}</p>
                </div>
                <span style="font-size: 1.75rem; opacity: 0.8;">{card['icon']}</span>
            </div>
            <p style="
                color: #667788;
                font-size: 0.68rem;
                margin: 0.5rem 0 0;
            ">{card['subtitle']}</p>
        </div>
        """

    card_html += "</div>"

    st.html(card_html)
