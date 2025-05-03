# modules/barcode_scanner.py

import cv2
from pyzbar.pyzbar import decode
import streamlit as st
from PIL import Image
import numpy as np
import tempfile
import time
import os

def scan_barcode_from_camera():
    st.subheader("📷 Barcode or QR Scanner")

    mode = st.radio("Select Scanner Mode", ["Use Webcam", "Upload Image"])

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

    elif mode == "Use Webcam":
        if st.button("Start Camera Scanner"):
            st.info("Press 'Q' on the webcam window to stop scanning.")

            cap = cv2.VideoCapture(0)
            scanned_code = None

            while True:
                ret, frame = cap.read()
                if not ret:
                    st.error("❌ Cannot access webcam.")
                    break

                decoded_objs = decode(frame)
                for obj in decoded_objs:
                    scanned_code = obj.data.decode("utf-8")
                    x, y, w, h = obj.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, scanned_code, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                cv2.imshow("Barcode Scanner - Press Q to stop", frame)

                if cv2.waitKey(1) & 0xFF == ord("q") or scanned_code:
                    break

            cap.release()
            cv2.destroyAllWindows()

            if scanned_code:
                st.success(f"Scanned Code: {scanned_code}")
                return scanned_code
            else:
                st.warning("No barcode detected.")
        return None
