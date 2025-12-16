"""
Add event smoothness and overall success score columns to event_analysis table
"""
import sqlite3

def add_success_scoring_columns():
    """Add new columns for comprehensive success scoring"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    try:
        # Add event_smoothness column (0-10 rating)
        cursor.execute('''
            ALTER TABLE event_analysis
            ADD COLUMN event_smoothness DECIMAL(3,1) CHECK(event_smoothness >= 0 AND event_smoothness <= 10)
        ''')
        print("[OK] Added event_smoothness column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("[OK] event_smoothness column already exists")
        else:
            raise

    try:
        # Add overall_success_score column (calculated 0-10)
        cursor.execute('''
            ALTER TABLE event_analysis
            ADD COLUMN overall_success_score DECIMAL(3,1) CHECK(overall_success_score >= 0 AND overall_success_score <= 10)
        ''')
        print("[OK] Added overall_success_score column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("[OK] overall_success_score column already exists")
        else:
            raise

    conn.commit()
    conn.close()
    print("\nDatabase update complete!")

if __name__ == "__main__":
    add_success_scoring_columns()
