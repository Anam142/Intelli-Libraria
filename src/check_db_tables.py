import sqlite3

def check_database(db_path):
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return
            
        print("Tables in the database:")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * 50)
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"\nTotal rows: {count}")
            
            # Display first few rows if any
            if count > 0:
                print("\nFirst 5 rows:")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = cursor.fetchall()
                for row in rows:
                    print(f"  {row}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    db_path = "intelli_libraria.db"
    print(f"Checking database: {db_path}")
    check_database(db_path)
