-- Insert sample users (1 admin, 4 members)
-- Password for all users is '1234' (plain text for now, will be hashed in migration 004)
INSERT INTO users (user_code, username, full_name, email, phone, role, status, password_hash) VALUES
('USR-000001', 'admin', 'Admin User', 'admin@lms.test', '03001234567', 'admin', 'active', '1234'),
('USR-000002', 'johnsmith', 'John Smith', 'john.smith@example.com', '03011234567', 'member', 'active', '1234'),
('USR-000003', 'sarahj', 'Sarah Johnson', 'sarah.j@example.com', '03021234567', 'member', 'active', '1234'),
('USR-000004', 'michaelb', 'Michael Brown', 'michael.b@example.com', '03031234567', 'member', 'inactive', '1234'),
('USR-000005', 'emmaw', 'Emma Wilson', 'emma.w@example.com', '03041234567', 'member', 'active', '1234');

-- Insert sample books
INSERT INTO books (book_code, title, authors, isbn, quantity_total, quantity_available, branch) VALUES
('BK-000001', 'The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 5, 3, 'Main Branch'),
('BK-000002', 'To Kill a Mockingbird', 'Harper Lee', '9780061120084', 3, 1, 'Main Branch'),
('BK-000003', '1984', 'George Orwell', '9780451524935', 4, 4, 'Downtown Branch'),
('BK-000004', 'Pride and Prejudice', 'Jane Austen', '9780141439518', 2, 0, 'Main Branch'),
('BK-000005', 'The Hobbit', 'J.R.R. Tolkien', '9780547928227', 3, 2, 'Downtown Branch'),
('BK-000006', 'The Catcher in the Rye', 'J.D. Salinger', '9780316769488', 2, 2, 'Main Branch'),
('BK-000007', 'To the Lighthouse', 'Virginia Woolf', '9780156907392', 1, 1, 'Main Branch'),
('BK-000008', 'Moby Dick', 'Herman Melville', '9781503280786', 3, 3, 'Downtown Branch');

-- Insert sample transactions
INSERT INTO transactions (book_id, user_id, issue_date, due_date, return_date, status) VALUES
(1, 2, '2025-07-01', '2025-07-15', '2025-07-14', 'Returned'),
(2, 2, '2025-08-01', '2025-08-15', NULL, 'Issued'),
(4, 3, '2025-07-20', '2025-08-03', NULL, 'Overdue'),
(5, 5, '2025-08-05', '2025-08-19', NULL, 'Issued');

-- Insert sample reservations
INSERT INTO reservations (book_id, user_id, reserved_at, status) VALUES
(4, 5, '2025-08-10 10:30:00', 'Active'),
(2, 3, '2025-07-25 14:15:00', 'Fulfilled');

-- Insert sample fines
INSERT INTO fines (transaction_id, amount, reason, paid) VALUES
(3, 50.0, 'Overdue book: 2 days late', 0);

-- Insert sample reminders
INSERT INTO reminders (title, description, due_on, priority, created_by) VALUES
('Inventory Check', 'Check and update book inventory', '2025-09-01 09:00:00', 'Normal', 1),
('Membership Renewal', 'Contact members for renewal', '2025-08-20 10:00:00', 'High', 1);

-- Insert sample feedback
INSERT INTO feedback (user_id, message, satisfaction_score) VALUES
(2, 'Great book collection! The library is well-maintained and staff is very helpful.', 5),
(3, 'The due date reminder system could be improved. I almost missed returning my book.', 3),
(5, 'More copies of popular books would be great. Had to wait a while for the book I wanted.', 4);

-- Update book available quantities based on transactions
UPDATE books SET quantity_available = quantity_total - 
    (SELECT COUNT(*) FROM transactions WHERE book_id = books.id AND status = 'Issued');
