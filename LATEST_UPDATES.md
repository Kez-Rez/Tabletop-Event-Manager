# Latest Updates - ALL Core Features Complete!

## 🎉 What's New

### ✅ Ticket Tier Management (NEW!)
Now you can manage multiple ticket tiers with different prices!

**Location:** When editing an event, go to the **Ticket Tiers** tab

**Features:**
- **Add Multiple Tiers** - Early Bird, General Admission, VIP, etc.
- **Set Individual Prices** - Different price for each tier
- **Track Quantities** - Set available quantity and sold quantity for each tier
- **Auto-sorted by Price** - Tiers display in order from lowest to highest price
- **Edit & Delete** - Modify or remove tiers as needed

**How It Works:**
1. Open an existing event
2. Click the "Ticket Tiers" tab
3. Click "+ Add Ticket Tier"
4. Enter tier name, price, and quantity
5. Save!

All ticket tier data is automatically included in:
- Post-Event Analysis (shows tickets sold vs available)
- Financial calculations (revenue from ticket sales)
- Printable PDF event sheets

### ✅ Prize Support Tracking (NEW!)
Track all your prize items in detail!

**Location:** When editing an event, go to the **Prize Support** tab

**Features:**
- **Detailed Prize Records** - Description, quantity, cost per item
- **Auto-calculated Totals** - Total cost calculates automatically
- **Received Status** - Mark prizes as received or pending
- **Cost Tracking** - Track individual and total costs

**Example Uses:**
- "1st Place - Booster Box" (Qty: 1, Cost: $150)
- "Participation Promos" (Qty: 24, Cost each: $2, Total: $48)
- "Store Credit Vouchers" (Qty: 3, Cost each: $25, Total: $75)

Prize costs are automatically included in your event's financial calculations!

### ✅ Event Notes System (NEW!)
Add notes to your events with printout control!

**Location:** When editing an event, go to the **Notes** tab

**Features:**
- **Add Unlimited Notes** - As many notes as you need
- **Printout Selection** - Checkbox to include note in PDF event sheet
- **Visual Indicators** - See at a glance which notes will print
- **Easy Management** - Edit and delete notes anytime

**How It Works:**
1. Open an event and go to the "Notes" tab
2. Click "+ Add Note"
3. Type your note
4. Check "Include in printable event sheet" if you want it on the PDF
5. Save!

**Perfect For:**
- Special announcements
- Rule clarifications
- Prize distribution details
- Parking/location information
- Important reminders

### ✅ Printable PDF Event Sheets (NEW!)
Generate professional event day sheets as PDFs!

**How To Access:**
1. Open any existing event
2. Click "Print Event Sheet" button (next to Save)
3. Choose where to save the PDF
4. Open it automatically or save for later

**What's Included:**
- Event title, date, and time
- Event details (type, format, pairing method, app)
- Maximum capacity
- Ticket tiers with pricing
- Event description
- Event day checklist (organised by category)
- Notes marked for printout
- Space for handwritten notes

**Perfect For:**
- Day-of-event reference
- Staff briefing sheets
- Judge information
- Keeping at the event counter

### ✅ Calendar Widget in Template Dialog (NEW!)
No more typing dates when creating events from templates!

The "Create from Template" dialog now has the same visual calendar picker as the main event form. Click the date field to select from a calendar instead of typing!

### ✅ Post-Event Analysis Tab
Complete your event lifecycle with comprehensive post-event tracking!

**How It Works:**
1. Mark your event as "Event Completed" in the Event Details tab
2. Save the event
3. Reopen the event - you'll now see the **Post-Event Analysis** tab!

**Features:**
- **Actual Attendance Tracking** - Record how many people actually attended
- **Attendance Percentage** - Automatically calculates attendance vs capacity
- **Success Rating (1-10)** - Rate the event's success with an interactive slider
- **Financial Summary** - Automatic calculation of:
  - Total Revenue (from ticket sales)
  - Total Costs (event costs + labour costs)
  - Profit/Loss (color-coded: green for profit, red for loss)
- **Ticket Sales Analysis** - See sold vs available for each ticket tier
- **Notes/Feedback** - Record what went well, what to improve
- **Template Feedback** - If the event was created from a template, add feedback that will appear when creating future events from that template!

All financial data is automatically pulled from your ticket tiers and cost records!

### ✅ Full Settings Page
You can now manage EVERYTHING from the Settings page!

Click **Settings** in the sidebar to access:

---

## Settings Tabs

