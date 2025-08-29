import sqlite3

def check_status():
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Check the current table structure
        cursor.execute("PRAGMA table_info(transactions)")
        print("\n=== Table Structure ===")
        for col in cursor.fetchall():
            print(f"{col[1]} ({col[2]}) - Default: {col[4]}")
        
        # Check the current CHECK constraint
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        table_sql = cursor.fetchone()
        if table_sql:
            print("\n=== Table Definition ===")
            print(table_sql[0])
        
        # Check current status values
        cursor.execute("SELECT DISTINCT status, LENGTH(status) as len FROM transactions")
        print("\n=== Current Status Values ===")
        for row in cursor.fetchall():
            print(f"Status: '{row[0]}' (Length: {row[1]})")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_status()
