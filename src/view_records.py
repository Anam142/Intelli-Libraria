"""
Utility script to view all records from the database.
Run with: python view_records.py
"""
import os
import sys
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.database import get_db

def print_table(title: str, rows: List[Dict[str, Any]]) -> None:
    """Print a table of records with proper formatting."""
    if not rows:
        print(f"\n{title} - No records found")
        return
    
    print(f"\n{'='*80}\n{title.upper()}\n{'='*80}")
    
    # Get all unique keys from all rows
    all_keys = set()
    for row in rows:
        all_keys.update(row.keys())
    
    # Convert to list and sort
    headers = sorted(all_keys)
    
    # Calculate column widths
    col_widths = {}
    for h in headers:
        col_widths[h] = max(len(str(h)), *[len(str(row.get(h, ''))) for row in rows])
    
    # Print headers
    header = " | ".join(h.ljust(col_widths[h]) for h in headers)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(row.get(h, '')).ljust(col_widths[h]) for h in headers))

def get_all_records(table_name: str) -> List[Dict[str, Any]]:
    """Get all records from a table."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        return [dict(row) for row in cursor.fetchall()]

def get_table_names() -> List[str]:
    """Get all table names in the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'schema_migrations'
            ORDER BY name
        """)
        return [row['name'] for row in cursor.fetchall()]

def main():
    print("\n" + "="*80)
    print("INTELLI-LIBRARIA DATABASE RECORDS")
    print("="*80)
    
    # Get all table names
    table_names = get_table_names()
    
    # Get and display records from each table
    for table in table_names:
        records = get_all_records(table)
        print_table(f"{table} ({len(records)} records)", records)
    
    print("\n" + "="*80)
    print("END OF RECORDS")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
