# Database Configuration Guide

This document explains the database setup and verification process for Intelli-Libraria.

## Database Location

The application uses SQLite with the database file located at:
```
data/library.db
```

## Setup and Verification

### 1. Verify Database

Run the verification script to check if the database is properly set up:

```bash
python verify_database.py
```

This will check:
- If the database file exists
- If all required tables are present
- If the tables have the correct structure

### 2. Migrate Existing Database (if needed)

If you have an existing database in the root directory, migrate it to the new location:

```bash
python migrate_database.py
```

This will:
- Copy the database from `library.db` to `data/library.db`
- Verify the migration was successful
- Preserve all existing data

### 3. Check Database Connection

To test the database connection and view its contents:

```bash
python test_db_connection.py
```

## Database Schema

### Transactions Table
```sql
CREATE TABLE transactions (
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
```

## Troubleshooting

### Common Issues

1. **Database not found**
   - Ensure the `data` directory exists
   - Check if `data/library.db` exists

2. **Missing tables**
   - Run the database migrations
   - Check the application logs for errors

3. **Permission issues**
   - Ensure the application has write access to the `data` directory

### Logs

Check these log files for more information:
- `database_verification.log` - Database verification logs
- `migration.log` - Database migration logs
- `app.log` - Application logs

## Development

When making changes to the database schema, update:
1. The schema documentation in this file
2. The `db_config.py` file with the new schema
3. The verification scripts if needed
