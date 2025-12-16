# TT Events Manager - Complete System Specification

## Executive Summary

TT Events Manager is a desktop application for managing board game and tabletop gaming events at a gaming venue. It handles event planning, ticketing, player tracking, post-event analysis, financial reporting, and operational workflows.

**Technology Stack:**
- **Language:** Python 3.11+
- **GUI Framework:** CustomTkinter (modern tkinter wrapper)
- **Database:** SQLite 3
- **Charting:** Matplotlib
- **PDF Generation:** ReportLab (for exporting event details)

**Application Type:** Desktop application with local SQLite database

---

## 1. System Architecture

### 1.1 Application Structure

```
TT Events Manager/
├── main.py                      # Application entry point and main window
├── database.py                  # Database initialization and schema
├── event_manager.py             # Business logic for event CRUD operations
├── pdf_generator.py             # PDF export functionality
├── template_manager.py          # Template CRUD operations
├── events.db                    # SQLite database file
├── backups/                     # Automatic daily backups
│   └── events_backup_YYYYMMDD.db
├── views/                       # UI components (each is a CTkFrame)
│   ├── __init__.py
│   ├── events_view.py          # Main events list view
│   ├── event_details_view.py   # Detailed event management (multi-tab)
│   ├── event_form_view.py      # Event creation/edit form
│   ├── event_dialogs.py        # Event-related dialogs
│   ├── templates_view.py       # Template management view
│   ├── settings_view.py        # Settings and configuration
│   ├── analysis_view.py        # Post-event analytics and charts
│   ├── help_view.py            # Help documentation with rich text editor
│   ├── feature_requests_view.py # Feature request tracking
│   ├── deleted_events_view.py  # Soft-deleted events management
│   ├── calendar_view.py        # Calendar for viewing events and bookings
│   ├── calendar_entry_form_view.py # Form for calendar entries
│   ├── table_booking_view.py   # Table booking management
│   ├── ticket_tier_form_view.py # Ticket tier configuration
│   └── feedback_view.py        # Feedback template management
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── text_selection.py       # Text selection handling
│   ├── navigation.py           # View navigation management
│   └── dialog_scaling.py       # Dialog window scaling utilities
├── widgets/                     # Custom widgets
│   ├── __init__.py
│   └── selectable_label.py     # Selectable text labels
└── migrations/                  # Database migration scripts
    ├── add_*.py                # Various migration scripts
    ├── update_*.py
    └── fix_*.py
```

### 1.2 Main Application Flow

**Startup Sequence:**
1. Initialize Database (create tables if not exist)
2. Perform automatic daily backup
3. Create main window (1200x800, min 800x600)
4. Initialize navigation manager
5. Create sidebar with navigation buttons
6. Load initial view (Events View)

**Navigation Structure:**
- Sidebar with buttons for each major view
- Single content area that swaps between views
- Each view is a CTkFrame that fills the content area

---

## 2. Database Schema

### 2.1 Core Tables

