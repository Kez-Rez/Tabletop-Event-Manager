"""Add table booking management features"""
import sqlite3
from datetime import datetime

def migrate(db_path: str = "events.db"):
    """Add tables and settings for table booking management"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create daily capacity overrides table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_capacity_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            override_date DATE NOT NULL UNIQUE,
            total_tables INTEGER NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add default settings for table management
    default_settings = [
        ('total_tables_available', '10'),  # Default number of tables
        ('default_setup_padding_minutes', '30'),  # Default setup time before event
        ('default_breakdown_padding_minutes', '15'),  # Default breakdown time after event
        ('show_table_warnings', '1'),  # Show conflict warnings
    ]

    for key, value in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO settings (setting_key, setting_value)
            VALUES (?, ?)
        ''', (key, value))

    # Create event type setup padding overrides table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_type_padding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type_id INTEGER NOT NULL UNIQUE,
            setup_padding_minutes INTEGER DEFAULT 30,
            breakdown_padding_minutes INTEGER DEFAULT 15,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_type_id) REFERENCES event_types(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Table booking features migration completed successfully")

if __name__ == '__main__':
    migrate()
