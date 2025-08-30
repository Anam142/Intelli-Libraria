"""
Project Paths Configuration
--------------------------
This module sets up the project's root path and ensures consistent imports.
"""
import os
import sys
from pathlib import Path

# Get the project root directory (the directory containing this file)
PROJECT_ROOT = Path(__file__).parent.absolute()

# Add the project root to Python path if not already there
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Define common paths
DATA_DIR = PROJECT_ROOT / 'data'
DB_PATH = DATA_DIR / 'library.db'

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True, parents=True)

def get_absolute_path(relative_path: str) -> str:
    """Convert a relative path to an absolute path relative to project root."""
    return str(PROJECT_ROOT / relative_path)

# Example usage:
# from project_paths import PROJECT_ROOT, DB_PATH
# from services.borrow_service import BorrowService
