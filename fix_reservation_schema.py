import sqlite3
import sys

def fix_reservation_schema():
    """
    Fix the database schema for reservations:
    1. Creates the reservations table with proper foreign keys if it doesn't exist
    2. Ensures user_id and book_id are properly set as foreign keys
    """
    try:
        # Connect to the database
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create the reservations table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            reservation_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON reservations(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservations_book_id ON reservations(book_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status)')
        
        # Add a trigger to update the updated_at timestamp
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_reservations_timestamp
        AFTER UPDATE ON reservations
        BEGIN
            UPDATE reservations 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END;
        ''')
        
        conn.commit()
        print("✅ Database schema for reservations has been updated successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error updating database schema: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_add_reservation_function():
    """
    Update the add_reservation function in database.py to include proper validation
    """
    try:
        with open('database.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the add_reservation function
        start_idx = -1
        end_idx = -1
        for i, line in enumerate(lines):
            if 'def add_reservation(' in line:
                start_idx = i
            elif start_idx != -1 and line.strip() == '' and i > start_idx + 5:  # Look for the end of the function
                end_idx = i
                break
        
        if start_idx == -1:
            print("❌ Could not find add_reservation function in database.py")
            return False
            
        # The updated function
        new_function = '''def add_reservation(book_id, user_id, reservation_date, status="Active"):
    """
    Add a new reservation to the database with proper validation.
    
    Args:
        book_id (int/str): ID of the book to reserve
        user_id (int/str): ID of the user making the reservation
        reservation_date (str): Date of reservation in 'YYYY-MM-DD' format
        status (str, optional): Status of the reservation. Defaults to 'Active'.
                               Must be one of: 'Active', 'Fulfilled', 'Cancelled'
    
    Returns:
        tuple: (success: bool, message: str) - Status and message
    """
    conn = None
    try:
        # Convert user_id to integer
        try:
            user_id = int(user_id)
            book_id = int(book_id)
        except (ValueError, TypeError):
            return False, "Error: User ID and Book ID must be valid numbers"
            
        conn = create_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            return False, f"Error: User with ID {user_id} not found"
            
        # Check if the book exists and is available
        cursor.execute("SELECT id, title, stock FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            return False, f"Error: Book with ID {book_id} not found"
            
        if book[2] <= 0:  # Check stock
            return False, f"Error: '{book[1]}' is currently out of stock"
            
        # Insert the reservation
        cursor.execute("""
            INSERT INTO reservations (book_id, user_id, reservation_date, status)
            VALUES (?, ?, ?, ?)
        """, (book_id, user_id, reservation_date, status))
        
        # Decrement the book stock
        cursor.execute("""
            UPDATE books 
            SET stock = stock - 1 
            WHERE id = ? AND stock > 0
        """, (book_id,))
        
        conn.commit()
        return True, f"Successfully reserved '{book[1]}' for user ID {user_id}"
        
    except sqlite3.Error as e:
        error_msg = str(e)
        if conn:
            conn.rollback()
        return False, f"Database error: {error_msg}"
    finally:
        if conn:
            conn.close()
'''
        
        # Replace the old function with the new one
        if end_idx == -1:  # If we couldn't find the end, replace to the end of file
            lines = lines[:start_idx] + [new_function + '\n']
        else:
            lines = lines[:start_idx] + [new_function + '\n'] + lines[end_idx:]
        
        # Write the file back
        with open('database.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        print("✅ Updated add_reservation function in database.py")
        return True
        
    except Exception as e:
        print(f"❌ Error updating database.py: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing reservation system...")
    
    # Fix the database schema
    if not fix_reservation_schema():
        print("❌ Failed to fix database schema")
        sys.exit(1)
    
    # Update the add_reservation function
    if not update_add_reservation_function():
        print("❌ Failed to update add_reservation function")
        sys.exit(1)
    
    print("\n🎉 Reservation system has been fixed successfully!")
    print("Please restart your application for the changes to take effect.")
