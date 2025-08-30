import random
import sqlite3
from datetime import datetime, timedelta
from database import create_connection, add_book, add_user, get_books_count, get_members_count

def generate_isbn():
    """Generate a random 13-digit ISBN."""
    return ''.join([str(random.randint(0, 9)) for _ in range(13)])

def generate_phone():
    """Generate a random phone number."""
    return f"03{random.randint(10, 99)}{random.randint(1000000, 9999999)}"

def generate_address():
    """Generate a random address."""
    streets = ['Main St', 'First Ave', 'Park Rd', 'Elm St', 'Oak Ave', 'Pine St', 'Maple Dr', 'Cedar Ln']
    cities = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Multan', 'Peshawar', 'Quetta']
    return f"{random.randint(1, 999)} {random.choice(streets)}, {random.choice(cities)}"

def generate_sample_books(count=100):
    """Generate sample book data."""
    first_words = ['The', 'A', 'My', 'His', 'Her', 'Our', 'Their', 'This', 'That', 'These', 'Those']
    nouns = ['Book', 'Story', 'Novel', 'Tale', 'Adventure', 'Journey', 'Mystery', 'Secret', 'Life', 'Time']
    adjectives = ['Great', 'Last', 'First', 'Final', 'Lost', 'Hidden', 'Forgotten', 'Ancient', 'Modern', 'Mysterious']
    authors_first = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'William', 'Emma']
    authors_last = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Garcia', 'Rodriguez', 'Wilson']
    
    books = []
    for i in range(count):
        title = f"{random.choice(adjectives)} {random.choice(nouns)} {random.choice(['of', 'in', 'with', 'without', 'and'])} {random.choice(nouns)}"
        author = f"{random.choice(authors_first)} {random.choice(authors_last)}"
        isbn = generate_isbn()
        edition = f"{random.randint(1, 10)}th Edition" if random.random() > 0.3 else None
        stock = random.randint(1, 20)
        books.append((title, author, isbn, edition, stock))
    
    return books

def generate_sample_users(count=30):
    """Generate sample user data."""
    first_names = ['Ali', 'Ahmed', 'Fatima', 'Ayesha', 'Muhammad', 'Hassan', 'Hussain', 'Zainab', 'Maryam', 'Ibrahim',
                  'Amina', 'Yusuf', 'Zain', 'Sara', 'Aisha', 'Omar', 'Usman', 'Umar', 'Khadija', 'Ayesha']
    last_names = ['Khan', 'Ahmed', 'Ali', 'Raza', 'Hussain', 'Rizvi', 'Zaidi', 'Naqvi', 'Jafri', 'Rizvi', 'Shah',
                 'Malik', 'Sheikh', 'Qureshi', 'Siddiqui', 'Farooqi', 'Hashmi', 'Rashid', 'Kazmi', 'Rizwan']
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
    
    users = []
    for i in range(count):
        first = random.choice(first_names)
        last = random.choice(last_names)
        full_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 100)}@{random.choice(domains)}"
        role = 'Admin' if i < 3 else 'Member'  # First 3 users as admins
        status = 'Active' if random.random() > 0.1 else 'Inactive'  # 90% active
        phone = generate_phone()
        contact = f"+92{phone[1:]}"  # Convert to international format
        address = generate_address()
        users.append((full_name, email, role, status, phone, contact, address))
    
    return users

def add_sample_data():
    """Add more sample books and users to the database."""
    try:
        # Get database connection
        conn = create_connection()
        cursor = conn.cursor()
        
        # Get current counts
        existing_books = get_books_count()
        existing_users = get_members_count()
        print(f"Current database: {existing_books} books and {existing_users} users.")
        
        # Add more sample books (50 more)
        print("Adding more sample books...")
        books = generate_sample_books(50)  # Generate 50 more sample books
        for book in books:
            title, author, isbn, edition, stock = book
            try:
                add_book(title, author, isbn, edition, stock)
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"Skipping duplicate ISBN: {isbn}")
                    continue
                raise
        
        # Add more sample users (20 more)
        print("Adding more sample users...")
        users = generate_sample_users(20)  # Generate 20 more sample users
        for user in users:
            full_name, email, role, status, phone, contact, address = user
            try:
                add_user(full_name, email, role, status, phone, contact, address)
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"Skipping duplicate email: {email}")
                    continue
                raise
        
        # Get updated counts
        new_book_count = get_books_count()
        new_user_count = get_members_count()
        
        added_books = new_book_count - existing_books
        added_users = new_user_count - existing_users
        
        print(f"Successfully added {added_books} new books and {added_users} new users to the database.")
        print(f"Total now: {new_book_count} books and {new_user_count} users.")
        return True
        
    except Exception as e:
        print(f"Error adding sample data: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Starting to add sample data...")
    success = add_sample_data()
    if success:
        print("Sample data added successfully!")
    else:
        print("Failed to add sample data.")
