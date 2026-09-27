"""
VARSHAAI — Full Stack Launcher
Starts the FastAPI ML backend on http://localhost:8000 and automatically opens the website.
"""

import sys
import os
import time
import webbrowser
import threading

# Add backend directory to sys.path so 'app' can be imported
workspace_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(workspace_root, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def open_browser():
    time.sleep(1.5)
    print("\n[VARSHAAI] Opening http://localhost:8000 in your browser...\n")
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    threading.Thread(target=open_browser, daemon=True).start()
    print("=" * 70)
    print("  VARSHAAI — Regime-Aware AI Rainfall Forecast Post-Processing (SIH 26080)")
    print("  Server starting at: http://localhost:8000")
    print("  API Docs available at: http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=backend_dir)
