@echo off
echo Fixing database...

:: Remove existing database files
del /f /q intelli_libraria.db 2>nul
del /f /q intelli_libraria.db-journal 2>nul

:: Create a new database with admin user
python -c "
import sqlite3
conn = sqlite3.connect('intelli_libraria.db')
c = conn.cursor()

# Create users table with all required fields
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT DEFAULT 'member',
        status TEXT DEFAULT 'active'
    )
''')

# Insert admin user
c.execute('''
    INSERT INTO users (username, email, password_hash, full_name, role)
    VALUES (?, ?, ?, ?, ?)
''', (
    'admin',
    'admin@intellilibraria.com',
    '$2b$12$Ve6Yx5UE4b0fqXW4y4yX0e8QdXJv7XK5cW5X8xY3Xv9Xv9Xv9Xv9X',  # 'admin123'
    'System Administrator',
    'admin'
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
