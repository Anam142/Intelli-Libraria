# Make functions available at the package level
from .database import (
    create_connection,
    get_borrowed_books_count,
    get_borrowed_count,
    get_overdue_count,
    get_members_count,
    get_books_count,
    get_book_by_id,
    get_all_books,
    add_book,
    update_book,
    delete_book,
    get_all_users,
    get_user_by_id,
    add_user,
    update_user,
    delete_user,
    get_recent_transactions,
    get_next_book_id,
    execute_query
)

# This makes the functions available when someone does: import database
__all__ = [
    'create_connection',
    'get_borrowed_books_count',
    'get_borrowed_count',
    'get_overdue_count',
    'get_members_count',
    'get_books_count',
    'get_book_by_id',
    'get_all_books',
    'add_book',
    'update_book',
    'delete_book',
    'get_all_users',
    'get_user_by_id',
    'add_user',
    'update_user',
    'delete_user',
    'get_recent_transactions',
    'get_next_book_id',
    'execute_query'
]
