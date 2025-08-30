import os

def find_database_files():
    print("Searching for database files...")
    found = False
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.db', '.sqlite', '.sqlite3', '.db3')):
                db_path = os.path.join(root, file)
                size = os.path.getsize(db_path) / 1024  # Size in KB
                print(f"\nFound database: {db_path}")
                print(f"Size: {size:.2f} KB")
                print("Tables:")
                
                try:
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    
                    if tables:
                        for table in tables:
                            print(f"  - {table[0]}")
                    else:
                        print("  No tables found")
                    
                    conn.close()
                    found = True
                    
                except Exception as e:
                    print(f"  Error reading database: {e}")
    
    if not found:
        print("No database files found in the current directory or its subdirectories.")
    
    print("\nSearch complete.")

if __name__ == "__main__":
    find_database_files()
