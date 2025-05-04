# app.py

import streamlit as st
import os
import sys
import base64
from datetime import datetime
from modules import (
    db_utils,
    auth,
    auth_customer,
    products,
    purchases,
    sales,
    barcode_scanner,
    receipt,
    email_utils,
    reports,
    backup,
    low_stock_alerts,
    materials,
    customer_orders
)

st.set_page_config(page_title="Akkea Inventory", layout="wide")

# ---------------- Ensure products table has image_path column ----------------
db_utils.init_db()
try:
    db_utils.run_query("ALTER TABLE products ADD COLUMN image_path TEXT")
except:
    pass  # column may already exist

materials.init_materials_table()

# # ---------------- LOGO ----------------
# def get_logo_path():
#     if getattr(sys, 'frozen', False):
#         return os.path.join(sys._MEIPASS, "assets", "logo.png")
#     return os.path.join("assets", "logo.png")

# logo_path = get_logo_path()
# if os.path.exists(logo_path):
#     with open(logo_path, "rb") as f:
#         logo_data = f.read()
#     logo_base64 = base64.b64encode(logo_data).decode()
#     st.sidebar.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" width="300"/></div>', unsafe_allow_html=True)
# else:
#     st.sidebar.warning("⚠️ logo.png not found")

# ---------------- ROLE SELECTOR ----------------
if not st.session_state.get("customer_logged_in", False) and not st.session_state.get("logged_in", False):
    login_type = st.sidebar.radio("Select Access Type", ["Admin/Staff", "Customer"])
else:
    login_type = "Customer" if st.session_state.get("customer_logged_in") else "Admin/Staff"

# ---------------- LOGIN ----------------
if login_type == "Admin/Staff":
    logged_in, user, role = auth.login()
    if not logged_in:
        st.stop()
else:
    if "customer_logged_in" not in st.session_state:
        st.session_state.customer_logged_in = False
        st.session_state.customer_user = ""

    if not st.session_state.customer_logged_in:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            auth_customer.login()
        with tab2:
            auth_customer.register()
        st.stop()
    user = st.session_state.customer_user
    role = "customer"

# Sidebar logo and menu
# st.sidebar.image("assets/logo.png", width=300)
# def get_logo_path():
#     if getattr(sys, 'frozen', False):
#         # If bundled as an .exe by PyInstaller
#         return os.path.join(sys._MEIPASS, "assets", "logo.png")
#     return os.path.join("assets", "logo.png")

# logo_path = get_logo_path()

# if os.path.exists(logo_path):
#     with open("assets/logo.png", "rb") as f:
#         logo_data = f.read()
#     logo_base64 = base64.b64encode(logo_data).decode()
#     st.sidebar.markdown(
#         f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" width="300"/></div>',
#         unsafe_allow_html=True
#     )
# else:
#     st.sidebar.warning("⚠️ `logo.png` not found in `assets/` folder.")

# ---------------- MENU ----------------
if role == "admin":
    menu = [
        "🏠 Dashboard", "📦 Products", "🛒 Purchases", "🧾 Sales", "📷 Barcode Scanner",
        "📄 Generate Receipt", "📧 Email Receipt", "📊 Reports Dashboard",
        "📁 Export / Backup", "🔔 Low Stock Alerts", "☁️ Sync to Firebase"
    ]
elif role == "staff":
    menu = [
        "🏠 Dashboard", "📦 Products", "🛒 Purchases", "🧾 Sales",
        "📷 Barcode Scanner", "📄 Generate Receipt"
    ]
else:
    menu = ["🛍 View Products", "🛒 My Cart", "📦 My Orders", "🔑 Change Password"]

page = st.sidebar.radio("📂 Menu", menu)

if role in ["admin", "staff"]:
    if st.sidebar.button("🔓 Logout"):
        auth.logout()
        st.rerun()
else:
    if st.sidebar.button("🔓 Logout"):
        auth_customer.logout()

# ---------------- ROUTING ----------------

if page == "🏠 Dashboard":
    # st.markdown(f"""
    #     <div style='text-align: center;'>
    #         <img src="data:image/png;base64,{logo_base64}" width="750" style="object-fit: contain;"/>
    #     </div>
    # """, unsafe_allow_html=True)
    now = datetime.now().strftime("%A, %B %d, %Y — %I:%M %p")
    st.markdown(f"<p style='text-align: center; font-size: 16px; color: gray;'>📅 {now}</p>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>👋 Welcome, <b>{user}</b></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Role: <code>{role.capitalize()}</code></p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    prod_count = db_utils.fetch_all("SELECT COUNT(*) FROM products")[0][0]
    purchase_count = db_utils.fetch_all("SELECT COUNT(*) FROM purchases")[0][0]
    sales_count = db_utils.fetch_all("SELECT COUNT(*) FROM sales")[0][0]

    st.markdown(f"""
        <div style="display: flex; justify-content: center; gap: 60px; margin-top: 20px;">
            <div style="text-align: center;"><div style="font-size: 26px;">📦 Total Products</div><div style="font-size: 44px; font-weight: bold;">{prod_count}</div></div>
            <div style="text-align: center;"><div style="font-size: 26px;">🛒 Purchases</div><div style="font-size: 44px; font-weight: bold;">{purchase_count}</div></div>
            <div style="text-align: center;"><div style="font-size: 26px;">🧾 Sales</div><div style="font-size: 44px; font-weight: bold;">{sales_count}</div></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    low_stock = db_utils.fetch_all("SELECT name, stock FROM products WHERE stock < 5")
    if low_stock:
        st.markdown("### 🔔 Low Stock Alerts")
        for name, stock in low_stock:
            st.warning(f"🔻 **{name}** only has **{stock}** left!")
    else:
        st.success("✅ All stocks are sufficient.")

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
    st.title("📷 Upload Barcode or QR Code")
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
            qty = col2.number_input("Qty", min_value=0, step=1, key=f"qty{i}")
            price = col3.number_input("Unit Price (₱)", min_value=0.0, step=0.1, key=f"price{i}")
            if name and qty > 0:
                items.append({"name": name, "qty": qty, "unit_price": price})
        submitted = st.form_submit_button("Generate Receipt")

    if submitted and invoice_no and customer_name and items:
        total = sum(i["qty"] * i["unit_price"] for i in items)
        path = receipt.generate_receipt(invoice_no, customer_name, items, total)
        st.success(f"Receipt saved at: {path}")
        with open(path, "rb") as f:
            st.download_button("📥 Download Receipt", f, file_name=os.path.basename(path))
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
                sender_email, app_password, recipient,
                subject="Your Receipt from Akkea",
                body_text="Thank you for your purchase! Please see your receipt attached.",
                pdf_path="temp_receipt.pdf"
            )
            st.success(msg) if success else st.error(msg)
        else:
            st.warning("Please provide both email and a file.")

elif page == "📊 Reports Dashboard":
    reports.show_dashboard()

elif page == "📁 Export / Backup":
    backup.export_inventory()

elif page == "🔔 Low Stock Alerts":
    low_stock_alerts.check_low_stock()

elif page == "☁️ Sync to Firebase":
    db_utils.sync_to_firebase_button()

elif page == "🛍 View Products":
    customer_orders.view_products()

elif page == "🛒 My Cart":
    customer_orders.view_cart()

elif page == "📦 My Orders":
    customer_orders.view_my_orders()

elif page == "🔑 Change Password":
    auth_customer.change_password()
