import sqlite3

def check_book_availability(book_id):
    """Check if a book is available for borrowing."""
    try:
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Get book details
        cursor.execute('SELECT id, title, stock FROM books WHERE id = ?', (book_id,))
        book = cursor.fetchone()
        
        if not book:
            print(f"❌ Book with ID {book_id} not found!")
            return False
            
        book_id, title, stock = book
        print(f"\n📚 Book: {title} (ID: {book_id})")
        print(f"   Stock available: {stock}")
        
        return stock > 0
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def check_user_borrow_status(user_id):
    """Check user's current borrow status."""
    try:
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Get user details
        cursor.execute('''
            SELECT id, username, full_name, 
                   COALESCE(role, 'Member') as role,
                   COALESCE(status, 'Active') as status
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User with ID {user_id} not found!")
            return False
            
        user_id, username, full_name, role, status = user
        print(f"\n👤 User: {full_name} (ID: {user_id}, Role: {role}, Status: {status})")
        
        # Check if user is active
        if status.lower() != 'active':
            print(f"❌ User account is not active (Status: {status})")
            return False
            
        # Check current borrow count
        cursor.execute('''
            SELECT COUNT(*) 
            FROM transactions 
            WHERE user_id = ? 
            AND status IN ('Issued', 'Borrowed')
        ''', (user_id,))
        
        borrowed_count = cursor.fetchone()[0] or 0
        max_borrow_limit = 5  # Default borrow limit
        
        print(f"   Books currently borrowed: {borrowed_count}/{max_borrow_limit}")
        
        if borrowed_count >= max_borrow_limit:
            print("❌ User has reached the maximum borrow limit")
            return False
            
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_borrow(book_id, user_id):
    """Test the book borrowing process."""
    print("\n" + "="*50)
    print(f"🔍 Testing borrow process - Book ID: {book_id}, User ID: {user_id}")
    print("="*50)
    
    # Check book availability
    if not check_book_availability(book_id):
        print("\n❌ Cannot proceed: Book is not available for borrowing")
        return False
        
    # Check user's borrow status
    if not check_user_borrow_status(user_id):
        print("\n❌ Cannot proceed: User cannot borrow more books")
        return False
    
    # If we get here, borrowing should be possible
    print("\n✅ All checks passed! This book should be borrowable by this user.")
    return True

if __name__ == "__main__":
    print("📖 Library Book Borrowing Test")
    print("-" * 30)
    
    while True:
        try:
            book_id = input("\nEnter Book ID (or 'q' to quit): ").strip()
            if book_id.lower() == 'q':
                break
                
            user_id = input("Enter User ID: ").strip()
            if user_id.lower() == 'q':
                break
                
            test_borrow(int(book_id), int(user_id))
            
        except ValueError:
            print("❌ Please enter valid numeric IDs")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
    
    print("\n👋 Test completed. Goodbye!")