#### events
The primary table for storing event information.

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,                    -- FK to event_templates
    event_name TEXT NOT NULL,
    event_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    event_type_id INTEGER,                  -- FK to event_types
    playing_format_id INTEGER,              -- FK to playing_formats
    pairing_method_id INTEGER,              -- FK to pairing_methods
    pairing_app_id INTEGER,                 -- FK to pairing_apps
    max_capacity INTEGER,
    tickets_available INTEGER,
    description TEXT,
    is_organised BOOLEAN DEFAULT 0,         -- Checklist completion flag
    tickets_live BOOLEAN DEFAULT 0,         -- Tickets on sale flag
    is_advertised BOOLEAN DEFAULT 0,        -- Advertised flag
    is_completed BOOLEAN DEFAULT 0,         -- Event has finished
    is_deleted BOOLEAN DEFAULT 0,           -- Soft delete flag
    is_cancelled BOOLEAN DEFAULT 0,         -- Cancellation flag
    cancellation_reason TEXT,               -- Why event was cancelled
    cancelled_at TIMESTAMP,                 -- When cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES event_templates(id),
    FOREIGN KEY (event_type_id) REFERENCES event_types(id),
    FOREIGN KEY (playing_format_id) REFERENCES playing_formats(id),
    FOREIGN KEY (pairing_method_id) REFERENCES pairing_methods(id),
    FOREIGN KEY (pairing_app_id) REFERENCES pairing_apps(id)
)
```

#### event_templates
Reusable templates for creating events quickly.

```sql
CREATE TABLE event_templates (
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
```

#### event_types
Categorization of events (e.g., "Magic: The Gathering", "Board Game Night")

```sql
CREATE TABLE event_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### playing_formats
Game formats (e.g., "Commander", "Standard", "Draft")

```sql
CREATE TABLE playing_formats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### pairing_methods
How players are matched (e.g., "Swiss", "Single Elimination")

```sql
CREATE TABLE pairing_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### pairing_apps
Software used for pairing (e.g., "EventLink", "Companion")

```sql
CREATE TABLE pairing_apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 2.2 Event Details Tables

#### ticket_tiers
Ticketing system with multiple pricing tiers per event.

```sql
CREATE TABLE ticket_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    tier_name TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity_available INTEGER,
    quantity_sold INTEGER DEFAULT 0,          -- Filled during post-event
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
)
```

#### event_checklist_items
Per-event checklist for task management.

```sql
CREATE TABLE event_checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT 0,
    category TEXT,                            -- Categorization (optional)
    show_in_notes_tab BOOLEAN DEFAULT 0,      -- Show in event notes
    show_on_dashboard BOOLEAN DEFAULT 0,       -- Show on event dashboard
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
)
```

#### prize_items
Prize support for events.

```sql
CREATE TABLE prize_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    prize_name TEXT NOT NULL,
    quantity_required INTEGER,
    quantity_per_player INTEGER DEFAULT 0,     -- For per-player prizes
    supplier TEXT,                             -- Where prize came from
    quantity_handed_out INTEGER DEFAULT 0,     -- Filled during post-event
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
)
```

#### event_costs
Additional costs associated with an event.

```sql
CREATE TABLE event_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    category_id INTEGER,                      -- FK to cost_categories
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES cost_categories(id)
)
```

#### cost_categories
Categories for event costs.

```sql
CREATE TABLE cost_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### labour_costs
Staff labour tracking per event.

```sql
CREATE TABLE labour_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    staff_name TEXT,
    staff_count INTEGER,
    hours_worked DECIMAL(5,2),
    hourly_rate DECIMAL(10,2),
    total_cost DECIMAL(10,2),
    rate_type TEXT,                           -- e.g., "Manager", "Staff"
    work_status TEXT,                         -- e.g., "Completed"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
)
```

#### event_players
Player registration for events.

```sql
CREATE TABLE event_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    player_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
)
```

#### event_notes
Notes associated with events.

```sql
CREATE TABLE event_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
)
```

### 2.3 Post-Event Analysis Tables

#### event_analysis
Post-event metrics and financial analysis.

```sql
CREATE TABLE event_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL UNIQUE,
    actual_attendance INTEGER,                 -- How many showed up
    attendee_satisfaction INTEGER,             -- Rating 0-10 (enjoyment)
    event_smoothness DECIMAL(3,1),            -- Rating 0-10 (operations)
    overall_success_score DECIMAL(3,1),       -- enjoyment + smoothness
    profit_margin DECIMAL(10,2),              -- revenue - costs
    revenue_total DECIMAL(10,2),              -- Total ticket revenue
    cost_total DECIMAL(10,2),                 -- Total costs
    notes TEXT,                                -- Post-event notes
    satisfaction_loved_pct INTEGER,           -- % who "loved" it
    satisfaction_liked_pct INTEGER,           -- % who "liked" it
    satisfaction_disliked_pct INTEGER,        -- % who "disliked" it
    success_rating INTEGER,                   -- Legacy rating field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
)
```

### 2.4 Template System Tables

Templates allow quick creation of recurring events. Each template can have associated data.

#### template_ticket_tiers
```sql
CREATE TABLE template_ticket_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    tier_name TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity_available INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE
)
```

#### template_checklist_items
```sql
CREATE TABLE template_checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    category TEXT,
    show_in_notes_tab BOOLEAN DEFAULT 0,
    show_on_dashboard BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE
)
```

#### template_prize_items
```sql
CREATE TABLE template_prize_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    prize_name TEXT NOT NULL,
    quantity_required INTEGER,
    quantity_per_player INTEGER DEFAULT 0,
    supplier TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE
)
```

#### template_feedback
```sql
CREATE TABLE template_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    feedback_type TEXT NOT NULL,              -- "Attendance", "Success", etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE
)
```

