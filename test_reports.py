import os
import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMessageBox

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database

def test_database_connection():
    """Test database connection and basic queries"""
    try:
        # Test connection
        conn = database.create_connection()
        if not conn:
            return "Failed to connect to database"
            
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print("\nTables in database:", tables)
        
        # Check transactions table
        if 'transactions' in tables:
            cursor.execute("PRAGMA table_info(transactions)")
            columns = [c[1] for c in cursor.fetchall()]
            print("\nTransactions columns:", columns)
            
            # Check for sample data
            cursor.execute("SELECT COUNT(*) FROM transactions")
            count = cursor.fetchone()[0]
            print(f"Found {count} transactions")
            
            # Test overdue query
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
            print(f"\nFound {len(overdue)} overdue books:")
            for book in overdue:
                print(f"- {book[1]} (Due: {book[3]}, {book[4]:.0f} days overdue)")
        
        # Test get_overdue_books function
        print("\nTesting get_overdue_books():")
        overdue_books = database.get_overdue_books()
        print(f"Found {len(overdue_books)} overdue books")
        for book in overdue_books[:3]:
            print(f"- {book['book_title']} (Due: {book['due_date']}, {book.get('days_overdue', 0):.0f} days overdue)")
        
        # Test get_user_activity function
        print("\nTesting get_user_activity():")
        user_activity = database.get_user_activity(30)
        print(f"Found activity for {len(user_activity)} users")
        for user in user_activity[:3]:
            print(f"- {user['user_name']}: {user.get('total_borrowed', 0)} books borrowed, {user.get('overdue_books', 0)} overdue")
        
        return "Database tests completed successfully!"
        
    except Exception as e:
        return f"Error during database test: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()

def show_message(title, message):
    """Show a message box with the test results"""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Information)
    msg.exec_()

if __name__ == "__main__":
    print("Testing database connection and report generation...")
    result = test_database_connection()
    print(f"\nTest result: {result}")
    
    # Show a message box with the results
    show_message("Database Test Results", result)