### 1️⃣ **Event Types**
- View all your event types (MTG, Lorcana, Warhammer, etc.)
- **Add** new event types
- **Edit** existing event types (rename them)
- **Delete** event types you don't need

### 2️⃣ **Playing Formats**
- Manage all playing formats (Standard, Commander, Draft, etc.)
- **Add** new formats (e.g., "Oathbreaker", "Brawl")
- **Edit** format names
- **Delete** unused formats

### 3️⃣ **Pairing Methods**
- Manage pairing methods (Swiss, Single Elimination, etc.)
- **Add** new methods
- **Edit** method names
- **Delete** unused methods

### 4️⃣ **Pairing Apps**
- Manage pairing apps (Cardle.io, EventLink, Melee, etc.)
- **Add** new apps you use
- **Edit** app names
- **Delete** apps you don't use

### 5️⃣ **Award Rates** 💰
Configure Australian award rates for labour cost calculations:
- **Weekday After 6pm Rate** - Default: $25.50/hour
- **Saturday Rate** - Default: $30.00/hour
- **Sunday Rate** - Default: $35.00/hour

These rates are used when calculating labour costs for events!

### 6️⃣ **Backup** 💾
- **Backup Database Now** button
- Choose where to save your backup
- Backup file includes date/time stamp
- Keep your data safe!

---

## How to Use Settings

### Managing Dropdown Options

**To Add:**
1. Go to Settings → Click the relevant tab
2. Click **+ Add [Type]**
3. Enter the name
4. Click **Save**

**To Edit:**
1. Find the item in the list
2. Click **Edit**
3. Change the name
4. Click **Save**

**To Delete:**
1. Find the item in the list
2. Click **Delete**
3. Confirm deletion

**Examples:**
- Add "Pokemon TCG" to Event Types
- Add "Pauper" to Playing Formats
- Add "Triple Elimination" to Pairing Methods
- Add "TopCut" to Pairing Apps

### Updating Award Rates

1. Go to Settings → **Award Rates** tab
2. Enter new hourly rates
3. Click **Save Rates**

The new rates will be used for all future labour cost calculations!

### Backing Up Your Database

1. Go to Settings → **Backup** tab
2. Click **Backup Database Now**
3. Choose where to save it
4. File saved as: `events_backup_YYYYMMDD_HHMMSS.db`

**Pro tip:** Backup before making major changes!

---

## All Recent Features Summary

### ✅ Calendar Date Picker
- Click the date field to see a visual calendar
- No more typing dates manually!

### ✅ Editable Dropdowns
- Type custom values directly into dropdowns
- OR select from existing options
- Custom values save automatically

### ✅ Tickets Available Field
- Track inventory: Maximum Capacity vs Tickets Available
- Helps you know when to order more tickets

### ✅ Empty Dropdowns by Default
- All dropdowns start blank
- Choose only what you need
- Cleaner interface

### ✅ Number Validation
- Capacity and Tickets fields only accept whole numbers
- Clear error messages if you enter invalid data
- No more "16e" errors!

### ✅ Incomplete Checklist Items on Event Cards
- See what needs to be done at a glance
- Shows up to 3 incomplete items
- "+X more..." if there are additional items

### ✅ Settings Page (NEW!)
- Manage all dropdown values
- Configure award rates
- Backup your database
- Everything in one place!

---

## Quick Reference

### Your Dropdown Values Live In:
- **Settings → Event Types** - Magic, Lorcana, Warhammer, etc.
- **Settings → Playing Formats** - Commander, Standard, Draft, etc.
- **Settings → Pairing Methods** - Swiss, Elimination, etc.
- **Settings → Pairing Apps** - Cardle.io, Melee, etc.

### Your Data Lives In:
- **events.db** - Main database file
- Back it up from **Settings → Backup**

### Your Configuration:
- **Settings → Award Rates** - Labour cost hourly rates

---

## Tips

**Keeping Things Organised:**
- Use consistent naming (e.g., "Magic: The Gathering" not "MTG" and "Magic")
- Delete options you don't use anymore
- Update award rates when they change
- Backup regularly!

**Custom Values:**
- You can type new values directly in event/template forms
- OR add them in Settings first
- Either way works - choose what's easier!

**Backups:**
- Backup before big changes
- Keep backups in a safe location (cloud storage, external drive)
- Name them clearly so you know what's what

---

## What's Still Coming

- Dashboard with Statistics view (showing overview of all events)

---

**Everything works together beautifully now!** 🎨💜

Your BG Events Manager is getting really powerful! 🚀
