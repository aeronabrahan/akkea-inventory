# modules/auth_customer.py

import streamlit as st
import json
import bcrypt
import os

CUSTOMER_DB = "customers.json"

def load_customers():
    if not os.path.exists(CUSTOMER_DB):
        return {}
    with open(CUSTOMER_DB, "r") as f:
        return json.load(f)

def save_customers(data):
    with open(CUSTOMER_DB, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register():
    st.subheader("📝 Customer Registration")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if not username or not password:
            st.warning("Please fill all fields.")
            return
        if password != confirm:
            st.error("Passwords do not match.")
            return

        customers = load_customers()
        if username in customers:
            st.error("Username already exists.")
            return

        customers[username] = {
            "password": hash_password(password),
            "cart": []
        }
        save_customers(customers)
        st.success("Account created. You can now log in.")

def login():
    st.subheader("🔐 Customer Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        customers = load_customers()
        if username in customers and check_password(password, customers[username]["password"]):
            st.session_state.customer_logged_in = True
            st.session_state.customer_user = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")


def change_password():
    st.subheader("🔑 Change Password")
    username = st.session_state.get("customer_user")
    customers = load_customers()

    old_pw = st.text_input("Old Password", type="password")
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm New Password", type="password")

    if st.button("Update Password"):
        if not check_password(old_pw, customers[username]["password"]):
            st.error("Old password incorrect.")
            return
        if new_pw != confirm_pw:
            st.error("New passwords do not match.")
            return

        customers[username]["password"] = hash_password(new_pw)
        save_customers(customers)
        st.success("Password updated successfully.")

def logout():
    st.session_state.customer_logged_in = False
    st.session_state.customer_user = ""
    st.success("Logged out.")
    st.rerun()