#### template_notes
```sql
CREATE TABLE template_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    send_to_template BOOLEAN DEFAULT 0,       -- Include when using template
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE
)
```

### 2.5 Calendar and Booking Tables

#### calendar_entries
Non-event calendar entries (meetings, closures, etc.)

```sql
CREATE TABLE calendar_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    entry_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    description TEXT,
    entry_type TEXT,                          -- "Meeting", "Closure", etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### standalone_bookings
Table bookings not tied to specific events.

```sql
CREATE TABLE standalone_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    customer_name TEXT,
    contact_info TEXT,
    num_tables INTEGER,
    booking_notes TEXT,
    deposit_amount DECIMAL(10,2),
    booking_status TEXT,                      -- "Confirmed", "Pending", etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### operating_hours
Store operating hours for the venue.

```sql
CREATE TABLE operating_hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week INTEGER NOT NULL,            -- 0=Monday, 6=Sunday
    open_time TIME,
    close_time TIME,
    is_closed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### date_specific_hours
Override operating hours for specific dates.

```sql
CREATE TABLE date_specific_hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    specific_date DATE NOT NULL UNIQUE,
    open_time TIME,
    close_time TIME,
    is_closed BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### daily_capacity_overrides
Override table capacity for specific dates.

```sql
CREATE TABLE daily_capacity_overrides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    override_date DATE NOT NULL UNIQUE,
    tables_available INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### event_type_padding
Padding time before/after events by type.

```sql
CREATE TABLE event_type_padding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type_id INTEGER NOT NULL UNIQUE,
    padding_before_minutes INTEGER DEFAULT 0,
    padding_after_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_type_id) REFERENCES event_types(id) ON DELETE CASCADE
)
```

### 2.6 Help and Documentation Tables

#### help_content
Editable help documentation sections.

```sql
CREATE TABLE help_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_name TEXT NOT NULL,               -- Unique identifier
    title TEXT,                               -- Display title
    content TEXT NOT NULL,                    -- HTML content
    sort_order INTEGER DEFAULT 0,
    current_version INTEGER DEFAULT 1,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by TEXT,                         -- User initials
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### help_revisions
Version history for help content.

```sql
CREATE TABLE help_revisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    help_content_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_notes TEXT,
    modified_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (help_content_id) REFERENCES help_content(id) ON DELETE CASCADE
)
```

#### event_type_guides
Guides specific to event types.

```sql
CREATE TABLE event_type_guides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type_id INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,                    -- HTML content
    current_version INTEGER DEFAULT 1,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_type_id) REFERENCES event_types(id) ON DELETE CASCADE
)
```

#### guide_revisions
Version history for event type guides.

```sql
CREATE TABLE guide_revisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guide_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_notes TEXT,
    modified_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guide_id) REFERENCES event_type_guides(id) ON DELETE CASCADE
)
```

### 2.7 System Tables

#### settings
Application settings and configuration.

```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Common settings:**
- `manager_rate`: Hourly rate for manager labour
- `staff_rate`: Hourly rate for staff labour
- `backup_location`: Custom backup location path

#### feature_requests
Track feature requests from users.

```sql
CREATE TABLE feature_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT,                            -- "Low", "Medium", "High"
    status TEXT DEFAULT 'Pending',            -- "Pending", "In Progress", etc.
    submitted_by TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
)
```

#### checklist_categories
Categories for checklist items.

```sql
CREATE TABLE checklist_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### feedback_items
Template feedback configuration.

