# modules/firebase_utils.py

import os
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account

FIREBASE_KEY_PATH = "firebase_key.json"

@st.cache_resource(show_spinner=False)
def get_firestore():
    if not os.path.exists(FIREBASE_KEY_PATH):
        st.error("Firebase key file not found.")
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(FIREBASE_KEY_PATH)
        return firestore.Client(credentials=creds)
    except Exception as e:
        st.error(f"Failed to connect to Firebase: {e}")
        return None


def add_document(collection, doc_id, data):
    db = get_firestore()
    if db:
        db.collection(collection).document(doc_id).set(data)


def update_document(collection, doc_id, data):
    db = get_firestore()
    if db:
        db.collection(collection).document(doc_id).update(data)


def get_document(collection, doc_id):
    db = get_firestore()
    if db:
        doc = db.collection(collection).document(doc_id).get()
        if doc.exists:
            return doc.to_dict()
    return None


def get_all_documents(collection):
    db = get_firestore()
    if db:
        docs = db.collection(collection).stream()
        return {doc.id: doc.to_dict() for doc in docs}
    return {}


def delete_document(collection, doc_id):
    db = get_firestore()
    if db:
        db.collection(collection).document(doc_id).delete()
