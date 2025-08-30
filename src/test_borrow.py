import sys
from pathlib import Path
import logging

# Add project root to path to allow absolute imports
PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.borrow_service import BorrowService
from utils.database_utils import verify_database, DB_PATH

def test_borrow(book_id, user_id):
    """Test the book borrowing functionality.
    
    Args:
        book_id: ID of the book to borrow
        user_id: ID of the user borrowing the book
    """
    print("\n=== Testing Book Borrowing ===")
    print(f"Database path: {DB_PATH}")
    
    # Verify database first
    if not verify_database():
        print("Error: Database verification failed!")
        return
        
    print("✓ Database verified successfully")
    
    # Initialize the borrow service
    try:
        service = BorrowService()
        print("✓ BorrowService initialized successfully")
        
        # Attempt to borrow the book
        print(f"\nAttempting to borrow book ID {book_id} for user ID {user_id}")
        success, message = service.borrow_book(user_id, book_id)
        
        if success:
            print(f"✓ Success: {message}")
        else:
            print(f"✗ Failed: {message}")
            
    except Exception as e:
        print(f"✗ Error initializing BorrowService: {str(e)}")
        return

if __name__ == "__main__":
    print("=== Test Book Borrowing ===")
    print("This script tests the book borrowing functionality.")
    print("Make sure the server is not running when running this test.\n")
    
    try:
        # Get input with validation
        while True:
            try:
                book_id = input("Enter book ID (or 'q' to quit): ").strip()
                if book_id.lower() == 'q':
                    print("Exiting...")
                    sys.exit(0)
                    
                user_id = input("Enter user ID: ").strip()
                if not book_id or not user_id:
                    print("Error: Both book ID and user ID are required\n")
                    continue
                    
                test_borrow(int(book_id), int(user_id))
                print("\nTest completed. Press Ctrl+C to exit or run again with new IDs.")
                
            except ValueError:
                print("Error: Please enter valid numeric IDs\n")
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}\n")
                
    except Exception as e:
        print(f"\nA critical error occurred: {str(e)}")
        sys.exit(1)
