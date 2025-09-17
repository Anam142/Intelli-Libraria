import sqlite3
import os

def get_db_connection():
    db_path = os.path.join('data', 'library.db')
    if not os.path.exists(db_path):
        db_path = 'library.db'  # Fallback to root directory
        if not os.path.exists(db_path):
            raise FileNotFoundError("Could not find library database file")
    return sqlite3.connect(db_path)

def check_table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
        (table_name,)
    )
    return cursor.fetchone() is not None

def check_column_exists(conn, table_name, column_name):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    return column_name in columns

def add_status_column(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            ALTER TABLE reservations 
            ADD COLUMN status TEXT DEFAULT 'Active' 
            CHECK(status IN ('Active', 'Fulfilled', 'Cancelled'))
        """)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding status column: {e}")
        return False

def main():
    try:
        conn = get_db_connection()
        
        if not check_table_exists(conn, 'reservations'):
            print("Error: 'reservations' table does not exist in the database.")
            return
            
        print("Checking reservations table structure...")
        
        # Check and add status column if needed
        if not check_column_exists(conn, 'reservations', 'status'):
            print("Adding status column to reservations table...")
            if add_status_column(conn):
                print("Successfully added status column")
            else:
                print("Failed to add status column")
        else:
            print("Status column already exists")
        
        # Show current table structure
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(reservations)")
        print("\nCurrent reservations table structure:")
        print("-" * 50)
        print(f"{'Column':<15} {'Type':<10} {'Not Null':<8} {'Default':<15} {'PK'}")
        print("-" * 50)
        for col in cursor.fetchall():
            print(f"{col[1]:<15} {col[2]:<10} {bool(col[3]):<8} {str(col[4]):<15} {col[5]}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
