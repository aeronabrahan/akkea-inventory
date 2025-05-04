import sqlite3
import os
import sys
import json
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account

# === Safe path for .db file ===
if getattr(sys, 'frozen', False):
    # Running as .exe
    base_dir = os.path.join(os.getenv('APPDATA'), 'AkkeaInventory')
else:
    # Running in dev mode
    base_dir = os.path.abspath(os.path.dirname(__file__))

os.makedirs(base_dir, exist_ok=True)
DB_FILE = os.path.join(base_dir, "akkea_inventory.db")


# === Firebase ===
KEY_PATH = "firebase_key.json"

def get_firestore():
    if not os.path.exists(KEY_PATH):
        st.error("Missing Firebase key: firebase_key.json")
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(KEY_PATH)
        db = firestore.Client(credentials=creds)
        return db
    except Exception as e:
        st.error(f"Firebase error: {e}")
        return None


# === Core Database Operations ===
def get_connection():
    return sqlite3.connect(DB_FILE)

def run_query(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_all(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


# === Sync Queue ===
def queue_sync(table, operation, record_dict):
    run_query(
        "INSERT INTO sync_queue (table_name, operation, record) VALUES (?, ?, ?)",
        (table, operation, json.dumps(record_dict))
    )


# === Firebase Sync Button ===
def sync_to_firebase_button():
    st.subheader("☁️ Sync to Firebase")

    db = get_firestore()
    if not db:
        return

    queue = fetch_all("SELECT id, table_name, operation, record FROM sync_queue")
    if not queue:
        st.success("✅ No records to sync.")
        return

    if st.button("🔁 Sync Now"):
        synced = []
        for row_id, table, op, record_str in queue:
            record = json.loads(record_str)
            try:
                doc_id = record.get("item_id") or record.get("purchase_id") or str(row_id)
                doc_ref = db.collection(table).document(doc_id)

                if op == "insert":
                    doc_ref.set(record)
                elif op == "update":
                    doc_ref.update(record)
                elif op == "delete":
                    doc_ref.delete()

                synced.append(row_id)
            except Exception as e:
                st.warning(f"❌ Failed to sync {row_id}: {e}")

        for row_id in synced:
            run_query("DELETE FROM sync_queue WHERE id = ?", (row_id,))
        st.success(f"✅ Synced {len(synced)} record(s) to Firebase.")


# === Table Initialization ===
def init_db():
    run_query("""
        CREATE TABLE IF NOT EXISTS products (
            item_id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            category TEXT,
            unit TEXT,
            stock INTEGER,
            price REAL,
            photo TEXT,
            qr_code TEXT
        )
    """)

    run_query("""
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT,
            transaction_date TEXT,
            item_id TEXT,
            description TEXT,
            quantity INTEGER,
            unit TEXT,
            amount REAL
        )
    """)

    run_query("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date TEXT,
            item_id TEXT,
            quantity INTEGER,
            price REAL
        )
    """)

    run_query("""
        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT,
            operation TEXT,
            record TEXT
        )
    """)
