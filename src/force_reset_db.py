#!/usr/bin/env python3
"""
Force reset the database by terminating all Python processes and removing database files.
"""
import os
import sys
import time
import signal
import psutil
from pathlib import Path

def kill_python_processes():
    """Kill all Python processes except the current one."""
    current_pid = os.getpid()
    killed = 0
    
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Check if this is a Python process and not the current one
                if 'python' in proc.info['name'].lower() and proc.info['pid'] != current_pid:
                    proc.kill()
                    killed += 1
                    time.sleep(0.5)  # Give it a moment to terminate
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return killed
    except Exception as e:
        print(f"⚠️  Warning: Could not terminate all Python processes: {e}")
        return killed

def reset_database():
    """Reset the database by removing all related files."""
    db_path = Path('intelli_libraria.db')
    journal_path = Path(f"{db_path}-journal")
    
    # Kill any Python processes that might be using the database
    print("🔄 Terminating Python processes...")
    killed = kill_python_processes()
    if killed > 0:
        print(f"✅ Terminated {killed} Python process(es)")
    
    # Remove database files
    print("\n🗑️  Removing database files...")
    try:
        if db_path.exists():
            db_path.unlink()
            print(f"✅ Removed: {db_path}")
        
        if journal_path.exists():
            journal_path.unlink()
            print(f"✅ Removed: {journal_path}")
            
        print("\n✅ Database reset complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error resetting database: {e}")
        print("\nPlease try the following steps manually:")
        print("1. Close all Python windows and applications")
        print("2. Manually delete these files if they exist:")
        print(f"   - {db_path}")
        print(f"   - {journal_path}")
        return False

if __name__ == "__main__":
    print("🔧 FORCE DATABASE RESET TOOL 🔧")
    print("This will terminate all Python processes and reset the database.")
    print("Make sure to save your work in other applications!\n")
    
    confirm = input("Are you sure you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("\nOperation cancelled.")
        sys.exit(0)
    
    if reset_database():
        print("\n✅ Success! You can now restart your application.")
        print("The database will be recreated with default settings.")
