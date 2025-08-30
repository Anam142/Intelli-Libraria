import os

def list_files():
    print("Current working directory:", os.getcwd())
    print("\nFiles and directories:")
    for item in os.listdir():
        print(f"- {item}")

if __name__ == "__main__":
    list_files()
