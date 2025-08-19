"""
Data Transfer Objects (DTOs) for Intelli-Libraria.

These dataclasses represent the data structures used throughout the application.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum

class UserRole(str, Enum):
    ADMIN = 'Admin'
    MEMBER = 'Member'

class UserStatus(str, Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'

class TransactionStatus(str, Enum):
    ISSUED = 'Issued'
    RETURNED = 'Returned'
    OVERDUE = 'Overdue'

class ReservationStatus(str, Enum):
    ACTIVE = 'Active'
    FULFILLED = 'Fulfilled'
    CANCELLED = 'Cancelled'

class ReminderPriority(str, Enum):
    LOW = 'Low'
    NORMAL = 'Normal'
    HIGH = 'High'

@dataclass
class User:
    id: Optional[int] = None
    user_code: str = ""
    full_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.MEMBER
    status: UserStatus = UserStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=data.get('id'),
            user_code=data['user_code'],
            full_name=data['full_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            role=UserRole(data.get('role', UserRole.MEMBER)),
            status=UserStatus(data.get('status', UserStatus.ACTIVE)),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else None
        )

@dataclass
class Book:
    id: Optional[int] = None
    book_code: str = ""
    title: str = ""
    authors: Optional[str] = None
    isbn: Optional[str] = None
    quantity_total: int = 1
    quantity_available: int = 1
    branch: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        return cls(
            id=data.get('id'),
            book_code=data['book_code'],
            title=data['title'],
            authors=data.get('authors'),
            isbn=data.get('isbn'),
            quantity_total=int(data.get('quantity_total', 1)),
            quantity_available=int(data.get('quantity_available', 1)),
            branch=data.get('branch'),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else None
        )

@dataclass
class Transaction:
    id: Optional[int] = None
    book_id: int = 0
    user_id: int = 0
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    return_date: Optional[date] = None
    status: TransactionStatus = TransactionStatus.ISSUED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Joined fields
    book_title: Optional[str] = None
    user_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        return cls(
            id=data.get('id'),
            book_id=data['book_id'],
            user_id=data['user_id'],
            issue_date=date.fromisoformat(data['issue_date']) if 'issue_date' in data and data['issue_date'] else None,
            due_date=date.fromisoformat(data['due_date']) if 'due_date' in data and data['due_date'] else None,
            return_date=date.fromisoformat(data['return_date']) if 'return_date' in data and data['return_date'] else None,
            status=TransactionStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else None,
            book_title=data.get('book_title'),
            user_name=data.get('user_name')
        )

@dataclass
class Reservation:
    id: Optional[int] = None
    book_id: int = 0
    user_id: int = 0
    reserved_at: Optional[datetime] = None
    status: ReservationStatus = ReservationStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Joined fields
    book_title: Optional[str] = None
    user_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reservation':
        return cls(
            id=data.get('id'),
            book_id=data['book_id'],
            user_id=data['user_id'],
            reserved_at=datetime.fromisoformat(data['reserved_at']) if 'reserved_at' in data and data['reserved_at'] else None,
            status=ReservationStatus(data.get('status', ReservationStatus.ACTIVE)),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else None,
            book_title=data.get('book_title'),
            user_name=data.get('user_name')
        )

@dataclass
class Fine:
    id: Optional[int] = None
    transaction_id: int = 0
    amount: float = 0.0
    reason: Optional[str] = None
    paid: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Joined fields
    user_name: Optional[str] = None
    book_title: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fine':
        return cls(
            id=data.get('id'),
            transaction_id=data['transaction_id'],
            amount=float(data['amount']),
            reason=data.get('reason'),
            paid=bool(data.get('paid', False)),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else None,
            user_name=data.get('user_name'),
            book_title=data.get('book_title')
        )

@dataclass
class Reminder:
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    due_on: Optional[datetime] = None
    priority: ReminderPriority = ReminderPriority.NORMAL
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Joined field
    creator_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reminder':
        return cls(
            id=data.get('id'),
            title=data['title'],
            description=data.get('description'),
            due_on=datetime.fromisoformat(data['due_on']) if 'due_on' in data and data['due_on'] else None,
            priority=ReminderPriority(data.get('priority', ReminderPriority.NORMAL)),
            created_by=data.get('created_by'),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else None,
            creator_name=data.get('creator_name')
        )

@dataclass
class Feedback:
    id: Optional[int] = None
    user_id: Optional[int] = None
    message: str = ""
    satisfaction_score: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Joined field
    user_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Feedback':
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            message=data['message'],
            satisfaction_score=data.get('satisfaction_score'),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None,
            user_name=data.get('user_name')
        )

# Type aliases for pagination and filtering
PaginationParams = Dict[str, int]  # {'page': 1, 'per_page': 10}
FilterParams = Dict[str, Any]  # {'status': 'Active', 'branch': 'Main'}
SearchResult = Dict[str, Any]  # Generic search result type
