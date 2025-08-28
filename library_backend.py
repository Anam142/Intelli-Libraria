import sqlite3
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from enum import Enum
import logging
from database import (
    create_connection,
    get_borrowed_books_count,
    get_book_by_id,
    get_user_by_id
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('library_backend')

class UserRole(str, Enum):
    ADMIN = 'admin'
    LIBRARIAN = 'librarian'
    MEMBER = 'member'

class LibraryBackend:
    def __init__(self, db_path=None):
        # Always use centralized DB path
        if db_path is None:
            from data.database import DB_PATH
            self.db_path = DB_PATH
        else:
            self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        """Initialize database with required tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT CHECK(role IN ('admin', 'librarian', 'member')) DEFAULT 'member',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Books table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    isbn TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    available_quantity INTEGER DEFAULT 1,
                    total_quantity INTEGER DEFAULT 1
                )
            ''')
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date TIMESTAMP NOT NULL,
                    return_date TIMESTAMP,
                    status TEXT DEFAULT 'borrowed',
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (book_id) REFERENCES books(id)
                )
            ''')
            
            # Create admin user if not exists
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                self.add_user(
                    username='admin',
                    email='admin@intellilibraria.test',
                    password='admin123',
                    full_name='System Administrator',
                    role=UserRole.ADMIN
                )
            
            conn.commit()
    
    # User Management
    def add_user(self, username, email, password, full_name, role=UserRole.MEMBER):
        """Add a new user to the system."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, bcrypt.hash(password), full_name, role))
                return True
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed: {e}")
            return False
    
    def authenticate_user(self, username, password):
        """Authenticate a user and return user data if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, full_name, role, password_hash 
                FROM users WHERE username = ?
            ''', (username,))
            user = cursor.fetchone()
            
            if user and bcrypt.verify(password, user[5]):
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'full_name': user[3],
                    'role': user[4]
                }
            return None
    
    # Book Management
    def add_book(self, isbn, title, author, quantity=1, edition='1st Edition'):
        """Add a new book to the library."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO books (isbn, title, author, stock, edition)
                    VALUES (?, ?, ?, ?, ?)
                ''', (isbn, title, author, quantity, edition))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logger.error(f"Book addition failed: {e}")
            return None
    
    def search_books(self, query=None):
        """Search for books by title, author, or ISBN."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            if query:
                query = f"%{query}%"
                cursor.execute('''
                    SELECT * FROM books 
                    WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
                ''', (query, query, query))
            else:
                cursor.execute('SELECT * FROM books')
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Borrowing & Returning
    def borrow_book(self, user_id, book_id, days=14):
        """Borrow a book.
        
        Args:
            user_id: ID of the user borrowing the book
            book_id: ID of the book to borrow
            days: Number of days the book can be borrowed for (default: 14)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                
                # First, verify the book exists and is available
                cursor.execute('''
                    SELECT id, title, stock 
                    FROM books 
                    WHERE id = ?
                ''', (book_id,))
                
                book = cursor.fetchone()
                if not book:
                    msg = f"Book with ID {book_id} not found"
                    logger.error(msg)
                    return False, msg
                
                book_dict = dict(book)
                stock = book_dict.get('stock', 0)
                    
                if stock <= 0:
                    msg = f"Book '{book_dict.get('title', 'Unknown')}' is out of stock (Stock: {stock})"
                    logger.warning(msg)
                    return False, msg
                
                # Check if user exists and is active
                cursor.execute('''
                    SELECT id, full_name, status
                    FROM users 
                    WHERE id = ?
                ''', (user_id,))
                
                user = cursor.fetchone()
                if not user:
                    msg = f"User with ID {user_id} not found"
                    logger.error(msg)
                    return False, msg
                    
                user_dict = dict(user)
                
                # Check if user account is active
                if user_dict.get('status', '').lower() != 'active':
                    msg = f"User account is not active (Status: {user_dict.get('status', 'Unknown')})"
                    logger.warning(msg)
                    return False, msg
                
                # Check if user has reached borrow limit
                cursor.execute('''
                    SELECT COUNT(*) as count 
                    FROM transactions 
                    WHERE user_id = ? 
                    AND status = 'borrowed'
                ''', (user_id,))
                
                borrowed_count = cursor.fetchone()['count']
                max_borrow_limit = 5  # Default borrow limit
                
                if borrowed_count >= max_borrow_limit:
                    msg = f"User has reached the maximum borrow limit of {max_borrow_limit} books"
                    logger.warning(msg)
                    return False, msg
                
                # Calculate due date
                due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
                
                # Start transaction
                cursor.execute('BEGIN TRANSACTION')
                
                # Update book quantity
                cursor.execute('''
                    UPDATE books 
                    SET stock = stock - 1 
                    WHERE id = ? AND stock > 0
                ''', (book_id,))
                
                if cursor.rowcount == 0:
                    msg = f"Failed to update stock for book {book_id}. It may be out of stock."
                    logger.error(msg)
                    conn.rollback()
                    return False, msg
                
                # Create transaction record
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    INSERT INTO transactions 
                    (user_id, book_id, borrow_date, due_date, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'borrowed', ?, ?)
                ''', (user_id, book_id, now, due_date, now, now))
                
                conn.commit()
                logger.info(f"Successfully borrowed book {book_id} for user {user_id}")
                return True, "Book borrowed successfully"
                
        except sqlite3.Error as e:
            logger.error(f"Database error in borrow_book: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in borrow_book: {str(e)}")
            return False, f"An unexpected error occurred: {str(e)}"
    
    def return_book(self, transaction_id):
        """Return a borrowed book.
        
        Args:
            transaction_id: ID of the transaction to return
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Start transaction
                cursor.execute('BEGIN TRANSACTION')
                
                # Get transaction details
                cursor.execute('''
                    SELECT id, book_id, status 
                    FROM transactions 
                    WHERE id = ?
                ''', (transaction_id,))
                
                transaction = cursor.fetchone()
                if not transaction:
                    return False, "Transaction not found"
                    
                transaction = dict(transaction)
                
                # Check if already returned
                if transaction.get('status') == 'returned':
                    return False, "This book has already been returned"
                
                # Update transaction
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    UPDATE transactions 
                    SET return_date = ?,
                        status = 'returned',
                        updated_at = ?
                    WHERE id = ? 
                    AND return_date IS NULL
                ''', (now, now, transaction_id))
                
                if cursor.rowcount == 0:
                    conn.rollback()
                    return False, "Failed to update transaction. It may have already been returned."
                
                # Update book stock
                cursor.execute('''
                    UPDATE books 
                    SET stock = stock + 1,
                        updated_at = ?
                    WHERE id = ?
                ''', (now, transaction['book_id']))
                
                if cursor.rowcount == 0:
                    conn.rollback()
                    return False, "Failed to update book stock. Book not found."
                
                conn.commit()
                logger.info(f"Successfully processed return for transaction {transaction_id}")
                return True, "Book returned successfully"
                
        except sqlite3.Error as e:
            logger.error(f"Database error in return_book: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in return_book: {str(e)}")
            return False, f"An unexpected error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Initialize the library system
    library = LibraryBackend()
    
    # Add a test book
    book_id = library.add_book("1234567890", "Sample Book", "Author Name")
    print(f"Added book with ID: {book_id}")
    
    # Search for books
    books = library.search_books("Sample")
    print("Found books:", books)
