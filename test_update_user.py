"""
Test script to verify user update functionality.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from data.models import User
from data.repositories.users_repo import UserRepository

def test_user_update():
    print("Testing user update functionality...")
    
    # Initialize repository
    user_repo = UserRepository()
    
    # Get the first user from the database
    users = user_repo.get_all(limit=1)
    
    if not users:
        print("No users found in the database. Please add a user first.")
        return
    
    user = users[0]
    print(f"\nOriginal user data:")
    print(f"ID: {user.id}")
    print(f"Name: {user.full_name}")
    print(f"Email: {user.email}")
    
    # Update user data
    original_name = user.full_name
    original_email = user.email
    
    user.full_name = "Updated Test User"
    user.email = f"updated.{user.id}@test.com"
    
    # Save changes
    if user_repo.update(user):
        print("\nUser updated successfully!")
        
        # Verify the update
        updated_user = user_repo.get_by_id(user.id)
        if updated_user:
            print("\nUpdated user data:")
            print(f"ID: {updated_user.id}")
            print(f"Name: {updated_user.full_name}")
            print(f"Email: {updated_user.email}")
            
            # Revert changes
            user.full_name = original_name
            user.email = original_email
            if user_repo.update(user):
                print("\nSuccessfully reverted changes.")
            else:
                print("\nWarning: Could not revert changes!")
        else:
            print("Error: Could not retrieve updated user!")
    else:
        print("\nFailed to update user!")

if __name__ == "__main__":
    test_user_update()
