# BG Events Manager - User Guide

## Getting Started

### First Launch
1. Double-click `main.py` or run `python main.py` from the terminal
2. The application will automatically create the database (`events.db`) on first run
3. You'll see the Dashboard with a welcome message

### Navigation
Use the sidebar buttons to navigate between sections:
- **Dashboard** - Overview and quick stats (coming soon)
- **Events** - Manage all your events
- **Templates** - Create and manage event templates
- **Analysis** - View success metrics (coming soon)
- **Settings** - Configure app settings (coming soon)
- **Backup Database** - Manually backup your data

## Working with Templates

Templates are reusable event configurations. Create them once, use them many times!

### Creating a Template

1. Click **Templates** in the sidebar
2. Click **+ New Template**
3. Fill in the template details:
   - **Template Name** (required) - e.g., "Weekly Commander Night"
   - **Event Type** - Magic: The Gathering, Lorcana, Warhammer, etc.
   - **Playing Format** - Commander, Standard, Draft, etc.
   - **Pairing Method** - Swiss, Single Elimination, etc.
   - **Pairing App** - Cardle.io, EventLink, Melee, Challonge, etc.
   - **Maximum Capacity** - How many players can attend
   - **Description** - Additional event details
4. Click **Save Template**

### Adding Checklist Items to a Template

After creating a template:
1. Click the **Checklist Items** tab
2. Click **+ Add Item**
3. Select a category (Before Event, Day Of, After Event)
4. Enter the item description
5. Click **Add Item**

Examples of checklist items:
- **Before Event**: Order prize packs, advertise on social media, prepare venue
- **Day Of**: Set up tables, test pairings app, prepare sign-in sheet
- **After Event**: Clean venue, update records, collect feedback

### Creating an Event from a Template

1. Go to **Templates**
2. Find your template
3. Click **Create Event**
4. Enter the event date (YYYY-MM-DD format)
5. Optionally change the event name
6. Click **Create Event**

The new event will include:
- All template settings
- All checklist items
- Any feedback notes from previous events using this template

## Working with Events

### Creating a New Event (Without Template)

1. Click **Events** in the sidebar
2. Click **+ New Event**
3. Fill in all event details:
   - **Event Name** (required)
   - **Event Date** (required, YYYY-MM-DD format)
   - **Start Time** (HH:MM format, e.g., 18:00)
   - **End Time** (HH:MM format, e.g., 22:00)
   - Event type, format, pairing method, app
   - Maximum capacity
   - Description
4. Set status checkboxes:
   - ☑ Fully Organised - Event is ready to go
   - ☑ Tickets Live - Tickets are on sale
   - ☑ Advertised - Event has been promoted
5. Click **Save Event**

### Viewing/Editing an Event

1. Go to **Events**
2. Click **View/Edit** on any event card
3. Use the tabs to access different sections:
   - **Overview** - Basic event info and status
   - **Checklist** - Track what needs to be done
   - **Financial** - Costs and labour tracking
   - **Tickets** - Manage ticket tiers (coming soon)
   - **Prizes** - Track prize support (coming soon)
   - **Notes** - Add event notes (coming soon)
   - **Post-Event** - Analysis after completion (coming soon)

### Event Checklist

The checklist helps you track all the tasks needed to run your event:

1. Open an event
2. Go to the **Checklist** tab
3. Check off items as you complete them
4. Add new items with **+ Add Item** if needed
5. Delete items that aren't relevant

Checklist items are organised by category:
- **Before Event** - Things to do in advance
- **Day Of** - Tasks on event day
- **After Event** - Post-event cleanup and follow-up

### Labour Cost Calculation

The app automatically calculates labour costs based on Australian award rates:

1. Open an event
2. Go to the **Financial** tab
3. Enter the number of staff working
4. Click **Calculate Labour Cost**

The app uses:
- Event start and end times
- Day of week
- Award rates from Settings:
  - Weekday after 6pm rate
  - Saturday rate
  - Sunday rate

