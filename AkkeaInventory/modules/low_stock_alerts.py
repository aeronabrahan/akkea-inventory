# modules/low_stock_alerts.py

import streamlit as st
import pandas as pd
from modules.db_utils import fetch_all
from modules.email_utils import send_email_receipt

def check_low_stock():
    st.title("🔔 Low Stock Alerts")

    rows = fetch_all("SELECT * FROM products WHERE stock < 5")
    if not rows:
        st.success("✅ All products have sufficient stock.")
        return

    df = pd.DataFrame(rows, columns=["Item ID", "Name", "Description", "Category", "Unit", "Stock", "Price"])
    st.warning("⚠️ The following items are low in stock:")
    st.dataframe(df)

    if st.button("📧 Send Low Stock Email"):
        email_body = "The following items are low in stock:\n\n"
        for index, row in df.iterrows():
            email_body += f"- {row['Name']} ({row['Stock']} {row['Unit']})\n"

        success, msg = send_email_receipt(
            gmail_user="helloakkea@gmail.com",
            gmail_app_password="jnyn bupx jxts uxbc",
            to_email="helloakkea@gmail.com",
            subject="Akkea Inventory – Low Stock Alert",
            body_text=email_body,
            pdf_path=None  # No attachment
        )

        if success:
            st.success("Low stock email sent.")
        else:
            st.error(msg)
