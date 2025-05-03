# modules/sync.py

import json
import os
import ast
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
from modules.db_utils import fetch_all, run_query

KEY_PATH = "firebase_key.json"

def init_firestore():
    if not os.path.exists(KEY_PATH):
        st.error("Firebase service key file not found.")
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(KEY_PATH)
        db = firestore.Client(credentials=creds)
        return db
    except Exception as e:
        st.error(f"Failed to connect to Firebase: {e}")
        return None

def queue_sync(table_name, operation, record_dict):
    """Adds operation to local sync queue"""
    run_query(
        "INSERT INTO sync_queue (table_name, operation, record) VALUES (?, ?, ?)",
        (table_name, operation, json.dumps(record_dict))
    )

def sync_with_firebase():
    st.subheader("☁️ Sync with Firebase")

    if st.button("🔄 Sync Now"):
        db = init_firestore()
        if not db:
            return

        queue = fetch_all("SELECT id, table_name, operation, record FROM sync_queue")
        if not queue:
            st.success("✅ Everything is already synced.")
            return

        synced_ids = []
        for row in queue:
            row_id, table_name, operation, record_str = row
            record = ast.literal_eval(record_str)

            try:
                doc_id = record.get("item_id") or record.get("purchase_id") or str(row_id)
                doc_ref = db.collection(table_name).document(doc_id)

                if operation == "insert":
                    doc_ref.set(record)
                elif operation == "update":
                    doc_ref.update(record)
                elif operation == "delete":
                    doc_ref.delete()

                synced_ids.append(row_id)
            except Exception as e:
                st.warning(f"Failed to sync row ID {row_id}: {e}")

        # Remove synced entries
        for sid in synced_ids:
            run_query("DELETE FROM sync_queue WHERE id = ?", (sid,))

        st.success(f"✅ Synced {len(synced_ids)} record(s) to Firebase.")
