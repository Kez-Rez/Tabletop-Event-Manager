"""Bulk recalculate revenue for all completed events"""
import sqlite3
from datetime import datetime

def recalculate_all_event_revenue():
    """Recalculate revenue, costs, and profit for all completed events"""
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all completed events
    cursor.execute('SELECT id, event_name FROM events WHERE is_completed = 1')
    completed_events = cursor.fetchall()

    if not completed_events:
        print("No completed events found.")
        conn.close()
        return

    print(f"Found {len(completed_events)} completed events to recalculate.\n")

    updated_count = 0
    skipped_count = 0

    for event in completed_events:
        event_id = event['id']
        event_name = event['event_name']

        # Calculate revenue from ticket sales
        cursor.execute('''
            SELECT SUM(price * COALESCE(quantity_sold, 0)) as revenue
            FROM ticket_tiers
            WHERE event_id = ?
        ''', (event_id,))
        result = cursor.fetchone()
        revenue = float(result['revenue']) if result and result['revenue'] else 0.0

        # Calculate labour costs
        cursor.execute('''
            SELECT SUM(total_cost) as labour_cost
            FROM labour_costs
            WHERE event_id = ?
        ''', (event_id,))
        result = cursor.fetchone()
        labour_cost = float(result['labour_cost']) if result and result['labour_cost'] else 0.0

        # Calculate other costs
        cursor.execute('''
            SELECT SUM(amount) as other_costs
            FROM event_costs
            WHERE event_id = ?
        ''', (event_id,))
        result = cursor.fetchone()
        other_costs = float(result['other_costs']) if result and result['other_costs'] else 0.0

        # Calculate totals
        total_cost = labour_cost + other_costs
        profit_margin = revenue - total_cost

        # Check if event_analysis record exists
        cursor.execute('SELECT id FROM event_analysis WHERE event_id = ?', (event_id,))
        existing = cursor.fetchone()

        if existing:
            # Update existing record (preserving other fields like attendance, satisfaction)
            cursor.execute('''
                UPDATE event_analysis
                SET revenue_total = ?,
                    cost_total = ?,
                    profit_margin = ?
                WHERE event_id = ?
            ''', (revenue, total_cost, profit_margin, event_id))
            action = "Updated"
            updated_count += 1
        else:
            # Create new record with just financial data
            cursor.execute('''
                INSERT INTO event_analysis
                (event_id, revenue_total, cost_total, profit_margin)
                VALUES (?, ?, ?, ?)
            ''', (event_id, revenue, total_cost, profit_margin))
            action = "Created"
            updated_count += 1

        # Print summary for this event
        if revenue > 0 or total_cost > 0:
            print(f"{action} - Event {event_id}: {event_name}")
            print(f"  Revenue: ${revenue:.2f}")
            print(f"  Costs: ${total_cost:.2f} (Labour: ${labour_cost:.2f}, Other: ${other_costs:.2f})")
            print(f"  Profit: ${profit_margin:.2f}")
            print()
        else:
            print(f"Skipped - Event {event_id}: {event_name} (no financial data)")
            skipped_count += 1

    conn.commit()
    conn.close()

    print("=" * 60)
    print(f"[SUCCESS] Recalculation complete!")
    print(f"  Updated: {updated_count} events")
    print(f"  Skipped: {skipped_count} events (no financial data)")
    print(f"  Total: {len(completed_events)} completed events")
    print("\nYou can now view updated revenue in the Analysis view!")

if __name__ == '__main__':
    print("=" * 60)
    print("Event Revenue Recalculation Tool")
    print("=" * 60)
    print()
    recalculate_all_event_revenue()
