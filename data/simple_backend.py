"""
Simple, reusable SQLite backend for Intelli Libraria using a single database file
named 'intelli_libraria.db' at the project root.

This module exposes:
 - get_connection(): obtain a connection to the single DB
 - init_db(): create required tables once if they do not exist
 - CRUD helpers for Users, Books, Borrow_Return, Reminders
 - generic execute()/query_all()/query_one() helpers

Schema (as requested):
 - Users(id, username, password, email, contact, role)
 - Books(id, title, author, category, quantity, availability)
 - Borrow_Return(id, user_id, book_id, issue_date, return_date, status)
 - Reminders(id, user_id, book_id, due_date, message)

Notes:
 - All dates are stored as TEXT (ISO-8601) for simplicity
 - Foreign keys are enforced
 - The database file is created on first use and reused thereafter
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Optional, Tuple


# Resolve the single database file path (prefer the one defined in data/database.py)
try:
    # DB_PATH in data/database.py points to the project root 'intelli_libraria.db'
    from .database import DB_PATH as DEFAULT_DB_PATH  # type: ignore
except Exception:
    DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'intelli_libraria.db')


def _ensure_directory(db_path: str) -> None:
    directory = os.path.dirname(db_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a SQLite connection to the single DB file."""
    path = db_path or DEFAULT_DB_PATH
    _ensure_directory(path)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


@contextmanager
def db_conn(db_path: Optional[str] = None):
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute(query: str, params: Iterable[Any] = ()) -> int:
    """Execute a write query and return affected rowcount."""
    with db_conn() as conn:
        cur = conn.execute(query, tuple(params))
        return cur.rowcount


def query_all(query: str, params: Iterable[Any] = ()) -> List[Dict[str, Any]]:
    with db_conn() as conn:
        cur = conn.execute(query, tuple(params))
        return [dict(r) for r in cur.fetchall()]


def query_one(query: str, params: Iterable[Any] = ()) -> Optional[Dict[str, Any]]:
    with db_conn() as conn:
        cur = conn.execute(query, tuple(params))
        row = cur.fetchone()
        return dict(row) if row else None


