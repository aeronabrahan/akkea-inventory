# modules/qr_utils.py

import qrcode
import os
from pathlib import Path

QR_DIR = "qr_codes"

def ensure_qr_folder():
    Path(QR_DIR).mkdir(exist_ok=True)

def generate_qr(item_id):
    ensure_qr_folder()
    filename = f"{item_id}.png"
    filepath = os.path.join(QR_DIR, filename)

    if os.path.exists(filepath):
        return filepath  # Already exists

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(item_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)
    return filepath

def generate_qr_for_all(item_ids):
    ensure_qr_folder()
    for item_id in item_ids:
        generate_qr(item_id)
