import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    """Manages all database operations for TT Events Manager"""

    def __init__(self, db_path: str = "events.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Event types table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Playing formats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playing_formats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Pairing methods table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pairing_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Pairing apps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pairing_apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Event templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                event_type_id INTEGER,
                playing_format_id INTEGER,
                pairing_method_id INTEGER,
                pairing_app_id INTEGER,
                max_capacity INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_type_id) REFERENCES event_types(id),
                FOREIGN KEY (playing_format_id) REFERENCES playing_formats(id),
                FOREIGN KEY (pairing_method_id) REFERENCES pairing_methods(id),
                FOREIGN KEY (pairing_app_id) REFERENCES pairing_apps(id)
            )
        ''')

        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER,
                event_name TEXT NOT NULL,
                event_date DATE NOT NULL,
                start_time TIME,
                end_time TIME,
                event_type_id INTEGER,
                playing_format_id INTEGER,
                pairing_method_id INTEGER,
                pairing_app_id INTEGER,
                max_capacity INTEGER,
                tickets_available INTEGER,
                description TEXT,
                number_of_rounds INTEGER,
                tables_booked INTEGER DEFAULT 0,
                include_attendees INTEGER DEFAULT 0,
                is_organised BOOLEAN DEFAULT 0,
                tickets_live BOOLEAN DEFAULT 0,
                is_advertised BOOLEAN DEFAULT 0,
                is_completed BOOLEAN DEFAULT 0,
                is_cancelled BOOLEAN DEFAULT 0,
                is_deleted BOOLEAN DEFAULT 0,
                deleted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES event_templates(id),
                FOREIGN KEY (event_type_id) REFERENCES event_types(id),
                FOREIGN KEY (playing_format_id) REFERENCES playing_formats(id),
                FOREIGN KEY (pairing_method_id) REFERENCES pairing_methods(id),
                FOREIGN KEY (pairing_app_id) REFERENCES pairing_apps(id)
            )
        ''')

        # Ticket tiers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_tiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                tier_name TEXT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                quantity_available INTEGER NOT NULL,
                quantity_sold INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')

        # Checklist categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklist_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Template checklist items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_checklist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                category_id INTEGER,
                description TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES checklist_categories(id)
            )
        ''')

        # Event checklist items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_checklist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                category_id INTEGER,
                description TEXT NOT NULL,
                is_completed BOOLEAN DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                show_on_dashboard BOOLEAN DEFAULT 0,
                include_in_pdf BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES checklist_categories(id)
            )
        ''')

        # Cost categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Event costs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                category_id INTEGER,
                description TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES cost_categories(id)
            )
        ''')

        # Labour costs table (calculated automatically)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS labour_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                staff_count INTEGER DEFAULT 1,
                hours_worked DECIMAL(5,2),
                hourly_rate DECIMAL(10,2),
                total_cost DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')

        # Prize support items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prize_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                cost_per_item DECIMAL(10,2),
                total_cost DECIMAL(10,2),
                is_received BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                recipients INTEGER DEFAULT 1,
                quantity_handed_out INTEGER DEFAULT 0,
                item_type TEXT DEFAULT 'prize',
                quantity_per_player INTEGER,
                supplier TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')

        # Event notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                note_text TEXT NOT NULL,
                show_in_notes_tab BOOLEAN DEFAULT 0,
                include_in_printout BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')

        # Template feedback notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                feedback_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')

        # Post-event analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL UNIQUE,
                actual_attendance INTEGER,
                attendee_satisfaction DECIMAL(3,1) CHECK(attendee_satisfaction >= 0 AND attendee_satisfaction <= 10),
                satisfaction_loved_pct INTEGER CHECK(satisfaction_loved_pct >= 0 AND satisfaction_loved_pct <= 100),
                satisfaction_liked_pct INTEGER CHECK(satisfaction_liked_pct >= 0 AND satisfaction_liked_pct <= 100),
                satisfaction_disliked_pct INTEGER CHECK(satisfaction_disliked_pct >= 0 AND satisfaction_disliked_pct <= 100),
                profit_margin DECIMAL(10,2),
                revenue_total DECIMAL(10,2),
                cost_total DECIMAL(10,2),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')

        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT NOT NULL UNIQUE,
                setting_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Feature requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Submitted',
                submitted_by TEXT,
                submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Help content table (editable help sections)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS help_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section_name TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                current_version INTEGER DEFAULT 1,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Event type guides table
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

        # Guide revisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guide_revisions (
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

        # Help content revisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS help_revisions (
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

        # Calendar entries table (for manual entries like public holidays)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date DATE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                entry_type TEXT DEFAULT 'misc',
                color TEXT DEFAULT '#90EE90',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert default checklist categories
        default_categories = [
            ('Before the Event', 1),
            ('During the Event', 2),
            ('After the Event', 3),
            ('Other', 4)
        ]

        for category, order in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO checklist_categories (name, sort_order)
                VALUES (?, ?)
            ''', (category, order))

        # Only insert defaults if tables are empty (first-time setup)
        # Check if event_types table is empty
        cursor.execute('SELECT COUNT(*) as count FROM event_types')
        if cursor.fetchone()['count'] == 0:
            # Insert default cost categories
            default_cost_categories = [
                'Labour',
                'Prize Support',
                'Materials',
                'Food & Drink',
                'Other'
            ]

            for category in default_cost_categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO cost_categories (name)
                    VALUES (?)
                ''', (category,))

            # Insert default event types
            default_event_types = [
                'Magic: The Gathering',
                'Lorcana',
                'Riftbound',
                'Other TCG',
                'Board Game Night',
                'Board Game Tournament',
                'D&D Session',
                'Warhammer 40k',
                'Kill Team',
                'Blood Bowl',
                'Other Warhammer'
            ]

            for event_type in default_event_types:
                cursor.execute('''
                    INSERT OR IGNORE INTO event_types (name)
                    VALUES (?)
                ''', (event_type,))

            # Insert default playing formats
            default_formats = [
                'Standard',
                'Modern',
                'Commander',
                'Draft',
                'Sealed',
                'Pioneer',
                'Legacy',
                'Vintage',
                'Pauper',
                'Casual'
            ]

            for format_name in default_formats:
                cursor.execute('''
                    INSERT OR IGNORE INTO playing_formats (name)
                    VALUES (?)
                ''', (format_name,))

            # Insert default pairing methods
            default_pairing_methods = [
                'Swiss',
                'Single Elimination',
                'Double Elimination',
                'Round Robin',
                'Pods',
                'Free Play'
            ]

            for method in default_pairing_methods:
                cursor.execute('''
                    INSERT OR IGNORE INTO pairing_methods (name)
                    VALUES (?)
                ''', (method,))

            # Insert default pairing apps
            default_pairing_apps = [
                'EventLink',
                'Melee',
                'Challonge',
                'Companion App',
                'Manual'
            ]

            for app in default_pairing_apps:
                cursor.execute('''
                    INSERT OR IGNORE INTO pairing_apps (name)
                    VALUES (?)
                ''', (app,))

        # Insert default help content sections
        default_help_sections = [
            ('getting_started', 'Getting Started', '''
