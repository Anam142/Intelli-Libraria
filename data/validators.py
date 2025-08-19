"""
Input validation and business rule enforcement for Intelli-Libraria.
"""
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional, TypeVar, Type, Callable
from dataclasses import is_dataclass, fields

from .models import *
from .errors import ValidationError, BusinessRuleError, UniquenessError

T = TypeVar('T')

def validate_not_empty(value: Any, field: str) -> None:
    """Validate that a required field is not empty."""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(field, "This field is required")

def validate_length(value: str, field: str, min_len: int = None, max_len: int = None) -> None:
    """Validate string length constraints."""
    if not isinstance(value, str):
        return  # Let type checking handle non-string values
        
    if min_len is not None and len(value) < min_len:
        raise ValidationError(
            field, 
            f"Must be at least {min_len} characters long (got {len(value)})"
        )
    if max_len is not None and len(value) > max_len:
        raise ValidationError(
            field, 
            f"Must be at most {max_len} characters long (got {len(value)})"
        )

def validate_email(email: str, field: str = 'email') -> None:
    """Validate email format."""
    if not email:
        return  # Empty is handled by required check
        
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        raise ValidationError(field, "Invalid email format")

def validate_phone(phone: str, field: str = 'phone') -> None:
    """Validate phone number format (basic validation)."""
    if not phone:
        return  # Empty is handled by required check
        
    phone_regex = r'^\+?[0-9\s-]{10,20}$'
    if not re.match(phone_regex, phone):
        raise ValidationError(field, "Invalid phone number format")

def validate_isbn(isbn: str, field: str = 'isbn') -> None:
    """Validate ISBN-10 or ISBN-13 format."""
    if not isbn:
        return  # Empty is handled by required check
        
    # Remove hyphens and spaces
    isbn = re.sub(r'[\s-]', '', isbn)
    
    # Check length
    if len(isbn) == 10:
        # Validate ISBN-10
        if not re.match(r'^\d{9}[\dXx]$', isbn):
            raise ValidationError(field, "Invalid ISBN-10 format")
            
        # Calculate checksum
        total = 0
        for i in range(9):
            total += int(isbn[i]) * (10 - i)
        check = isbn[9].upper()
        check_digit = 10 if check == 'X' else int(check)
        
        if (total + check_digit) % 11 != 0:
            raise ValidationError(field, "Invalid ISBN-10 checksum")
            
    elif len(isbn) == 13:
        # Validate ISBN-13
        if not re.match(r'^\d{13}$', isbn):
            raise ValidationError(field, "Invalid ISBN-13 format")
            
        # Calculate checksum
        total = 0
        for i in range(12):
            weight = 1 if i % 2 == 0 else 3
            total += int(isbn[i]) * weight
        check_digit = (10 - (total % 10)) % 10
        
        if int(isbn[12]) != check_digit:
            raise ValidationError(field, "Invalid ISBN-13 checksum")
    else:
        raise ValidationError(field, "ISBN must be 10 or 13 digits")

def validate_date_range(
    date_value: date, 
    field: str, 
    min_date: date = None, 
    max_date: date = None
) -> None:
    """Validate that a date is within the specified range."""
    if not date_value:
        return  # None is handled by required check
        
    if min_date and date_value < min_date:
        raise ValidationError(
            field, 
            f"Date must be on or after {min_date.strftime('%Y-%m-%d')}",
            date_value
        )
        
    if max_date and date_value > max_date:
        raise ValidationError(
            field, 
            f"Date must be on or before {max_date.strftime('%Y-%m-%d')}",
            date_value
        )

def validate_quantity(quantity: int, field: str, min_val: int = 0) -> None:
    """Validate quantity values (must be >= min_val)."""
    if quantity is None:
        return  # None is handled by required check
        
    if not isinstance(quantity, int):
        raise ValidationError(field, "Quantity must be an integer")
        
    if quantity < min_val:
        raise ValidationError(
            field, 
            f"Quantity must be at least {min_val} (got {quantity})",
            quantity
        )

