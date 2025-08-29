-- Backup the current table
CREATE TABLE transactions_backup AS SELECT * FROM transactions;

-- Create a new table with the correct CHECK constraint
CREATE TABLE transactions_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT,
    status TEXT NOT NULL CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- Copy data with fixed status values
INSERT INTO transactions_new
SELECT 
    id, 
    user_id, 
    book_id, 
    borrow_date, 
    due_date, 
    return_date, 
    LOWER(TRIM(status)) as status,
    created_at, 
    updated_at
FROM transactions
WHERE LOWER(TRIM(status)) IN ('borrowed', 'returned', 'overdue', 'lost');

-- Replace the old table
DROP TABLE transactions;
ALTER TABLE transactions_new RENAME TO transactions;

-- Recreate indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_book_id ON transactions(book_id);

-- Verify the fix
SELECT '=== Current Status Values ===' as info;
SELECT DISTINCT status, LENGTH(status) as length FROM transactions;

-- Show the number of rows processed
SELECT '=== Rows Processed ===' as info;
SELECT COUNT(*) as total_rows FROM transactions;
