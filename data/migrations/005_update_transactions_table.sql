-- Migration to update transactions table for proper borrowing functionality
PRAGMA foreign_keys=off;
BEGIN TRANSACTION;

-- Create a backup of the current transactions table if it exists
CREATE TABLE IF NOT EXISTS transactions_old(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    borrow_date TIMESTAMP,
    due_date TIMESTAMP,
    return_date TIMESTAMP,
    status TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Copy existing data to backup if the table exists
INSERT INTO transactions_old
SELECT * FROM transactions WHERE 0;  -- This creates the structure without data

-- Drop the old table if it exists
DROP TABLE IF EXISTS transactions;

-- Create the new transactions table with the correct schema
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NOT NULL,
    return_date TIMESTAMP,
    status TEXT CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')) DEFAULT 'borrowed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Copy data from old table to new table
INSERT INTO transactions (id, user_id, book_id, borrow_date, due_date, return_date, status, created_at, updated_at)
SELECT 
    id, 
    user_id, 
    book_id,
    COALESCE(issue_date, datetime('now')),  -- Use issue_date if exists, otherwise current time
    due_date,
    return_date,
    CASE 
        WHEN return_date IS NOT NULL THEN 'returned'
        WHEN due_date < date('now') AND status != 'returned' THEN 'overdue'
        ELSE COALESCE(status, 'borrowed')
    END,
    COALESCE(created_at, datetime('now')),
    COALESCE(updated_at, datetime('now'))
FROM transactions_old;

-- Drop the old table
DROP TABLE IF EXISTS transactions_old;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_book_id ON transactions(book_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);

COMMIT;
PRAGMA foreign_keys=on;