```sql
CREATE TABLE feedback_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_type TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 3. Core Business Logic

### 3.1 EventManager Class

**Location:** `event_manager.py`

**Responsibilities:**
- CRUD operations for events
- Event lifecycle management
- Labour cost calculations
- Data validation

**Key Methods:**
```python
get_all_events(include_completed=True) -> List[Dict]
get_event_by_id(event_id) -> Optional[Dict]
create_event(event_data) -> int
update_event(event_id, event_data) -> bool
delete_event(event_id) -> bool  # Soft delete
restore_event(event_id) -> bool
create_event_from_template(template_id, event_name, event_date) -> int
get_labour_costs(event_id) -> List[Dict]
add_labour_cost(event_id, labour_data) -> int
get_total_labour_cost(event_id) -> float
```

### 3.2 Template Manager

**Location:** `template_manager.py`

**Responsibilities:**
- Template CRUD operations
- Copy template data to events

**Key Methods:**
```python
get_all_templates() -> List[Dict]
get_template_by_id(template_id) -> Optional[Dict]
create_template(template_data) -> int
update_template(template_id, template_data) -> bool
delete_template(template_id) -> bool
```

### 3.3 Database Class

**Location:** `database.py`

**Responsibilities:**
- Database initialization
- Schema management
- Connection management
- Reference data population

**Key Methods:**
```python
get_connection() -> sqlite3.Connection
init_database() -> None
populate_reference_data() -> None
```

### 3.4 PDF Generator

**Location:** `pdf_generator.py`

**Responsibilities:**
- Export event details to PDF
- Multi-page layout
- Section formatting

**Key Methods:**
```python
generate_event_pdf(event_data, output_path) -> None
```

---

## 4. User Interface Components

### 4.1 Main Window Structure

**Location:** `main.py` - `BGEventsApp` class

**Layout:**
```
┌────────────────────────────────────────────────────┐
│  [Sidebar - 200px]  │  [Content Area - remainder]  │
│                     │                               │
│  [Events]           │                               │
│  [Templates]        │                               │
│  [Calendar]         │    Current View               │
│  [Table Bookings]   │    (swapped based on          │
│  [Analysis]         │     navigation)               │
│  [Settings]         │                               │
│  [Help]             │                               │
│  [Feature Requests] │                               │
│  [Deleted Events]   │                               │
│                     │                               │
└────────────────────────────────────────────────────┘
```

**Color Scheme:**
- Background: Light mode (#F5F5F5)
- Primary Purple: #8B5FBF
- Secondary Purple: #C5A8D9
- Light Purple: #E6D9F2
- Accent Colors: Pastel blues, pinks, purples

**Features:**
- Zoom in/out (Ctrl+Plus/Minus)
- Reset zoom (Ctrl+0)
- Manual backup (Ctrl+B)
- Automatic daily backup on startup
- Last backup status displayed in main view

### 4.2 Events View

**Location:** `views/events_view.py`

**Features:**
- List of all events with color-coded status
- Filter by completion status
- Quick status indicators (organized, advertised, tickets live)
- Search functionality
- Create new event button
- Click event to open detailed view

**Status Colors:**
- Completed: Green
- Cancelled: Red
- Upcoming: Purple

### 4.3 Event Details View

**Location:** `views/event_details_view.py`

**Multi-tab interface:**

**Tab 1: Event Details**
- Event name, date, times
- Event type, format, pairing method
- Description
- Capacity and ticket availability
- Status flags (organised, advertised, tickets live, completed)
- Cancel event button

**Tab 2: Tickets**
- Multiple ticket tiers
- Price, quantity available
- Add/edit/delete tiers
- Export to PDF button

**Tab 3: Checklist**
- Task list for event preparation
- Categorized tasks
- Checkboxes for completion
- Add/edit/delete tasks
- Overall organization status

**Tab 4: Prizes**
- Prize items with quantities
- Supplier tracking
- Per-player quantity calculation
- Quantity handed out (post-event)
- Add/edit/delete prizes

**Tab 5: Materials**
- Additional costs tracking
- Cost categories
- Amount entry
- Add/edit/delete cost items

**Tab 6: Labour**
- Staff labour tracking
- Hours worked, hourly rate
- Automatic rate lookup from settings
- Total labour cost calculation
- Add/edit/delete labour entries

**Tab 7: Players**
- Player registration list
- Add/remove players
- Player count display

**Tab 8: Notes**
- Free-text notes
- Checklist items flagged for notes view
- Add/edit/delete notes

**Tab 9: Post-Event**
- Actual attendance entry
- Attendee satisfaction rating (0-10)
- Event smoothness rating (0-10)
- Overall success score (calculated: enjoyment + smoothness)
- Ticket quantities sold entry (per tier)
- Prize quantities handed out entry
- Financial summary:
  - Total revenue (calculated from tickets)
  - Labour costs
  - Other costs
  - Total costs
  - Profit/loss
- Post-event notes
- **Save Post-Event Analysis** button
- **Unsaved data warning indicator** (appears when ticket data hasn't been saved)

### 4.4 Event Form View

**Location:** `views/event_form_view.py`

**Purpose:** Create or edit event basic details

**Fields:**
- Event name
- Date picker
- Start/end time
- Event type dropdown
- Playing format dropdown
- Pairing method dropdown
- Pairing app dropdown
- Max capacity
- Description text box
- Template selection (for new events)

### 4.5 Templates View

**Location:** `views/templates_view.py`

**Features:**
- List of all templates
- Create new template
- Edit template
- Delete template (with confirmation)
- Each template shows:
  - Name
  - Event type
  - Associated data counts (tickets, checklist items, prizes)
- Multi-tab template editor (similar to event details)

### 4.6 Calendar View

**Location:** `views/calendar_view.py`

**Features:**
- Month view calendar
- Shows events and calendar entries
- Color coding by entry type
- Click date to see details
- Navigate months
- Add calendar entries (non-event items)

### 4.7 Table Booking View

**Location:** `views/table_booking_view.py`

**Features:**
- List of table bookings
- Create/edit/delete bookings
- Booking details:
  - Date, time range
  - Customer name, contact
  - Number of tables
  - Deposit amount
  - Booking status
  - Notes

### 4.8 Analysis View

**Location:** `views/analysis_view.py`

**Features:**
- Period selector (Last 7/30/90 days, 6 months, year, all time)
- **Key Performance Indicators (KPI cards):**
  - Total events
  - Completed events
  - Cancelled events
  - Total attendees
  - Average attendees per event
  - Total revenue
  - Total costs
  - Total profit
  - Average revenue per event
  - Average revenue per attendee
  - Average attendee satisfaction
  - Average event smoothness
  - Average overall success score
  - Cancellation rate

- **Trend Graphs (matplotlib):**
  - Attendance over time
  - Ticket revenue over time
  - Satisfaction over time
  - Smoothness over time
  - Overall success score over time

- **Performance by Event Type Table:**
  - Event count
  - Total/average attendance
  - Total/average revenue
  - Average satisfaction

- **Capacity Utilization Table:**
  - Event name, date, capacity, actual attendance
  - Utilization percentage

- **Top Performing Events Table:**
  - Sorted by revenue
  - Shows attendance, revenue, satisfaction

### 4.9 Settings View

**Location:** `views/settings_view.py`

**Tabs:**

**Labour Rates Tab:**
- Manager hourly rate
- Staff hourly rate
- Save button

**Backup Tab:**
- Backup Database Now button
- Instructions for backup/restore
- Database file information

**Reference Data Tabs:**
- Event Types: Add/edit/delete
- Playing Formats: Add/edit/delete
- Pairing Methods: Add/edit/delete
- Pairing Apps: Add/edit/delete
- Cost Categories: Add/edit/delete
- Checklist Categories: Add/edit/delete

**Operating Hours Tab:**
- Set hours for each day of week
- Mark days as closed
- Save button

**Table Capacity Tab:**
- Default table capacity
- Date-specific overrides

### 4.10 Help View

**Location:** `views/help_view.py`

**Features:**

**Tab 1: Help & FAQ**
- Editable help sections (stored in database)
- Rich text editor with Word-like features:
  - Bold, italic formatting
  - Headings (H1, H2, H3)
  - Bullet points
  - Checkboxes
  - Numbered lists
  - Auto-continue lists
- Edit/Save buttons with version tracking
- Save dialog requests initials and change notes
- Version history stored in help_revisions table
- Sections include:
  - Getting Started
  - Frequently Asked Questions
  - Troubleshooting
  - Database Backups & Recovery

**Tab 2: Event Type Guides**
- Select event type from dropdown
- Display guide content
- Edit button (same rich text editor)
- Print button (exports to HTML and opens in browser)
- Create new guide if none exists
- Version tracking for guides

### 4.11 Feature Requests View

**Location:** `views/feature_requests_view.py`

**Features:**
- List of feature requests
- Add new request
- Edit status and priority
- Mark as completed
- Filter by status

### 4.12 Deleted Events View

**Location:** `views/deleted_events_view.py`

**Features:**
- List of soft-deleted events
- Restore event button
- Permanent delete button (with confirmation)
- View event details (read-only)

---

## 5. Key Workflows

### 5.1 Creating an Event

**Method 1: From Template**
1. Navigate to Events view
2. Click "Create Event"
3. Select template from dropdown
4. Enter event name and date
5. Click "Create from Template"
6. Template data (tickets, checklist, prizes, notes) copied to new event
7. Event Details view opens for the new event

**Method 2: From Scratch**
1. Navigate to Events view
2. Click "Create Event"
3. Leave template blank
4. Fill in event details
5. Click "Create Event"
6. Event Details view opens for the new event
7. Manually add tickets, checklist, prizes, etc.

### 5.2 Managing Event Lifecycle

**Phase 1: Planning**
- Create event
- Configure ticket tiers
- Set up checklist
- Add prize support
- Add material costs
- Add notes

**Phase 2: Pre-Event**
- Complete checklist tasks
- Mark as "Organised" when checklist complete
- Set "Tickets Live" when tickets go on sale
- Set "Advertised" when promoted
- Register players

**Phase 3: Event Day**
- Run the event
- Track actual attendance

**Phase 4: Post-Event**
1. Navigate to Post-Event tab
2. Enter actual attendance
3. Enter ticket quantities sold (per tier)
4. **Warning appears:** "Unsaved Ticket Data" (if not saved yet)
5. Enter prize quantities handed out
6. Enter satisfaction rating (0-10)
7. Enter smoothness rating (0-10)
8. System calculates:
   - Overall success score (satisfaction + smoothness)
   - Revenue (from ticket sales)
   - Total costs (labour + materials)
   - Profit/loss
9. Add post-event notes
10. **Click "Save Post-Event Analysis"**
11. Warning disappears
12. Mark event as "Completed"

**Phase 5: Analysis**
- Navigate to Analysis view
- View KPIs, trends, and comparisons
- Export reports

### 5.3 Post-Event Revenue Calculation

**Critical Workflow:**

Revenue is NOT automatically calculated. It requires explicit save action:

1. **User enters ticket quantities sold** in Post-Event tab
2. Real-time revenue display updates
3. **Warning banner appears:** "⚠️ Warning: Unsaved Ticket Data"
4. User clicks **"Save Post-Event Analysis"** button
5. System executes calculation:
```sql
-- Calculate revenue
SELECT SUM(price * quantity_sold) as revenue
FROM ticket_tiers
WHERE event_id = ?

