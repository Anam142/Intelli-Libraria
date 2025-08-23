from passlib.hash import bcrypt

def reset_admin_password():
    try:
        # Import after checking basic functionality
        from library_backend import LibraryBackend
        
        # Initialize the library
        lib = LibraryBackend('intelli_libraria.db')
        
        # Hash the new password
        new_password = 'admin123'
        hashed_password = bcrypt.hash(new_password)
        
        # Update the admin password
        conn = lib._get_connection()
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            # Create admin user if not exists
            print("Creating new admin user...")
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'admin@intellilibraria.test', hashed_password, 'System Administrator', 'admin'))
        else:
            # Update existing admin password
            print("Updating admin password...")
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?
                WHERE username = 'admin'
            ''', (hashed_password,))
        
        conn.commit()
        print("✅ Admin password has been reset to 'admin123'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTry installing required packages first:")
        print("pip install passlib")

if __name__ == "__main__":
    print("Resetting admin password...")
    reset_admin_password()
