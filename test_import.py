import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.admin_login import AdminLogin
    print("Successfully imported AdminLogin!")
except ImportError as e:
    print(f"Error importing AdminLogin: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
