# modules/barcode_scanner.py

from pyzbar.pyzbar import decode
import streamlit as st
from PIL import Image
import numpy as np
import tempfile
import time
import os

def scan_barcode_from_camera():
    st.subheader("📷 Barcode or QR Scanner")

    mode = st.radio("Select Scanner Mode", ["Upload Image"])

    if mode == "Upload Image":
        uploaded = st.file_uploader("Upload a barcode or QR code image", type=["png", "jpg", "jpeg"])
        if uploaded:
            img = Image.open(uploaded).convert("RGB")
            result = decode(np.array(img))

            if result:
                decoded = result[0].data.decode("utf-8")
                st.success(f"Decoded Value: {decoded}")
                return decoded
            else:
                st.warning("No barcode or QR code detected.")
        return None
