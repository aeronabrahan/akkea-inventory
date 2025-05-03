# modules/purchases.py

import streamlit as st
import uuid
from datetime import datetime
from modules.db_utils import run_query, fetch_all

def add_purchase():
    st.subheader("🛒 Add New Purchase Entry")

    # Auto-generate unique Purchase ID
    purchase_id = str(uuid.uuid4())[:8].upper()

    invoice_no = st.text_input("Invoice No.")
    transaction_date = st.date_input("Transaction Date", datetime.now())
    
    # Fetch all item IDs and names for dropdown
    products = fetch_all("SELECT item_id, name FROM products")
    product_options = {f"{name} ({item_id})": item_id for item_id, name in products}

    product_choice = st.selectbox("Select Product", list(product_options.keys()))
    item_id = product_options.get(product_choice, "")
    
    description = st.text_input("Description")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    unit = st.selectbox("Unit", ["pcs", "box", "kg", "pack", "set", "liters", "others"])
    amount = st.number_input("Amount (Per Unit Cost)", min_value=0.0, step=0.1)

    if st.button("Add Purchase Entry"):
        if item_id and invoice_no:
            try:
                # Insert into purchases table
                run_query("""
                    INSERT INTO purchases (purchase_id, invoice_no, transaction_date, item_id, description, quantity, unit, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    purchase_id,
                    invoice_no,
                    transaction_date.strftime("%Y-%m-%d"),
                    item_id,
                    description,
                    quantity,
                    unit,
                    amount
                ))

                # Update stock in products table
                run_query("""
                    UPDATE products
                    SET stock = stock + ?
                    WHERE item_id = ?
                """, (quantity, item_id))

                st.success("Purchase entry added and inventory updated.")
            except Exception as e:
                st.error(f"Failed to add purchase: {e}")
        else:
            st.warning("Please fill in all required fields.")

def view_purchases():
    st.subheader("📑 Purchase Records")

    rows = fetch_all("""
        SELECT p.purchase_id, p.invoice_no, p.transaction_date, pr.name, p.description,
               p.quantity, p.unit, p.amount
        FROM purchases p
        JOIN products pr ON p.item_id = pr.item_id
        ORDER BY p.transaction_date DESC
    """)

    if rows:
        st.table([
            {
                "Purchase ID": r[0],
                "Invoice No.": r[1],
                "Date": r[2],
                "Product": r[3],
                "Description": r[4],
                "Qty": r[5],
                "Unit": r[6],
                "Unit Cost": f"{r[7]:.2f}",
                "Total": f"{r[5]*r[7]:.2f}"
            } for r in rows
        ])
    else:
        st.info("No purchases recorded yet.")
