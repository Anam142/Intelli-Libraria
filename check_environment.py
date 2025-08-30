import os
import sys

def check_environment():
    print("Python Environment Information:")
    print(f"Python Version: {sys.version}")
    print(f"Current Working Directory: {os.getcwd()}")
    print("\nDirectory Contents:")
    try:
        for item in os.listdir():
            item_path = os.path.join(os.getcwd(), item)
            item_type = "[DIR] " if os.path.isdir(item_path) else "[FILE]"
            print(f"{item_type} {item}")
    except Exception as e:
        print(f"Error listing directory: {e}")

if __name__ == "__main__":
    check_environment()
