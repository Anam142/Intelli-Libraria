"""
Book Management Script for Intelli-Libraria

This script provides functions to:
1. Add new books to the database
2. Update quantities of existing books
3. List all books in the database

Usage:
    python manage_books.py --action [add|update|list] [--file BOOKS_FILE]

Example:
    python manage_books.py --action add
    python manage_books.py --action update
    python manage_books.py --action list
"""
import os
import argparse
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from data.database import get_db

# Recommended books to add (title, author, isbn, edition, quantity, branch)
RECOMMENDED_BOOKS = [
    # Computer Science
    ('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', '3rd', 3, 'Main Library'),
    ('The Pragmatic Programmer', 'David Thomas', '9780135957059', '2nd', 4, 'Main Library'),
    ('Clean Architecture', 'Robert C. Martin', '9780134494166', '1st', 3, 'Main Library'),
    
    # Programming
    ('Eloquent JavaScript', 'Marijn Haverbeke', '9781593279509', '3rd', 2, 'Main Library'),
    ('Python for Data Analysis', 'Wes McKinney', '9781098104030', '3rd', 3, 'Main Library'),
    ('Effective Java', 'Joshua Bloch', '9780134685991', '3rd', 2, 'Main Library'),
    
    # Web Development
    ('You Don\'t Know JS', 'Kyle Simpson', '9781491904428', '1st', 2, 'Main Library'),
    ('Learning React', 'Alex Banks', '9781492051725', '2nd', 3, 'Main Library'),
    
    # Data Science
    ('The Hundred-Page Machine Learning Book', 'Andriy Burkov', '9781999579500', '1st', 2, 'Main Library'),
    ('Python Data Science Handbook', 'Jake VanderPlas', '9781491912058', '1st', 3, 'Main Library'),
    
    # System Design
    ('Designing Data-Intensive Applications', 'Martin Kleppmann', '9781449373320', '1st', 2, 'Main Library'),
    ('System Design Interview', 'Alex Xu', '9781736049112', '1st', 3, 'Main Library'),
    
    # Soft Skills
    ('Atomic Habits', 'James Clear', '9780735211292', '1st', 5, 'Main Library'),
    ('Deep Work', 'Cal Newport', '9781455586691', '1st', 3, 'Main Library'),
    
    # Classic Computer Science
    ('The Art of Computer Programming', 'Donald Knuth', '9780321751041', '1st', 1, 'Reference Section'),
    
    # Additional Recommendations
    ('Grokking Algorithms', 'Aditya Bhargava', '9781617292231', '1st', 4, 'Main Library'),
    ('The Clean Coder', 'Robert C. Martin', '9780137081073', '1st', 3, 'Main Library'),
    ('Refactoring', 'Martin Fowler', '9780134757599', '2nd', 2, 'Main Library'),
    ('The Mythical Man-Month', 'Fred Brooks', '9780201835953', '1st', 2, 'Reference Section'),
    ('Code Complete', 'Steve McConnell', '9780735619678', '2nd', 3, 'Main Library'),
    ('The Pragmatic Programmer', 'Andrew Hunt', '9780201616224', '1st', 3, 'Main Library'),
    ('Designing Distributed Systems', 'Brendan Burns', '9781491983645', '1st', 2, 'Main Library'),
    ('Site Reliability Engineering', 'Betsy Beyer', '9781491929124', '1st', 2, 'Main Library'),
    ('The DevOps Handbook', 'Gene Kim', '9781942788003', '1st', 2, 'Main Library'),
    ('Accelerate', 'Nicole Forsgren', '9781942788331', '1st', 2, 'Main Library'),
    ('The Phoenix Project', 'Gene Kim', '9781942788294', '1st', 3, 'Main Library'),
    ('The Unicorn Project', 'Gene Kim', '9781942788768', '1st', 2, 'Main Library')
]

# Books to update quantities (title, author, additional_quantity)
BOOKS_TO_UPDATE = [
    ('Digital Fundamentals', 'Thomas C. Floyd', 2),
    ('Digital Design', 'M. Morris Mano', 3),
    ('The 8051', 'J. Scott', 2),
    ('C Programming How to C++', 'Paul Reidel', 1),
    ('Java 2', 'Herbert Schildt', 2),
    ('Computer Networks', 'Andrew S. Tanenbaum', 1),
    ('Operating System Concepts', 'Abraham Silberschatz', 2),
    ('Clean Code', 'Robert C. Martin', 3),
    ('Design Patterns', 'Erich Gamma', 2),
    ('Python Crash Course', 'Eric Matthes', 1)
]

def generate_book_code(title, isbn):
    """Generate a unique book code based on title and ISBN."""
    if isbn and len(isbn) >= 8:
        return f"BK-{isbn[:8]}"
    # Fallback to hashing the title if no ISBN
    return f"BK-{abs(hash(title)) % 10000:04d}"

def add_books(books):
    """Add new books to the database."""
    added = 0
    skipped = 0
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        for title, authors, isbn, edition, quantity, branch in books:
            try:
                book_code = generate_book_code(title, isbn)
                
                # Check if book with same title and author exists
                cursor.execute(
                    'SELECT id FROM books WHERE title = ? AND authors = ?',
                    (title, authors)
                )
                if cursor.fetchone() is not None:
                    print(f"Skipping existing book: {title} by {authors}")
                    skipped += 1
                    continue
                
                # Add the new book
                cursor.execute('''
                INSERT INTO books 
                (book_code, title, authors, isbn, quantity_total, quantity_available, branch)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (book_code, title, authors, isbn, quantity, quantity, branch))
                
                added += 1
                print(f"Added: {title} by {authors}")
                
            except Exception as e:
                print(f"Error adding {title}: {str(e)}")
        
        conn.commit()
    
    return added, skipped

def update_quantities(updates):
    """Update quantities of existing books."""
    updated = 0
    not_found = 0
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        for title, authors, additional_quantity in updates:
            try:
                # Update both total and available quantities
                cursor.execute('''
                UPDATE books 
                SET quantity_total = quantity_total + ?,
                    quantity_available = quantity_available + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE title = ? AND authors = ?
                ''', (additional_quantity, additional_quantity, title, authors))
                
                if cursor.rowcount > 0:
                    updated += 1
                    print(f"Updated: {title} (+{additional_quantity} copies)")
                else:
                    not_found += 1
                    print(f"Not found: {title} by {authors}")
                
            except Exception as e:
                print(f"Error updating {title}: {str(e)}")
        
        conn.commit()
    
    return updated, not_found

def list_books():
    """List all books in the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT 
            book_code, 
            title, 
            authors, 
            quantity_total as total,
            quantity_available as available,
            branch
        FROM books
        ORDER BY title
        ''')
        
        books = cursor.fetchall()
        
        if not books:
            print("No books found in the database.")
            return
        
        print("\n{:<10} {:<50} {:<30} {:<6} {:<6} {:<15}".format(
            "Code", "Title", "Author", "Total", "Avail", "Branch"
        ))
        print("-" * 120)
        
        for book in books:
            print("{:<10} {:<50.47} {:<30.27} {:<6} {:<6} {:<15}".format(
                book['book_code'],
                book['title'],
                book['authors'],
                book['total'],
                book['available'],
                book['branch'] or 'N/A'
            ))
        
        print(f"\nTotal books in database: {len(books)}")

def main():
    parser = argparse.ArgumentParser(description='Manage books in the library database')
    parser.add_argument('--action', choices=['add', 'update', 'list'], required=True,
                        help='Action to perform: add, update, or list books')
    
    args = parser.parse_args()
    
    if args.action == 'add':
        print("Adding recommended books to the database...")
        added, skipped = add_books(RECOMMENDED_BOOKS)
        print(f"\nAdded {added} new books. Skipped {skipped} existing books.")
        
    elif args.action == 'update':
        print("Updating book quantities...")
        updated, not_found = update_quantities(BOOKS_TO_UPDATE)
        print(f"\nUpdated {updated} books. {not_found} books not found.")
        
    elif args.action == 'list':
        list_books()
    
    print("\nOperation completed successfully!")

if __name__ == "__main__":
    main()
