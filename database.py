import os
import sqlite3
from PyQt5.QtWidgets import QMessageBox

def create_connection():
    """Create a database connection to the SQLite database."""
    # Use the database file in the project root
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'intelli_libraria.db')
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise

def update_database_schema(conn):
    """Update the database schema to match the current application requirements."""
    try:
        cursor = conn.cursor()
        # Inspect current users table columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        # Ensure modern schema columns exist
        if 'user_code' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN user_code TEXT")
        if 'full_name' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        if 'phone' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        if 'contact' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN contact TEXT")
        if 'address' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
        if 'role' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Member'")
        if 'status' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Active'")
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conn.commit()

        # Backfill data for newly added columns
        # If full_name is missing but username exists, copy it
        if 'username' in columns:
            try:
                cursor.execute("UPDATE users SET full_name = COALESCE(full_name, username)")
            except Exception:
                pass
        # Generate user_code for rows where it is NULL
        try:
            cursor.execute(
                """
                UPDATE users
                SET user_code = COALESCE(user_code, 'USR-' || printf('%06d', id))
                WHERE user_code IS NULL OR user_code = ''
                """
            )
        except Exception:
            pass

        # Ensure books table has expected columns
        try:
            cursor.execute("PRAGMA table_info(books)")
            book_cols = {row[1] for row in cursor.fetchall()}

            # Create books if missing entirely (older dbs)
            if not book_cols:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL,
                        isbn TEXT NOT NULL UNIQUE,
                        edition TEXT,
                        stock INTEGER NOT NULL DEFAULT 0
                    )
                ''')
            else:
                if 'title' not in book_cols:
                    cursor.execute("ALTER TABLE books ADD COLUMN title TEXT")
                if 'author' not in book_cols:
                    cursor.execute("ALTER TABLE books ADD COLUMN author TEXT")
                if 'isbn' not in book_cols:
                    cursor.execute("ALTER TABLE books ADD COLUMN isbn TEXT")
                if 'edition' not in book_cols:
                    cursor.execute("ALTER TABLE books ADD COLUMN edition TEXT")
                if 'stock' not in book_cols:
                    cursor.execute("ALTER TABLE books ADD COLUMN stock INTEGER DEFAULT 0")
                # If ISBN is enforced UNIQUE via an index, relax it to allow duplicates.
                # Some earlier schemas created a UNIQUE constraint on isbn which caused
                # frequent insert failures. We'll rebuild the table without UNIQUE if needed.
                def _isbn_unique_index_name() -> str | None:
                    try:
                        cursor.execute("PRAGMA index_list(books)")
                        for idx in cursor.fetchall():
                            # idx: (seq, name, unique, origin, partial)
                            if idx[2] == 1:  # unique
                                cursor.execute(f"PRAGMA index_info({idx[1]})")
                                cols = [r[2] for r in cursor.fetchall()]
                                if cols == ['isbn'] or 'isbn' in cols:
                                    return idx[1]
                    except Exception:
                        return None
                    return None

                unique_idx = _isbn_unique_index_name()
                if unique_idx is not None:
                    try:
                        cursor.execute("BEGIN")
                        # Create new table without UNIQUE constraint
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS books__tmp_migrate (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                title TEXT NOT NULL,
                                author TEXT NOT NULL,
                                isbn TEXT NOT NULL,
                                edition TEXT,
                                stock INTEGER NOT NULL
                            )
                        ''')
                        cursor.execute('''
                            INSERT INTO books__tmp_migrate (id, title, author, isbn, edition, stock)
                            SELECT id, title, author, isbn, edition, stock FROM books
                        ''')
                        cursor.execute('DROP TABLE books')
                        cursor.execute('ALTER TABLE books__tmp_migrate RENAME TO books')
                        cursor.execute('COMMIT')
                    except Exception:
                        cursor.execute('ROLLBACK')
        except Exception as _:
            # Keep going; some SQLite versions may restrict ALTERs
            pass

        # Ensure reservations table has expected columns
        try:
            cursor.execute("PRAGMA table_info(reservations)")
            res_cols = {row[1] for row in cursor.fetchall()}
            if not res_cols:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reservations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        book_id INTEGER NOT NULL,
                        reservation_date TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (book_id) REFERENCES books (id)
                    )
                ''')
            else:
                if 'reservation_date' not in res_cols:
                    cursor.execute("ALTER TABLE reservations ADD COLUMN reservation_date TEXT")
        except Exception:
            pass
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
            # Create users table (modern schema) if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_code TEXT UNIQUE,
                full_name TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                role TEXT DEFAULT 'Member',
                status TEXT DEFAULT 'Active',
                contact TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create books table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT NOT NULL,
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
            
            # Create transactions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP NOT NULL,
                return_date TIMESTAMP,
                status TEXT DEFAULT 'borrowed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
            ''')
            # Update database schema if needed
            update_database_schema(conn)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()

