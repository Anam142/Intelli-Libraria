-- Check the table structure
SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions';

-- Check current status values
SELECT DISTINCT status, LENGTH(status) as length FROM transactions;

-- Count rows
SELECT COUNT(*) as total_rows FROM transactions;
