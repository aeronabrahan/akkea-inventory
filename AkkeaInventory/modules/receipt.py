# modules/receipt.py

import os
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from datetime import datetime
from pathlib import Path
import platform
import subprocess
import re

LOGO_PATH = "assets/logo.png"

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def generate_receipt(invoice_no, customer_name, items, total_amount):
    date_today = datetime.now().strftime("%Y-%m-%d")
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    clean_name = sanitize_filename(customer_name)

    save_dir = Path(f"receipts/{clean_name}/{date_today}")
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = f"Receipt_{invoice_no.replace(' ', '_')}.pdf"
    filepath = save_dir / filename

    c = canvas.Canvas(str(filepath), pagesize=LETTER)
    width, height = LETTER

    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, 50, height - 100, width=120, preserveAspectRatio=True)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 70, "Akkea")
    c.setFont("Helvetica", 10)
    c.drawString(200, height - 85, "Crafting Dreams, Printing Wonders.")
    c.drawString(200, height - 100, "Your Go-To for Handmade Joy")
    c.line(40, height - 110, width - 40, height - 110)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 140, f"Invoice #: {invoice_no}")
    c.drawString(300, height - 140, f"Date: {date_now}")
    c.drawString(50, height - 160, f"Customer: {customer_name}")

    c.setFont("Helvetica-Bold", 11)
    y = height - 190
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Qty")
    c.drawString(300, y, "Unit Price")
    c.drawString(400, y, "Total")

    y -= 20
    c.setFont("Helvetica", 10)

    for item in items:
        c.drawString(50, y, item['name'])
        c.drawString(250, y, str(item['qty']))
        c.drawString(300, y, f"₱{item['unit_price']:.2f}")
        c.drawString(400, y, f"₱{item['qty'] * item['unit_price']:.2f}")
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 100

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y, "Total:")
    c.drawString(400, y, f"₱{total_amount:.2f}")

    c.save()
    return str(filepath)

def auto_print(filepath):
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(filepath, "print")
        elif system == "Darwin":
            subprocess.run(["open", "-a", "Preview", filepath])
        elif system == "Linux":
            subprocess.run(["lp", filepath])
        else:
            raise Exception("Unsupported OS")
    except Exception as e:
        print(f"Auto-print failed: {e}")
