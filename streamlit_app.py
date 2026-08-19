"""
PartForge Enterprise — Streamlit Cloud Entrypoint.
Redirects to the main dashboard in src/ui/app.py.
"""

import sys
from pathlib import Path

# Ensure root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

# Execute the main UI app
import src.ui.app
