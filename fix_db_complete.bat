@echo off
echo Fixing database...

:: Change to the correct directory
cd /d "%~dp0"

:: Stop any running Python processes
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

:: Remove existing database files
del /f /q intelli_libraria.db 2>nul
del /f /q intelli_libraria.db-journal 2>nul
del /f /q intelli_libraria.db-shm 2>nul
del /f /q intelli_libraria.db-wal 2>nul

echo Creating fresh database with correct schema...
python -c "
import sqlite3
conn = sqlite3.connect('intelli_libraria.db')
cursor = conn.cursor()

# Create users table with all required fields
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_code TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
        role TEXT CHECK(role IN ('Admin','Member','Librarian')) DEFAULT 'Member',
        status TEXT CHECK(status IN ('Active','Inactive','Suspended')) DEFAULT 'Active',
        max_books INTEGER DEFAULT 5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create other necessary tables
cursor.executescript('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        authors TEXT,
        isbn TEXT UNIQUE,
        quantity_total INTEGER NOT NULL DEFAULT 1 CHECK(quantity_total >= 0),
        quantity_available INTEGER NOT NULL DEFAULT 1 CHECK(quantity_available >= 0),
        branch TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        issue_date DATE NOT NULL,
        due_date DATE NOT NULL,
        return_date DATE,
        status TEXT CHECK(status IN ('Issued','Returned','Overdue')) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
    );
    
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        reserved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status IN ('Active','Fulfilled','Cancelled')) DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
''')

# Create admin user
from auth_utils import get_password_hash
admin_password = get_password_hash('admin123')
cursor.execute('''
    INSERT INTO users (
        user_code, username, email, password_hash, 
        full_name, phone, role, status, max_books
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    'ADMIN001',                      # user_code
    'admin',                        # username
    'admin@intellilibraria.com',    # email
    admin_password,                 # password_hash
    'System Administrator',         # full_name
    '1234567890',                   # phone
    'Admin',                        # role
    'Active',                       # status
    100                             # max_books
))

conn.commit()
conn.close()
"

echo.
echo ✅ Database reset complete!
echo.
echo Login with:
echo   Username: admin
echo   Password: admin123
echo.
pause
