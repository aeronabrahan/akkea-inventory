import sqlite3
import os

# ✅ Use a writable path on Streamlit Cloud
DB_FILE = os.path.join("/tmp", "akkea_inventory.db")

def get_connection():
    return sqlite3.connect(DB_FILE)

def run_query(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_all(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

def init_db():
    run_query("""
        CREATE TABLE IF NOT EXISTS products (
            item_id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            category TEXT,
            unit TEXT,
            stock INTEGER,
            price REAL
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
