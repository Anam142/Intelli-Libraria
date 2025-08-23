import bcrypt
from typing import Union

def get_password_hash(password: str) -> str:
    """
    Hash a password for storing in the database.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: Union[str, bytes], hashed_password: str) -> bool:
    """
    Verify a stored password against one provided by user.
    
    Args:
        plain_password: The password provided by the user
        hashed_password: The hashed password from the database
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        return False
    
    try:
        # Handle both string and bytes input for plain_password
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
            
        return bcrypt.checkpw(plain_password, hashed_password.encode('utf-8'))
    except (ValueError, TypeError, Exception):
        return False

def is_password_hashed(password_hash: str) -> bool:
    """
    Check if a password is already hashed with bcrypt.
    
    Args:
        password_hash: The password hash to check
        
    Returns:
        bool: True if the password is hashed with bcrypt
    """
    if not password_hash:
        return False
    return password_hash.startswith('$2b$')
