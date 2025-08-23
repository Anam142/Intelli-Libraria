import sqlite3
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('library_backend')

class UserRole(str, Enum):
    ADMIN = 'admin'
    LIBRARIAN = 'librarian'
    MEMBER = 'member'

class LibraryBackend:
    def __init__(self, db_path='intelli_libraria.db'):
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
    def add_book(self, isbn, title, author, quantity=1):
        """Add a new book to the library."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO books (isbn, title, author, available_quantity, total_quantity)
                    VALUES (?, ?, ?, ?, ?)
                ''', (isbn, title, author, quantity, quantity))
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logger.error(f"Book addition failed: {e}")
            return None
    
    def search_books(self, query=None):
        """Search for books by title, author, or ISBN."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if query:
                query = f"%{query}%"
                cursor.execute('''
                    SELECT * FROM books 
                    WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
                ''', (query, query, query))
            else:
                cursor.execute('SELECT * FROM books')
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # Borrowing & Returning
    def borrow_book(self, user_id, book_id, days=14):
        """Borrow a book."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                due_date = datetime.now() + timedelta(days=days)
                
                # Check if book is available
                cursor.execute('''
                    UPDATE books 
                    SET available_quantity = available_quantity - 1
                    WHERE id = ? AND available_quantity > 0
                    RETURNING id
                ''', (book_id,))
                
                if not cursor.fetchone():
                    return False
                
                # Create transaction
                cursor.execute('''
                    INSERT INTO transactions (user_id, book_id, due_date)
                    VALUES (?, ?, ?)
                ''', (user_id, book_id, due_date))
                
                conn.commit()
                return True
                
            except sqlite3.Error as e:
                conn.rollback()
                logger.error(f"Error borrowing book: {e}")
                return False
    
    def return_book(self, transaction_id):
        """Return a borrowed book."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                
                # Update transaction
                cursor.execute('''
                    UPDATE transactions 
                    SET return_date = CURRENT_TIMESTAMP,
                        status = 'returned'
                    WHERE id = ? AND return_date IS NULL
                    RETURNING book_id
                ''', (transaction_id,))
                
                book_id = cursor.fetchone()
                if not book_id:
                    return False
                
                # Update book availability
                cursor.execute('''
                    UPDATE books 
                    SET available_quantity = available_quantity + 1
                    WHERE id = ?
                ''', (book_id[0],))
                
                conn.commit()
                return True
                
            except sqlite3.Error as e:
                conn.rollback()
                logger.error(f"Error returning book: {e}")
                return False

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
