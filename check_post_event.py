"""Check post-event analysis table structure"""
import sqlite3

conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Check table structure
cursor.execute('PRAGMA table_info(event_analysis)')
cols = cursor.fetchall()
print('Columns in event_analysis table:')
for col in cols:
    print(f'  - {col[1]} ({col[2]})')

# Check if we have any analysis data
cursor.execute('SELECT COUNT(*) FROM event_analysis')
count = cursor.fetchone()[0]
print(f'\nTotal analysis records: {count}')

if count > 0:
    cursor.execute('''
        SELECT
            event_id,
            actual_attendance,
            attendee_satisfaction,
            event_smoothness,
            overall_success_score
        FROM event_analysis
        LIMIT 3
    ''')
    records = cursor.fetchall()
    print('\nSample records:')
    for rec in records:
        print(f'  Event {rec[0]}: Attendance={rec[1]}, Satisfaction={rec[2]}, Smoothness={rec[3]}, Success={rec[4]}')

conn.close()
