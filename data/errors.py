"""
Custom exceptions for the Intelli-Libraria data layer.
"""

class DataError(Exception):
    """Base class for all data-related exceptions."""
    pass

class ValidationError(DataError):
    """Raised when data validation fails."""
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation error for field '{field}': {message} (value: {value})")

class NotFoundError(DataError):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str, **kwargs):
        self.resource = resource
        self.kwargs = kwargs
        details = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        super().__init__(f"{resource} not found with {details}")

class ConstraintError(DataError):
    """Raised when a database constraint is violated."""
    def __init__(self, constraint: str, message: str = None):
        self.constraint = constraint
        self.message = message or f"Constraint violation: {constraint}"
        super().__init__(self.message)

class UniquenessError(ConstraintError):
    """Raised when a unique constraint is violated."""
    def __init__(self, field: str, value: Any):
        self.field = field
        self.value = value
        super().__init__(
            constraint=f"unique_{field}",
            message=f"{field.capitalize()} '{value}' already exists"
        )

class ForeignKeyError(ConstraintError):
    """Raised when a foreign key constraint is violated."""
    def __init__(self, table: str, field: str, value: Any):
        self.table = table
        self.field = field
        self.value = value
        super().__init__(
            constraint=f"fk_{table}_{field}",
            message=f"Referenced {field} {value} in {table} not found"
        )

class StateError(DataError):
    """Raised when an operation is not allowed in the current state."""
    def __init__(self, message: str):
        super().__init__(f"Invalid state: {message}")

class BusinessRuleError(DataError):
    """Raised when a business rule is violated."""
    def __init__(self, rule: str, message: str):
        self.rule = rule
        self.message = message
        super().__init__(f"Business rule '{rule}' violated: {message}")

# Specific business rule errors
class BookNotAvailableError(BusinessRuleError):
    """Raised when trying to issue a book that's not available."""
    def __init__(self, book_id: int, available: int):
        super().__init__(
            rule="book_availability",
            message=f"Book {book_id} is not available (available: {available})"
        )

class UserBorrowingLimitError(BusinessRuleError):
    """Raised when user tries to borrow more books than allowed."""
    def __init__(self, user_id: int, current: int, limit: int):
        super().__init__(
            rule="user_borrowing_limit",
            message=f"User {user_id} has reached borrowing limit ({current}/{limit})"
        )

class OverdueBooksError(BusinessRuleError):
    """Raised when user has overdue books."""
    def __init__(self, user_id: int, overdue_count: int):
        super().__init__(
            rule="no_overdue_books",
            message=f"User {user_id} has {overdue_count} overdue books"
        )

class ReservationExistsError(BusinessRuleError):
    """Raised when trying to create a duplicate reservation."""
    def __init__(self, user_id: int, book_id: int):
        super().__init__(
            rule="unique_active_reservation",
            message=f"User {user_id} already has an active reservation for book {book_id}"
        )
