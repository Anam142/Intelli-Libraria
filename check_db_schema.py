import sqlite3
import os

def check_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'intelli_libraria.db')
    print(f"Checking database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Error: Database file does not exist!")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
            
        # Check transactions table structure
        if 'transactions' in [t[0] for t in tables]:
            print("\nTransactions table structure:")
            cursor.execute("PRAGMA table_info(transactions)")
            for column in cursor.fetchall():
                print(f"- {column[1]} ({column[2]})")
                
        # Check users table structure
        if 'users' in [t[0] for t in tables]:
            print("\nUsers table structure:")
            cursor.execute("PRAGMA table_info(users)")
            for column in cursor.fetchall():
                print(f"- {column[1]} ({column[2]})")
                
        # Check books table structure
        if 'books' in [t[0] for t in tables]:
            print("\nBooks table structure:")
            cursor.execute("PRAGMA table_info(books)")
            for column in cursor.fetchall():
                print(f"- {column[1]} ({column[2]})")
                
        # Check for sample data
        print("\nSample data checks:")
        for table in ['transactions', 'users', 'books']:
            if table in [t[0] for t in tables]:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"- {table}: {count} rows")
                except sqlite3.Error as e:
                    print(f"- Error checking {table}: {e}")
        
        # Test overdue query
        print("\nTesting overdue books query:")
        try:
            cursor.execute("""
                SELECT t.id, b.title, u.full_name, t.due_date, 
                       julianday('now') - julianday(t.due_date) as days_overdue
                FROM transactions t
                JOIN books b ON t.book_id = b.id
                JOIN users u ON t.user_id = u.id
                WHERE t.status = 'Issued' 
                AND t.due_date < date('now')
                LIMIT 5
            """)
            overdue = cursor.fetchall()
            print(f"Found {len(overdue)} overdue books")
            for book in overdue:
                print(f"- {book[1]} (Due: {book[3]}, {book[4]:.0f} days overdue)")
        except sqlite3.Error as e:
            print(f"Error testing overdue query: {e}")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database()
