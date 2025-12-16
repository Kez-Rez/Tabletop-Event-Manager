"""Add backup help section to the help system"""
import sqlite3
from datetime import datetime

def add_backup_help():
    """Add comprehensive backup help section"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Create backup help content
    backup_content = r"""<h1>Database Backups - Protecting Your Data</h1>
<p></p>
<h2>What Are Backups?</h2>
<p>Backups are complete copies of your events.db database file. They contain all your event data, templates, checklists, settings, and everything else stored in the application.</p>
<p></p>
<h2>Two Types of Backups</h2>
<p></p>
<h3>1. Automatic Daily Backups</h3>
<ul>
<li>Created automatically on the first launch each day</li>
<li>Stored in the backups/ folder in your program directory</li>
<li>Named with the date: events_backup_YYYYMMDD.db (e.g., events_backup_20251215.db)</li>
<li>Keeps only the last 7 backups (older backups are automatically deleted)</li>
<li>Backup status shown at the bottom of the main window</li>
</ul>
<p></p>
<h3>2. Manual Backups</h3>
<ul>
<li>Created whenever you want with Ctrl+B or from Settings → Backup tab</li>
<li>You choose where to save them</li>
<li>Named with date and time: events_backup_YYYYMMDD_HHMMSS.db</li>
<li>Kept forever (you manage them)</li>
<li>Recommended before major changes</li>
</ul>
<p></p>
<h2>How to Create a Manual Backup</h2>
<p></p>
<ol>
<li>Press Ctrl+B or go to Settings → Backup tab</li>
<li>Click "Backup Database Now"</li>
<li>Choose a safe location (recommend cloud storage or external drive)</li>
<li>Click Save</li>
</ol>
<p></p>
<h2>How to Restore from a Backup</h2>
<p>If your database becomes corrupted or you need to recover old data:</p>
<p></p>
<ol>
<li>Close the application completely</li>
<li>Find your backup file in the backups/ folder or wherever you saved manual backups</li>
<li>Delete or rename the current events.db file</li>
<li>Copy your backup file and rename it to events.db</li>
<li>Restart the application</li>
</ol>
<p></p>
<h3>Example Recovery:</h3>
<ul>
<li>Delete: events.db</li>
<li>Copy: backups/events_backup_20251215.db</li>
<li>Rename to: events.db</li>
<li>Restart program</li>
</ul>
<p></p>
<h2>Best Practices</h2>
<p></p>
<ul class="checklist">
<li class="unchecked">Create a manual backup before making major changes</li>
<li class="unchecked">Keep manual backups in a safe location (cloud storage, external drive)</li>
<li class="unchecked">Check the backup status at the bottom of the main window</li>
<li class="unchecked">Test your backup recovery process at least once</li>
<li class="unchecked">Automatic backups are great for recent data, but keep important manual backups elsewhere</li>
</ul>
<p></p>
<h2>Understanding Backup Files</h2>
<p>Backup files are complete, standalone copies of your database. This means:</p>
<ul>
<li>You can copy them to any computer with this program</li>
<li>Your data will work perfectly after restoration</li>
<li>They contain everything - events, templates, settings, etc.</li>
<li>Each backup is independent and complete</li>
</ul>
<p></p>
<h2>Where Are Backups Stored?</h2>
<p></p>
<h3>Automatic Backups:</h3>
<p>Located in: backups/ folder in your program directory</p>
<p>Example: C:\Users\YourName\Documents\Learning Programming\BG Events\backups\</p>
<p></p>
<h3>Manual Backups:</h3>
<p>Wherever you choose to save them when creating the backup</p>
<p></p>
<h2>Troubleshooting</h2>
<p></p>
<h3>Q: The program stopped working - how do I recover?</h3>
<p>Follow the restore steps above to replace events.db with your most recent backup file.</p>
<p></p>
<h3>Q: I don't see any automatic backups</h3>
<p>Check the backups/ folder. If it doesn't exist, the program will create it on next launch. Create a manual backup immediately.</p>
<p></p>
<h3>Q: Can I backup to cloud storage?</h3>
<p>Yes! When creating manual backups, save them to OneDrive, Google Drive, Dropbox, or any cloud storage location.</p>
<p></p>
<h3>Q: How much space do backups use?</h3>
<p>Backups are the same size as your events.db file - typically a few MB. Not much space needed!</p>
<p></p>
<p><b>Remember: Regular backups are your safety net. Create them often!</b></p>"""

    # Get the highest sort_order
    cursor.execute('SELECT MAX(sort_order) FROM help_content')
    max_sort = cursor.fetchone()[0]
    next_sort = (max_sort or 0) + 1

    # Check if backup help already exists
    cursor.execute("SELECT id FROM help_content WHERE section_name = 'database_backups'")
    existing = cursor.fetchone()

    if existing:
        print(f"Updating existing backup help section (ID: {existing[0]})")
        cursor.execute('''
            UPDATE help_content
            SET content = ?, current_version = current_version + 1, last_modified = ?, modified_by = ?
            WHERE id = ?
        ''', (backup_content, datetime.now(), 'System', existing[0]))
    else:
        print("Creating new backup help section")
        cursor.execute('''
            INSERT INTO help_content (section_name, title, content, sort_order, current_version, last_modified, modified_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('database_backups', 'Database Backups & Recovery', backup_content, next_sort, 1, datetime.now(), 'System'))

    conn.commit()
    print("[SUCCESS] Backup help section added successfully!")
    print(f"  Sort order: {next_sort}")
    print("  You can view it in Help & FAQ tab")

    conn.close()

if __name__ == '__main__':
    add_backup_help()
