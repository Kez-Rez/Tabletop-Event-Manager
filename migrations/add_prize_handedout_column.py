"""Add quantity_handed_out column to prize_items table"""
import sqlite3

def add_column():
    """Add quantity_handed_out column"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            ALTER TABLE prize_items
            ADD COLUMN quantity_handed_out INTEGER DEFAULT 0
        ''')
        print("Added quantity_handed_out column to prize_items table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("quantity_handed_out column already exists")
        else:
            raise

    conn.commit()
    conn.close()

    print("\nPrize tracking enhancement added successfully!")

if __name__ == "__main__":
    add_column()
