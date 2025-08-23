import sqlite3
import os

def test_sqlite():
    # Remove test database if it exists
    if os.path.exists('test.db'):
        os.remove('test.db')
    
    try:
        # Create and connect to the database
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # Create a test table
        cursor.execute('''
            CREATE TABLE test (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER
            )
        ''')
        
        # Insert some test data
        cursor.execute("INSERT INTO test (name, value) VALUES (?, ?)", ("test1", 123))
        cursor.execute("INSERT INTO test (name, value) VALUES (?, ?)", ("test2", 456))
        
        # Commit changes
        conn.commit()
        
        # Query the data
        cursor.execute("SELECT * FROM test")
        rows = cursor.fetchall()
        
        print("✅ SQLite test successful!")
        print("Test data retrieved:")
        for row in rows:
            print(f"- {row}")
            
    except Exception as e:
        print(f"❌ SQLite test failed: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
        # Clean up
        if os.path.exists('test.db'):
            os.remove('test.db')

if __name__ == "__main__":
    print("Testing SQLite functionality...")
    test_sqlite()
