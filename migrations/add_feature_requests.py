"""Add feature requests table to database"""
import sqlite3

def add_feature_requests_table():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Create feature requests table
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

    print("[OK] Created feature_requests table")

    # Add initial analytics feature requests
    initial_requests = [
        (
            "Individual Bookings/Transactions Tracking",
            "Create a bookings table to track individual ticket purchases with:\n" +
            "- Customer name and email\n" +
            "- Member vs non-member status\n" +
            "- Booking date (to track lead time)\n" +
            "- Booking source (how they heard about it)\n" +
            "- Payment method\n" +
            "- Attendance tracking (did they show up?)\n" +
            "- Cancellation and refund tracking\n\n" +
            "This would unlock: no-show rates, booking patterns, member analysis, customer history, marketing effectiveness",
            "High",
            "Submitted"
        ),
        (
            "Waitlist Management System",
            "Add waitlist tracking to capture demand beyond capacity:\n" +
            "- Track customers on waitlist\n" +
            "- Monitor conversion from waitlist to bookings\n" +
            "- Understand true demand for events\n" +
            "- Automatic notifications when spots open up",
            "Medium",
            "Submitted"
        ),
        (
            "Customer Database",
            "Create a customer/member management system:\n" +
            "- Track all customers with contact info\n" +
            "- Event attendance history\n" +
            "- Total lifetime spend\n" +
            "- Preferred event types\n" +
            "- Member status tracking\n\n" +
            "Enables: repeat customer identification, loyalty analysis, personalized marketing",
            "High",
            "Submitted"
        ),
        (
            "Marketing Campaign Tracking",
            "Track marketing effectiveness:\n" +
            "- Campaign costs per event\n" +
            "- Platform used (Facebook, Instagram, email, etc.)\n" +
            "- Reach and impressions\n" +
            "- Conversion tracking\n" +
            "- ROI calculation",
            "Medium",
            "Submitted"
        ),
        (
            "Customer Feedback System",
            "Post-event survey and feedback collection:\n" +
            "- Event ratings from customers\n" +
            "- Feedback comments\n" +
            "- Would attend again indicator\n" +
            "- Track satisfaction trends over time",
            "Low",
            "Submitted"
        ),
        (
            "External Factors Tracking",
            "Track external factors affecting event success:\n" +
            "- Weather conditions on event day\n" +
            "- Competing events in the area\n" +
            "- School holidays/term time\n" +
            "- Helps identify patterns in attendance fluctuations",
            "Low",
            "Submitted"
        )
    ]

    for title, description, priority, status in initial_requests:
        cursor.execute('''
            INSERT INTO feature_requests (title, description, priority, status, submitted_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, priority, status, 'System - Analytics Analysis'))

    print(f"[OK] Added {len(initial_requests)} initial feature requests")

    conn.commit()
    conn.close()
    print("\nFeature requests table setup complete!")

if __name__ == '__main__':
    add_feature_requests_table()