**Example:**
- Event: Friday 18:00 - 22:00 (4 hours)
- Staff: 2 people
- Rate: $25.50/hour (weekday after 6pm)
- Total: 4 hours × $25.50 × 2 staff = **$204.00**

### Event Status Tracking

Track your event's progress with status badges:

- **Organised** (Green) - All planning complete, ready to run
- **Tickets Live** (Blue) - Tickets are on sale
- **Advertised** (Orange) - Event has been promoted
- **Completed** (Purple) - Event has finished

Toggle these in the event Overview tab as you progress.

### Filtering Events

On the Events page:
- ☑ **Show Completed Events** - Toggle to show/hide finished events
- This helps you focus on upcoming events

## Tips and Best Practices

### Template Strategy

Create templates for:
- **Recurring events** (Weekly Commander, Friday Night Magic)
- **Event series** (Prerelease events, quarterly tournaments)
- **Different event types** (Casual nights, competitive tournaments)

### Checklist Tips

Standard checklist items to consider:
- Order prizes 2 weeks before
- Create Facebook event 1 week before
- Test pairings app day before
- Set up tables 30 mins before
- Collect player feedback after

### Labour Cost Planning

1. Set event times early to calculate labour
2. Adjust staff count based on expected attendance
3. Factor labour into ticket pricing
4. Review Settings if award rates change

### Organisation Workflow

Recommended process:
1. Create event (from template or new)
2. Work through checklist items
3. Mark "Organised" when everything is ready
4. Mark "Tickets Live" when you start selling
5. Mark "Advertised" after promotion
6. Mark "Completed" after the event finishes
7. Complete post-event analysis

## Database and Backups

### Database File

Your data is stored in `events.db` in the application folder.

**Important:** This file contains all your events, templates, and settings. Keep it safe!

### Manual Backup

1. Click **Backup Database** in the sidebar
2. Choose a backup location
3. A copy of `events.db` will be saved with the date

Recommended: Backup before major changes or regularly (weekly/monthly).

### Restoring from Backup

If you need to restore:
1. Close the application
2. Replace `events.db` with your backup file
3. Restart the application

### Automatic Backups

For extra safety, use a cloud sync service:
- Copy BG Events folder to Dropbox/Google Drive/OneDrive
- Run the app from the synced folder
- Your data will be backed up automatically

## Colour Scheme

The app uses a pleasant pastel colour scheme:
- **Purple** (#8B5FBF) - Primary buttons and headings
- **Pink** (#D4A5D4) - Secondary elements
- **Pale Purple** (#E6D9F2) - Sidebar
- **Light Background** (#F5F0F6) - Main area
- **White** - Content cards

This creates a calm, organised working environment.

## Australian English

All text in the app uses Australian English spelling:
- Organised, not organized
- Colour, not color
- Analyse, not analyze
- Centre, not center

## Keyboard Shortcuts

(Coming soon)

## Troubleshooting

### App won't start
- Ensure Python 3.8+ is installed
- Run `pip install -r requirements.txt`
- Check for error messages in terminal

### Can't see my events
- Check "Show Completed Events" filter
- Verify events exist in database
- Try restarting the app

### Labour cost not calculating
- Ensure event has start and end times
- Times must be in HH:MM format
- Check Settings for award rates

### Lost my data
- Check for `events.db` file in app folder
- Look for backup files
- Database might be in a different location

## Getting Help

Found a bug or have a suggestion?
- Check the GitHub issues page
- Create a new issue with details
- Include screenshots if helpful

## What's Coming Next

Upcoming features:
- Ticket tier management
- Prize support tracking
- Post-event analysis and success metrics
- Printable event day sheets
- Settings page
- Dashboard with statistics
- Automatic backup reminders
- Export to Excel/CSV

---

**Enjoy running your events!** 🎲🃏♟️
