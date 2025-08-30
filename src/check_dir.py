import os

def check_directory():
    # Get current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # List all files and directories in the current directory
    print("\nContents of current directory:")
    for item in os.listdir():
        full_path = os.path.join(cwd, item)
        if os.path.isdir(full_path):
            print(f"[DIR]  {item}")
        else:
            print(f"[FILE] {item}")
    
    # Check if data directory exists
    data_dir = os.path.join(cwd, 'data')
    print("\nChecking data directory:")
    if os.path.exists(data_dir):
        print(f"Data directory exists at: {data_dir}")
        print("Contents of data directory:")
        for item in os.listdir(data_dir):
            print(f"  - {item}")
    else:
        print("Data directory does not exist")

if __name__ == "__main__":
    check_directory()
