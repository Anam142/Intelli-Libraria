#!/usr/bin/env python3
"""
Script to update plain text passwords to hashed versions in the database.
This should be run once to migrate existing users to the new hashed password system.
"""
import sqlite3
from auth_utils import get_password_hash

def update_user_passwords():
    """Update all plain text passwords in the users table to hashed versions."""
    from data.database import DB_PATH as db_path
    updated_count = 0
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all users with non-bcrypt hashed passwords
        cursor.execute("SELECT id, username, password_hash FROM users")
        users = cursor.fetchall()
        
        for user in users:
            password_hash = user['password_hash']
            
            # Skip if password is already hashed with bcrypt
            if password_hash and password_hash.startswith('$2b$'):
                continue
                
            # Get the password (either plain text or old hash)
            password = password_hash if password_hash else 'admin123'  # default password if empty
            
            # Update with new hashed password
            new_hash = get_password_hash(password)
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, user['id'])
            )
            updated_count += 1
            print(f"Updated password for user: {user['username']}")
        
        conn.commit()
        print(f"\n✅ Successfully updated {updated_count} user(s)")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔒 Updating user passwords to use bcrypt hashing...")
    print("This will update all plain text passwords in the database.")
    confirm = input("Are you sure you want to continue? (y/n): ")
    
    if confirm.lower() == 'y':
        update_user_passwords()
    else:
        print("Operation cancelled.")