-- Calculate labour costs
SELECT SUM(total_cost) as labour_cost
FROM labour_costs
WHERE event_id = ?

-- Calculate other costs
SELECT SUM(amount) as other_costs
FROM event_costs
WHERE event_id = ?

-- Save to event_analysis table
UPDATE event_analysis
SET revenue_total = ?,
    cost_total = ?,
    profit_margin = ?,
    actual_attendance = ?,
    attendee_satisfaction = ?,
    event_smoothness = ?,
    overall_success_score = ?
WHERE event_id = ?
```
6. Warning banner disappears
7. Data now appears in Analysis view

**Important:** If user doesn't click "Save Post-Event Analysis", revenue remains NULL in the database and won't appear in analytics.

### 5.4 Bulk Revenue Recalculation

**Utility Script:** `recalculate_event_revenue.py`

**Purpose:** Fix revenue data for events where ticket sales were entered but not saved.

**Usage:**
```bash
python recalculate_event_revenue.py
```

**What it does:**
- Finds all completed events
- Calculates revenue from ticket_tiers table
- Calculates costs from labour_costs and event_costs
- Updates event_analysis table
- Reports results

### 5.5 Template Creation and Use

**Creating a Template:**
1. Navigate to Templates view
2. Click "Create Template"
3. Fill in template details
4. Add ticket tiers, checklist items, prizes, notes
5. Save template

**Using a Template:**
1. Create event "From Template"
2. All template data is copied to the new event
3. User can modify as needed

**Benefits:**
- Faster event creation
- Consistency across similar events
- Standardized checklists and pricing

### 5.6 Backup and Restore

**Automatic Backup:**
- Runs on first application launch each day
- Creates `backups/events_backup_YYYYMMDD.db`
- Keeps last 7 backups
- Deletes older backups automatically

**Manual Backup:**
- Press Ctrl+B or go to Settings > Backup
- Choose save location
- Creates `events_backup_YYYYMMDD_HHMMSS.db`
- Stored wherever user chooses

**Restore:**
1. Close application
2. Locate backup file
3. Delete/rename current `events.db`
4. Copy backup file and rename to `events.db`
5. Restart application

---

## 6. Key UI Patterns

### 6.1 Navigation Pattern

**Sidebar Navigation:**
- Fixed 200px width sidebar
- Buttons for each major view
- Active view button highlighted
- Content area swaps entire frame

**Implementation:**
```python
class NavigationManager:
    def navigate_to(self, view_name):
        # Hide current view
        self.current_view.pack_forget()
        # Show new view
        self.views[view_name].pack(fill="both", expand=True)
        self.current_view = self.views[view_name]
