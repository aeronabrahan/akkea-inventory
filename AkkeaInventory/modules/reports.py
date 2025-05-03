# modules/reports.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modules.db_utils import fetch_all

def show_dashboard():
    st.title("📊 Reports Dashboard")

    purchases = fetch_all("SELECT transaction_date, quantity, amount FROM purchases")
    if not purchases:
        st.info("No purchase data available yet.")
        return

    df = pd.DataFrame(purchases, columns=["Date", "Qty", "Unit Cost"])
    df["Date"] = pd.to_datetime(df["Date"])
    df["Total"] = df["Qty"] * df["Unit Cost"]
    df = df.sort_values("Date")

    total_purchase = df["Total"].sum()
    total_qty = df["Qty"].sum()

    st.metric("💰 Total Purchase Value", f"₱{total_purchase:,.2f}")
    st.metric("📦 Total Quantity Purchased", f"{total_qty:,.0f}")

    st.markdown("---")
    st.subheader("🗓 Purchase Value Over Time")
    df_by_date = df.groupby("Date").sum(numeric_only=True)
    st.line_chart(df_by_date["Total"])

    st.subheader("📦 Quantity Over Time")
    st.bar_chart(df_by_date["Qty"])
