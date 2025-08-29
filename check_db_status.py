import sqlite3

def check_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Get the schema of the transactions table
        cursor.execute("PRAGMA table_info(transactions)")
        columns = cursor.fetchall()
        print("\nTransactions table columns:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Get the table creation SQL to see the CHECK constraint
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        table_sql = cursor.fetchone()
        if table_sql:
            print("\nTable creation SQL:")
            print(table_sql[0])
        
        # Get distinct status values currently in the table
        cursor.execute("SELECT DISTINCT status FROM transactions")
        statuses = cursor.fetchall()
        print("\nCurrent status values in the database:")
        for status in statuses:
            print(f"- {status[0]!r}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
