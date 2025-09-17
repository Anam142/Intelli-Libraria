-- Indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_name_email ON users(full_name, email);

-- Fix: the column name is 'author' (singular), not 'authors'
CREATE INDEX IF NOT EXISTS idx_books_title_author ON books(title, author);

-- Indexes for transactions table
CREATE INDEX IF NOT EXISTS idx_transactions_user_status ON transactions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_transactions_book_status ON transactions(book_id, status);
-- Normalize to lowercase status values used elsewhere
CREATE INDEX IF NOT EXISTS idx_transactions_due_date ON transactions(due_date);

-- Indexes for reservations table
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
CREATE INDEX IF NOT EXISTS idx_reservations_book_status ON reservations(book_id, status);

-- Indexes for fines table
CREATE INDEX IF NOT EXISTS idx_fines_paid ON fines(paid);
CREATE INDEX IF NOT EXISTS idx_fines_transaction ON fines(transaction_id);

-- Indexes for feedback table
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);

-- Indexes for reminders table
CREATE INDEX IF NOT EXISTS idx_reminders_due_priority ON reminders(due_on, priority);
