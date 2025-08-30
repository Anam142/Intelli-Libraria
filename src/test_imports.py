"""
Test script to verify that imports and database connections work correctly.
Run this script from the project root directory.
"""
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test that all required imports work."""
    print("\n=== Testing Imports ===")
    
    # Test database configuration
    try:
        from db_config import get_connection, DB_PATH
        print(f"✅ db_config imports work")
        print(f"   Database path: {DB_PATH}")
        
        # Test database connection
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"✅ Database connection successful")
            print(f"   Found tables: {', '.join(tables) if tables else 'No tables found'}")
            conn.close()
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    except ImportError as e:
        print(f"❌ Failed to import db_config: {e}")
    
    # Test borrow service
    try:
        from services.borrow_service import BorrowService
        print("\n✅ BorrowService import works")
        
        # Test creating a BorrowService instance
        try:
            service = BorrowService()
            print("✅ BorrowService initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize BorrowService: {e}")
    except ImportError as e:
        print(f"❌ Failed to import BorrowService: {e}")

if __name__ == "__main__":
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python path: {sys.path}")
    test_imports()
