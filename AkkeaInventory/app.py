# app.py

import streamlit as st

# Set page config first
st.set_page_config(page_title="Akkea Inventory", layout="wide")

import os
import sys
import base64
import time
import pytz
from datetime import datetime
from modules import (
    db_utils,
    auth,
    products,
    purchases,
    sales,
    barcode_scanner,
    receipt,
    email_utils,
    reports,
    backup,
    low_stock_alerts,
    sync,
    materials
)

# Initialize tables
db_utils.init_db()
materials.init_materials_table()

# Login
logged_in, user, role = auth.login()
if not logged_in:
    st.stop()

# Sidebar logo and menu
# st.sidebar.image("assets/logo.png", width=300)
def get_logo_path():
    if getattr(sys, 'frozen', False):
        # If bundled as an .exe by PyInstaller
        return os.path.join(sys._MEIPASS, "assets", "logo.png")
    return os.path.join("assets", "logo.png")

logo_path = get_logo_path()

if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_data = f.read()
    logo_base64 = base64.b64encode(logo_data).decode()
    st.sidebar.markdown(
        f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" width="300"/></div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.warning("⚠️ `logo.png` not found in `assets/` folder.")

st.sidebar.title("Akkea Inventory")

menu_admin = [
    "🏠 Dashboard",
    "📦 Products",
    "🛒 Purchases",
    "🧾 Sales",
    "📷 Barcode Scanner",
    "📄 Generate Receipt",
    "📧 Email Receipt",
    "📊 Reports Dashboard",
    "📁 Export / Backup",
    "🔔 Low Stock Alerts",
    "☁️ Sync to Firebase"
]
menu_staff = [
    "🏠 Dashboard",
    "📦 Products",
    "🛒 Purchases",
    "🧾 Sales",
    "📷 Barcode Scanner",
    "📄 Generate Receipt"
]

menu = menu_admin if role == "admin" else menu_staff
page = st.sidebar.radio("📂 Menu", menu)

# Logout
if st.sidebar.button("🔓 Logout"):
    auth.logout()
    st.rerun()

# ---------------- ROUTING ----------------

if page == "🏠 Dashboard":
    # Load and center logo
    with open("assets/logo.png", "rb") as f:
        logo_data = f.read()
    logo_base64 = base64.b64encode(logo_data).decode()

    st.markdown(
        f"""
        <div style='text-align: center; margin-top: -350px; margin-bottom: -300px;'>
            <img src="data:image/png;base64,{logo_base64}" width="750" style="object-fit: contain;" />
        </div>
        """,
        unsafe_allow_html=True
    )

    # Date & greeting
    now = datetime.now().strftime("%A, %B %d, %Y — %I:%M %p")
    st.markdown(f"<p style='text-align: center; font-size: 16px; color: gray;'>📅 {now}</p>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>👋 Welcome, <b>{user}</b></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Role: <code>{role.capitalize()}</code></p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Get summary stats
    prod_count = db_utils.fetch_all("SELECT COUNT(*) FROM products")[0][0]
    purchase_count = db_utils.fetch_all("SELECT COUNT(*) FROM purchases")[0][0]
    sales_count = db_utils.fetch_all("SELECT COUNT(*) FROM sales")[0][0]

    # Display metrics with larger styling
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; gap: 60px; margin-top: 20px;">
            <div style="text-align: center;">
                <div style="font-size: 26px;">📦 Total Products</div>
                <div style="font-size: 44px; font-weight: bold;">{prod_count}</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 26px;">🛒 Purchases</div>
                <div style="font-size: 44px; font-weight: bold;">{purchase_count}</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 26px;">🧾 Sales</div>
                <div style="font-size: 44px; font-weight: bold;">{sales_count}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Low stock alert summary
    st.markdown("<hr>", unsafe_allow_html=True)
    low_stock_items = db_utils.fetch_all("SELECT name, stock FROM products WHERE stock < 5")
    if low_stock_items:
        st.markdown("### 🔔 Low Stock Alerts")
        for name, stock in low_stock_items:
            st.warning(f"🔻 **{name}** only has **{stock}** left in stock!")
    else:
        st.success("✅ No low stock items at the moment.")

elif page == "📦 Products":
    st.title("📦 Product Management")
    products.add_product()
    st.markdown("---")
    products.view_products()

elif page == "🛒 Purchases":
    st.title("🛒 Purchase Entry")
    purchases.add_purchase()
    st.markdown("---")
    purchases.view_purchases()

elif page == "🧾 Sales":
    st.title("🧾 Sales Module")
    sales.add_sale()
    st.markdown("---")
    sales.view_sales()

elif page == "📷 Barcode Scanner":
    st.title("📷 Camera Barcode Scanner")
    scanned = barcode_scanner.scan_barcode_from_camera()
    if scanned:
        st.success(f"Scanned: {scanned}")

elif page == "📄 Generate Receipt":
    st.title("📄 Generate Customer Receipt")

    invoice_no = st.text_input("Invoice No.")
    customer_name = st.text_input("Customer Name")
    auto_print = st.checkbox("🖨️ Auto-Print Receipt", value=True)

    with st.form("receipt_form"):
        st.markdown("**Add Items:**")
        items = []
        for i in range(1, 6):
            col1, col2, col3 = st.columns([4, 2, 2])
            name = col1.text_input(f"Item {i} Name", key=f"item{i}")
            qty = col2.number_input(f"Qty", min_value=0, step=1, key=f"qty{i}")
            price = col3.number_input(f"Unit Price (₱)", min_value=0.0, step=0.1, key=f"price{i}")
            if name and qty > 0:
                items.append({"name": name, "qty": qty, "unit_price": price})
        submitted = st.form_submit_button("Generate Receipt")

    if submitted and invoice_no and customer_name and items:
        total = sum(i["qty"] * i["unit_price"] for i in items)
        path = receipt.generate_receipt(invoice_no, customer_name, items, total)
        st.success(f"Receipt generated at: {path}")
        with open(path, "rb") as f:
            st.download_button("📥 Download Receipt", f, file_name=path.split("/")[-1])
        if auto_print:
            receipt.auto_print(path)

elif page == "📧 Email Receipt":
    st.title("📧 Send Receipt via Gmail")

    sender_email = "helloakkea@gmail.com"
    app_password = "jnyn bupx jxts uxbc"
    st.markdown(f"**Sender Gmail:** `{sender_email}` (fixed)")
    recipient = st.text_input("Customer's Email")
    uploaded_pdf = st.file_uploader("Upload Receipt PDF", type=["pdf"])

    if st.button("📤 Send Email"):
        if recipient and uploaded_pdf:
            with open("temp_receipt.pdf", "wb") as f:
                f.write(uploaded_pdf.read())
            success, msg = email_utils.send_email_receipt(
                sender_email,
                app_password,
                recipient,
                subject="Your Receipt from Akkea",
                body_text="Thank you for your purchase! Please see your receipt attached.",
                pdf_path="temp_receipt.pdf"
            )
            if success:
                st.success(msg)
            else:
                st.error(msg)
        else:
            st.warning("Please provide recipient email and a receipt file.")

elif page == "📊 Reports Dashboard":
    reports.show_dashboard()

elif page == "📁 Export / Backup":
    backup.export_inventory()

elif page == "🔔 Low Stock Alerts":
    low_stock_alerts.check_low_stock()

elif page == "☁️ Sync to Firebase":
    sync.sync_with_firebase()
