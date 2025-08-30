import sqlite3

def get_db_info():
    try:
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Get all tables
        print("\n📋 Tables in the database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 Table: {table_name}")
            print("Structure:")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Show row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Rows: {count}")
            
            # Show first few rows if any
            if count > 0:
                print("  Sample data:")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                for row in cursor.fetchall():
                    print(f"    {row}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Database Information 🔍")
    get_db_info()
