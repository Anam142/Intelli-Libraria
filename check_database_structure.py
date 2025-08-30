import sqlite3
import os

def check_database_structure():
    db_path = 'intelli_libraria_fresh.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("=== Database Structure ===\n")
        print(f"Tables: {', '.join(tables)}\n")
        
        # Check each table's structure
        for table in tables:
            print(f"=== {table} ===")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                print(f"  {col['name']} ({col['type']})")
            
            # Show row count
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"\n  Rows: {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 1;")
                sample = cursor.fetchone()
                if sample:
                    print("\n  Sample row:")
                    for key in sample.keys():
                        print(f"    {key}: {sample[key]}")
            
            print("\n" + "-"*40 + "\n")
        
        # Check for any remaining borrow_date references
        cursor.execute("""
            SELECT name, sql 
            FROM sqlite_master 
            WHERE sql LIKE '%borrow_date%';
        """)
        
        borrow_refs = cursor.fetchall()
        if borrow_refs:
            print("⚠️  Found references to 'borrow_date' in:")
            for obj in borrow_refs:
                print(f"- {obj['name']}")
        else:
            print("✅ No references to 'borrow_date' found in the database.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database_structure()
    input("\nPress Enter to exit...")