```

### 6.2 Multi-Tab Detail Views

**Pattern used in:**
- Event Details View
- Template Editor
- Settings View

**Structure:**
```python
self.tabview = ctk.CTkTabview(parent)
self.tab_details = self.tabview.add("Event Details")
self.tab_tickets = self.tabview.add("Tickets")
# etc...
```

### 6.3 Data Entry Forms

**Common pattern for lists (tickets, checklist, prizes):**
- Scrollable frame containing list
- Each item in a bordered frame
- Edit/Delete buttons per item
- "Add" button at bottom
- Immediate save to database on edit/delete

### 6.4 Dialogs

**Standard dialog pattern:**
```python
class MyDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Dialog Title")
        self.geometry("400x300")
        self.transient(parent)  # Modal
        self.grab_set()
        # Center on parent
        # Create UI
```

### 6.5 KPI Cards

**Pattern in Analysis View:**
```python
kpi_card = ctk.CTkFrame(parent, fg_color=color, corner_radius=8)
value_label = ctk.CTkLabel(kpi_card, text=value, font=large_bold)
name_label = ctk.CTkLabel(kpi_card, text=name, font=small_normal)
```

**3-column grid layout with equal width columns**

### 6.6 Charts

**Using Matplotlib with CustomTkinter:**
```python
fig = Figure(figsize=(12, 10))
ax = fig.add_subplot(5, 1, 1)  # 5 rows, 1 column, position 1
ax.plot(dates, values, marker='o', linewidth=2)
ax.set_title('Title')
ax.set_ylabel('Y-axis Label')