<h1>Welcome to TT Events Manager</h1>

<p>TT Events Manager is a comprehensive event management system designed specifically for tabletop gaming stores and event organizers.</p>

<h2>Quick Start Guide</h2>

<ol>
<li><b>Create Event Templates</b> - Set up reusable templates for your regular events</li>
<li><b>Schedule Events</b> - Use templates or create custom events</li>
<li><b>Manage Tickets</b> - Set up ticket tiers and track sales</li>
<li><b>Track Costs</b> - Record labour, prize support, and other expenses</li>
<li><b>Post-Event Analysis</b> - Review attendance, satisfaction, and profitability</li>
</ol>

<h2>Navigation</h2>

<ul>
<li><b>Dashboard</b> - View important checklist items and prize tracking</li>
<li><b>Events</b> - Manage your upcoming and past events</li>
<li><b>Templates</b> - Create and edit event templates</li>
<li><b>Analysis</b> - View trends and performance metrics</li>
<li><b>Settings</b> - Configure labour rates and backup settings</li>
</ul>
            ''', 1),
            ('faq', 'Frequently Asked Questions', '''
<h1>Frequently Asked Questions</h1>

<h2>Events</h2>

<h3>How do I create a new event?</h3>
<p>Click the "Events" button in the sidebar, then click "New Event". You can either create an event from scratch or use an existing template.</p>

<h3>How do I cancel an event?</h3>
<p>Open the event details and check the "Event Cancelled" checkbox. You can also add a cancellation reason for your records.</p>

<h2>Templates</h2>

<h3>What are event templates?</h3>
<p>Templates let you save common event configurations (event type, format, capacity, checklist items) that you can reuse when creating new events.</p>

<h2>Analysis</h2>

<h3>What satisfaction score should I aim for?</h3>
<p>The satisfaction score ranges from 0-10. A score of 7+ is generally considered good, while 8+ is excellent.</p>

<h3>How is the satisfaction score calculated?</h3>
<p>The score is calculated from the breakdown percentages: (Loved% × 9 + Liked% × 6 + Didn't Enjoy% × 2.5) ÷ 100</p>
            ''', 2),
            ('troubleshooting', 'Troubleshooting', '''
<h1>Troubleshooting</h1>

<h2>Database Issues</h2>

<h3>Creating Backups</h3>
<p>Always create regular backups of your database. Go to Settings > Backup to create a manual backup or configure automatic backups.</p>

<h3>Restoring from Backup</h3>
<p>If you need to restore from a backup, close the application and replace events.db with your backup file.</p>

<h2>Performance</h2>

<h3>Application Running Slowly</h3>
<p>If the application is slow, try these steps:</p>
<ol>
<li>Close other applications to free up memory</li>
<li>Create a backup and restart the application</li>
<li>Archive old completed events if you have many events in the database</li>
</ol>

<h2>Need More Help?</h2>

<p>For additional support or feature requests, use the Feature Requests menu to submit your feedback.</p>
            ''', 3)
        ]

        for section_name, title, content, sort_order in default_help_sections:
            cursor.execute('''
                INSERT OR IGNORE INTO help_content (section_name, title, content, sort_order)
                VALUES (?, ?, ?, ?)
            ''', (section_name, title, content, sort_order))

        # Insert default settings
        default_settings = [
            ('weekday_before_6pm_rate', '22.00'),
            ('weekday_after_6pm_rate', '25.50'),
            ('saturday_rate', '30.00'),
            ('sunday_rate', '35.00'),
            ('public_holiday_rate', '40.00'),
            ('backup_location', ''),
            ('colour_scheme', 'pastel')
        ]

        for key, value in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO settings (setting_key, setting_value)
                VALUES (?, ?)
            ''', (key, value))

        conn.commit()
        conn.close()

    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value by key"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT setting_value FROM settings WHERE setting_key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result['setting_value'] if result else None

    def update_setting(self, key: str, value: str):
        """Update a setting value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now()))
        conn.commit()
        conn.close()
