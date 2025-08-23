from library_backend import LibraryBackend, UserRole

def test_library():
    # Initialize the library system
    print("Initializing library system...")
    library = LibraryBackend('test_library.db')
    
    print("\n=== Testing Authentication ===")
    # Test admin login
    admin = library.authenticate_user('admin', 'admin123')
    if admin:
        print(f"✅ Admin login successful: {admin['full_name']} ({admin['role']})")
    else:
        print("❌ Admin login failed")
    
    print("\n=== Adding Test Book ===")
    # Add a test book
    book_id = library.add_book(
        isbn='9781234567890',
        title='Sample Book',
        author='Test Author',
        quantity=5
    )
    if book_id:
        print(f"✅ Added book with ID: {book_id}")
    else:
        print("❌ Failed to add book")
    
    print("\n=== Listing Books ===")
    # List all books
    books = library.search_books()
    if books:
        print("\nAvailable Books:")
        for book in books:
            print(f"- {book['title']} by {book['author']} (Available: {book['available_quantity']}/{book['total_quantity']})")
    else:
        print("❌ No books found")

if __name__ == "__main__":
    test_library()
