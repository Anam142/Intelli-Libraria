import sqlite3
import os

def ensure_admin_user():
    db_path = 'intelli_libraria.db'
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found")
        return False
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ensure required columns exist
        cursor.execute('PRAGMA table_info(users)')
        cols = {row[1] for row in cursor.fetchall()}
        needed = [
            ('username', "ALTER TABLE users ADD COLUMN username TEXT"),
            ('email', "ALTER TABLE users ADD COLUMN email TEXT"),
            ('password_hash', "ALTER TABLE users ADD COLUMN password_hash TEXT"),
            ('full_name', "ALTER TABLE users ADD COLUMN full_name TEXT"),
            ('role', "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'member'"),
            ('status', "ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Active'"),
        ]
        for col, stmt in needed:
            if col not in cols:
                try:
                    cursor.execute(stmt)
                except Exception:
                    pass

        # Upsert admin user
        cursor.execute("SELECT id FROM users WHERE lower(username) = 'admin'")
        row = cursor.fetchone()
        if row is None:
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, full_name, role, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ('admin', 'admin@intellilibraria.com', '1234', 'System Administrator', 'admin', 'Active')
            )
            print("Created admin user with password 1234")
        else:
            cursor.execute(
                """
                UPDATE users
                SET email = COALESCE(email, ?),
                    password_hash = ?,
                    full_name = COALESCE(full_name, ?),
                    role = 'admin',
                    status = 'Active'
                WHERE id = ?
                """,
                ('admin@intellilibraria.com', '1234', 'System Administrator', row[0])
            )
            print("Updated admin user; password set to 1234 and status Active")

        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    ensure_admin_user()
