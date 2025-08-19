import sqlite3
from PyQt5.QtWidgets import QMessageBox

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect("intelli_libraria.db")
    except sqlite3.Error as e:
        print(e)
    return conn

def update_database_schema(conn):
    """Update the database schema to match the current application requirements."""
    try:
        cursor = conn.cursor()
        # Add phone column if it doesn't exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'phone' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
            conn.commit()
            print("Database schema updated: Added 'phone' column to users table")
    except sqlite3.Error as e:
        print(f"Error updating database schema: {e}")

def execute_query(query, params=()):
    """Execute a query and return the results.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query. Defaults to ().
        
    Returns:
        list: List of dictionaries representing the query results
    """
    conn = create_connection()
    if conn is not None:
        try:
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            # Convert Row objects to dictionaries
            return [dict(row) for row in result]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            conn.close()
    return []

def create_tables():
    """Create the necessary tables if they don't exist."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Create users table (if not exists)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT DEFAULT '1234',
                role TEXT,
                status TEXT,
                contact TEXT,
                address TEXT,
                phone TEXT
            )
            ''')
            # Create books table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT NOT NULL UNIQUE,
                edition TEXT,
                stock INTEGER NOT NULL
            )
            ''')
            # Create reservations table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                reservation_date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
            """)
            # Update database schema if needed
            update_database_schema(conn)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()

def add_book(title, author, isbn, edition, stock):
    """Add a new book to the books table."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author, isbn, edition, stock) VALUES (?, ?, ?, ?, ?)",
                       (title, author, isbn, edition, stock))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Handle cases like duplicate ISBNs if you add a UNIQUE constraint
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_books():
    """Fetch all books from the database."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                id, 
                title, 
                author, 
                isbn, 
                edition,
                stock,
                id as book_code,  # Using id as book_code
                '' as publisher,  # Not in schema
                '' as publication_year,  # Not in schema
                '' as category  # Not in schema
            FROM books 
            ORDER BY title
        """)
        books = cursor.fetchall()
        return books
    except sqlite3.Error as e:
        print(f"Database error in get_all_books: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_next_book_id():
    """Get the next available book ID."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) + 1 FROM books")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 1
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 1
    finally:
        if conn:
            conn.close()

def get_book_by_id(book_id):
    """Fetch a single book by its ID."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, author, isbn, edition, stock 
            FROM books 
            WHERE id = ?
            """, 
            (book_id,)
        )
        book = cursor.fetchone()
        if book:
            return {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'isbn': book[3],
                'edition': book[4],
                'stock': book[5]
            }
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_book_with_id(book_id, title, author, isbn, edition, stock):
    """Add a new book with a specific ID to the books table."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO books (id, title, author, isbn, edition, stock) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (book_id, title, author, isbn, edition, stock))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_book(book_id):
    """Delete a book from the database by its ID."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting book: {e}")
            return False
        finally:
            conn.close()
    return False

def update_book(book_id, title, author, isbn, edition, stock):
    """Update an existing book in the database.
    
    Args:
        book_id (int): ID of the book to update
        title (str): Book title
        author (str): Book author
        isbn (str): Book ISBN
        edition (str): Book edition
        stock (int): Number of copies in stock
        
    Returns:
        bool: True if the update was successful, False otherwise
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE books 
                SET title = ?, author = ?, isbn = ?, edition = ?, stock = ?
                WHERE id = ?
            ''', (title, author, isbn, edition, stock, book_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating book: {e}")
            return False
        finally:
            conn.close()
    return False

def add_reservation(user_id, book_id, reservation_date):
    """Add a new reservation to the reservations table."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reservations (user_id, book_id, reservation_date) VALUES (?, ?, ?)",
                       (user_id, book_id, reservation_date))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_reservations():
    """Fetch all reservations with user and book details."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # Join query to get user and book information
        cursor.execute("""
        SELECT r.id, b.title, u.username, r.reservation_date
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        JOIN books b ON r.book_id = b.id
        ORDER BY r.reservation_date DESC
        """)
        reservations = cursor.fetchall()
        return reservations
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def delete_reservation(reservation_id):
    """Delete a reservation from the database by its ID."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_users():
    """Fetch all users from the database.
    
    Returns:
        list: A list of dictionaries containing user data
    """
    conn = create_connection()
    try:
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_code, full_name, email, phone, role, status, 
                   contact, address, created_at, updated_at 
            FROM users 
            ORDER BY full_name
        """)
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def add_user(full_name, email, role, status, phone=None, contact=None, address=None):
    """Add a new user to the database.
    
    Args:
        full_name (str): User's full name
        email (str): User's email (must be unique)
        role (str): User role ('Admin' or 'Member')
        status (str): User status ('Active' or 'Inactive')
        phone (str, optional): User's phone number
        contact (str, optional): Alternative contact information
        address (str, optional): User's address
        
    Returns:
        bool: True if user was added successfully, False otherwise
    """
    import uuid
    
    # Generate a unique user code (e.g., 'USR-xxxxx')
    user_code = f"USR-{str(uuid.uuid4())[:8].upper()}"
    
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users 
            (user_code, full_name, email, phone, role, status, contact, address) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_code, full_name, email, phone or contact, role, status, contact, address))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.email" in str(e):
            QMessageBox.warning(None, "Error", "A user with this email already exists.")
        elif "UNIQUE constraint failed: users.user_code" in str(e):
            # Retry with a new user code if there's a collision (very rare)
            return add_user(full_name, email, role, status, phone, contact, address)
        else:
            QMessageBox.warning(None, "Error", "Failed to add user. Please check the data and try again.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        QMessageBox.warning(None, "Error", f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_user(user_id):
    """Delete a user from the database by their ID."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_user_by_id(user_id):
    """Fetch a single user by their ID.
    
    Args:
        user_id (int): The ID of the user to fetch
        
    Returns:
        dict: A dictionary containing user data, or None if not found
    """
    conn = create_connection()
    try:
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_code, full_name, email, phone, role, status, contact, address, 
                   created_at, updated_at 
            FROM users 
            WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_user(user_id, full_name, email, role, status, phone=None, contact=None, address=None):
    """Update an existing user's details.
    
    Args:
        user_id (int): ID of the user to update
        full_name (str): User's full name
        email (str): User's email (must be unique)
        role (str): User role ('Admin' or 'Member')
        status (str): User status ('Active' or 'Inactive')
        phone (str, optional): User's phone number
        contact (str, optional): Alternative contact information
        address (str, optional): User's address
        
    Returns:
        bool: True if user was updated successfully, False otherwise
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET full_name = ?, email = ?, phone = ?, role = ?, status = ?, contact = ?, address = ?
            WHERE id = ?
        """, (full_name, email, phone or contact, role, status, contact, address, user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.email" in str(e):
            QMessageBox.warning(None, "Error", "A user with this email already exists.")
        else:
            QMessageBox.warning(None, "Error", "Failed to update user. Please check the data and try again.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        QMessageBox.warning(None, "Error", f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Initialize the database and tables when this module is imported
create_tables()
