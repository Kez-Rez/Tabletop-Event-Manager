"""Fix help system schema - add missing columns and standardize names"""
import sqlite3
import shutil
from datetime import datetime

def fix_help_system_schema():
    # Create backup
    backup_name = f"events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2('events.db', backup_name)
    print(f"[BACKUP] Created backup: {backup_name}")

    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    print("\nFixing help system schema...")

    # Step 1: Add missing columns to help_content
    print("[1/4] Adding title and sort_order to help_content...")
    try:
        cursor.execute('ALTER TABLE help_content ADD COLUMN title TEXT')
        print("  - Added title column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("  - title column already exists")
        else:
            raise

    try:
        cursor.execute('ALTER TABLE help_content ADD COLUMN sort_order INTEGER DEFAULT 0')
        print("  - Added sort_order column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("  - sort_order column already exists")
        else:
            raise

    try:
        cursor.execute('ALTER TABLE help_content ADD COLUMN current_version INTEGER DEFAULT 1')
        print("  - Added current_version column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("  - current_version column already exists")
        else:
            raise

    # Step 2: Set title from section_name for existing records
    print("[2/4] Setting titles for existing records...")
    cursor.execute('UPDATE help_content SET title = section_name WHERE title IS NULL')
    print(f"  - Updated {cursor.rowcount} records")

    # Step 3: Fix guide_revisions columns
    print("[3/4] Checking guide_revisions columns...")
    cursor.execute('PRAGMA table_info(guide_revisions)')
    guide_cols = [col[1] for col in cursor.fetchall()]

    if 'modified_date' in guide_cols and 'created_at' not in guide_cols:
        # Need to recreate table with correct column names
        print("  - Recreating guide_revisions with correct column names...")
        cursor.execute('''
            CREATE TABLE guide_revisions_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guide_id INTEGER NOT NULL,
                version_number INTEGER NOT NULL,
                content TEXT NOT NULL,
                change_notes TEXT,
                modified_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (guide_id) REFERENCES event_type_guides(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            INSERT INTO guide_revisions_new (id, guide_id, version_number, content, change_notes, modified_by, created_at)
            SELECT id, guide_id, version_number, content, change_notes, modified_by, modified_date
            FROM guide_revisions
        ''')

        cursor.execute('DROP TABLE guide_revisions')
        cursor.execute('ALTER TABLE guide_revisions_new RENAME TO guide_revisions')
        print("  - Recreated guide_revisions table")
    else:
        print("  - guide_revisions columns are correct")

    # Step 4: Fix help_revisions columns
    print("[4/4] Checking help_revisions columns...")
    cursor.execute('PRAGMA table_info(help_revisions)')
    help_cols = [col[1] for col in cursor.fetchall()]

    if 'modified_date' in help_cols and 'created_at' not in help_cols:
        # Need to recreate table with correct column names
        print("  - Recreating help_revisions with correct column names...")
        cursor.execute('''
            CREATE TABLE help_revisions_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                help_content_id INTEGER NOT NULL,
                version_number INTEGER NOT NULL,
                content TEXT NOT NULL,
                change_notes TEXT,
                modified_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (help_content_id) REFERENCES help_content(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            INSERT INTO help_revisions_new (id, help_content_id, content, change_notes, modified_by, created_at)
            SELECT id, help_content_id, content, change_notes, modified_by, modified_date
            FROM help_revisions
        ''')

        # Check if version_number exists in old table
        if 'version_number' in help_cols:
            cursor.execute('DROP TABLE help_revisions_new')
            cursor.execute('''
                CREATE TABLE help_revisions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    help_content_id INTEGER NOT NULL,
                    version_number INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    change_notes TEXT,
                    modified_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (help_content_id) REFERENCES help_content(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('''
                INSERT INTO help_revisions_new (id, help_content_id, version_number, content, change_notes, modified_by, created_at)
                SELECT id, help_content_id, version_number, content, change_notes, modified_by, modified_date
                FROM help_revisions
            ''')

        cursor.execute('DROP TABLE help_revisions')
        cursor.execute('ALTER TABLE help_revisions_new RENAME TO help_revisions')
        print("  - Recreated help_revisions table")
    else:
        print("  - help_revisions columns are correct")

    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("SUCCESS! Help system schema fixed.")
    print("Changes:")
    print("- Added title, sort_order, current_version to help_content")
    print("- Standardized revision table column names")
    print(f"Backup saved as: {backup_name}")
    print("="*60)

    return True

if __name__ == '__main__':
    fix_help_system_schema()
