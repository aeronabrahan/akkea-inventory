# modules/materials.py

import streamlit as st
from modules.db_utils import run_query, fetch_all
import pandas as pd
import math

def init_materials_table():
    run_query("""
        CREATE TABLE IF NOT EXISTS materials_used (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT,
            material_name TEXT,
            size TEXT,
            quantity INTEGER,
            price REAL,
            shipping REAL
        )
    """)

def show_materials_for_product(item_id):
    st.subheader("🧰 Materials Used for This Product")

    with st.form("add_material_form"):
        material_name = st.text_input("Tools/Material Name")
        size = st.text_input("Size (optional)")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        price = st.number_input("Price (₱)", min_value=0.0, step=0.1)
        shipping = st.number_input("Shipping Fee (₱)", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("➕ Add Material")

        if submitted and material_name:
            run_query("""
                INSERT INTO materials_used (item_id, material_name, size, quantity, price, shipping)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (item_id, material_name, size, quantity, price, shipping))
            st.success("✅ Material added.")

    rows = fetch_all("SELECT id, material_name, size, quantity, price, shipping FROM materials_used WHERE item_id = ?", (item_id,))
    if not rows:
        st.info("No materials added yet.")
        return

    st.markdown("### 🧾 Existing Materials")
    for r in rows:
        mat_id, name, size, qty, price, shipping = r
        total = price + shipping
        per_unit = total / qty if qty else 0

        with st.expander(f"🧰 {name} ({qty} units at ₱{per_unit:.2f})"):
            col1, col2 = st.columns(2)
            new_name = col1.text_input("Material Name", value=name, key=f"name_{mat_id}")
            new_size = col2.text_input("Size", value=size, key=f"size_{mat_id}")
            new_qty = col1.number_input("Quantity", min_value=1, value=qty, step=1, key=f"qty_{mat_id}")
            new_price = col2.number_input("Price", min_value=0.0, value=price, step=0.1, key=f"price_{mat_id}")
            new_ship = col1.number_input("Shipping", min_value=0.0, value=shipping, step=0.1, key=f"ship_{mat_id}")

            col3, col4 = st.columns(2)
            if col3.button("💾 Save Changes", key=f"save_{mat_id}"):
                run_query("""
                    UPDATE materials_used
                    SET material_name=?, size=?, quantity=?, price=?, shipping=?
                    WHERE id=?
                """, (new_name, new_size, new_qty, new_price, new_ship, mat_id))
                st.success("✅ Updated successfully.")
                st.experimental_rerun()

            if col4.button("❌ Delete", key=f"del_{mat_id}"):
                run_query("DELETE FROM materials_used WHERE id = ?", (mat_id,))
                st.warning("❌ Material deleted.")
                st.experimental_rerun()

    # Cost Calculation Summary
    st.markdown("---")
    all_rows = fetch_all("SELECT quantity, price, shipping FROM materials_used WHERE item_id = ?", (item_id,))
    total_cost = 0.0
    for q, p, s in all_rows:
        total = p + s
        per_unit = total / q if q else 0
        total_cost += per_unit

    st.markdown(f"### 🧮 Production Cost Per Unit: **₱{total_cost:,.2f}**")
    suggested_price = math.ceil((total_cost * 2) / 5) * 5
    st.markdown(f"### 💡 Suggested Selling Price: **₱{suggested_price:,.2f}** (2x cost, rounded up to ₱5)")
