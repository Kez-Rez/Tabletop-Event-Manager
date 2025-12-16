"""Fix checklist items with NULL category_id by setting them to 'Other' category"""
import sqlite3

def fix_null_categories():
    """Assign NULL category_id items to 'Other' category"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Get the ID of the 'Other' category
    cursor.execute("SELECT id FROM checklist_categories WHERE name = 'Other'")
    other_category = cursor.fetchone()

    if not other_category:
        print("Error: 'Other' category not found in database")
        conn.close()
        return

    other_id = other_category[0]
    print(f"'Other' category ID: {other_id}")

    # Count items with NULL category_id
    cursor.execute("SELECT COUNT(*) FROM event_checklist_items WHERE category_id IS NULL")
    null_count = cursor.fetchone()[0]
    print(f"Found {null_count} checklist items with NULL category_id")

    # Update NULL category_id to 'Other'
    cursor.execute("""
        UPDATE event_checklist_items
        SET category_id = ?
        WHERE category_id IS NULL
    """, (other_id,))

    updated_count = cursor.rowcount
    conn.commit()

    print(f"Updated {updated_count} checklist items to 'Other' category")

    # Verify
    cursor.execute("SELECT COUNT(*) FROM event_checklist_items WHERE category_id IS NULL")
    remaining_null = cursor.fetchone()[0]
    print(f"Remaining items with NULL category_id: {remaining_null}")

    conn.close()
    print("\nDone!")

if __name__ == "__main__":
    fix_null_categories()
