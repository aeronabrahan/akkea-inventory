# modules/sales.py

import streamlit as st
import uuid
from datetime import datetime
from modules.db_utils import run_query, fetch_all

def add_sale():
    st.subheader("🧾 Record a Sale")

    sale_id = str(uuid.uuid4())[:8].upper()
    customer_name = st.text_input("Customer Name")
    transaction_date = st.date_input("Date", datetime.now())

    products = fetch_all("SELECT item_id, name, stock, price FROM products")
    product_map = {f"{name} (Stock: {stock})": (item_id, price, stock)
                   for item_id, name, stock, price in products}
    product_choice = st.selectbox("Select Product", list(product_map.keys()))

    item_id, unit_price, current_stock = product_map.get(product_choice, ("", 0.0, 0))

    if current_stock < 1:
        st.warning("⚠️ This product is out of stock and cannot be sold.")
        quantity = 0
    else:
        quantity = st.number_input("Quantity Sold", min_value=1, max_value=current_stock, step=1)

    total_price = unit_price * quantity

    if st.button("Record Sale"):
        if item_id and quantity <= current_stock:
            try:
                run_query("""
                    INSERT INTO sales (sale_id, customer_name, transaction_date, item_id, quantity, unit_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (sale_id, customer_name, transaction_date.strftime("%Y-%m-%d"), item_id, quantity, unit_price))

                run_query("UPDATE products SET stock = stock - ? WHERE item_id = ?", (quantity, item_id))
                st.success(f"✅ Sale recorded. Total: ₱{total_price:,.2f}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Invalid quantity or item selection.")

def view_sales():
    st.subheader("📃 Sales History")

    rows = fetch_all("""
        SELECT s.sale_id, s.customer_name, s.transaction_date, p.name, s.quantity, s.unit_price
        FROM sales s
        JOIN products p ON s.item_id = p.item_id
        ORDER BY s.transaction_date DESC
    """)
    if rows:
        formatted = [
            {
                "Sale ID": r[0],
                "Customer": r[1],
                "Date": r[2],
                "Product": r[3],
                "Qty": r[4],
                "Unit Price": f"₱{r[5]:,.2f}",
                "Total": f"₱{r[4]*r[5]:,.2f}"
            } for r in rows
        ]
        st.table(formatted)
    else:
        st.info
