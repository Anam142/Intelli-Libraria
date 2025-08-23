import sys
import os

def check_environment():
    print("Python Environment Check")
    print("=" * 50)
    
    # Python version
    print(f"Python Version: {sys.version}")
    
    # Current working directory
    print(f"\nCurrent Directory: {os.getcwd()}")
    
    # List files in current directory
    print("\nFiles in current directory:")
    for f in os.listdir('.'):
        if f.endswith(('.py', '.db')):
            print(f"- {f}")
    
    # Check for required packages
    print("\nChecking required packages:")
    try:
        import sqlite3
        print("✅ sqlite3 (built-in)")
    except ImportError:
        print("❌ sqlite3 not available")
    
    try:
        import passlib.hash
        print("✅ passlib")
    except ImportError:
        print("❌ passlib not installed")
        print("   Install with: pip install passlib")

if __name__ == "__main__":
    check_environment()
