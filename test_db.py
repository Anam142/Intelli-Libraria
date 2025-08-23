import sqlite3
import os

# Check if database file exists
from data.database import DB_PATH
if not os.path.exists(DB_PATH):
    print(f"Error: Database file '{DB_PATH}' not found!")
    exit(1)

# Connect to database
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\nTables in database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Check books table structure
    if 'books' in [t[0] for t in tables]:
        cursor.execute("PRAGMA table_info(books)")
        columns = cursor.fetchall()
        print("\nBooks table columns:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Check book count
        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        print(f"\nTotal books in database: {count}")
        
        # Show first 5 books
        if count > 0:
            cursor.execute("SELECT * FROM books LIMIT 5")
            print("\nFirst 5 books:")
            for row in cursor.fetchall():
                print(row)
    
    conn.close()
    
except Exception as e:
    print(f"\nError accessing database: {e}")
    if 'conn' in locals():
        conn.close()
