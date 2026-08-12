"""
AI Product Manager — Entry Point
Run with: python run.py
"""
import subprocess
import sys
import os

def main():
    """Launch the Streamlit UI."""
    app_path = os.path.join(os.path.dirname(__file__), "ui", "app.py")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false",
    ])

if __name__ == "__main__":
    main()
