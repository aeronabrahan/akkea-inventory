# modules/barcode_scanner.py

import streamlit as st
import os

def scan_barcode_from_camera():
    if "STREAMLIT_SERVER_ROOT" in os.environ:
        st.warning("📷 Camera barcode scanning is not supported on Streamlit Cloud.")
        return None

    try:
        import cv2
        from pyzbar.pyzbar import decode
    except ImportError:
        st.error("📦 Required libraries (cv2, pyzbar) not installed or supported in this environment.")
        return None

    st.warning("📷 Barcode scanning is only supported in the local Windows EXE version.")
    return None
