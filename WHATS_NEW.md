# What's New - Recent Updates

## ✨ Latest Features Added

### 1. Editable Dropdown Menus
**You can now type your own custom values!**

All dropdown menus (Event Type, Playing Format, Pairing Method, Pairing App) are now fully editable:
- Click the dropdown and type any custom value
- Your custom value is automatically saved to the database
- It will appear in the dropdown list for future events
- Works in both Events and Templates

**Example:**
- Need a new event type like "One Piece TCG"? Just type it in!
- Want to add "Sealed Draft" as a format? Type it directly!
- No need to go to settings first (though you still can)

### 2. Tickets Available Field
**Track how many tickets you have for each event!**

New field added to events:
- **Maximum Capacity** - Total spots available
- **Tickets Available** - How many tickets you currently have to sell

This helps you track:
- When you need to order more tickets
- How close you are to capacity
- Ticket inventory management

**Found in:** Event creation/edit form, right next to Maximum Capacity

### 3. Incomplete Checklist Items on Event Cards
**See what needs to be done at a glance!**

Event cards now show incomplete checklist items directly on the main Events page:
- Shows up to 3 incomplete items in grey (☐ checkbox)
- If more than 3, shows "+X more..."
- Only shows items that haven't been checked off yet
- Helps you see what's left to do without opening the event

**Example event card now shows:**
```
MTG Commander Night
Friday, 24 November 2024 • Commander • Swiss

[Organised] [Tickets Live] [Advertised]

To Do:
☐ Order prize packs
☐ Set up tables
☐ Prepare sign-in sheet
   +2 more...
```

## 🔧 Technical Improvements

### Database Updates
- Added `tickets_available` column to events table
- Automatic migration on next app launch
- Custom dropdown values saved permanently

### Smart Dropdown Behavior
- When you type a new value, it's automatically added to the database
- The value becomes available in all future events/templates
- No duplicates - checks existing values first
- Case-sensitive matching

## 📝 How to Use New Features

### Adding Custom Dropdown Values

**Method 1: Type directly (NEW!)**
1. Create or edit an event/template
2. Click any dropdown (Event Type, Format, etc.)
3. Type your custom value
4. Save the event
5. Your value is now permanently available!

**Method 2: Settings page (Coming soon)**
- Will allow you to view and manage all dropdown values
- Delete unused values
- Rename existing values

### Using Tickets Available

1. Create or edit an event
2. Set **Maximum Capacity** (e.g., 24 players)
3. Set **Tickets Available** (e.g., 20 tickets on hand)
4. Save the event
5. Update as you sell/order tickets

### Viewing Incomplete Checklist Items

1. Create an event from a template (or add checklist items manually)
2. Go to the event's Checklist tab
3. Check off items as you complete them
4. Return to the Events list page
5. See remaining items displayed on the event card

## 🐛 Bug Fixes

- Fixed database schema to support new fields
- Improved dropdown population logic
- Better handling of empty/null values

## 🔜 Coming Next

- **Settings page** to manage all dropdown values
- View all event types, formats, methods, apps
- Delete or rename existing values
- Backup/restore database from settings

## 💡 Tips

**Custom Values:**
- Keep names consistent (e.g., "Magic: The Gathering" not "MTG" and "Magic")
- Use proper capitalisation
- Values are permanent unless deleted from settings (coming soon)

**Tickets:**
- Set both capacity and tickets available
- Update tickets available when you order more
- Helps track inventory and sales

**Checklist Items:**
- Add items to templates for recurring events
- Items automatically copy to new events
- Check them off as you go
- Incomplete items remind you what's left

---

**Enjoy the new features!** 🎉

If you find any bugs or have suggestions, let me know!
