import streamlit as st
import bcrypt

# Pre-hashed passwords (use bcrypt.hashpw("yourpassword".encode(), bcrypt.gensalt()))
def load_users():
    return {
        "admin": {
            "password": b"$2b$12$LZJhrYxJXQ6vZYxzqKfq9ubtNEn6XT8u7NT0J0uHez8LCK6uKUcHG",  # password: admin
            "role": "admin"
        },
        "staff": {
            "password": b"$2b$12$5F8K5sToXUqvJw3KxM5peOBFD7cI6Fu3Ygu3YarFv4l7EZaN4iFYK",  # password: staff
            "role": "staff"
        }
    }


# Utility function to hash new passwords (not used in app flow, just for reference)
def hash_password(plain_pw):
    return bcrypt.hashpw(plain_pw.encode(), bcrypt.gensalt())

# To generate new passwords (you can run this in a separate script if needed)
if __name__ == "__main__":
    print("Admin:", hash_password("admin"))
    print("Staff:", hash_password("staff"))

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
            hashed = users[username]["password"]
            if bcrypt.checkpw(password.encode(), hashed):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = users[username]["role"]
                st.rerun()  # safely rerun after setting state
                return  # prevents continued execution
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
