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
        list: List of tuples containing (book_title, author, user_name, due_date, status)
    """
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                b.title, 
                b.author,
                u.full_name,
                t.due_date,
                t.status
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            JOIN users u ON t.user_id = u.id
            ORDER BY t.issue_date DESC
            LIMIT ?
        """, (limit,))
        
        return cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Error fetching recent transactions: {e}")
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
        # Validate foreign keys exist to avoid silent failures
        try:
            cursor.execute("SELECT 1 FROM users WHERE id = ? LIMIT 1", (user_id,))
            if cursor.fetchone() is None:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Database Error", "User ID does not exist. Please enter a valid User ID.")
                return False
            cursor.execute("SELECT 1 FROM books WHERE id = ? LIMIT 1", (book_id,))
            if cursor.fetchone() is None:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Database Error", "Book ID does not exist. Please select a valid book.")
                return False
        except Exception:
            # If validation fails for any reason, continue to insert and let DB decide
            pass

        cursor.execute(
            "INSERT INTO reservations (user_id, book_id, reservation_date) VALUES (?, ?, ?)",
            (user_id, book_id, reservation_date)
        )
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
