import sqlite3

def check_database_structure():
    try:
        # Connect to the database
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("Tables in the database:")
        print("-" * 30)
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * 30)
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Print column information
            print("Column Name | Type | Not Null | Default Value | PK")
            print("-" * 60)
            for col in columns:
                cid, name, type_, notnull, dflt_value, pk = col
                print(f"{name} | {type_} | {bool(notnull)} | {dflt_value} | {pk}")
            
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nTotal rows: {count}")
            
            # Show sample data if any
            if count > 0:
                print("\nSample data (first 3 rows):")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                for row in cursor.fetchall():
                    print(row)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error checking database structure: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_database_structure()
