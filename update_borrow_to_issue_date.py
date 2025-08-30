import os
import re
from pathlib import Path

def update_file(file_path):
    """Update issue_date to issue_date in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace issue_date with issue_date in SQL queries and code
        updated_content = re.sub(
            r'\b(issue_date)\b', 
            'issue_date', 
            content,
            flags=re.IGNORECASE
        )
        
        # Only write if changes were made
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    project_root = Path(__file__).parent.absolute()
    updated_count = 0
    
    # File extensions to process
    extensions = ('.py', '.sql')
    
    # Walk through all files in the project
    for root, _, files in os.walk(project_root):
        # Skip virtual environment and other non-project directories
        if any(skip_dir in root for skip_dir in ('venv', '.git', '__pycache__', 'migrations')):
            continue
            
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    updated_count += 1
    
    print(f"\nUpdate complete! {updated_count} files were updated.")

if __name__ == "__main__":
    print("=== Updating issue_date to issue_date in project files ===\n")
    main()
    input("\nPress Enter to exit...")
