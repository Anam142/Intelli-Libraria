#!/usr/bin/env python3
"""
Script to verify admin user and test login functionality.
"""
from db_utils import DatabaseManager
from auth_utils import verify_password

def verify_admin_login():
    """Verify admin login and password hashing."""
    db = DatabaseManager()
    
    try:
        # Get admin user
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = 'admin'"
            )
            admin = cursor.fetchone()
            
            if not admin:
                print("❌ Admin user not found. Creating one...")
                db.create_admin_user('admin123')
                print("✅ Created admin user with password 'admin123'")
                return True
                
            print(f"\n🔍 Found admin user:")
            print(f"   Username: {admin['username']}")
            print(f"   Role: {admin['role']}")
            print(f"   Password Hash: {admin['password_hash'][:15]}...")
            
            # Test login
            is_valid = verify_password('admin123', admin['password_hash'])
            if is_valid:
                print("\n✅ Login successful! Password is properly hashed.")
                return True
            else:
                print("\n❌ Login failed. Password verification failed.")
                print("   Updating password to hashed version...")
                db.create_admin_user('admin123')  # This will update the password
                print("✅ Updated admin password. Please try logging in again.")
                return False
                
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Verifying admin login...")
    verify_admin_login()
    print("\nTo log in, use:")
    print("  Username: admin")
    print("  Password: admin123")
