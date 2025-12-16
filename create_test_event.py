"""Create a test event to verify post-event analysis display"""
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Create a test event
event_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
cursor.execute('''
    INSERT INTO events (event_name, event_date, start_time, end_time, max_capacity, is_completed)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('POST-EVENT TEST', event_date, '18:00', '22:00', 32, 0))

event_id = cursor.lastrowid
print(f"Created test event with ID: {event_id}")

# Add ticket tiers
cursor.execute('''
    INSERT INTO ticket_tiers (event_id, tier_name, price, quantity_available, quantity_sold)
    VALUES (?, ?, ?, ?, ?)
''', (event_id, 'Standard Entry', 15.00, 30, 0))

cursor.execute('''
    INSERT INTO ticket_tiers (event_id, tier_name, price, quantity_available, quantity_sold)
    VALUES (?, ?, ?, ?, ?)
''', (event_id, 'VIP Entry', 25.00, 10, 0))

print("Added 2 ticket tiers")

# Add prize items
cursor.execute('''
    INSERT INTO prize_items (event_id, description, quantity, cost_per_item, total_cost, is_received, quantity_handed_out)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (event_id, 'Booster Pack', 12, 4.50, 54.00, 1, 0))

cursor.execute('''
    INSERT INTO prize_items (event_id, description, quantity, cost_per_item, total_cost, is_received, quantity_handed_out)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (event_id, 'Playmat', 3, 25.00, 75.00, 1, 0))

print("Added 2 prize items")

# Add a labour cost entry
cursor.execute('''
    INSERT INTO labour_costs (event_id, staff_name, hours_worked, hourly_rate, total_cost, rate_type, work_status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (event_id, 'Test Staff', 4.0, 25.50, 102.00, 'weekday_after_6pm', 'full'))

print("Added labour cost entry")

conn.commit()
conn.close()

print(f"\n✓ Test event created successfully!")
print(f"Event ID: {event_id}")
print(f"Event Name: POST-EVENT TEST")
print(f"\nNow open the application and navigate to this event's Post-Event tab to verify:")
print("1. Attendee Satisfaction Breakdown with scale explanation")
print("2. Event Smoothness Rating with detailed examples")
print("3. Overall Success Score display")
print("4. Real-time ticket revenue updates")
print("5. Real-time prize remaining updates")
