"""
AI Product Manager — Entry Point
Run with: python run.py

Live deployment: https://sprint-craft.streamlit.app
"""
import subprocess
import sys
import os

LIVE_URL = "https://sprint-craft.streamlit.app"

def main():
    """Launch the Streamlit UI locally."""
    app_path = os.path.join(os.path.dirname(__file__), "ui", "app.py")
    print(f"\n🌐 Live app: {LIVE_URL}")
    print("🖥️  Local:    http://localhost:8501\n")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "true",
    ])

if __name__ == "__main__":
    main()