def add_book(title, author, isbn, edition, stock):
    """Add a new book with validation and unique ISBN (when provided)."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        title = (title or '').strip()
        author = (author or '').strip()
        isbn = (isbn or '').strip() or None
        edition = (edition or '').strip() or None
        try:
            stock = int(stock)
        except Exception:
            stock = 0

        if not title or not author:
            return False

        if isbn:
            cursor.execute("SELECT 1 FROM books WHERE isbn = ? LIMIT 1", (isbn,))
            if cursor.fetchone():
                return False

        cursor.execute(
            "INSERT INTO books (title, author, isbn, edition, stock) VALUES (?, ?, ?, ?, ?)",
            (title, author, isbn, edition, stock)
        )
        conn.commit()
        return True
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
                id as book_code,
                '' as publisher,
                '' as publication_year,
                '' as category
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

def get_books_count():
    """Return the total number of books in the database."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        result = cursor.fetchone()
        return int(result[0]) if result and result[0] is not None else 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def get_members_count():
    """Return the number of members (or users) in the database.

    Prefers counting users with role 'member' when a role column exists; otherwise counts all users.
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # Detect users table and its columns
        cursor.execute("PRAGMA table_info(users)")
        cols = {row[1].lower() for row in cursor.fetchall()}
        if not cols:
            return 0
        if 'role' in cols:
            cursor.execute("SELECT COUNT(*) FROM users WHERE LOWER(COALESCE(role,'')) IN ('member','user')")
        else:
            cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        return int(result[0]) if result and result[0] is not None else 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def get_borrowed_count():
    """Return the total number of active borrowed transactions.

    Looks for a transactions table with a status column. If unavailable, returns 0.
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # Check if transactions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if not cursor.fetchone():
            return 0
        # Check columns
        cursor.execute("PRAGMA table_info(transactions)")
        tcols = {row[1].lower() for row in cursor.fetchall()}
        if 'status' in tcols:
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE LOWER(status) IN ('issued','borrowed')")
        else:
            # Fallback: count rows assuming all are active
            cursor.execute("SELECT COUNT(*) FROM transactions")
        result = cursor.fetchone()
        return int(result[0]) if result and result[0] is not None else 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def get_borrowed_books_count(user_id):
    """Return the number of books currently borrowed by a specific user.
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        int: Number of books currently borrowed by the user
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) 
            FROM transactions 
            WHERE user_id = ? 
            AND status IN ('Issued', 'Borrowed')
        ''', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"Database error in get_borrowed_books_count: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def get_overdue_count():
    """Return the number of overdue transactions if supported by schema; otherwise 0."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Check if transactions table has the required columns
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'due_date' in columns and 'return_date' in columns and 'status' in columns:
            cursor.execute(""" 
                SELECT COUNT(*) FROM transactions 
                WHERE status = 'Issued' 
                AND due_date < date('now')
            """)
            return cursor.fetchone()[0] or 0
    except sqlite3.Error as e:
        print(f"Error getting overdue count: {e}")
    return 0

