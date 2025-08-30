import sqlite3
import os

def inspect_database():
    db_path = 'intelli_libraria.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=== Database Inspection ===\n")
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("Tables in database:", ", ".join(tables))
        
        # Check transactions table
        if 'transactions' in tables:
            print("\n=== Transactions Table ===")
            
            # Get schema
            cursor.execute("PRAGMA table_info(transactions);")
            columns = cursor.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"  {col['name']} ({col['type']})")
            
            # Check for issue_date and borrow_date
            col_names = [col['name'] for col in columns]
            if 'issue_date' in col_names:
                print("\n✅ 'issue_date' column exists")
            if 'borrow_date' in col_names:
                print("⚠️  'borrow_date' column still exists (should be migrated to issue_date)")
            
            # Show sample data
            try:
                cursor.execute("SELECT * FROM transactions LIMIT 1;")
                sample = cursor.fetchone()
                if sample:
                    print("\nSample transaction:")
                    for key in sample.keys():
                        print(f"  {key}: {sample[key]}")
            except Exception as e:
                print(f"\n⚠️  Error reading transaction data: {e}")
        
        # Check for views or triggers that might reference borrow_date
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type IN ('view', 'trigger') AND sql LIKE '%borrow_date%';")
        problematic_objects = cursor.fetchall()
        
        if problematic_objects:
            print("\n⚠️  Found database objects that reference 'borrow_date':")
            for obj in problematic_objects:
                print(f"\n{obj['name']}:")
                print("  " + "\n  ".join(obj['sql'].split('\n')))
        
    except Exception as e:
        print(f"\n❌ Error inspecting database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    inspect_database()
    input("\nPress Enter to exit...")
