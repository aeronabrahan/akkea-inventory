# modules/db_utils.py

import sqlite3
from pathlib import Path

DB_FILE = Path("db/inventory.db")

def get_connection():
    """Establish a database connection."""
    return sqlite3.connect(DB_FILE)

def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    # Create products table
    cur.execute("""
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

    # Create purchases table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id TEXT PRIMARY KEY,
            invoice_no TEXT,
            transaction_date TEXT,
            item_id TEXT,
            description TEXT,
            quantity INTEGER,
            unit TEXT,
            amount REAL,
            FOREIGN KEY (item_id) REFERENCES products(item_id)
        )
    """)

    # Create sync queue for offline changes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT,
            operation TEXT,
            record TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id TEXT PRIMARY KEY,
            customer_name TEXT,
            transaction_date TEXT,
            item_id TEXT,
            quantity INTEGER,
            unit_price REAL,
            FOREIGN KEY (item_id) REFERENCES products(item_id)
        )
    """)

    conn.commit()
    conn.close()

def run_query(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

def fetch_all(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows