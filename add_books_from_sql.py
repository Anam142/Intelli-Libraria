"""
Script to add books to the database from SQL-like INSERT statements.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from data.models import Book
from data.repositories.books_repo import BookRepository

def add_books_from_sql():
    """Add books to the database from SQL-like INSERT statements."""
    # List of books to add (title, author, isbn, edition, quantity)
    books_data = [
        ('Digital Fundamentals', 'Thomas C. Floyd', '012345613135', '11th', 5),
        ('Digital Design', 'M. Morris Mano', '012345661754', '6th', 5),
        ('The 8051', 'J. Scott', '012345606021', '4th', 5),
        ('Microcontrollers', 'Mackenzie', None, '9th', 5),
        ('C Programming How to C++', 'Paul Reidel', '012345612053', '9th', 5),
        ('C++', 'D.S. Malhi', '012345616051', '8th', 5),
        ('Java 2', 'Herbert Schildt', '0072224207', '5th', 1),
        ('Digital Logic and Computer Design', 'M. Morris Mano', '257230133', '2nd', 2),
        ('Digital Design', 'M. Morris Mano', '8120320516', '3rd', 1),
        ('Database System', 'Thomas Connolly', '8131707164', '3rd', 1),
        ('Computer Networks', 'Andrew S. Tanenbaum', '9780132126953', '5th', 3),
        ('Operating System Concepts', 'Abraham Silberschatz', '9781118063330', '9th', 4),
        ('Artificial Intelligence: A Modern Approach', 'Stuart Russell', '9780136042594', '3rd', 2),
        ('Machine Learning', 'Tom M. Mitchell', '0070428077', '1st', 3),
        ('Deep Learning', 'Ian Goodfellow', '9780262035613', '1st', 2),
        ('Python Crash Course', 'Eric Matthes', '9781593279288', '2nd', 4),
        ('Learning SQL', 'Alan Beaulieu', '9780596520830', '2nd', 3),
        ('Clean Code', 'Robert C. Martin', '9780132350884', '1st', 2),
        ('Design Patterns', 'Erich Gamma', '9780201633610', '1st', 3),
        ('The Pragmatic Programmer', 'Andrew Hunt', '9780201616224', '1st', 2),
        ('Computer Organization and Design', 'David A. Patterson', '9780124077263', '5th', 2),
        ('Compilers: Principles, Techniques, and Tools', 'Alfred V. Aho', '9780321486813', '2nd', 1),
        ('Introduction to the Theory of Computation', 'Michael Sipser', '9781133187790', '3rd', 2),
        ('Data Structures and Algorithms in Java', 'Robert Lafore', '9780672324536', '2nd', 2),
        ('Head First Java', 'Kathy Sierra', '9780596009205', '2nd', 3),
        ('Agile Software Development', 'Robert C. Martin', '9780135974445', '1st', 2),
        ('Software Engineering', 'Ian Sommerville', '9780133943030', '10th', 3),
        ('Programming Pearls', 'Jon Bentley', '9780201657883', '2nd', 1),
        ('Code Complete', 'Steve McConnell', '9780735619678', '2nd', 2)
    ]
    
    book_repo = BookRepository()
    added_count = 0
    skipped_count = 0
    
    print("Adding books to the database...")
    
    for title, authors, isbn, edition, quantity in books_data:
        try:
            # Check if book with same title and author already exists
            existing_book = book_repo.search(
                query=title,
                filters={'authors': authors}
            )
            
            if existing_book['total'] > 0:
                print(f"Skipping existing book: {title} by {authors}")
                skipped_count += 1
                continue
                
            # Create a new book
            book = Book(
                book_code=f"BK-{isbn[:8] if isbn else 'NONE'}",
                title=title,
                authors=authors,
                isbn=isbn,
                quantity_total=quantity,
                quantity_available=quantity,
                branch="Main Library"
            )
            
            # Add the book to the database
            book_repo.add(book)
            added_count += 1
            print(f"Added: {title} by {authors}")
            
        except Exception as e:
            print(f"Error adding {title}: {str(e)}")
    
    print(f"\nAdded {added_count} new books to the database.")
    print(f"Skipped {skipped_count} existing books.")
    print("Done!")

if __name__ == "__main__":
    add_books_from_sql()
