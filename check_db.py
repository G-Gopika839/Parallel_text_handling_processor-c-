import sqlite3
import os

db_path = "results.db"

def check_integrity():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return
    
    print(f"Checking integrity of {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        print(f"Integrity check result: {result[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM reviews")
        count = cursor.fetchone()[0]
        print(f"Total reviews: {count}")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        triggers = cursor.fetchall()
        print(f"Triggers: {triggers}")
        
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Operational Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_integrity()
