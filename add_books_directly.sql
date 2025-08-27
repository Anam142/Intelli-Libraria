-- SQL script to add books to the database
BEGIN TRANSACTION;

-- First, check if the books table exists and has the correct structure
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    authors TEXT,
    isbn TEXT,
    quantity_total INTEGER NOT NULL DEFAULT 1,
    quantity_available INTEGER NOT NULL DEFAULT 1,
    branch TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert the books
INSERT OR IGNORE INTO books (book_code, title, authors, isbn, quantity_total, quantity_available, branch) VALUES
('BK-01234561', 'Digital Fundamentals', 'Thomas C. Floyd', '012345613135', 5, 5, 'Main Library'),
('BK-01234566', 'Digital Design', 'M. Morris Mano', '012345661754', 5, 5, 'Main Library'),
('BK-01234560', 'The 8051', 'J. Scott', '012345606021', 5, 5, 'Main Library'),
('BK-NONE', 'Microcontrollers', 'Mackenzie', NULL, 5, 5, 'Main Library'),
('BK-01234561', 'C Programming How to C++', 'Paul Reidel', '012345612053', 5, 5, 'Main Library'),
('BK-01234561', 'C++', 'D.S. Malhi', '012345616051', 5, 5, 'Main Library'),
('BK-00722242', 'Java 2', 'Herbert Schildt', '0072224207', 1, 1, 'Main Library'),
('BK-2572301', 'Digital Logic and Computer Design', 'M. Morris Mano', '257230133', 2, 2, 'Main Library'),
('BK-81203205', 'Digital Design', 'M. Morris Mano', '8120320516', 1, 1, 'Main Library'),
('BK-81317071', 'Database System', 'Thomas Connolly', '8131707164', 1, 1, 'Main Library'),
('BK-97801321', 'Computer Networks', 'Andrew S. Tanenbaum', '9780132126953', 3, 3, 'Main Library'),
('BK-97811180', 'Operating System Concepts', 'Abraham Silberschatz', '9781118063330', 4, 4, 'Main Library'),
('BK-97801360', 'Artificial Intelligence: A Modern Approach', 'Stuart Russell', '9780136042594', 2, 2, 'Main Library'),
('BK-00704280', 'Machine Learning', 'Tom M. Mitchell', '0070428077', 3, 3, 'Main Library'),
('BK-97802620', 'Deep Learning', 'Ian Goodfellow', '9780262035613', 2, 2, 'Main Library'),
('BK-97815932', 'Python Crash Course', 'Eric Matthes', '9781593279288', 4, 4, 'Main Library'),
('BK-97805965', 'Learning SQL', 'Alan Beaulieu', '9780596520830', 3, 3, 'Main Library'),
('BK-97801323', 'Clean Code', 'Robert C. Martin', '9780132350884', 2, 2, 'Main Library'),
('BK-97802016', 'Design Patterns', 'Erich Gamma', '9780201633610', 3, 3, 'Main Library'),
('BK-97802016', 'The Pragmatic Programmer', 'Andrew Hunt', '9780201616224', 2, 2, 'Main Library'),
('BK-97801240', 'Computer Organization and Design', 'David A. Patterson', '9780124077263', 2, 2, 'Main Library'),
('BK-97803214', 'Compilers: Principles, Techniques, and Tools', 'Alfred V. Aho', '9780321486813', 1, 1, 'Main Library'),
('BK-97811331', 'Introduction to the Theory of Computation', 'Michael Sipser', '9781133187790', 2, 2, 'Main Library'),
('BK-97806723', 'Data Structures and Algorithms in Java', 'Robert Lafore', '9780672324536', 2, 2, 'Main Library'),
('BK-97805960', 'Head First Java', 'Kathy Sierra', '9780596009205', 3, 3, 'Main Library'),
('BK-97801359', 'Agile Software Development', 'Robert C. Martin', '9780135974445', 2, 2, 'Main Library'),
('BK-97801339', 'Software Engineering', 'Ian Sommerville', '9780133943030', 3, 3, 'Main Library'),
('BK-97802016', 'Programming Pearls', 'Jon Bentley', '9780201657883', 1, 1, 'Main Library'),
('BK-97807356', 'Code Complete', 'Steve McConnell', '9780735619678', 2, 2, 'Main Library');

COMMIT;

-- Verify the books were added
SELECT 'Total books in database:', COUNT(*) FROM books;
