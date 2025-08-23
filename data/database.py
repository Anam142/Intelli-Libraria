"""
Database connection and migration management for Intelli-Libraria.

This module provides a singleton database connection pool, migration runner,
and context manager for database operations.
"""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

# Database file path (single shared DB for the whole app)
# Place the DB in the project root and name it 'intelli_libraria.db'
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'intelli_libraria.db')
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'migrations')

# Custom row factory for namedtuple-like access
class DictRow(dict):    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'DictRow' object has no attribute '{name}'") from None

def dict_factory(cursor, row):
    """Convert database row to dictionary."""
    fields = [column[0] for column in cursor.description]
    return DictRow(zip(fields, row))

class Database:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = None):
        if not self._initialized:
            self.db_path = db_path or DB_PATH
            self._ensure_db_directory()
            self._run_migrations()
            self._initialized = True

    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection with row factory set."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = dict_factory
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    @contextmanager
    def get_conn(self) -> Iterator[sqlite3.Connection]:
        """Context manager for database connections with automatic commit/rollback."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _get_migration_files(self) -> list[tuple[int, str]]:
        """Get sorted list of migration files."""
        migrations = []
        for f in Path(MIGRATIONS_DIR).glob('*.sql'):
            try:
                migration_id = int(f.stem.split('_')[0])
                migrations.append((migration_id, str(f)))
            except (ValueError, IndexError):
                continue
        return sorted(migrations, key=lambda x: x[0])

    def _get_applied_migrations(self, conn: sqlite3.Connection) -> set[int]:
        """Get set of applied migration IDs."""
        try:
            cursor = conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute("SELECT id, name FROM schema_migrations")
            return {row['id'] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            print(f"Error checking applied migrations: {e}")
            return set()

    def _run_migrations(self):
        """Run all pending migrations."""
        with self.get_conn() as conn:
            applied = self._get_applied_migrations(conn)
            cursor = conn.cursor()
            
            for migration_id, migration_file in self._get_migration_files():
                if migration_id in applied:
                    continue

                try:
                    with open(migration_file, 'r', encoding='utf-8') as f:
                        sql = f.read()
                    
                    cursor.executescript(sql)
                    cursor.execute(
                        "INSERT INTO schema_migrations (id, name) VALUES (?, ?)",
                        (migration_id, os.path.basename(migration_file))
                    )
                    print(f"Applied migration: {migration_file}")
                except Exception as e:
                    print(f"Error applying migration {migration_file}: {e}")
                    raise

# Singleton instance
db = Database()

# Helper function for common usage
@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    """Helper function to get a database connection."""
    with db.get_conn() as conn:
        yield conn

def init_db():
    """Initialize the database by running all migrations."""
    print(f"Initializing database at {DB_PATH}")
    db._run_migrations()
    print("Database initialization complete")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Database management')
    parser.add_argument('--init', action='store_true', help='Initialize the database')
    args = parser.parse_args()
    
    if args.init:
        init_db()
