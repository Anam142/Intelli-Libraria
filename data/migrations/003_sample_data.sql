-- Insert sample users (1 admin, 4 members)
-- Password for all users is '1234' (plain text for now, will be hashed in migration 004)
-- Using INSERT OR IGNORE to skip existing users
INSERT OR IGNORE INTO users (user_code, username, full_name, email, phone, role, status, password_hash) VALUES
('USR-000001', 'admin', 'Admin User', 'admin@lms.test', '03001234567', 'admin', 'Active', '1234'),
('USR-000002', 'johnsmith', 'John Smith', 'john.smith@example.com', '03011234567', 'member', 'Active', '1234'),
('USR-000003', 'sarahj', 'Sarah Johnson', 'sarah.j@example.com', '03021234567', 'member', 'Active', '1234'),
('USR-000004', 'michaelb', 'Michael Brown', 'michael.b@example.com', '03031234567', 'member', 'Inactive', '1234'),
('USR-000005', 'emmaw', 'Emma Wilson', 'emma.w@example.com', '03041234567', 'member', 'Active', '1234');

-- Insert sample books
-- Using INSERT OR IGNORE to skip existing books
-- Match current schema: books(id, title, author, isbn, edition, stock, available)
INSERT OR IGNORE INTO books (title, author, isbn, edition, stock, available) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', NULL, 5, 3),
('To Kill a Mockingbird', 'Harper Lee', '9780061120084', NULL, 3, 1),
('1984', 'George Orwell', '9780451524935', NULL, 4, 4),
('Pride and Prejudice', 'Jane Austen', '9780141439518', NULL, 2, 0),
('The Hobbit', 'J.R.R. Tolkien', '9780547928227', NULL, 3, 2),
('The Catcher in the Rye', 'J.D. Salinger', '9780316769488', NULL, 2, 2),
('To the Lighthouse', 'Virginia Woolf', '9780156907392', NULL, 1, 1),
('Moby Dick', 'Herman Melville', '9781503280786', NULL, 3, 3);

-- Insert sample transactions
-- Using INSERT OR IGNORE to skip existing transactions
-- Match current transactions schema and status casing
-- Use stable lookups to honor foreign keys
INSERT OR IGNORE INTO transactions (book_id, user_id, issue_date, due_date, return_date, status)
SELECT b.id, u.id, '2025-07-01', '2025-07-15', '2025-07-14', 'returned'
FROM books b JOIN users u ON u.username = 'johnsmith' WHERE b.isbn = '9780743273565';

INSERT OR IGNORE INTO transactions (book_id, user_id, issue_date, due_date, return_date, status)
SELECT b.id, u.id, '2025-08-01', '2025-08-15', NULL, 'borrowed'
FROM books b JOIN users u ON u.username = 'johnsmith' WHERE b.isbn = '9780061120084';

INSERT OR IGNORE INTO transactions (book_id, user_id, issue_date, due_date, return_date, status)
SELECT b.id, u.id, '2025-07-20', '2025-08-03', NULL, 'overdue'
FROM books b JOIN users u ON u.username = 'sarahj' WHERE b.isbn = '9780141439518';

INSERT OR IGNORE INTO transactions (book_id, user_id, issue_date, due_date, return_date, status)
SELECT b.id, u.id, '2025-08-05', '2025-08-19', NULL, 'borrowed'
FROM books b JOIN users u ON u.username = 'emmaw' WHERE b.isbn = '9780547928227';

-- Insert sample reservations
-- Using INSERT OR IGNORE to skip existing reservations
-- Only insert reservations for books that aren't currently borrowed by the same user
-- Match current reservations schema (reservation_date)
INSERT OR IGNORE INTO reservations (book_id, user_id, reservation_date, status)
SELECT b.id, u.id, '2025-08-10', 'Active'
FROM books b JOIN users u ON u.username = 'emmaw'
WHERE b.isbn = '9780141439518'
AND NOT EXISTS (
    SELECT 1 FROM transactions t WHERE t.book_id = b.id AND t.user_id = u.id AND t.return_date IS NULL
);

INSERT OR IGNORE INTO reservations (book_id, user_id, reservation_date, status)
SELECT b.id, u.id, '2025-07-25', 'Fulfilled'
FROM books b JOIN users u ON u.username = 'sarahj'
WHERE b.isbn = '9780061120084'
AND NOT EXISTS (
    SELECT 1 FROM transactions t WHERE t.book_id = b.id AND t.user_id = u.id AND t.return_date IS NULL
);

-- Insert sample fines
-- Using INSERT OR IGNORE to skip existing fines
-- Attach fine to the specific overdue transaction inserted above
INSERT OR IGNORE INTO fines (transaction_id, amount, reason, paid)
SELECT t.id, 50.0, 'Overdue book: 2 days late', 0
FROM transactions t
JOIN books b ON t.book_id = b.id AND b.isbn = '9780141439518'
JOIN users u ON t.user_id = u.id AND u.username = 'sarahj'
WHERE t.status = 'overdue'
LIMIT 1;

-- Insert sample reminders
-- Using INSERT OR IGNORE to skip existing reminders
INSERT OR IGNORE INTO reminders (title, description, due_on, priority, created_by) VALUES
('Inventory Check', 'Check and update book inventory', '2025-09-01 09:00:00', 'Normal', 1),
('Membership Renewal', 'Contact members for renewal', '2025-08-20 10:00:00', 'High', 1);

-- Insert sample feedback
-- Using INSERT OR IGNORE to skip existing feedback
INSERT OR IGNORE INTO feedback (user_id, message, satisfaction_score) VALUES
(2, 'Great book collection! The library is well-maintained and staff is very helpful.', 5),
(3, 'The due date reminder system could be improved. I almost missed returning my book.', 3),
(5, 'More copies of popular books would be great. Had to wait a while for the book I wanted.', 4);

-- Update book available quantities based on transactions
-- Recompute available from current stock minus active loans
UPDATE books SET available = stock - 
    (SELECT COUNT(*) FROM transactions WHERE book_id = books.id AND return_date IS NULL);
