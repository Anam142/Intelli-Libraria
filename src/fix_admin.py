import sqlite3
from auth_utils import get_password_hash

def check_and_fix_admin():
    db_path = 'intelli_libraria.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            print("Admin user exists. Checking password...")
            # Print current password hash
            cursor.execute("SELECT password_hash FROM users WHERE username = 'admin'")
            current_hash = cursor.fetchone()[0]
            print(f"Current password hash: {current_hash}")
            
            # Update password to 'admin123' with new hash
            new_hash = get_password_hash('admin123')
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = 'admin'",
                (new_hash,)
            )
            conn.commit()
            print(f"Updated admin password. New hash: {new_hash}")
        else:
            print("Admin user not found. Creating admin...")
            # Create admin user
            cursor.execute('''
            INSERT INTO users (
                user_code, username, email, password_hash, full_name, role, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                'ADMIN-001',
                'admin',
                'admin@libraria.com',
                get_password_hash('admin123'),
                'System Administrator',
                'admin',
                'active'
            ))
            conn.commit()
            print("Created admin user with password 'admin123'")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Checking and fixing admin user...")
    check_and_fix_admin()
    print("Done. Please try logging in with:")
    print("Username: admin")
    print("Password: admin123")
