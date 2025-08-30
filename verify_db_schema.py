import sqlite3
import os

def check_database():
    db_path = 'intelli_libraria.db'
    print(f"Checking database: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print("Error: Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        print("\n=== Database Tables ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tables:", ", ".join(tables) if tables else "No tables found")
        
        # Check transactions table structure
        if 'transactions' in tables:
            print("\n=== Transactions Table Structure ===")
            cursor.execute("PRAGMA table_info(transactions)")
            print("Columns:")
            for col in cursor.fetchall():
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULLABLE'}" +
                      f" - DEFAULT: {col[4] if col[4] is not None else 'None'}")
            
            # Check for sample data
            try:
                cursor.execute("SELECT COUNT(*) FROM transactions")
                count = cursor.fetchone()[0]
                print(f"\nFound {count} transaction records")
                
                if count > 0:
                    print("\nSample transaction:")
                    cursor.execute("SELECT * FROM transactions LIMIT 1")
                    col_names = [desc[0] for desc in cursor.description]
                    row = cursor.fetchone()
                    for name, value in zip(col_names, row):
                        print(f"  {name}: {value}")
            except Exception as e:
                print(f"Error reading transactions: {e}")
        
        # Check indexes
        print("\n=== Indexes ===")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='transactions'")
        indexes = cursor.fetchall()
        if indexes:
            for idx in indexes:
                print(f"- {idx[0]}: {idx[1]}")
        else:
            print("No indexes found on transactions table")
        
        return True
        
    except Exception as e:
        print(f"Error checking database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Database Verification Tool ===\n")
    if check_database():
        print("\n✓ Database verification complete")
    else:
        print("\n✗ Database verification failed")
    
    input("\nPress Enter to exit...")
