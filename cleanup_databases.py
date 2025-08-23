import os
import shutil

def cleanup_databases():
    # Paths to check
    main_db = 'intelli_libraria.db'
    data_dir = 'data'
    
    try:
        # Ensure we have at least one database file
        if not os.path.exists(main_db) and os.path.exists(os.path.join(data_dir, main_db)):
            # If main db is in data directory, move it to root
            shutil.move(os.path.join(data_dir, main_db), main_db)
        
        # List of files to remove
        files_to_remove = [
            'intelli_libraria.db.backup',
            'intelli_libraria.db.bak',
            'intelli_libraria.db.old',
            'intelli_libraria_backup.db',
            'intelli_libraria_new.db',
            'lms.db',
            'test_library.db'
        ]
        
        # Remove backup files in the main directory
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)
                print(f"✅ Removed: {file}")
        
        # Remove backup files in data directory if it exists
        if os.path.exists(data_dir):
            for file in files_to_remove:
                path = os.path.join(data_dir, file)
                if os.path.exists(path):
                    os.remove(path)
                    print(f"✅ Removed: {path}")
        
        # Verify we have the main database
        if os.path.exists(main_db):
            print(f"\n✅ Cleanup complete!")
            print(f"Main database: {os.path.abspath(main_db)}")
        else:
            print("\n⚠️  Warning: No main database file found after cleanup")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    print("Cleaning up database files...")
    cleanup_databases()
