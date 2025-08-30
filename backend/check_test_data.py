#!/usr/bin/env python3
"""
Script to check and display test data from the CTAS database
"""

import sqlite3
import json
from datetime import datetime

def check_database():
    """Check database tables and show sample data"""
    try:
        # Connect to database
        conn = sqlite3.connect('ctas.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("=== CTAS Test Database Overview ===")
        print(f"Database: tests/ctas.db")
        print(f"Tables found: {len(tables)}\n")
        
        for table in tables:
            table_name = table[0]
            print(f"📊 Table: {table_name}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Records: {count}")
            
            if count > 0:
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"   Columns: {', '.join([col[1] for col in columns])}")
                
                # Show sample data (first 2 rows)
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                rows = cursor.fetchall()
                
                if rows:
                    print("   Sample data:")
                    for i, row in enumerate(rows, 1):
                        print(f"     Row {i}: {dict(zip([col[1] for col in columns], row))}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()