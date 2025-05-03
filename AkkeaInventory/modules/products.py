# modules/products.py

import streamlit as st
import pandas as pd
from modules.db_utils import fetch_all, run_query
from modules.qr_utils import generate_qr, generate_qr_for_all
from modules import materials
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO
from PIL import Image
import base64
import os

IMAGE_DIR = "product_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

def add_product():
    st.subheader("➕ Add New Product")

    item_id = st.text_input("Item ID (Barcode or Code)")
    name = st.text_input("Product Name")
    description = st.text_input("Description")
    category = st.text_input("Category")
    unit = st.selectbox("Unit", ["pcs", "box", "kg", "pack", "set", "liters", "others"])
    stock = st.number_input("Initial Stock", min_value=0, step=1)
    price = st.number_input("Selling Price (₱)", min_value=0.0, step=0.1)
    uploaded_image = st.file_uploader("Upload Product Photo", type=["jpg", "jpeg", "png"])

    if st.button("Add Product"):
        if item_id and name:
            try:
                run_query("""
                    INSERT INTO products (item_id, name, description, category, unit, stock, price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (item_id, name, description, category, unit, stock, price))

                generate_qr(item_id)

                if uploaded_image:
                    image = Image.open(uploaded_image).convert("RGB")
                    image.save(os.path.join(IMAGE_DIR, f"{item_id}.jpg"))

                st.success(f"✅ Product '{name}' added successfully with QR and photo.")
            except Exception as e:
                st.error(f"⚠️ Failed to add: {e}")
        else:
            st.warning("Item ID and Name are required.")

def view_products():
    st.subheader("📦 Inventory")

    data = fetch_all("SELECT * FROM products ORDER BY name ASC")
    if not data:
        st.info("No products found.")
        return

    records = []
    for row in data:
        item_id, name, desc, cat, unit, stock, price = row

        qr_path = f"qr_codes/{item_id}.png"
        qr_html = ""
        if os.path.exists(qr_path):
            img = Image.open(qr_path).resize((60, 60))
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_b64 = base64.b64encode(buffer.getvalue()).decode()
            qr_html = f'<img src="data:image/png;base64,{img_b64}" width="60">'

        img_path = os.path.join(IMAGE_DIR, f"{item_id}.jpg")
        img_html = ""
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((60, 60))
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            img_b64 = base64.b64encode(buffer.getvalue()).decode()
            img_html = f'<img src="data:image/jpeg;base64,{img_b64}" width="60">'

        records.append({
            "Photo": img_html,
            "QR": qr_html,
            "Item ID": item_id,
            "Name": name,
            "Description": desc,
            "Category": cat,
            "Unit": unit,
            "Stock": stock,
            "Price": f"₱{price:,.2f}"
        })

    df = pd.DataFrame(records)

    col1, col2 = st.columns(2)
    search_name = col1.text_input("🔍 Search by Name").lower()
    category_filter = col2.text_input("Filter by Category").lower()

    if search_name:
        df = df[df["Name"].str.lower().str.contains(search_name)]
    if category_filter:
        df = df[df["Category"].str.lower().str.contains(category_filter)]

    st.markdown("### 🖼 Product Table with QR & Photo")
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("---")
    if st.button("📤 Export to Google Sheets"):
        export_to_google_sheets(df)

    if st.button("🔁 Generate QR Codes for All"):
        all_ids = [row[0] for row in fetch_all("SELECT item_id FROM products")]
        generate_qr_for_all(all_ids)
        st.success("✅ QR codes generated for all products.")

    st.markdown("---")
    st.subheader("✏️ Edit or ❌ Delete Product")
    if len(df) == 0:
        st.info("No products to edit.")
        return

    selected_id = st.selectbox("Select Item ID", [r["Item ID"] for r in records])
    raw = fetch_all("SELECT name, description, category, unit, stock, price FROM products WHERE item_id = ?", (selected_id,))
    if raw:
        name, desc, cat, unit, stock, price = raw[0]

        tabs = st.tabs(["📝 Edit Product", "🧰 Materials Used"])
        with tabs[0]:
            new_name = st.text_input("Edit Name", value=name)
            new_desc = st.text_input("Edit Description", value=desc)
            new_cat = st.text_input("Edit Category", value=cat)
            new_unit = st.text_input("Edit Unit", value=unit)
            new_stock = st.number_input("Edit Stock", value=int(stock), step=1)
            new_price = st.number_input("Edit Price (₱)", value=float(price), step=0.1)
            new_photo = st.file_uploader("Replace Product Photo", type=["jpg", "jpeg", "png"])

            col3, col4 = st.columns(2)
            if col3.button("✅ Update Product"):
                run_query("""
                    UPDATE products SET name=?, description=?, category=?, unit=?, stock=?, price=?
                    WHERE item_id=?
                """, (new_name, new_desc, new_cat, new_unit, new_stock, new_price, selected_id))
                if new_photo:
                    image = Image.open(new_photo).convert("RGB")
                    image.save(os.path.join(IMAGE_DIR, f"{selected_id}.jpg"))
                st.success("✅ Product updated. Refresh to see changes.")

            if col4.button("❌ Delete Product"):
                run_query("DELETE FROM products WHERE item_id = ?", (selected_id,))
                if os.path.exists(os.path.join(IMAGE_DIR, f"{selected_id}.jpg")):
                    os.remove(os.path.join(IMAGE_DIR, f"{selected_id}.jpg"))
                st.warning(f"❌ Product '{selected_id}' deleted. Refresh to see changes.")

        with tabs[1]:
            materials.show_materials_for_product(selected_id)

def export_to_google_sheets(df):
    st.info("Connecting to Google Sheets...")
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("firebase_key.json", scopes=scope)
        client = gspread.authorize(creds)

        df_export = df.drop(columns=["Photo", "QR"])
        sheet = client.create("Akkea Inventory Export")
        ws = sheet.sheet1
        ws.update([df_export.columns.tolist()] + df_export.values.tolist())

        st.success("✅ Exported to Google Sheets!")
        st.markdown(f"[Open Sheet]({sheet.url})")
    except Exception as e:
        st.error(f"❌ Failed to export: {e}")