class ModelValidator:
    """Base class for model validators."""
    
    @classmethod
    def validate(cls, obj: T) -> T:
        """Validate the model instance."""
        if not is_dataclass(obj):
            raise ValueError("Can only validate dataclass instances")
            
        # Get the validator method for this class
        validator = getattr(cls, f"validate_{obj.__class__.__name__.lower()}", None)
        if validator:
            validator(obj)
            
        return obj
    
    @classmethod
    def validate_user(cls, user: 'User') -> None:
        """Validate User model."""
        validate_not_empty(user.user_code, 'user_code')
        validate_length(user.user_code, 'user_code', min_len=3, max_len=20)
        
        validate_not_empty(user.full_name, 'full_name')
        validate_length(user.full_name, 'full_name', min_len=2, max_len=100)
        
        if user.email:
            validate_email(user.email, 'email')
            validate_length(user.email, 'email', max_len=100)
            
        if user.phone:
            validate_phone(user.phone, 'phone')
            validate_length(user.phone, 'phone', max_len=20)
    
    @classmethod
    def validate_book(cls, book: 'Book') -> None:
        """Validate Book model."""
        validate_not_empty(book.book_code, 'book_code')
        validate_length(book.book_code, 'book_code', min_len=3, max_len=20)
        
        validate_not_empty(book.title, 'title')
        validate_length(book.title, 'title', max_len=200)
        
        if book.authors:
            validate_length(book.authors, 'authors', max_len=200)
            
        if book.isbn:
            validate_isbn(book.isbn, 'isbn')
            
        validate_quantity(book.quantity_total, 'quantity_total')
        validate_quantity(book.quantity_available, 'quantity_available')
        
        if book.quantity_available > book.quantity_total:
            raise ValidationError(
                'quantity_available',
                f"Available quantity ({book.quantity_available}) cannot exceed total quantity ({book.quantity_total})"
            )
            
        if book.branch:
            validate_length(book.branch, 'branch', max_len=100)
    
    @classmethod
    def validate_transaction(cls, transaction: 'Transaction') -> None:
        """Validate Transaction model."""
        if transaction.issue_date and transaction.due_date:
            if transaction.issue_date > transaction.due_date:
                raise ValidationError(
                    'due_date',
                    "Due date must be after issue date",
                    transaction.due_date
                )
                
        if transaction.return_date and transaction.issue_date:
            if transaction.return_date < transaction.issue_date:
                raise ValidationError(
                    'return_date',
                    "Return date must be on or after issue date",
                    transaction.return_date
                )
    
    @classmethod
    def validate_reservation(cls, reservation: 'Reservation') -> None:
        """Validate Reservation model."""
        if reservation.reserved_at and reservation.reserved_at > datetime.now():
            raise ValidationError(
                'reserved_at',
                "Reservation date cannot be in the future",
                reservation.reserved_at
            )
    
    @classmethod
    def validate_fine(cls, fine: 'Fine') -> None:
        """Validate Fine model."""
        if fine.amount < 0:
            raise ValidationError(
                'amount',
                "Fine amount cannot be negative",
                fine.amount
            )
    
    @classmethod
    def validate_reminder(cls, reminder: 'Reminder') -> None:
        """Validate Reminder model."""
        validate_not_empty(reminder.title, 'title')
        validate_length(reminder.title, 'title', max_len=200)
        
        if reminder.due_on and reminder.due_on < datetime.now():
            raise ValidationError(
                'due_on',
                "Due date cannot be in the past",
                reminder.due_on
            )
    
    @classmethod
    def validate_feedback(cls, feedback: 'Feedback') -> None:
        """Validate Feedback model."""
        validate_not_empty(feedback.message, 'message')
        validate_length(feedback.message, 'message', min_len=10, max_len=2000)
        
        if feedback.satisfaction_score is not None:
            if not (1 <= feedback.satisfaction_score <= 5):
                raise ValidationError(
                    'satisfaction_score',
                    "Satisfaction score must be between 1 and 5",
                    feedback.satisfaction_score
                )

# Convenience function for validating models
def validate(obj: T) -> T:
    """Validate a model instance using the appropriate validator."""
    return ModelValidator.validate(obj)
