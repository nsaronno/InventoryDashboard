"""
Generate Sample Inventory Data.

Creates a realistic sample Excel file for testing the dashboard.
Run: python generate_sample_data.py
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

# ── Configuration ──
NUM_ORDERS = 6
ITEMS_PER_ORDER_RANGE = (8, 18)

ORDER_NUMBERS = [
    "ORD-2024-001", "ORD-2024-002", "ORD-2024-003",
    "ORD-2024-004", "ORD-2024-005", "ORD-2024-006",
]

COMPANIES = [
    "Greif Industrial Packaging",
    "Mauser Packaging Solutions",
    "Schütz Container Systems",
    "Bway Corporation",
    "THIELMANN Container",
    "Hoover Ferguson Group",
]

ITEMS = [
    ("DRFI01876NA20001", "Steel Drum Ring 17-inch"),
    ("DRFI02234NA30002", "HDPE Liner 22-inch"),
    ("BOLT-M10X50-SS", "Stainless Bolt M10x50mm"),
    ("GSKT-NBR-15IN", "NBR Gasket 15-inch"),
    ("CLMP-BAND-22", "Band Clamp Assembly 22-inch"),
    ("PLUG-BUNG-2IN", "Bung Plug 2-inch NPS"),
    ("LID-STL-OT-22", "Open Top Steel Lid 22-inch"),
    ("RING-BOLT-17", "Bolt Ring 17-inch Diameter"),
    ("PAINT-EPXY-BLU", "Epoxy Paint Blue 1-Gallon"),
    ("SEAL-LDPE-22", "LDPE Seal Ring 22-inch"),
    ("HNDL-WIRE-STL", "Wire Handle Steel"),
    ("DRUM-BODY-55G", "Steel Drum Body 55-Gallon"),
    ("LABEL-HAZ-DOT", "DOT Hazmat Label 4x4"),
    ("PALLET-WD-48", "Wood Pallet 48x48"),
    ("STRAP-STL-3/4", "Steel Strapping 3/4-inch"),
    ("FOAM-INSERT-22", "Foam Insert 22-inch"),
    ("VALVE-BALL-2IN", "Ball Valve 2-inch FNPT"),
    ("FLANGE-WN-150", "Weld Neck Flange 150#"),
    ("TUBE-SS-1/2OD", "SS Tubing 1/2-inch OD"),
    ("FILTER-MESH-40", "Wire Mesh Filter 40-micron"),
]


def generate_data() -> pd.DataFrame:
    """Generate realistic BOM vs inventory data."""
    rows = []

    for i, order in enumerate(ORDER_NUMBERS):
        company = COMPANIES[i]
        num_items = np.random.randint(*ITEMS_PER_ORDER_RANGE)
        selected_items = np.random.choice(len(ITEMS), size=num_items, replace=False)

        for idx in selected_items:
            item_code, item_desc = ITEMS[idx]
            bom_qty = np.random.choice([5, 10, 15, 20, 25, 50, 100, 200, 500])

            # Create intentional shortages for ~35% of items
            if np.random.random() < 0.35:
                on_hand = int(bom_qty * np.random.uniform(0.1, 0.85))
            else:
                on_hand = int(bom_qty * np.random.uniform(1.0, 2.5))

            rows.append({
                "var.orno": order,
                "addr.line1": company,
                "bom.item1": item_code,
                "bom.dsca1": item_desc,
                "bom.qty1": bom_qty,
                "on.hand1": on_hand,
            })

    return pd.DataFrame(rows)


def main():
    """Generate and save sample data."""
    df = generate_data()

    # Save to sample_data directory
    output_dir = os.path.join(os.path.dirname(__file__), "sample_data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sample_inventory.xlsx")

    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"✅ Generated {len(df)} rows across {df['var.orno'].nunique()} orders")
    print(f"   Shortage items: {(df['bom.qty1'] > df['on.hand1']).sum()}")
    print(f"   Saved to: {output_path}")


if __name__ == "__main__":
    main()
