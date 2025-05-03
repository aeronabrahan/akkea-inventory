# modules/backup.py

import streamlit as st
import pandas as pd
from modules.db_utils import fetch_all

def export_inventory():
    st.title("📁 Backup / Export Inventory")

    rows = fetch_all("SELECT * FROM products")
    if not rows:
        st.warning("No product data to export.")
        return

    df = pd.DataFrame(rows, columns=["Item ID", "Name", "Description", "Category", "Unit", "Stock", "Price"])
    df["Price"] = df["Price"].apply(lambda x: f"₱{x:,.2f}")
    st.dataframe(df)

    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, file_name="inventory_backup.csv")

    with col2:
        excel_path = "inventory_backup.xlsx"
        df.to_excel(excel_path, index=False)
        with open(excel_path, "rb") as f:
            st.download_button("⬇️ Download Excel", f, file_name="inventory_backup.xlsx")
