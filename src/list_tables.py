import sqlite3

def list_tables(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return
            
        print("Tables in the database:")
        for table in tables:
            print(f"- {table[0]}")
            
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    db_path = "intelli_libraria.db"
    print(f"Listing tables in {db_path}:")
    list_tables(db_path)
