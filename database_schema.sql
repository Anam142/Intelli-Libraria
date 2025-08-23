-- Intelli Libraria - Database Schema
-- Created: 2025-08-21
-- Purpose: Complete SQLite schema for Library Management System

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_code TEXT UNIQUE NOT NULL,  -- Format: USR-000001
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    role TEXT CHECK(role IN ('admin', 'librarian', 'member')) NOT NULL DEFAULT 'member',
    status TEXT CHECK(status IN ('active', 'inactive', 'suspended')) NOT NULL DEFAULT 'active',
    max_books INTEGER NOT NULL DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Publishers Table
CREATE TABLE IF NOT EXISTS publishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    address TEXT,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Authors Table
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name)
);

-- Books Table
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT UNIQUE NOT NULL,
    barcode TEXT UNIQUE NOT NULL,  -- Physical barcode for scanning
    title TEXT NOT NULL,
    edition TEXT,
    category_id INTEGER,
    publisher_id INTEGER,
    publication_year INTEGER,
    pages INTEGER,
    description TEXT,
    language TEXT DEFAULT 'English',
    quantity INTEGER NOT NULL DEFAULT 1,
    available_quantity INTEGER NOT NULL DEFAULT 0,
    location TEXT,  -- Shelf location
    cover_image BLOB,  -- Optional: Store book cover image
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE SET NULL,
    CHECK (available_quantity >= 0 AND available_quantity <= quantity)
);

-- Book-Author Relationship (Many-to-Many)
CREATE TABLE IF NOT EXISTS book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

-- Book Copies Table (For tracking individual copies of books)
CREATE TABLE IF NOT EXISTS book_copies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    barcode TEXT UNIQUE NOT NULL,  -- Unique barcode for each copy
    status TEXT CHECK(status IN ('available', 'checked_out', 'reserved', 'lost', 'damaged')) NOT NULL DEFAULT 'available',
    purchase_date DATE,
    price DECIMAL(10, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Fine Rules Table
CREATE TABLE IF NOT EXISTS fine_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    fine_per_day DECIMAL(10, 2) NOT NULL DEFAULT 0.50,
    grace_period_days INTEGER NOT NULL DEFAULT 7,
    max_fine DECIMAL(10, 2),
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Borrowing Transactions
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_copy_id INTEGER NOT NULL,
    borrowed_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NOT NULL,
    returned_date TIMESTAMP,
    fine_amount DECIMAL(10, 2) DEFAULT 0.00,
    fine_paid BOOLEAN DEFAULT 0,
    status TEXT CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')) NOT NULL DEFAULT 'borrowed',
    notes TEXT,
    created_by INTEGER,  -- Staff ID who processed the transaction
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_copy_id) REFERENCES book_copies(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Reservations
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    reservation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP NOT NULL,  -- How long the reservation is valid
    status TEXT CHECK(status IN ('pending', 'fulfilled', 'cancelled', 'expired')) NOT NULL DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Fines
CREATE TABLE IF NOT EXISTS fines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_id INTEGER,
    amount DECIMAL(10, 2) NOT NULL,
    reason TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending', 'paid', 'waived', 'overdue')) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_date TIMESTAMP,
    paid_amount DECIMAL(10, 2) DEFAULT 0.00,
    waived_by INTEGER,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE SET NULL,
    FOREIGN KEY (waived_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT CHECK(type IN ('due_date', 'overdue', 'reservation', 'fine', 'system')) NOT NULL,
    related_id INTEGER,  -- ID of related entity (transaction, reservation, etc.)
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- System Settings
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activity Log
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Triggers
-- Update timestamps on row update
CREATE TRIGGER IF NOT EXISTS update_users_timestamp
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Update book available quantity when copies are added/removed
CREATE TRIGGER IF NOT EXISTS update_book_quantity
AFTER INSERT ON book_copies
BEGIN
    UPDATE books 
    SET available_quantity = available_quantity + 1
    WHERE id = NEW.book_id AND NEW.status = 'available';
END;

-- Handle book status changes
CREATE TRIGGER IF NOT EXISTS update_book_copy_status
AFTER UPDATE OF status ON book_copies
BEGIN
    -- If status changed to/from 'available', update book's available_quantity
    IF OLD.status = 'available' AND NEW.status != 'available' THEN
        UPDATE books 
        SET available_quantity = available_quantity - 1 
        WHERE id = (SELECT book_id FROM book_copies WHERE id = NEW.id);
    ELSIF OLD.status != 'available' AND NEW.status = 'available' THEN
        UPDATE books 
        SET available_quantity = available_quantity + 1 
        WHERE id = (SELECT book_id FROM book_copies WHERE id = NEW.id);
    END IF;
END;

-- Create default admin user
INSERT OR IGNORE INTO users (
    user_code, 
    username, 
    email, 
    password_hash,  -- Default password: admin123 (bcrypt hash)
    full_name, 
    role, 
    status
) VALUES (
    'ADMIN-0001',
    'admin',
    'admin@intellilibraria.test',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'System Administrator',
    'admin',
    'active'
);

-- Insert default fine rules
INSERT OR IGNORE INTO fine_rules (
    name, 
    description, 
    fine_per_day, 
    grace_period_days, 
    max_fine,
    active
) VALUES 
    ('Standard Fine', 'Standard overdue book fine', 0.50, 7, 20.00, 1),
    ('Lost Book', 'Replacement cost for lost books', 0.00, 0, 50.00, 1),
    ('Damaged Book', 'Fine for damaged books', 0.00, 0, 30.00, 1);

-- Insert default categories
INSERT OR IGNORE INTO categories (name, description) VALUES 
    ('Fiction', 'Works of fiction including novels, short stories, and poetry'),
    ('Non-Fiction', 'Factual works including biographies, histories, and reference books'),
    ('Science', 'Scientific works and textbooks'),
    ('Technology', 'Technology and computer science books'),
    ('Art', 'Books about art, design, and photography'),
    ('History', 'Historical works and analyses'),
    ('Science Fiction', 'Science fiction and fantasy literature'),
    ('Biography', 'Biographies and memoirs'),
    ('Children', 'Children''s books'),
    ('Reference', 'Dictionaries, encyclopedias, and other reference works');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_barcode ON books(barcode);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_book_copy ON transactions(book_copy_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_reservations_user ON reservations(user_id);
CREATE INDEX IF NOT EXISTS idx_reservations_book ON reservations(book_id);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
CREATE INDEX IF NOT EXISTS idx_fines_user ON fines(user_id);
CREATE INDEX IF NOT EXISTS idx_fines_status ON fines(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);

-- Insert initial settings
INSERT OR IGNORE INTO settings (setting_key, setting_value, description) VALUES
    ('library_name', 'Intelli Libraria', 'Name of the library'),
    ('max_books_per_user', '5', 'Maximum number of books a user can borrow at once'),
    ('borrowing_period_days', '14', 'Default borrowing period in days'),
    ('reservation_expiry_days', '3', 'Number of days a reservation is held for pickup'),
    ('currency', 'USD', 'Currency used for fines and payments'),
    ('maintenance_mode', '0', 'Whether the system is in maintenance mode (1) or not (0)');
