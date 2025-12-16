"""Set include_in_pdf to 1 for all existing checklist items by default"""
import sqlite3

def fix_pdf_flags():
    """Update all checklist items to be included in PDF by default"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Count items currently excluded from PDF
    cursor.execute("SELECT COUNT(*) FROM event_checklist_items WHERE include_in_pdf = 0 OR include_in_pdf IS NULL")
    excluded_count = cursor.fetchone()[0]
    print(f"Found {excluded_count} checklist items NOT included in PDF")

    # Update all items to be included in PDF (unless user explicitly unchecked it)
    # Since we can't tell which were explicitly unchecked vs just default, we'll update all to 1
    cursor.execute("""
        UPDATE event_checklist_items
        SET include_in_pdf = 1
        WHERE include_in_pdf = 0 OR include_in_pdf IS NULL
    """)

    updated_count = cursor.rowcount
    conn.commit()

    print(f"Updated {updated_count} checklist items to include in PDF")

    # Verify
    cursor.execute("SELECT COUNT(*) FROM event_checklist_items WHERE include_in_pdf = 1")
    total_included = cursor.fetchone()[0]
    print(f"Total items now included in PDF: {total_included}")

    conn.close()
    print("\nDone!")

if __name__ == "__main__":
    fix_pdf_flags()
