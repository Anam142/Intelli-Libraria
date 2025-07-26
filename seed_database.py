import sqlite3
import database

def seed_data():
    # Create tables first
    database.create_tables()

    conn = sqlite3.connect('intelli_libraria.db')
    cursor = conn.cursor()

    # Seed Users with role and status
    users = [
        ('Alice', 'alice@example.com', 'Admin', 'Active'),
        ('Bob', 'bob@example.com', 'Member', 'Active'),
        ('Anam', 'anam@example.com', 'Admin', 'Active'),
        ('Charlie', 'charlie@example.com', 'Member', 'Inactive'),
        ('David', 'david@example.com', 'Member', 'Active')
    ]
    
    # Use INSERT OR IGNORE to avoid errors on re-running
    cursor.executemany("INSERT OR IGNORE INTO users (username, email, role, status) VALUES (?, ?, ?, ?)", users)

    # Seed Books
    books = [
        ('The Great Gatsby', 'F. Scott Fitzgerald', '978-0743273565', '1st Edition', 5),
        ('To Kill a Mockingbird', 'Harper Lee', '978-0061120084', '2nd Edition', 3),
        ('1984', 'George Orwell', '978-0451524935', '1st Edition', 8),
        ('Pride and Prejudice', 'Jane Austen', '978-0141439518', '3rd Edition', 2),
        ('The Catcher in the Rye', 'J.D. Salinger', '978-0316769488', '1st Edition', 4),
        ('The Lord of the Rings', 'J.R.R. Tolkien', '978-0618640157', '1st Edition', 1),
        ('Introduction to Algorithms', 'Thomas H. Cormen', '978-0262033848', '3rd Edition', 10),
        ('Clean Code', 'Robert C. Martin', '978-0132350884', '1st Edition', 7),
        ('Design Patterns', 'Erich Gamma', '978-0201633610', '1st Edition', 6),
        ('Ict', 'Test Author', '123-4567890123', '1st Edition', 5)
    ]
    cursor.executemany("INSERT OR IGNORE INTO books (title, author, isbn, edition, stock) VALUES (?, ?, ?, ?, ?)", books)

    conn.commit()
    conn.close()
    print("Database seeded successfully with sample data.")

if __name__ == '__main__':
    seed_data()
