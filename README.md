# TT Events Manager

A comprehensive desktop application for managing tabletop gaming events, designed specifically for game stores and event organizers.

## Features

### Event Management
- Create and manage events with full details (date, time, capacity, pricing)
- Template system for recurring events
- Event cancellation tracking with reasons
- Dashboard with priority alerts for upcoming deadlines

### Financial Tracking
- Automatic labour cost calculation based on time and day
- Prize support tracking with received status
- Cost breakdown by category
- Revenue and profit margin analysis
- Ticket tier management with pricing

### Checklists & Organization
- Dynamic checklists per event with categories
- Mark important items to show on dashboard
- Template checklists that copy to new events
- Prize tracking with handed-out status

### Analytics & Insights
- Comprehensive post-event analysis
- Attendance, revenue, and satisfaction trends over time
- Performance metrics by event type
- Capacity utilization tracking
- Visual graphs and KPIs
- Exportable reports

### Attendee Satisfaction
- Three-tier satisfaction breakdown (Loved it / Liked it / Didn't enjoy)
- Automatic weighted score calculation
- Satisfaction trends over time

### Event Type Guides
- Create custom guides for running each event type
- Rich text editing with formatting (headings, bold, italic)
- Checkbox lists for step-by-step procedures
- Auto-continuing bullets and indentation
- Version tracking with initials and change notes
- Print functionality for physical reference

### Help & Documentation
- Editable help system
- Built-in FAQ
- Version-controlled documentation

### Feature Requests
- Built-in feature request system
- Track ideas for future improvements
- Priority and status management

## Installation

### Requirements
- Python 3.8 or higher
- Windows 10 or higher (developed for Windows, may work on other platforms)

### Setup
1. Download or clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

```
python main.py
```

The database (`events.db`) is created automatically on first run.

## Keyboard Shortcuts

- **Ctrl+N** - Quick create new event
- **Ctrl+S** - Save current form
- **Ctrl+P** - Print current view
- **Ctrl+B** - Backup database
- **F1** - Open help

## Database Backups

The application automatically creates a backup on the first launch each day. Manual backups can also be created from the Settings menu.

**Backup locations:**
- Automatic: `backups/events_backup_YYYYMMDD.db`
- Manual: User-selected location

**Important:** Keep regular backups! The database contains all your event data.

## Building Standalone Executable

To create a standalone .exe file that doesn't require Python:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Run the build script:
   ```
   python build.py
   ```

3. The executable will be in the `dist` folder

Alternatively, build manually:
```
pyinstaller --onefile --windowed --name "TT Events Manager" --icon=icon.ico main.py
```

## Project Structure

```
BG Events/
├── main.py                 # Application entry point
├── database.py             # Database schema and operations
├── config.json             # User configuration
├── requirements.txt        # Python dependencies
├── views/                  # UI components
│   ├── events_view.py
│   ├── templates_view.py
│   ├── analysis_view.py
│   ├── help_view.py
│   └── ...
├── migrations/             # Database migration scripts (dev only)
└── backups/                # Automatic database backups
```

## Configuration

Edit `config.json` to customize:
- Database location
- Backup directory
- Default labour rates
- Theme preferences

## Data Export

Export your data:
- **Events to CSV**: Analysis → Export button
- **Event Sheets to PDF**: Event Details → Print Event Sheet
- **Analytics Data**: Analysis → Export Charts

## Troubleshooting

### Database Issues
- If the database becomes corrupted, restore from a backup in Settings
- Backups are stored in the `backups/` folder
- Keep at least the last 7 backups

### Application Won't Start
1. Ensure Python 3.8+ is installed
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check that `events.db` isn't locked by another process

### Data Not Saving
- Ensure you click the Save button
- Check all required fields are filled in
- Verify the database file isn't read-only

## Design Philosophy

- **Australian English** throughout the interface
- **Pastel colour scheme** (purples, pinks, blues) for a pleasant, organized interface
- **Intuitive workflow** mirroring real-world event planning processes
- **Comprehensive tracking** without overwhelming complexity

## Support

For bugs or feature requests, use the built-in Feature Requests menu in the application.

## Version

Current Version: 1.0.0

## Credits

Designed and developed by Kerry Restante

## License

Proprietary - All rights reserved
