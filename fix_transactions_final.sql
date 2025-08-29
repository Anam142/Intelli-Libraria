-- 1. Backup the current table
CREATE TABLE transactions_backup AS SELECT * FROM transactions;

-- 2. Create a new table with correct constraints
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

-- 3. Copy and fix data
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

-- 4. Replace the old table
DROP TABLE transactions;
ALTER TABLE transactions_new RENAME TO transactions;

-- 5. Recreate indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_book_id ON transactions(book_id);

-- 6. Verify
SELECT '=== Final Status Values ===';
SELECT DISTINCT status, LENGTH(status) as length FROM transactions;

SELECT '\n=== Rows Processed ===';
SELECT COUNT(*) as total_rows FROM transactions;
