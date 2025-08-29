import sqlite3

def check_status():
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Get the table creation SQL
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        table_sql = cursor.fetchone()
        if table_sql:
            print("\n=== Table Definition ===")
            print(table_sql[0])
        
        # Get distinct status values with their lengths
        cursor.execute("SELECT DISTINCT status, LENGTH(status) as len FROM transactions")
        print("\n=== Current Status Values ===")
        for status, length in cursor.fetchall():
            print(f"Status: '{status}' (Length: {length})")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_status()
