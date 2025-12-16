"""Add enhancements to labour_costs table for rate types and work tracking"""
import sqlite3

def add_columns():
    """Add rate_type and work_status columns to labour_costs table"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Add rate_type column (weekday or public_holiday)
    try:
        cursor.execute('''
            ALTER TABLE labour_costs
            ADD COLUMN rate_type TEXT DEFAULT 'weekday'
        ''')
        print("Added rate_type column to labour_costs table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("rate_type column already exists")
        else:
            raise

    # Add work_status column (full or partial)
    try:
        cursor.execute('''
            ALTER TABLE labour_costs
            ADD COLUMN work_status TEXT DEFAULT 'full'
        ''')
        print("Added work_status column to labour_costs table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("work_status column already exists")
        else:
            raise

    # Add staff_name column for tracking individual workers
    try:
        cursor.execute('''
            ALTER TABLE labour_costs
            ADD COLUMN staff_name TEXT
        ''')
        print("Added staff_name column to labour_costs table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("staff_name column already exists")
        else:
            raise

    conn.commit()
    conn.close()

    print("\nLabour costs enhancements added successfully!")

if __name__ == "__main__":
    add_columns()
