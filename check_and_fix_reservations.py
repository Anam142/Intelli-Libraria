import sqlite3
import os

def check_and_fix_db():
    db_path = os.path.join('data', 'library.db')
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if status column exists
        cursor.execute("PRAGMA table_info(reservations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'status' not in columns:
            print("Adding status column to reservations table...")
            cursor.execute("""
                ALTER TABLE reservations 
                ADD COLUMN status TEXT DEFAULT 'Active' 
                CHECK(status IN ('Active', 'Fulfilled', 'Cancelled'))
            """)
            conn.commit()
            print("Successfully added status column to reservations table")
        else:
            print("status column already exists in reservations table")
            
        # Verify the table structure
        cursor.execute("PRAGMA table_info(reservations)")
        print("\nCurrent reservations table structure:")
        print("-" * 50)
        print("Column Name | Type | Not Null | Default Value | PK")
        print("-" * 50)
        for col in cursor.fetchall():
            print(f"{col[1]:<11} | {col[2]:<4} | {bool(col[3]):<8} | {str(col[4]):<13} | {col[5]}")
        
        return True
        
    except Exception as e:
        print(f"Error checking/updating database: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if check_and_fix_db():
        print("\nDatabase check and update completed successfully!")
    else:
        print("\nThere were issues with the database check/update.")