canvas = FigureCanvasTkAgg(fig, parent)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)
```

### 6.7 Rich Text Editor

**Custom component for Help View:**
- Toolbar with formatting buttons (Bold, Italic, H1-H3, Lists)
- CTkTextbox with custom tags for formatting
- HTML conversion for storage
- Auto-continue lists on Enter
- Tab/Shift-Tab for indentation

---

## 7. Data Validation Rules

### 7.1 Event Validation

- Event name: Required, non-empty
- Event date: Required, valid date
- Start time: Optional, valid time format
- End time: Optional, must be after start time if both provided
- Max capacity: Optional, positive integer
- Ticket tiers: Each must have valid price (≥0)
- Satisfaction rating: 0-10 scale
- Smoothness rating: 0-10 scale

### 7.2 Financial Validation

- Prices: DECIMAL(10,2), non-negative
- Quantities: INTEGER, non-negative
- Labour hours: DECIMAL(5,2), non-negative
- Hourly rates: DECIMAL(10,2), non-negative

### 7.3 Soft Delete Pattern

Events are never hard-deleted from the database. Instead:
- `is_deleted` flag set to 1
- Event moves to "Deleted Events" view
- Can be restored or permanently deleted
- Related data (CASCADE) preserved until permanent delete

---

## 8. Technical Considerations

### 8.1 Database Connections

- Connection per operation (open, execute, close)
- Row factory set to sqlite3.Row for dict-like access
- Foreign keys enforced with ON DELETE CASCADE
- Timestamps use CURRENT_TIMESTAMP default

### 8.2 Scaling and Zoom

- Global scaling factor managed in main window
- All dialogs inherit scaling from main window
- Zoom controls:
  - Ctrl+Plus: Zoom in
  - Ctrl+Minus: Zoom out
  - Ctrl+0: Reset zoom
  - Ctrl+MouseWheel: Zoom in/out
- Title bar shows current zoom percentage

### 8.3 Text Selection

- Custom text selection handling for labels
- Implemented in utils/text_selection.py
- Global setup in main window initialization

### 8.4 PDF Generation

- Uses ReportLab library
- Multi-page support
- Sections: Event Info, Tickets, Checklist, Prizes, Notes
- Page numbers and headers

### 8.5 Error Handling

- MessageBox dialogs for user-facing errors
- Validation before database operations
- Try/except blocks around database operations
- Graceful degradation (e.g., missing data shows placeholders)

---

## 9. External Dependencies

### 9.1 Required Python Packages

```
customtkinter>=5.0.0
matplotlib>=3.5.0
reportlab>=3.6.0
Pillow>=9.0.0  (for customtkinter images)
```

### 9.2 Installation

```bash
pip install customtkinter matplotlib reportlab Pillow
```

---

## 10. Configuration and Settings

### 10.1 Application Settings

Stored in `settings` table:
- `manager_rate`: Manager hourly rate (default: empty)
- `staff_rate`: Staff hourly rate (default: empty)
- `backup_location`: Custom backup path (default: empty, uses ./backups/)

### 10.2 Default Values

**Event status flags:** All default to 0 (False)
**Labour rates:** Fetched from settings table when adding labour
**Backup retention:** Last 7 automatic backups
**Default window size:** 1200x800
**Minimum window size:** 800x600

---

## 11. Migration Strategy

### 11.1 Database Migrations

Location: `migrations/` directory

**Naming convention:** `action_description.py`

Examples:
- `add_help_system.py`
- `add_satisfaction_breakdown.py`
- `fix_include_attendees.py`

**Migration pattern:**
```python
import sqlite3
from datetime import datetime
import shutil

