"""
Test script to verify database connection and table structure.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database_utils import get_connection, verify_database

def main():
    print("=== Testing Database Connection ===")
    
    # Test database verification
    if not verify_database():
        print("❌ Database verification failed!")
        return
    
    # Test connection and basic queries
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Test query to check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nFound tables: {', '.join(tables)}")
        
        # Check transactions table structure
        cursor.execute("PRAGMA table_info(transactions)")
        print("\nTransactions table structure:")
        for col in cursor.fetchall():
            print(f"  {col[1]} ({col[2]}) {'NOT NULL' if col[3] else ''} {col[4] or ''}")
        
        # Check status values in transactions
        cursor.execute("SELECT DISTINCT status FROM transactions")
        statuses = [row[0] for row in cursor.fetchall()]
        print(f"\nCurrent status values in transactions: {statuses}")
        
        print("\n✅ Database connection and structure look good!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
