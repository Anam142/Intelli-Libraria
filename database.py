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
                address TEXT
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
        cursor.execute("SELECT id, title, author, isbn, edition, stock FROM books ORDER BY title")
        books = cursor.fetchall()
        return books
    except sqlite3.Error as e:
        print(f"Database error: {e}")
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
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

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
    """Fetch all users from the database."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, status, contact, address FROM users ORDER BY id")
        users = cursor.fetchall()
        return users
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def add_user(name, email, role, status, contact=None, address=None):
    """Add a new user to the database."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # Using a default password for simplicity, as it's a NOT NULL field
        cursor.execute("INSERT INTO users (username, email, role, status, password, contact, address) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (name, email, role, status, '1234', contact, address))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        QMessageBox.warning(None, "Error", "A user with this email already exists.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
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
    """Fetch a single user by their ID."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, status, contact, address FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        return user
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_user(user_id, name, email, role, status, contact=None, address=None):
    """Update an existing user's details."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET username = ?, email = ?, role = ?, status = ?, contact = ?, address = ?
            WHERE id = ?
        """, (name, email, role, status, contact, address, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Initialize the database and tables when this module is imported
create_tables()
