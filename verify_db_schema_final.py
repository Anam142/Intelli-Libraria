import sqlite3
import sys
from pathlib import Path

def verify_database_schema():
    db_path = Path('intelli_libraria.db')
    
    if not db_path.exists():
        print(f"Error: Database file '{db_path}' not found!")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if transactions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
        if not cursor.fetchone():
            print("Error: 'transactions' table not found!")
            return False
        
        # Get transactions table schema
        cursor.execute("PRAGMA table_info(transactions);")
        columns = [col[1] for col in cursor.fetchall()]
        
        print("\n=== Current Transactions Table Schema ===")
        print("Columns:", ", ".join(columns))
        
        # Check for issue_date and borrowed_date
        has_issue_date = 'issue_date' in columns
        has_borrow_date = 'borrow_date' in columns
        
        if has_borrow_date and not has_issue_date:
            print("\n❌ ERROR: Found 'borrow_date' column but missing 'issue_date'")
            print("You need to run the migration script to rename borrow_date to issue_date")
            return False
        elif not has_issue_date:
            print("\n❌ ERROR: Missing 'issue_date' column in transactions table")
            return False
        else:
            print("\n✅ 'issue_date' column exists in transactions table")
            
        # Check for foreign key constraints
        cursor.execute("PRAGMA foreign_key_list(transactions);")
        fk_constraints = cursor.fetchall()
        
        if not fk_constraints:
            print("\n⚠️ WARNING: No foreign key constraints found on transactions table")
        else:
            print("\n✅ Foreign key constraints:")
            for fk in fk_constraints:
                print(f"  - {fk[3]} -> {fk[2]}({fk[4]})")
        
        # Check sample data
        try:
            cursor.execute("SELECT id, user_id, book_id, issue_date, due_date, status FROM transactions LIMIT 1;")
            sample = cursor.fetchone()
            if sample:
                print("\n✅ Sample transaction data:")
                print(f"  ID: {sample[0]}, User ID: {sample[1]}, Book ID: {sample[2]}")
                print(f"  Issue Date: {sample[3]}, Due Date: {sample[4]}, Status: {sample[5]}")
            else:
                print("\nℹ️  No transaction data found in the database")
        except sqlite3.OperationalError as e:
            print(f"\n❌ Error querying transactions: {e}")
            return False
            
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Verifying Database Schema ===\n")
    success = verify_database_schema()
    
    if success:
        print("\n✅ Database schema verification completed successfully!")
    else:
        print("\n❌ Database schema verification found issues!")
        
    input("\nPress Enter to exit...")
