import sqlite3
import os
import sys
import atexit
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from auth_utils import get_password_hash, verify_password

class DatabaseManager:
    _instance = None
    
    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = None):
        """Initialize the database connection with thread safety."""
        if self._initialized:
            return
            
        if db_path is None:
            db_path = str(Path(__file__).parent / 'intelli_libraria.db')
            
        self.db_path = db_path
        self._connection = None
        self._create_tables()
        self._initialized = True
        atexit.register(self.close_connection)
    
    def _get_connection(self):
        """Get a thread-safe database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                timeout=30.0,  # 30 seconds timeout
                isolation_level=None,  # Auto-commit mode
                check_same_thread=False  # Allow multiple threads to use the connection
            )
            self._connection.execute('PRAGMA journal_mode=WAL')  # Better concurrency
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close_connection(self):
        """Close the database connection if it's open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_code TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                role TEXT CHECK(role IN ('admin', 'librarian', 'member')) NOT NULL DEFAULT 'member',
                status TEXT CHECK(status IN ('active', 'inactive', 'suspended')) NOT NULL DEFAULT 'active',
                max_books INTEGER NOT NULL DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
            ''')
            conn.commit()
    
    def create_admin_user(self, password: str = 'admin123') -> bool:
        """Create or update the admin user with the given password."""
        try:
            hashed_password = get_password_hash(password)
            admin_data = {
                'user_code': 'ADMIN001',
                'username': 'admin',
                'email': 'admin@intellilibraria.com',
                'password_hash': hashed_password,
                'full_name': 'System Administrator',
                'role': 'admin',
                'status': 'active',
                'max_books': 100
            }
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Check if admin exists
                cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
                admin = cursor.fetchone()
                
                if admin:
                    # Update existing admin
                    cursor.execute('''
                        UPDATE users 
                        SET password_hash = ?, full_name = ?, email = ?, status = 'active', role = 'admin'
                        WHERE username = 'admin'
                    ''', (hashed_password, admin_data['full_name'], admin_data['email']))
                else:
                    # Insert new admin
                    cursor.execute('''
                        INSERT INTO users (
                            user_code, username, email, password_hash, 
                            full_name, role, status, max_books
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        admin_data['user_code'],
                        admin_data['username'],
                        admin_data['email'],
                        admin_data['password_hash'],
                        admin_data['full_name'],
                        admin_data['role'],
                        admin_data['status'],
                        admin_data['max_books']
                    ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Database error in create_admin_user: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error in create_admin_user: {e}")
            return False

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials and return user data if valid."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM users 
                    WHERE username = ? AND status = 'active'
                ''', (username,))
                user = cursor.fetchone()
                
                if user and verify_password(password, user['password_hash']):
                    # Convert Row to dict for easier handling
                    return dict(user)
                return None
                
        except sqlite3.Error as e:
            print(f"Database error in verify_user: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in verify_user: {e}")
            return None

    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user with hashed password."""
        try:
            # Hash the password
            if 'password' in user_data:
                user_data['password_hash'] = get_password_hash(user_data.pop('password'))
            
            required_fields = ['user_code', 'username', 'email', 'password_hash', 'full_name']
            for field in required_fields:
                if field not in user_data:
                    raise ValueError(f"Missing required field: {field}")
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO users (
                    user_code, username, email, password_hash, full_name,
                    phone, address, role, status, max_books
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['user_code'],
                    user_data['username'],
                    user_data['email'],
                    get_password_hash(user_data['password']),
                    user_data['full_name'],
                    user_data.get('phone'),
                    user_data.get('address'),
                    user_data.get('role', 'member'),
                    user_data.get('status', 'active'),
                    user_data.get('max_books', 5)
                ))
                return True
        except sqlite3.IntegrityError as e:
            print(f"Error creating user: {e}")
            return False
    
    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials and return user data if valid."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM users WHERE username = ? AND status = ?',
                    (username, 'active')
                )
                user = cursor.fetchone()
                
                if user and verify_password(password, user['password_hash']):
                    # Update last login timestamp
                    cursor.execute(
                        'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                        (user['id'],)
                    )
                    conn.commit()
                    return dict(user)
                return None
        except Exception as e:
            print(f"Error verifying user: {e}")
            return None
    
    def create_admin_user(self, password: str = 'admin123'):
        """Create or update the default admin user with hashed password.
        
        Args:
            password: The admin password to set (will be hashed before storage)
        """
        admin_data = {
            'user_code': 'ADMIN-001',
            'username': 'admin',
            'email': 'admin@libraria.com',
            'password': password,
            'full_name': 'System Administrator',
            'role': 'admin',
            'status': 'active'
        }
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Check if admin exists
                cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', ('admin',))
                admin = cursor.fetchone()
                
                if admin:
                    # Update existing admin password if it's not hashed or needs update
                    admin_id, current_hash = admin
                    if not current_hash.startswith('$2b$'):  # bcrypt hash starts with $2b$
                        cursor.execute(
                            'UPDATE users SET password_hash = ? WHERE id = ?',
                            (get_password_hash(password), admin_id)
                        )
                        conn.commit()
                        print("Updated admin password with hashed version")
                else:
                    # Create new admin with hashed password
                    self.create_user(admin_data)
                    print("Created default admin user with hashed password")
        except Exception as e:
            print(f"Error creating admin user: {e}")

# Initialize database and create default admin user if needed
if __name__ == "__main__":
    db = DatabaseManager()
    db.create_admin_user()
