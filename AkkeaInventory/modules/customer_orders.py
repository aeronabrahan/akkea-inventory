# modules/customer_orders.py

import streamlit as st
import json
import os
from modules.db_utils import fetch_all

CART_FILE = "customer_cart.json"
ORDERS_FILE = "orders.json"


def load_cart():
    if not os.path.exists(CART_FILE):
        return {}
    with open(CART_FILE, "r") as f:
        return json.load(f)


def save_cart(cart):
    with open(CART_FILE, "w") as f:
        json.dump(cart, f, indent=4)


def add_to_cart(username, item_id, name, qty, unit_price):
    cart = load_cart()
    if username not in cart:
        cart[username] = []

    # Check if item exists already
    for item in cart[username]:
        if item["item_id"] == item_id:
            item["qty"] += qty
            save_cart(cart)
            return

    cart[username].append({
        "item_id": item_id,
        "name": name,
        "qty": qty,
        "unit_price": unit_price
    })
    save_cart(cart)


def view_products():
    st.subheader("🛍 Available Products")
    products = fetch_all("SELECT item_id, name, description, price, image_path, stock FROM products")
    username = st.session_state.get("customer_user")

    for pid, name, desc, price, img_path, stock in products:
        with st.container():
            cols = st.columns([1, 3])
            with cols[0]:
                if img_path and os.path.exists(img_path):
                    st.image(img_path, width=120)
            with cols[1]:
                st.markdown(f"### {name}  —  ₱{price:.2f}")
                st.caption(desc)
                st.write(f"Available Stock: {stock}")
                qty = st.number_input(f"Qty for {pid}", min_value=1, max_value=stock, key=f"qty_{pid}")
                if st.button(f"Add to Cart - {pid}"):
                    add_to_cart(username, pid, name, qty, price)
                    st.success(f"Added {qty} of {name} to your cart.")


def view_cart():
    st.subheader("🛒 Your Cart")
    username = st.session_state.get("customer_user")
    cart = load_cart()
    items = cart.get(username, [])

    if not items:
        st.info("Your cart is empty.")
        return

    total = 0
    for item in items:
        st.markdown(f"**{item['name']}** — Qty: {item['qty']} x ₱{item['unit_price']:.2f}")
        total += item["qty"] * item["unit_price"]

    st.markdown(f"### Total: ₱{total:.2f}")

    if st.button("✅ Checkout"):
        place_order(username, items)
        cart[username] = []
        save_cart(cart)
        st.success("Your order has been placed!")


def place_order(username, items):
    if not os.path.exists(ORDERS_FILE):
        orders = []
    else:
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)

    orders.append({
        "username": username,
        "items": items,
        "status": "Pending"
    })
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)


def view_my_orders():
    st.subheader("📦 My Orders")
    if not os.path.exists(ORDERS_FILE):
        st.info("No orders found.")
        return

    username = st.session_state.get("customer_user")
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)

    user_orders = [o for o in orders if o["username"] == username]
    if not user_orders:
        st.info("You haven’t placed any orders yet.")
        return

    for idx, order in enumerate(user_orders[::-1], 1):
        st.markdown(f"### Order #{len(user_orders) - idx + 1} — Status: {order['status']}")
        for item in order["items"]:
            st.markdown(f"- {item['name']} — {item['qty']} x ₱{item['unit_price']:.2f}")
        st.markdown("---")