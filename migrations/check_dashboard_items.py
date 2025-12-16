"""Check for checklist items marked as show_on_dashboard"""
import sqlite3

def check_items():
    """Check database for dashboard items"""
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("="*60)
    print("Checking Checklist Items for Dashboard Display")
    print("="*60)

    # Check if column exists
    cursor.execute("PRAGMA table_info(event_checklist_items)")
    columns = [col['name'] for col in cursor.fetchall()]
    print(f"\nColumns in event_checklist_items table:")
    for col in columns:
        print(f"  - {col}")

    if 'show_on_dashboard' not in columns:
        print("\n[ERROR] Column 'show_on_dashboard' does not exist!")
        print("Run: python add_show_on_dashboard.py")
        conn.close()
        return

    # Check all checklist items
    cursor.execute('''
        SELECT
            ci.id,
            ci.event_id,
            ci.description,
            ci.due_date,
            ci.is_completed,
            ci.show_on_dashboard,
            e.event_name
        FROM event_checklist_items ci
        JOIN events e ON ci.event_id = e.id
        ORDER BY ci.id
    ''')

    all_items = [dict(row) for row in cursor.fetchall()]

    print(f"\n\nTotal checklist items: {len(all_items)}")

    if all_items:
        print("\nAll Checklist Items:")
        print("-" * 60)
        for item in all_items:
            status = "[X]" if item['is_completed'] else "[ ]"
            dashboard = "YES" if item['show_on_dashboard'] else "NO"
            print(f"{status} [{item['event_name']}] {item['description']}")
            print(f"   Show on Dashboard: {dashboard} | Due: {item['due_date'] or 'Not set'}")
            print()

    # Check items marked for dashboard
    cursor.execute('''
        SELECT
            ci.id,
            ci.description,
            ci.due_date,
            ci.is_completed,
            ci.show_on_dashboard,
            e.event_name
        FROM event_checklist_items ci
        JOIN events e ON ci.event_id = e.id
        WHERE ci.show_on_dashboard = 1
    ''')

    dashboard_items = [dict(row) for row in cursor.fetchall()]

    print(f"\n\nItems marked for dashboard: {len(dashboard_items)}")

    if dashboard_items:
        print("\nDashboard Items:")
        print("-" * 60)
        for item in dashboard_items:
            status = "[X]" if item['is_completed'] else "[ ]"
            print(f"{status} [{item['event_name']}] {item['description']}")
            print(f"   Due: {item['due_date'] or 'Not set'}")
            print()
    else:
        print("\n[INFO] No checklist items are currently marked to show on dashboard.")
        print("To mark an item for dashboard:")
        print("  1. Go to an event")
        print("  2. Open the Checklist tab")
        print("  3. Edit a checklist item")
        print("  4. Check the 'Show on Dashboard' checkbox")

    conn.close()
    print("\n" + "="*60)

if __name__ == "__main__":
    check_items()