# Create backup
backup_name = f"events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
shutil.copy2('events.db', backup_name)

# Connect and migrate
conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Add column / create table / modify schema
cursor.execute('''ALTER TABLE ...''')

conn.commit()
conn.close()

print(f"Migration complete. Backup: {backup_name}")
```

### 11.2 Schema Evolution

**Safe operations:**
- Adding new tables
- Adding new columns with defaults
- Creating indexes
- Adding new reference data

**Requires care:**
- Removing columns (SQLite requires table rebuild)
- Changing data types
- Modifying foreign keys
- Data migrations

---

## 12. Future Enhancement Areas

### 12.1 Identified in Feature Requests

The application includes a Feature Requests view where users can track desired enhancements. Common requests:
- Email notifications
- Automated reporting
- Customer database integration
- Online ticket sales integration
- Calendar synchronization

### 12.2 Technical Debt

- Some large view files could be refactored into smaller components
- More comprehensive error logging
- Unit tests for business logic
- Integration tests for database operations

---

## 13. Deployment

### 13.1 Building Executable

Use PyInstaller to create standalone executable:

```bash
python build.py
```

**Build script creates:**
- Single-file executable
- Includes all dependencies
- Icon file included
- Output in `dist/` directory

### 13.2 Distribution Package

**Required files:**
- Executable (.exe on Windows)
- README with instructions
- Empty `events.db` created on first run
- License file

**User data:**
- Database: `events.db` (created in app directory)
- Backups: `backups/` directory (created automatically)

---

## 14. Key Design Decisions

### 14.1 Why SQLite?

- Single-user desktop application
- No server setup required
- Portable database file
- Built into Python
- Sufficient performance for typical use cases

### 14.2 Why CustomTkinter?

- Modern, clean UI
- Cross-platform
- Python-native (no web view)
- Good documentation
- Active development

### 14.3 Why Local First?

- No internet dependency
- Data privacy (local storage)
- Fast performance
- Simple deployment
- Backup/restore controlled by user

### 14.4 Revenue Calculation Design

- Explicit save action required (not automatic)
- Prevents accidental data loss
- Clear user intent
- Warning indicator prevents forgetting
- Bulk recalculation tool available for fixes

### 14.5 Soft Delete Pattern

- Prevents accidental data loss
- Allows recovery
- Audit trail preserved
- Can be permanently deleted if needed

---

## 15. Summary Checklist

To recreate this application, you need:

- [ ] Python 3.11+ environment
- [ ] Install dependencies (customtkinter, matplotlib, reportlab, Pillow)
- [ ] Create main.py with BGEventsApp class
- [ ] Create database.py with schema definitions
- [ ] Create event_manager.py with business logic
- [ ] Create template_manager.py
- [ ] Create pdf_generator.py
- [ ] Create all view files in views/ directory
- [ ] Create utility modules in utils/
- [ ] Implement navigation system
- [ ] Implement backup system
- [ ] Implement zoom/scaling
- [ ] Create help content and rich text editor
- [ ] Implement revenue calculation with warning indicator
- [ ] Create recalculation utility script
- [ ] Test all workflows
- [ ] Build executable with PyInstaller

---

**End of Specification**

*This document describes TT Events Manager as of December 2024.*
*Version: 1.0*
*Last Updated: 2024-12-15*
