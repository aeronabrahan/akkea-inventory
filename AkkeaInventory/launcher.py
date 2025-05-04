import os
import webbrowser
import time
import subprocess
import sys

def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    # Get the absolute path of this script (even inside the .exe)
    base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    app_path = os.path.join(base_dir, "app.py")

    # Launch browser
    open_browser()

    # Run Streamlit app with absolute path
    subprocess.Popen(f'start cmd /K streamlit run "{app_path}"', shell=True)
