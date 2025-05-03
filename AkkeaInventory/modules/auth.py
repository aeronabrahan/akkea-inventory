# modules/auth.py

import streamlit as st
import json
import bcrypt

def load_users():
    return {
        "admin": {"password": "hashed-password", "role": "admin"},
        "staff": {"password": "hashed-password", "role": "staff"}
    }


def login():
    """Handles login UI and session state"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

    if st.session_state.logged_in:
        return True, st.session_state.username, st.session_state.role

    users = load_users()

    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        if username in users:
            hashed = users[username]["password"].encode()
            if bcrypt.checkpw(password.encode(), hashed):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = users[username]["role"]
                # STOP right after rerun to avoid breaking the return call
                st.rerun()
                return  # <--- prevents further execution
            else:
                st.error("Incorrect password.")
        else:
            st.error("User not found.")

    return False, "", ""

def logout():
    """Clears session state"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
