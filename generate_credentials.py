import random
import string
from passlib.hash import bcrypt

def generate_username(full_name, existing_usernames=None):
    """Generate a unique username from full name"""
    if existing_usernames is None:
        existing_usernames = set()
    
    # Clean name and create base username
    name_parts = full_name.lower().split()
    base = name_parts[0] + (name_parts[-1][0] if len(name_parts) > 1 else '')
    
    # If base is taken, add numbers
    username = base
    i = 1
    while username in existing_usernames:
        username = f"{base}{i}"
        i += 1
    
    return username

def generate_password(length=10):
    """Generate a strong password with mixed characters"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(random.choice(chars) for _ in range(length))

def generate_credentials():
    """Generate a single set of login credentials"""
    first = random.choice(["John", "Jane", "Alex", "Sarah", "Chris"])
    last = random.choice(["Smith", "Doe", "Johnson", "Williams", "Brown"])
    full_name = f"{first} {last}"
    
    username = generate_username(full_name)
    password = generate_password()
    email = f"{username}@intellilibraria.test"
    
    return {
        'full_name': full_name,
        'username': username,
        'email': email,
        'password': password,
        'password_hash': bcrypt.hash(password)
    }

if __name__ == "__main__":
    creds = generate_credentials()
    print("Generated Credentials:")
    print(f"Name:     {creds['full_name']}")
    print(f"Username: {creds['username']}")
    print(f"Email:    {creds['email']}")
    print(f"Password: {creds['password']}")
    print(f"\nHashed Password: {creds['password_hash']}")
