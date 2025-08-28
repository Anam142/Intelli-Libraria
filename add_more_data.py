import sqlite3
import random
from datetime import datetime, timedelta

def get_db_connection():
    """Create and return a database connection."""
    return sqlite3.connect('intelli_libraria.db')

def get_books_count():
    """Return the current number of books in the database."""
    conn = get_db_connection()
    try:
        return conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    finally:
        conn.close()

def get_members_count():
    """Return the current number of members in the database."""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM users WHERE role = 'Member'").fetchone()[0]
    finally:
        conn.close()

def add_more_books(count=50):
    """Add more sample books to the database."""
    first_words = ['The', 'A', 'My', 'His', 'Her', 'Our', 'Their']
    nouns = ['Book', 'Story', 'Novel', 'Tale', 'Adventure', 'Journey', 'Mystery', 'Secret', 'Life', 'Time']
    adjectives = ['Great', 'Last', 'First', 'Final', 'Lost', 'Hidden', 'Ancient', 'Modern', 'Mysterious']
    authors = ['John Smith', 'Jane Doe', 'Michael Johnson', 'Sarah Williams', 'David Brown', 'Emily Davis']
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        added = 0
        
        for _ in range(count):
            title = f"{random.choice(adjectives)} {random.choice(nouns)} of {random.choice(nouns)}"
            author = random.choice(authors)
            isbn = ''.join([str(random.randint(0, 9)) for _ in range(13)])
            edition = f"{random.randint(1, 10)}th Edition"
            stock = random.randint(1, 20)
            
            try:
                cursor.execute(
                    'INSERT INTO books (title, author, isbn, edition, stock) VALUES (?, ?, ?, ?, ?)',
                    (title, author, isbn, edition, stock)
                )
                added += 1
            except sqlite3.IntegrityError:
                # Skip duplicate ISBNs
                continue
        
        conn.commit()
        return added
    finally:
        conn.close()

def add_more_users(count=20):
    """Add more sample users to the database."""
    first_names = ['Ali', 'Ahmed', 'Fatima', 'Ayesha', 'Muhammad', 'Hassan', 'Hussain', 'Zainab', 'Maryam', 'Ibrahim']
    last_names = ['Khan', 'Ahmed', 'Ali', 'Raza', 'Hussain', 'Rizvi', 'Zaidi', 'Naqvi', 'Jafri', 'Shah']
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        added = 0
        
        for _ in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            email = f"{first.lower()}.{last.lower()}{random.randint(100, 9999)}@{random.choice(domains)}"
            role = 'Member'
            status = 'Active' if random.random() > 0.1 else 'Inactive'
            phone = f"03{random.randint(10, 99)}{random.randint(1000000, 9999999)}"
            contact = f"+92{phone[1:]}"
            address = f"{random.randint(1, 999)} Street {random.randint(1, 50)}, City"
            
            try:
                cursor.execute(
                    '''INSERT INTO users 
                    (full_name, email, role, status, phone, contact, address, user_code, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))''',
                    (full_name, email, role, status, phone, contact, address, f"USR-{random.randint(100000, 999999)}")
                )
                added += 1
            except sqlite3.IntegrityError:
                # Skip duplicate emails
                continue
        
        conn.commit()
        return added
    finally:
        conn.close()

def main():
    print("Adding more sample data...")
    
    # Get current counts
    initial_books = get_books_count()
    initial_users = get_members_count()
    print(f"Current database: {initial_books} books and {initial_users} users.")
    
    # Add more books
    print("Adding more books...")
    books_added = add_more_books(50)
    
    # Add more users
    print("Adding more users...")
    users_added = add_more_users(20)
    
    # Show results
    print(f"\nAdded {books_added} new books and {users_added} new users.")
    print(f"Total now: {initial_books + books_added} books and {initial_users + users_added} users.")

if __name__ == "__main__":
    main()
