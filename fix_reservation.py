import sqlite3
import os
from PyQt5.QtWidgets import QMessageBox

def ensure_reservations_table():
    """Ensure the reservations table has the correct schema."""
    try:
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Check if status column exists
        cursor.execute("PRAGMA table_info(reservations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'status' not in columns:
            cursor.execute("""
                ALTER TABLE reservations 
                ADD COLUMN status TEXT DEFAULT 'Active' 
                CHECK(status IN ('Active', 'Fulfilled', 'Cancelled'))
            """)
            conn.commit()
            print("Added status column to reservations table")
        
        # Verify table structure
        cursor.execute("PRAGMA table_info(reservations)")
        print("\nReservations table structure:")
        print("-" * 50)
        print(f"{'Column':<15} {'Type':<10} {'Not Null':<8} {'Default':<15} {'PK'}")
        print("-" * 50)
        for col in cursor.fetchall():
            print(f"{col[1]:<15} {col[2]:<10} {bool(col[3]):<8} {str(col[4]):<15} {col[5]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def add_reservation(user_id, book_id, reservation_date=None):
    """
    Add a new reservation to the database with proper status handling.
    
    Args:
        user_id (int): ID of the user making the reservation
        book_id (int): ID of the book being reserved
        reservation_date (str, optional): Date in 'YYYY-MM-DD' format. Defaults to current datetime.
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = None
    try:
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Check if status column exists
        cursor.execute("PRAGMA table_info(reservations)")
        columns = [col[1] for col in cursor.fetchall()]
        has_status = 'status' in columns
        
        # Get user, book, and check for existing reservation
        cursor.execute("""
            SELECT u.status, b.title, b.quantity_available, 
                   (SELECT COUNT(*) FROM reservations r 
                    WHERE r.user_id = ? AND r.book_id = ? 
                    AND (r.status = 'Active' OR r.status IS NULL)) as existing_reservation
            FROM users u, books b 
            WHERE u.id = ? AND b.id = ?
        """, (user_id, book_id, user_id, book_id))
        
        result = cursor.fetchone()
        if not result:
            return False, "User or book not found."
            
        user_status, book_title, stock, existing_reservation = result
        
        # Validate conditions
        if user_status.lower() != 'active':
            return False, "User account is not active."
        if not stock or stock <= 0:
            return False, f"Book '{book_title}' is out of stock."
        if existing_reservation:
            return False, "You already have an active reservation for this book."
        
        # Prepare the reservation data
        reserved_at = reservation_date if reservation_date else 'datetime("now")'
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION;")
        
        try:
            if has_status:
                cursor.execute(
                    """
                    INSERT INTO reservations (user_id, book_id, reserved_at, status)
                    VALUES (?, ?, ?, 'Active')
                    """,
                    (user_id, book_id, reserved_at)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO reservations (user_id, book_id, reserved_at)
                    VALUES (?, ?, ?)
                    """,
                    (user_id, book_id, reserved_at)
                )
            
            # Update available quantity
            cursor.execute(
                """
                UPDATE books 
                SET quantity_available = quantity_available - 1 
                WHERE id = ? AND quantity_available > 0
                """,
                (book_id,)
            )
            
            # Commit the transaction
            conn.commit()
            return True, f"Reservation for '{book_title}' created successfully!"
            
        except Exception as e:
            conn.rollback()
            raise
        
    except sqlite3.IntegrityError as e:
        return False, f"Database integrity error: {str(e)}. Please try again."
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # First ensure the table has the correct schema
    if ensure_reservations_table():
        print("\nDatabase schema verified/updated successfully!")
        
        # Test adding a reservation
        user_id = 1  # Replace with actual user ID
        book_id = 1  # Replace with actual book ID
        
        print(f"\nTesting reservation for user {user_id}, book {book_id}...")
        success, message = add_reservation(user_id, book_id)
        print(f"Result: {success}")
        print(f"Message: {message}")
    else:
        print("\nFailed to verify/update database schema.")
