# generate_qr.py

import qrcode
import os
from pathlib import Path

def generate_qr(item_id, save_path="qr_codes"):
    # Ensure the output folder exists
    Path(save_path).mkdir(exist_ok=True)

    # Generate QR
    qr = qrcode.QRCode(
        version=1,  # automatic size
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(item_id)
    qr.make(fit=True)

    # Convert to image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save with the item ID as filename
    filename = f"{item_id}.png"
    filepath = os.path.join(save_path, filename)
    img.save(filepath)

    print(f"✅ QR code saved: {filepath}")

if __name__ == "__main__":
    while True:
        item_id = input("Enter Item ID to generate QR (or 'exit' to quit): ").strip()
        if item_id.lower() == "exit":
            break
        elif item_id:
            generate_qr(item_id)
