import sqlite3
import os

def check_database():
    db_path = 'data/library.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at: {os.path.abspath(db_path)}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\n📋 Database Tables:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Check users table
        if 'users' in [t[0] for t in tables]:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            print("\n👥 Users:")
            for user in users:
                print(f"ID: {user[0]}, Username: {user[2]}, Email: {user[3]}, Role: {user[9]}")
        
        # Check books table
        if 'books' in [t[0] for t in tables]:
            cursor.execute("SELECT COUNT(*) FROM books")
            book_count = cursor.fetchone()[0]
            print(f"\n📚 Total books: {book_count}")
            
            if book_count > 0:
                cursor.execute("SELECT id, title, author, available FROM books LIMIT 5")
                print("\nSample books:")
                for book in cursor.fetchall():
                    print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Available: {book[3]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Checking database contents...")
    check_database()
