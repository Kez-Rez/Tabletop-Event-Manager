"""Add editable help system with event type guides and version tracking"""
import sqlite3
import shutil
from datetime import datetime

def add_help_system():
    # Create backup
    backup_name = f"events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2('events.db', backup_name)
    print(f"[BACKUP] Created backup: {backup_name}")

    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Create help_content table for general help/FAQ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS help_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_name TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("[OK] Created help_content table")

    # Create event_type_guides table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_type_guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type_id INTEGER NOT NULL UNIQUE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            current_version INTEGER DEFAULT 1,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_type_id) REFERENCES event_types(id) ON DELETE CASCADE
        )
    ''')
    print("[OK] Created event_type_guides table")

    # Create guide_revisions table for version history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guide_revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            content TEXT NOT NULL,
            modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_by TEXT NOT NULL,
            change_notes TEXT,
            FOREIGN KEY (guide_id) REFERENCES event_type_guides(id) ON DELETE CASCADE
        )
    ''')
    print("[OK] Created guide_revisions table")

    # Create help_revisions table for help content history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS help_revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            help_content_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_by TEXT NOT NULL,
            change_notes TEXT,
            FOREIGN KEY (help_content_id) REFERENCES help_content(id) ON DELETE CASCADE
        )
    ''')
    print("[OK] Created help_revisions table")

    # Insert default help sections
    default_sections = [
        ('Getting Started', '''<h1>Welcome to TT Events Manager!</h1>

<h2>Quick Start Guide</h2>

<h3>1. Create Event Templates</h3>
<p>Templates save time by storing common event configurations. Go to the <b>Templates</b> tab to create templates for your recurring events.</p>

<h3>2. Create Events</h3>
<p>Use templates or create events from scratch in the <b>Events</b> tab. Fill in:</p>
<ul>
<li>Event name and date</li>
<li>Event type (Magic, Lorcana, etc.)</li>
<li>Capacity and ticket information</li>
<li>Checklists and tasks</li>
</ul>

<h3>3. Manage Pre-Event Tasks</h3>
<p>Use checklists to track preparation tasks. Mark items as "Show on Dashboard" for important deadlines.</p>

<h3>4. Post-Event Analysis</h3>
<p>After the event, record:</p>
<ul>
<li>Actual attendance</li>
<li>Satisfaction breakdown</li>
<li>Financial data (revenue and costs)</li>
</ul>

<h3>5. View Analytics</h3>
<p>Check the <b>Analysis</b> tab to see trends, performance metrics, and insights over time.</p>
'''),

        ('FAQ', '''<h1>Frequently Asked Questions</h1>

<h3>How do I mark an event as completed?</h3>
<p>Open the event details and check the "Is Completed" checkbox in the event information.</p>

<h3>How do I cancel an event?</h3>
<p>Open the event details and check the "Is Cancelled" checkbox. You can also add a cancellation reason and date.</p>

<h3>What is the satisfaction breakdown?</h3>
<p>Instead of guessing an overall satisfaction score, you enter what percentage of attendees:</p>
<ul>
<li><b>Loved it</b> (8-10/10): Very positive feedback</li>
<li><b>Liked it</b> (5-7/10): Moderate positive feedback</li>
<li><b>Didn't enjoy</b> (1-4/10): Negative feedback</li>
</ul>
<p>The system automatically calculates a weighted satisfaction score.</p>

<h3>How do I backup my data?</h3>
<p>Go to <b>Settings</b> and click the "Backup Database" button. Choose a location to save your backup file.</p>

<h3>Can I print event information?</h3>
<p>Yes! Open any event and click "Print Event Sheet" to generate a printable PDF with all event details.</p>
'''),

        ('Troubleshooting', '''<h1>Troubleshooting</h1>

<h3>The app won't start</h3>
<p>Try the following:</p>
<ol>
<li>Make sure Python and all dependencies are installed</li>
<li>Check that the database file (events.db) exists and isn't corrupted</li>
<li>Try running from command line to see error messages</li>
</ol>

<h3>Data isn't saving</h3>
<p>Check that:</p>
<ul>
<li>You clicked the "Save" button</li>
<li>All required fields are filled in</li>
<li>The database file isn't read-only</li>
</ul>

<h3>Analytics show no data</h3>
<p>Make sure you have:</p>
<ul>
<li>Marked events as "completed"</li>
<li>Entered post-event analysis data</li>
<li>Selected the correct time period filter</li>
</ul>

<h3>Need more help?</h3>
<p>Submit a feature request or bug report using the <b>Feature Requests</b> menu!</p>
''')
    ]

    for section_name, content in default_sections:
        cursor.execute('''
            INSERT OR IGNORE INTO help_content (section_name, content, modified_by)
            VALUES (?, ?, ?)
        ''', (section_name, content, 'System'))

    print(f"[OK] Added {len(default_sections)} default help sections")

    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("SUCCESS! Editable help system created.")
    print("Features:")
    print("- Editable help/FAQ sections")
    print("- Event type guides with rich formatting")
    print("- Version tracking with dates and initials")
    print("- Print functionality")
    print(f"Backup saved as: {backup_name}")
    print("="*60)

if __name__ == '__main__':
    add_help_system()
