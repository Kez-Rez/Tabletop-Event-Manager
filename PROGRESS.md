# BG Events Manager - Development Progress

## ✅ Completed Features

### Core Infrastructure
- ✅ SQLite database with comprehensive schema
- ✅ Database initialisation with default data
- ✅ Settings management system
- ✅ Pastel purple/pink/blue colour scheme throughout

### Events Management
- ✅ Create, edit, view, and delete events
- ✅ Event list view with filtering (show/hide completed)
- ✅ Full event details including:
  - Event name, date, times
  - Event type, format, pairing method, app
  - Maximum capacity
  - Description
  - Status toggles (organised, tickets live, advertised, completed)
- ✅ Event cards with status badges
- ✅ Event creation from templates with feedback notes

### Templates System
- ✅ Create, edit, view, and delete templates
- ✅ Template details (name, type, format, pairing, capacity, description)
- ✅ Dynamic checklist items per template
- ✅ Checklist categories (Before Event, Day Of, After Event)
- ✅ Create events from templates
- ✅ Template feedback system (notes that carry forward)
- ✅ Count of events using each template

### Financial Tracking
- ✅ Automatic labour cost calculation based on:
  - Event start/end time
  - Day of week
  - Configurable award rates (weekday, Saturday, Sunday)
  - Number of staff
- ✅ Database structure for:
  - Labour costs
  - Other event costs
  - Prize support items
  - Cost categories

### Checklists
- ✅ Template-based checklist items
- ✅ Event-specific checklist management
- ✅ Checklist categories
- ✅ Mark items as complete
- ✅ Add/delete checklist items

### User Interface
- ✅ Main navigation sidebar
- ✅ Dashboard page (placeholder)
- ✅ Events page with card-based list
- ✅ Templates page with card-based list
- ✅ Event edit dialog with validation
- ✅ Template edit dialog with tabbed interface
- ✅ Event details view with tabs (partially complete)
- ✅ Consistent colour scheme (pale blues, pinks, purples)
- ✅ Australian English spelling throughout

### Reference Data
- ✅ Event types (MTG, Lorcana, Riftbound, Warhammer, etc.)
- ✅ Playing formats (Standard, Commander, Draft, etc.)
- ✅ Pairing methods (Swiss, Single Elimination, etc.)
- ✅ Pairing apps (Cardle.io, EventLink, Melee, Challonge)
- ✅ Cost categories
- ✅ Checklist categories

## 🚧 In Progress / To Do

### Financial Features (Partially Complete)
- ⏳ UI for adding/editing other costs
- ⏳ Prize support item management UI
- ⏳ Financial summary/totals display
- ⏳ Cost breakdown by category

### Ticketing
- ⏳ Multiple ticket tiers per event
- ⏳ Track tickets sold vs available per tier
- ⏳ Update ticket sales after event
- ⏳ Revenue calculations

### Post-Event Analysis
- ⏳ Actual attendance tracking
- ⏳ Success rating (1-10 scale)
- ⏳ Profit margin calculation
- ⏳ Comparison to projections
- ⏳ Analysis dashboard/charts
- ⏳ Success tracking over time

### Notes System
- ⏳ Add/edit/delete event notes
- ⏳ Mark notes for inclusion in printout
- ⏳ Template feedback notes

### Printable Event Sheets
- ⏳ PDF generation for event day
- ⏳ Include event details, format, pairing info
- ⏳ Include checklist
- ⏳ Include selected notes
- ⏳ Space for additional handwritten notes

### Settings Page
- ⏳ Award rate configuration
- ⏳ Backup location selection
- ⏳ Add/manage event types
- ⏳ Add/manage formats
- ⏳ Add/manage pairing methods
- ⏳ Add/manage pairing apps

### Database Backup
- ⏳ Manual backup functionality
- ⏳ Backup location configuration
- ⏳ Backup file naming with date/time
- ⏳ Restore from backup

### Dashboard
- ⏳ Upcoming events timeline
- ⏳ Recent events
- ⏳ Quick stats (total events, upcoming, etc.)
- ⏳ Financial summary
- ⏳ Alerts/reminders

### Packaging
- ⏳ PyInstaller configuration
- ⏳ Standalone .exe creation
- ⏳ Icon for application
- ⏳ Installation instructions

## Database Schema

All tables created and ready:
- ✅ events
- ✅ event_types
- ✅ playing_formats
- ✅ pairing_methods
- ✅ pairing_apps
- ✅ event_templates
- ✅ template_checklist_items
- ✅ event_checklist_items
- ✅ checklist_categories
- ✅ ticket_tiers
- ✅ cost_categories
- ✅ event_costs
- ✅ labour_costs
- ✅ prize_items
- ✅ event_notes
- ✅ template_feedback
- ✅ event_analysis
- ✅ settings

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## File Structure

```
BG Events/
├── database.py              # Database management
├── event_manager.py         # Event CRUD operations
├── template_manager.py      # Template CRUD operations
├── main.py                  # Main application entry
├── requirements.txt         # Python dependencies
├── views/
│   ├── events_view.py       # Events list and management
│   ├── templates_view.py    # Templates list and management
│   └── event_details_view.py # Detailed event view (partial)
├── events.db                # SQLite database (created on first run)
├── README.md                # Project documentation
└── PROGRESS.md              # This file
```

## Next Steps

1. Complete financial tracking UI (costs, prizes)
2. Implement ticket management UI
3. Build post-event analysis functionality
4. Create printable event sheets (PDF)
5. Build settings page
6. Implement backup/restore functionality
7. Create dashboard with statistics
8. Package as standalone executable

## Australian English

All user-facing text uses Australian English spelling:
- Organised (not organized)
- Colour (not color)
- Favour (not favor)
- Centre (not center)
- Etc.
