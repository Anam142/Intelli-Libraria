import os
import sqlite3

def create_db():
    try:
        # Remove existing database if it exists
        if os.path.exists('intelli_libraria.db'):
            os.remove('intelli_libraria.db')
            print("Removed existing database")
        
        # Create new database
        conn = sqlite3.connect('intelli_libraria.db')
        c = conn.cursor()
        
        # Create users table
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
            '$2b$12$Ve6Yx5UE4b0fqXW4y4yX0e8QdXJv7XK5cW5X8xY3Xv9Xv9Xv9Xv9X',
            'System Administrator',
            'admin'
        ))
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database created successfully!")
        print("\nLogin with:")
        print("  Username: admin")
        print("  Password: admin123")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease close any applications using the database and try again.")

if __name__ == "__main__":
    print("Creating fresh database...")
    create_db()
