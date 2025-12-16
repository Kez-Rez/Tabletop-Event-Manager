# BG Events - Remaining Implementation Plan

## Overview
This document outlines the remaining features to be implemented for the post-event close workflow and pre-event analysis.

## Completed Features ✓
1. **Labour Costs System** - Full CRUD with multiple entries, rate types, work status
2. **Award Rates Settings** - All 5 rate types (weekday before/after 6pm, Saturday, Sunday, public holiday)
3. **Database Enhancements** - Added columns for:
   - `quantity_handed_out` to prize_items
   - `send_to_template` to event_notes

## Features to Implement

### 1. Notes Tab (Priority: HIGH)
**File**: `views/event_details_view.py` (lines 661-674)

Replace the placeholder methods with:

```python
def load_notes(self):
    """Load all notes for this event"""
    # Query event_notes table
    # Display each note with badges for:
    #   - Include in printout
    #   - Send to template
    # Show Edit/Delete buttons for each note

def create_note_card(self, note: dict):
    """Create visual card for a note"""
    # Display note text
    # Show badges
    # Add Edit/Delete buttons

def add_note(self):
    """Open NoteDialog"""
    from views.event_dialogs import NoteDialog
    dialog = NoteDialog(self, self.db, self.event_id, self.event_data.get('template_id'))
    self.wait_window(dialog)
    self.load_notes()
```

**Update NoteDialog** in `views/event_dialogs.py` (line 369):
- Add checkbox: "Send feedback to template" (`send_to_template`)
- When saving, if checked and event has a template_id:
  - Insert into `template_feedback` table
  - Link note to template for future events

### 2. Prizes Tab (Priority: HIGH)
**File**: `views/event_details_view.py` (lines 646-659)

Replace placeholder methods with:

```python
def load_prizes(self):
    """Load all prizes for this event"""
    # Query prize_items table
    # Display quantity, cost, received status, quantity_handed_out
    # Show Edit/Delete buttons

def create_prize_card(self, prize: dict):
    """Create visual card for a prize"""
    # Show description, quantity, cost
    # Display "Received" badge if is_received
    # Show handed out count vs total quantity
```

**Update PrizeDialog** in `views/event_dialogs.py` (line 159):
- Keep existing `recipients` field (for PDF print sheet)
- Add new field: "Quantity Handed Out" (editable number)
  - Default to 0
  - Can be edited during/after event
  - Shows in post-event analysis

### 3. Post-Event Analysis Enhancements (Priority: HIGH)

**File**: `views/event_details_view.py` - `load_post_event_analysis()` method

#### A. Ticket Sales Tracking
Currently shows "Actual Attendance". Replace with:

```python
# Ticket Sales Section
ctk.CTkLabel(parent, text="Ticket Sales", ...).pack()

# For each ticket tier, show:
for tier in ticket_tiers:
    # Display: Tier Name | Available | Sold
    # Editable "Quantity Sold" field
    # Auto-calculate revenue

# Total Revenue display (read-only)
```

#### B. Success Rating
Already partially implemented - just needs to be visible:
```python
# Success Rating (1-10)
ctk.CTkLabel(parent, text="Event Success Rating (1-10)", ...).pack()
self.entry_rating = ctk.CTkEntry(parent)
# Validation: 1-10 only
```

#### C. Prize Distribution Summary
Add section showing:
```python
# Prize Distribution
for prize in prizes:
    # Show: Prize | Quantity | Handed Out | Remaining
    # Highlight if remaining > 0 (extras)
```

### 4. Tickets Tab Update (Priority: MEDIUM)

**File**: `views/event_details_view.py` - `create_tickets_tab()` method

Currently manages ticket tiers. Enhance to show:
- Pre-event: Set up tiers (current functionality)
- Post-event: Update `quantity_sold` for each tier
  - This data feeds into post-event analysis revenue calculation

### 5. Pre-Event Analysis Tab (Priority: MEDIUM)

**New Tab** - Add to `event_details_view.py`:

```python
def create_pre_event_tab(self):
    """Create pre-event cost projection tab"""
    tab = self.tabview.tab("Pre-Event Analysis")

    # Projected Costs Section
    # - Labour costs (from labour_costs entries or estimate)
    # - Prize support (from prize_items table)
    # - Other costs (from event_costs table)
    # Total Projected Costs: $XXX

    # Ticket Revenue Projection
    # For each tier:
    #   - Price * Quantity Available = Max Revenue
    # Total Max Revenue: $XXX

    # Break-Even Analysis
    # Break-even attendance = Total Costs / Average Ticket Price
    # "You need X attendees to break even"

    # Suggested Ticket Price (ADVANCED)
    # Calculate: (Total Costs * 1.2) / Expected Attendance
    # "Suggested price: $XX for 20% profit margin"
```

### 6. "Close Event" Workflow (Priority: LOW)

**New Feature** - Add button in Overview tab:

```python
def close_event_workflow(self):
    """Guided workflow for closing an event"""
    # Step 1: Mark event as completed
    # Step 2: Navigate to Tickets tab - update sales
    # Step 3: Navigate to Prizes tab - update handed out
    # Step 4: Navigate to Notes tab - add feedback
    # Step 5: Navigate to Post-Event tab - complete analysis
    # Show progress indicator (Step X of 5)
```

## Implementation Order

### Phase 1 (Tonight - 2-3 hours)
1. ✓ Database updates (completed)
2. Notes Tab - Full CRUD
3. Prizes Tab - Full CRUD with handed out tracking
4. Post-Event: Ticket sales + Success rating

### Phase 2 (Next Session - 1-2 hours)
5. Pre-Event Analysis tab
6. Ticket price suggestion algorithm
7. Close Event guided workflow

## Database Schema Reference

### Tables to Use:
- `event_notes` - Has: id, event_id, note_text, include_in_printout, send_to_template, created_at
- `prize_items` - Has: id, event_id, description, quantity, cost_per_item, total_cost, recipients, is_received, quantity_handed_out, created_at
- `ticket_tiers` - Has: id, event_id, tier_name, price, quantity_available, quantity_sold, created_at
- `event_analysis` - Has: id, event_id, actual_attendance, success_rating, profit_margin, revenue_total, cost_total, notes, created_at
- `template_feedback` - Has: id, template_id, event_id, feedback_text, created_at

## Testing Checklist

After implementation:
- [ ] Create event with template
- [ ] Add notes with "send to template" checked
- [ ] Verify template_feedback table populated
- [ ] Create new event from same template
- [ ] Verify feedback notes appear
- [ ] Add prizes, mark as received
- [ ] Update handed out quantities
- [ ] Complete post-event analysis with ticket sales
- [ ] Verify all calculations correct
- [ ] Test pre-event projections
- [ ] Verify break-even calculations

## Files Modified

- `database.py` - Settings for all award rates
- `views/settings_view.py` - UI for all award rates
- `views/event_dialogs.py` - NoteDialog, PrizeDialog updates
- `views/event_details_view.py` - Notes, Prizes, Post-Event, Pre-Event tabs
- `event_manager.py` - Labour cost methods
- New migration files:
  - `add_prize_handedout_column.py`
  - `add_template_feedback_to_notes.py`

## Quick Reference Commands

```bash
# Run migrations
python add_prize_handedout_column.py
python add_template_feedback_to_notes.py

# Test labour costs
python test_labour_costs.py

# Run app
python main.py
```

## Notes
- Success rating field already exists in event_analysis table
- Template feedback system already has table structure
- Most database schema is already in place
- Main work is UI implementation and business logic
