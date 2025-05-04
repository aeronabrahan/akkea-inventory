# modules/customer_orders.py

import streamlit as st
from modules.firebase_utils import add_document, get_document, get_all_documents, update_document
import uuid
from datetime import datetime


def view_products():
    st.subheader("🛍 Available Products")
    products = get_all_documents("products")
    for pid, product in products.items():
        with st.container():
            st.markdown(f"### {product['name']}")
            st.write(product.get("description", "No description"))
            st.write(f"**Price:** ₱{product['price']:.2f}")
            st.write(f"**Stock:** {product['stock']}")
            if st.button("Add to Cart", key=f"add_{pid}"):
                add_to_cart(pid, product['name'], product['price'])
                st.success(f"Added {product['name']} to cart")


def add_to_cart(pid, name, price):
    username = st.session_state.customer_user
    cart = get_document("carts", username) or {}
    if pid in cart:
        cart[pid]["qty"] += 1
    else:
        cart[pid] = {"name": name, "price": price, "qty": 1}
    add_document("carts", username, cart)


def view_cart():
    st.subheader("🛒 My Cart")
    username = st.session_state.customer_user
    cart = get_document("carts", username) or {}
    if not cart:
        st.info("Your cart is empty.")
        return

    total = 0
    for pid, item in cart.items():
        st.write(f"**{item['name']}** — ₱{item['price']:.2f} × {item['qty']}")
        total += item['price'] * item['qty']

    st.write(f"### Total: ₱{total:.2f}")
    if st.button("Checkout"):
        create_order(username, cart, total)
        add_document("carts", username, {})  # empty cart
        st.success("✅ Order placed!")


def create_order(username, items, total):
    order_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    order = {
        "user": username,
        "items": items,
        "total": total,
        "timestamp": timestamp,
        "status": "Pending"
    }
    add_document("orders", order_id, order)


def view_my_orders():
    st.subheader("📦 My Orders")
    username = st.session_state.customer_user
    all_orders = get_all_documents("orders")
    user_orders = [o for o in all_orders.values() if o["user"] == username]

    if not user_orders:
        st.info("You have no orders yet.")
        return

    for o in sorted(user_orders, key=lambda x: x["timestamp"], reverse=True):
        st.write(f"**Order Date:** {o['timestamp']}")
        st.write(f"**Status:** {o['status']}")
        for pid, item in o['items'].items():
            st.write(f"- {item['name']} × {item['qty']} — ₱{item['price']:.2f} each")
        st.write(f"**Total:** ₱{o['total']:.2f}")
        st.markdown("---")
