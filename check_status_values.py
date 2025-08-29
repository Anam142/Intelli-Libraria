import sqlite3
import sys

def check_status_values(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the schema of the transactions table
        cursor.execute("PRAGMA table_info(transactions)")
        columns = cursor.fetchall()
        print("\nTransactions table columns:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Try to get the CHECK constraint for the status column
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        table_sql = cursor.fetchone()[0]
        print("\nTable creation SQL:")
        print(table_sql)
        
        # Get distinct status values in the table
        cursor.execute("SELECT DISTINCT status FROM transactions")
        statuses = cursor.fetchall()
        print("\nCurrent status values in the database:")
        for status in statuses:
            print(f"- {status[0]!r} (type: {type(status[0]).__name__})")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    db_path = "library.db"  # Default path - update if different
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    check_status_values(db_path)
