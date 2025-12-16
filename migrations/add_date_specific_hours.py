"""Add date-specific operating hours for special dates"""
import sqlite3

def migrate(db_path: str = "events.db"):
    """Create table for date-specific operating hours (holidays, special events, etc.)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create date-specific hours table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS date_specific_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            specific_date DATE NOT NULL UNIQUE,
            is_open INTEGER DEFAULT 1,
            open_time TIME,
            close_time TIME,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create index for faster date lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_date_specific_hours_date
        ON date_specific_hours(specific_date)
    ''')

    conn.commit()
    conn.close()
    print("Date-specific hours migration completed successfully")

if __name__ == '__main__':
    migrate()
