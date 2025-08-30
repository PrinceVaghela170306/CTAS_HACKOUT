import sqlite3
import json
from datetime import datetime

def show_time_series_data():
    """Display sample time series data from the database"""
    try:
        conn = sqlite3.connect('ctas.db')
        cursor = conn.cursor()
        
        # Get column info
        cursor.execute('PRAGMA table_info(time_series_data)')
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get sample data
        cursor.execute('SELECT * FROM time_series_data LIMIT 5')
        rows = cursor.fetchall()
        
        print("=== Time Series Data Sample ===")
        print(f"Total records in database: {len(rows)} (showing first 5)")
        print("\nColumns:", columns)
        print("\nSample Records:")
        
        for i, row in enumerate(rows, 1):
            data = dict(zip(columns, row))
            print(f"\nRecord {i}:")
            for key, value in data.items():
                if key == 'meta_data' and value:
                    try:
                        parsed_meta = json.loads(value)
                        print(f"  {key}: {json.dumps(parsed_meta, indent=4)}")
                    except:
                        print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}")
        
        # Show data types breakdown
        cursor.execute('SELECT DISTINCT series_type FROM time_series_data')
        series_types = [row[0] for row in cursor.fetchall()]
        print(f"\nAvailable data series types: {series_types}")
        
        # Show source types
        cursor.execute('SELECT DISTINCT source_type FROM time_series_data')
        source_types = [row[0] for row in cursor.fetchall()]
        print(f"Data sources: {source_types}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    show_time_series_data()