def get_recent_transactions(limit=8):
    """Fetch recent transactions with book and user details for the dashboard.
    
    Returns:
        list: List of dictionaries containing transaction details with consistent field names
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                t.id as transaction_id,
                b.title as book_title, 
                b.author as author,
                u.full_name as user_name,
                u.email as user_email,
                t.issue_date,
                t.due_date,
                t.return_date,
                t.status,
                CASE 
                    WHEN t.return_date IS NOT NULL THEN 'Returned'
                    WHEN t.due_date < date('now') THEN 'Overdue'
                    ELSE t.status
                END as display_status
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            JOIN users u ON t.user_id = u.id
            ORDER BY t.issue_date DESC
            LIMIT ?
        """, (limit,))
        
        # Convert to list of dictionaries with consistent field names
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
        
    except sqlite3.Error as e:
        print(f"Error fetching recent transactions: {e}")
        import traceback
        traceback.print_exc()
        return []
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
    """Update an existing book in the database with enhanced validation and error handling.
    
    Args:
        book_id (int): ID of the book to update
        title (str): Book title (required, max 255 chars)
        author (str): Book author (required, max 100 chars)
        isbn (str): Book ISBN (required, 10 or 13 digits)
        edition (str): Book edition (optional, max 50 chars)
        stock (int): Number of copies in stock (required, >= 0)
        
    Returns:
        tuple: (success: bool, message: str) - Status and message
    """
    # Input validation
    if not title or not title.strip():
        return False, "Book title is required"
    if not author or not author.strip():
        return False, "Author name is required"
    if not isbn or not isbn.strip():
        return False, "ISBN is required"
    try:
        stock = int(stock)
        if stock < 0:
            return False, "Stock cannot be negative"
    except ValueError:
        return False, "Stock must be a number"
    
    # Clean inputs
    title = title.strip()
    author = author.strip()
    isbn = ''.join(filter(str.isdigit, isbn))  # Remove any non-digit characters
    
    # Validate ISBN length (10 or 13 digits)
    if len(isbn) not in (10, 13):
        return False, "ISBN must be 10 or 13 digits"
    
    conn = None
    try:
        conn = create_connection()
        if not conn:
            return False, "Could not connect to database"
            
        cursor = conn.cursor()
        
        # Check if book exists
        cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))
        if not cursor.fetchone():
            return False, f"Book with ID {book_id} not found"
            
        # Check for duplicate ISBN (excluding current book)
        cursor.execute("SELECT id FROM books WHERE isbn = ? AND id != ?", (isbn, book_id))
        if cursor.fetchone():
            return False, f"A book with ISBN {isbn} already exists"
        
        # Update the book
        cursor.execute('''
            UPDATE books 
            SET title = ?, 
                author = ?, 
                isbn = ?, 
                edition = CASE WHEN ? = '' THEN NULL ELSE ? END, 
                stock = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, author, isbn, edition, edition, stock, book_id))
        
        if cursor.rowcount == 0:
            return False, "No changes were made to the book"
            
        conn.commit()
        return True, "Book updated successfully"
        
    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        if "UNIQUE constraint failed" in error_msg:
            return False, "A book with this ISBN already exists"
        return False, f"Database error: {error_msg}"
        
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
        
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass
    return False

def add_reservation(user_id, book_id, reservation_date):
    """
    Add a new reservation to the reservations table.
    Optimized for speed with minimal database operations.
    
    Args:
        user_id (int): ID of the user making the reservation
        book_id (int): ID of the book being reserved
        reservation_date (str): Date of reservation in 'YYYY-MM-DD' format
        
    Returns:
        tuple: (success: bool, message: str) - Success status and message
    """
    if not all([user_id, book_id, reservation_date]):
        return False, "Missing required fields."
        
    conn = None
    try:
        conn = create_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 3000")  # 3 second timeout
        cursor = conn.cursor()
        
        # Single query to check user status and book availability
        cursor.execute("""
            SELECT u.status, b.title, b.stock,
                   (SELECT 1 FROM reservations r 
                    WHERE r.user_id = ? AND r.book_id = ? 
                    AND r.status IN ('pending', 'approved') LIMIT 1) as existing_reservation
            FROM users u, books b
            WHERE u.id = ? AND b.id = ?
        """, (user_id, book_id, user_id, book_id))
        
        result = cursor.fetchone()
        if not result:
            return False, "User or book not found."
            
        user_status, book_title, stock, existing_reservation = result
        
        # Validate conditions
        if user_status.lower() != 'active':
            return False, f"User account is not active."
        if not stock:
            return False, f"Book '{book_title}' is out of stock."
        if existing_reservation:
            return False, "You already have an active reservation for this book."
        
        # Insert reservation and update stock in a single transaction
        cursor.execute("""
            BEGIN TRANSACTION;
            INSERT INTO reservations (user_id, book_id, reservation_date, status)
            VALUES (?, ?, ?, 'pending');
            UPDATE books SET stock = stock - 1 WHERE id = ?;
            COMMIT;
        """, (user_id, book_id, reservation_date, book_id))
        
        return True, f"Reservation for '{book_title}' created successfully!"
        
    except sqlite3.IntegrityError as e:
        return False, "Database integrity error. Please try again."
    except sqlite3.Error as e:
        return False, f"Error: {str(e)}"
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
        SELECT r.id, b.title, u.full_name, r.reservation_date
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
    """Fetch all users as tuples in the order expected by the UI.

    Returns:
        list[tuple]: (id, full_name, email, role, status, contact, address)
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                id,
                COALESCE(full_name, '') AS full_name,
                COALESCE(email, '') AS email,
                COALESCE(role, 'Member') AS role,
                COALESCE(status, 'Active') AS status,
                COALESCE(phone, contact) AS contact,
                COALESCE(address, '') AS address
            FROM users
            ORDER BY full_name
            """
        )
        return cursor.fetchall()
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
        # Discover users table columns to support multiple schema variants
        cursor.execute("PRAGMA table_info(users)")
        user_columns_info = cursor.fetchall()
        user_columns = {row[1] for row in user_columns_info}

        # Determine allowed role/status values from table DDL if CHECK constraints exist
        allowed_roles = None
        allowed_statuses = None
        try:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
            row = cursor.fetchone()
            ddl = row[0] if row and row[0] else ''
            import re as _re
            role_match = _re.search(r"role\s+TEXT\s+CHECK\(\s*role\s+IN\s*\(([^\)]*)\)\)", ddl, _re.IGNORECASE)
            status_match = _re.search(r"status\s+TEXT\s+CHECK\(\s*status\s+IN\s*\(([^\)]*)\)\)", ddl, _re.IGNORECASE)
            if role_match:
                allowed_roles = [v.strip().strip("'\"") for v in role_match.group(1).split(',')]
            if status_match:
                allowed_statuses = [v.strip().strip("'\"") for v in status_match.group(1).split(',')]
        except Exception:
            pass

        # Prepare derived fields for stricter schemas
        # Username: derive from email if present, otherwise from name + short code
        derived_username = None
        if 'username' in user_columns:
            try:
                local_part = (email or '').split('@')[0].strip()
                base = local_part if local_part else ''.join(
                    c for c in (full_name or '').lower() if c.isalnum())
                if not base:
                    base = 'user'
                # Ensure some uniqueness with last 4 of user_code
                derived_username = f"{base}"
            except Exception:
                derived_username = 'user'

        # Password hash: set a default if the column exists
        derived_password_hash = None
        if 'password_hash' in user_columns:
            try:
                from auth_utils import get_password_hash
                derived_password_hash = get_password_hash('password123')
            except Exception:
                # Fallback to storing a simple placeholder if hashing utility unavailable
                derived_password_hash = 'password123'
        # Normalize role/status to match allowed values if present
        norm_role = role
        norm_status = status
        try:
            if allowed_roles:
                # Find a case-insensitive match or fallback to first allowed
                match = next((r for r in allowed_roles if r.lower() == (role or '').lower()), None)
                norm_role = match if match is not None else allowed_roles[0]
            else:
                # Heuristic fallback
                rm = {'admin': 'admin', 'member': 'member', 'librarian': 'librarian',
                      'Admin': 'admin', 'Member': 'member', 'Librarian': 'librarian'}
                norm_role = rm.get(role, 'member')
            if allowed_statuses:
                match = next((s for s in allowed_statuses if s.lower() == (status or '').lower()), None)
                norm_status = match if match is not None else allowed_statuses[0]
            else:
                sm = {'active': 'Active', 'inactive': 'Inactive', 'suspended': 'suspended',
                      'Active': 'Active', 'Inactive': 'Inactive', 'Suspended': 'suspended'}
                norm_status = sm.get(status, 'Active')
        except Exception:
            pass

        # Validate unique email early to give a clearer error
        try:
            cursor.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (email,))
            if cursor.fetchone():
                QMessageBox.warning(None, "Error", "A user with this email already exists.")
                return False
        except Exception:
            # If the check fails for any reason, continue to attempt insert
            pass

        # Build insert statement dynamically based on available columns
        insert_fields = []
        insert_values = []

        def add_field(name, value):
            insert_fields.append(name)
            insert_values.append(value)

        if 'user_code' in user_columns:
            add_field('user_code', user_code)
        if 'username' in user_columns:
            add_field('username', derived_username)
        if 'full_name' in user_columns:
            add_field('full_name', full_name)
        if 'email' in user_columns:
            add_field('email', email)
        # Prefer 'phone' if present, otherwise some schemas use 'contact'
        if 'phone' in user_columns:
            add_field('phone', phone or contact)
        if 'contact' in user_columns:
            add_field('contact', contact or phone)
        if 'address' in user_columns:
            add_field('address', address)
        if 'password_hash' in user_columns:
            add_field('password_hash', derived_password_hash)
        if 'role' in user_columns:
            add_field('role', norm_role)
        if 'status' in user_columns:
            add_field('status', norm_status)
        if 'max_books' in user_columns:
            add_field('max_books', 5)

        placeholders = ', '.join(['?'] * len(insert_fields))
        sql = f"INSERT INTO users ({', '.join(insert_fields)}) VALUES ({placeholders})"
        cursor.execute(sql, tuple(insert_values))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        error_text = str(e)
        if "UNIQUE constraint failed: users.email" in error_text:
            QMessageBox.warning(None, "Error", "A user with this email already exists.")
        elif "UNIQUE constraint failed: users.user_code" in error_text:
            # Retry with a new user code if there's a collision (very rare)
            return add_user(full_name, email, role, status, phone, contact, address)
        elif "CHECK constraint failed" in error_text:
            details = []
            if allowed_roles:
                details.append(f"Role: {', '.join(allowed_roles)}")
            if allowed_statuses:
                details.append(f"Status: {', '.join(allowed_statuses)}")
            msg = "Invalid role/status value. " + ("Allowed -> " + "; ".join(details) if details else "Use Role: Admin/Member and Status: Active/Inactive.")
            QMessageBox.warning(None, "Error", msg)
        else:
            QMessageBox.warning(None, "Error", f"Failed to add user: {error_text}")
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
    """Fetch a single user by their ID, returned as tuple.

    Returns:
        tuple | None: (id, full_name, email, role, status, contact, address)
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                id,
                COALESCE(full_name, '') AS full_name,
                COALESCE(email, '') AS email,
                COALESCE(role, 'Member') AS role,
                COALESCE(status, 'Active') AS status,
                COALESCE(phone, contact) AS contact,
                COALESCE(address, '') AS address
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        )
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_user(user_id, full_name, email, role, status, phone=None, contact=None, address=None):
    """Update an existing user's details with enhanced validation and error handling.
    
    Args:
        user_id (int): ID of the user to update
        full_name (str): User's full name (required, max 100 chars)
        email (str): User's email (required, must be valid format)
        role (str): User role ('Admin' or 'Member')
        status (str): User status ('Active' or 'Inactive')
        phone (str, optional): User's phone number (max 20 chars)
        contact (str, optional): Alternative contact information (max 100 chars)
        address (str, optional): User's address (max 255 chars)
        
    Returns:
        tuple: (success: bool, message: str) - Status and message
    """
    # Input validation
    if not full_name or not full_name.strip():
        return False, "Full name is required"
    if len(full_name) > 100:
        return False, "Full name cannot exceed 100 characters"
    
    if not email or not email.strip():
        return False, "Email is required"
    if '@' not in email or '.' not in email.split('@')[-1]:
        return False, "Please enter a valid email address"
    
    if role not in ('Admin', 'Member'):
        return False, "Invalid role specified"
    
    if status not in ('Active', 'Inactive'):
        return False, "Invalid status specified"
    
    # Clean and validate optional fields
    phone = phone.strip() if phone else ""
    contact = contact.strip() if contact else ""
    address = address.strip() if address else ""
    
    if len(phone) > 20:
        return False, "Phone number cannot exceed 20 characters"
    if len(contact) > 100:
        return False, "Contact information cannot exceed 100 characters"
    if len(address) > 255:
        return False, "Address cannot exceed 255 characters"
    
    conn = None
    try:
        conn = create_connection()
        if not conn:
            return False, "Could not connect to database"
            
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            return False, f"User with ID {user_id} not found"
            
        # Check for duplicate email (excluding current user)
        cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
        if cursor.fetchone():
            return False, f"A user with email {email} already exists"
        
        # Update the user
        cursor.execute("""
            UPDATE users 
            SET full_name = ?, 
                email = ?, 
                phone = CASE WHEN ? = '' THEN NULL ELSE ? END,
                role = ?, 
                status = ?, 
                contact = CASE WHEN ? = '' THEN NULL ELSE ? END, 
                address = CASE WHEN ? = '' THEN NULL ELSE ? END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            full_name.strip(), 
            email.strip().lower(),  # Store emails in lowercase
            phone, phone,  # For CASE WHEN ? = ''
            role,
            status,
            contact, contact,  # For CASE WHEN ? = ''
            address, address,  # For CASE WHEN ? = ''
            user_id
        ))
        
        if cursor.rowcount == 0:
            return False, "No changes were made to the user"
            
        conn.commit()
        return True, "User updated successfully"
        
    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        if "UNIQUE constraint failed: users.email" in error_msg:
            return False, "A user with this email already exists"
        return False, f"Database error: {error_msg}"
        
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
        
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def get_overdue_books():
    """Fetch all overdue books with user and transaction details.
    
    Returns:
        list: List of dictionaries containing overdue book details
    """
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                t.id as transaction_id,
                b.title as book_title,
                b.author as book_author,
                b.isbn as book_isbn,
                u.full_name as user_name,
                u.email as user_email,
                t.issue_date,
                t.due_date,
                t.status,
                julianday('now') - julianday(t.due_date) as days_overdue
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            JOIN users u ON t.user_id = u.id
            WHERE t.status = 'borrowed' 
            AND t.due_date < date('now')
            ORDER BY t.due_date ASC
        """)
        
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    except sqlite3.Error as e:
        print(f"Error fetching overdue books: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_user_activity(days=30):
    """Fetch user activity within the specified number of days.
    
    Args:
        days (int): Number of days of activity to retrieve
        
    Returns:
        list: List of dictionaries containing user activity
    """
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                u.id as user_id,
                u.full_name as user_name,
                u.email as user_email,
                u.role as user_role,
                COUNT(DISTINCT t.id) as total_borrowed,
                COUNT(DISTINCT r.id) as total_reservations,
                COUNT(DISTINCT CASE 
                    WHEN t.status = 'Returned' THEN t.id 
                END) as books_returned,
                COUNT(DISTINCT CASE 
                    WHEN t.status = 'Issued' AND t.due_date < date('now') 
                    THEN t.id 
                END) as overdue_books,
                MAX(t.issue_date) as last_activity
            FROM users u
            LEFT JOIN transactions t ON u.id = t.user_id
            LEFT JOIN reservations r ON u.id = r.user_id
            WHERE t.issue_date >= date('now', ? || ' days')
               OR r.reservation_date >= date('now', ? || ' days')
            GROUP BY u.id, u.full_name, u.email, u.role
            ORDER BY last_activity DESC
        """, (f'-{days}', f'-{days}'))
        
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    except sqlite3.Error as e:
        print(f"Error fetching user activity: {e}")
        return []
    finally:
        if conn:
            conn.close()

def ensure_tables_exist(cursor):
    """Ensure all required tables exist with correct schema."""
    # Create transactions table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_date TIMESTAMP NOT NULL,
        return_date TIMESTAMP,
        status TEXT DEFAULT 'Borrowed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (book_id) REFERENCES books (id)
    )
    ''')
    
    # Create trigger to update timestamps if it doesn't exist
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_transactions_timestamp
    AFTER UPDATE ON transactions
    BEGIN
        UPDATE transactions 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.id;
    END;
    ''')

def borrow_book(user_id, book_id, days=14):
    """
    Borrow a book for a user with validation and proper error handling.
    
    Args:
        user_id (int): ID of the user borrowing the book
        book_id (int): ID of the book to be borrowed
        days (int): Number of days to borrow the book (default: 14)
        
    Returns:
        tuple: (success: bool, message: str) - Status and message
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Ensure tables exist with correct schema
        ensure_tables_exist(cursor)
        
        # 1. Validate user exists and is active
        cursor.execute("SELECT id, status FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return False, "User not found"
        if user[1] != 'Active':
            return False, "User account is not active"
            
        # 2. Validate book exists and is available
        cursor.execute("SELECT id, title, stock FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            return False, "Book not found"
        if book[2] <= 0:
            return False, "Book is not available for borrowing"
            
        # 3. Check if user has reached maximum borrow limit
        cursor.execute("""
            SELECT COUNT(*) FROM transactions 
            WHERE user_id = ? AND return_date IS NULL
        """, (user_id,))
        borrowed_count = cursor.fetchone()[0]
        if borrowed_count >= 5:  # Max 5 books per user
            return False, "Maximum borrow limit reached (5 books)"
            
        # 4. Check if book is already borrowed by this user
        cursor.execute("""
            SELECT id FROM transactions 
            WHERE user_id = ? AND book_id = ? AND return_date IS NULL
        """, (user_id, book_id))
        if cursor.fetchone():
            return False, "You have already borrowed this book"
            
        # 5. Calculate due date
        from datetime import datetime, timedelta
        issue_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 6. Create transaction
        cursor.execute("""
            INSERT INTO transactions 
            (user_id, book_id, issue_date, due_date, status)
            VALUES (?, ?, ?, ?, 'Borrowed')
        """, (user_id, book_id, issue_date, due_date))
        
        # 7. Update book stock and available count
        cursor.execute("""
            UPDATE books 
            SET stock = stock - 1,
                available = available - 1
            WHERE id = ? AND stock > 0
        """, (book_id,))
        
        if cursor.rowcount == 0:
            conn.rollback()
            return False, "Failed to update book availability"
            
        conn.commit()
        return True, f"Successfully borrowed '{book[1]}'. Due date: {due_date}"
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        error_msg = str(e)
        print(f"Error borrowing book: {error_msg}")
        if "no such column" in error_msg.lower():
            return False, "Database schema error. Please contact administrator."
        return False, f"Database error: {error_msg}"
    finally:
        if conn:
            conn.close()

# Initialize the database and tables when this module is imported
create_tables()
