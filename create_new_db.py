import sqlite3

def create_database():
    conn = sqlite3.connect('intelli_libraria_new.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            role TEXT DEFAULT 'member',
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert admin user
    cursor.execute('''
        INSERT INTO users (username, email, password, full_name, role)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@test.com', '1234', 'Admin User', 'admin'))
    
    conn.commit()
    conn.close()
    print("✅ New database created with admin user")
    print("Username: admin")
    print("Password: 1234")

if __name__ == "__main__":
    create_database()
