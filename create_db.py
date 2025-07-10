import sqlite3

conn = sqlite3.connect("intelli_libraria.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    contact TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("Database created successfully!") 