def init_db() -> None:
    """Create required tables if they don't exist (idempotent)."""
    with db_conn() as conn:
        cur = conn.cursor()
        # Users
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT,
                contact TEXT,
                role TEXT
            )
            """
        )
        # Books
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                category TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                availability INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        # Borrow_Return
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Borrow_Return (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                issue_date TEXT,
                return_date TEXT,
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE CASCADE
            )
            """
        )
        # Reminders
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                due_date TEXT,
                message TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE SET NULL,
                FOREIGN KEY (book_id) REFERENCES Books(id) ON DELETE SET NULL
            )
            """
        )


# ----------------------------- Users CRUD -----------------------------
def create_user(username: str, password: str, email: Optional[str], contact: Optional[str], role: Optional[str]) -> int:
    with db_conn() as conn:
        cur = conn.execute(
            "INSERT INTO Users(username, password, email, contact, role) VALUES(?,?,?,?,?)",
            (username, password, email, contact, role)
        )
        return cur.lastrowid


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    return query_one("SELECT * FROM Users WHERE id = ?", (user_id,))


def get_all_users() -> List[Dict[str, Any]]:
    return query_all("SELECT * FROM Users ORDER BY username")


def update_user(user_id: int, username: Optional[str] = None, password: Optional[str] = None,
                email: Optional[str] = None, contact: Optional[str] = None, role: Optional[str] = None) -> bool:
    fields: List[str] = []
    params: List[Any] = []
    if username is not None:
        fields.append("username = ?")
        params.append(username)
    if password is not None:
        fields.append("password = ?")
        params.append(password)
    if email is not None:
        fields.append("email = ?")
        params.append(email)
    if contact is not None:
        fields.append("contact = ?")
        params.append(contact)
    if role is not None:
        fields.append("role = ?")
        params.append(role)
    if not fields:
        return False
    params.append(user_id)
    rc = execute(f"UPDATE Users SET {', '.join(fields)} WHERE id = ?", tuple(params))
    return rc > 0


def delete_user(user_id: int) -> bool:
    return execute("DELETE FROM Users WHERE id = ?", (user_id,)) > 0


# ----------------------------- Books CRUD -----------------------------
def create_book(title: str, author: Optional[str], category: Optional[str], quantity: int, availability: Optional[int] = None) -> int:
    if availability is None:
        availability = quantity
    with db_conn() as conn:
        cur = conn.execute(
            "INSERT INTO Books(title, author, category, quantity, availability) VALUES(?,?,?,?,?)",
            (title, author, category, int(quantity), int(availability))
        )
        return cur.lastrowid


def get_book(book_id: int) -> Optional[Dict[str, Any]]:
    return query_one("SELECT * FROM Books WHERE id = ?", (book_id,))


def get_all_books() -> List[Dict[str, Any]]:
    return query_all("SELECT * FROM Books ORDER BY title")


def update_book(book_id: int, title: Optional[str] = None, author: Optional[str] = None,
                category: Optional[str] = None, quantity: Optional[int] = None,
                availability: Optional[int] = None) -> bool:
    fields: List[str] = []
    params: List[Any] = []
    if title is not None:
        fields.append("title = ?")
        params.append(title)
    if author is not None:
        fields.append("author = ?")
        params.append(author)
    if category is not None:
        fields.append("category = ?")
        params.append(category)
    if quantity is not None:
        fields.append("quantity = ?")
        params.append(int(quantity))
    if availability is not None:
        fields.append("availability = ?")
        params.append(int(availability))
    if not fields:
        return False
    params.append(book_id)
    rc = execute(f"UPDATE Books SET {', '.join(fields)} WHERE id = ?", tuple(params))
    return rc > 0


def delete_book(book_id: int) -> bool:
    return execute("DELETE FROM Books WHERE id = ?", (book_id,)) > 0


# -------------------------- Borrow_Return CRUD -------------------------
def create_borrow_record(user_id: int, book_id: int, issue_date: Optional[str], return_date: Optional[str], status: Optional[str]) -> int:
    with db_conn() as conn:
        cur = conn.execute(
            "INSERT INTO Borrow_Return(user_id, book_id, issue_date, return_date, status) VALUES(?,?,?,?,?)",
            (user_id, book_id, issue_date, return_date, status)
        )
        return cur.lastrowid


def get_borrow_record(record_id: int) -> Optional[Dict[str, Any]]:
    return query_one("SELECT * FROM Borrow_Return WHERE id = ?", (record_id,))


def get_all_borrow_records() -> List[Dict[str, Any]]:
    return query_all(
        """
        SELECT br.*, u.username AS user_username, b.title AS book_title
        FROM Borrow_Return br
        JOIN Users u ON br.user_id = u.id
        JOIN Books b ON br.book_id = b.id
        ORDER BY COALESCE(br.issue_date, '') DESC
        """
    )


def update_borrow_record(record_id: int, user_id: Optional[int] = None, book_id: Optional[int] = None,
                         issue_date: Optional[str] = None, return_date: Optional[str] = None,
                         status: Optional[str] = None) -> bool:
    fields: List[str] = []
    params: List[Any] = []
    if user_id is not None:
        fields.append("user_id = ?")
        params.append(user_id)
    if book_id is not None:
        fields.append("book_id = ?")
        params.append(book_id)
    if issue_date is not None:
        fields.append("issue_date = ?")
        params.append(issue_date)
    if return_date is not None:
        fields.append("return_date = ?")
        params.append(return_date)
    if status is not None:
        fields.append("status = ?")
        params.append(status)
    if not fields:
        return False
    params.append(record_id)
    rc = execute(f"UPDATE Borrow_Return SET {', '.join(fields)} WHERE id = ?", tuple(params))
    return rc > 0


def delete_borrow_record(record_id: int) -> bool:
    return execute("DELETE FROM Borrow_Return WHERE id = ?", (record_id,)) > 0


# ----------------------------- Reminders CRUD --------------------------
def create_reminder(user_id: Optional[int], book_id: Optional[int], due_date: Optional[str], message: Optional[str]) -> int:
    with db_conn() as conn:
        cur = conn.execute(
            "INSERT INTO Reminders(user_id, book_id, due_date, message) VALUES(?,?,?,?)",
            (user_id, book_id, due_date, message)
        )
        return cur.lastrowid


def get_reminder(reminder_id: int) -> Optional[Dict[str, Any]]:
    return query_one("SELECT * FROM Reminders WHERE id = ?", (reminder_id,))


def get_all_reminders() -> List[Dict[str, Any]]:
    return query_all(
        """
        SELECT r.*, u.username AS user_username, b.title AS book_title
        FROM Reminders r
        LEFT JOIN Users u ON r.user_id = u.id
        LEFT JOIN Books b ON r.book_id = b.id
        ORDER BY COALESCE(r.due_date, '')
        """
    )


def update_reminder(reminder_id: int, user_id: Optional[int] = None, book_id: Optional[int] = None,
                    due_date: Optional[str] = None, message: Optional[str] = None) -> bool:
    fields: List[str] = []
    params: List[Any] = []
    if user_id is not None:
        fields.append("user_id = ?")
        params.append(user_id)
    if book_id is not None:
        fields.append("book_id = ?")
        params.append(book_id)
    if due_date is not None:
        fields.append("due_date = ?")
        params.append(due_date)
    if message is not None:
        fields.append("message = ?")
        params.append(message)
    if not fields:
        return False
    params.append(reminder_id)
    rc = execute(f"UPDATE Reminders SET {', '.join(fields)} WHERE id = ?", tuple(params))
    return rc > 0


def delete_reminder(reminder_id: int) -> bool:
    return execute("DELETE FROM Reminders WHERE id = ?", (reminder_id,)) > 0


# Ensure DB exists and is initialized when imported (safe/idempotent)
init_db()


