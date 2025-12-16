"""Dialog classes for event management"""
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from typing import Optional


class TicketTierDialog(ctk.CTkToplevel):
    """Dialog for adding/editing ticket tiers"""

    def __init__(self, parent, db, event_id: int, ticket_data: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.event_id = event_id
        self.ticket_data = ticket_data

        self.title("Edit Ticket Tier" if ticket_data else "Add Ticket Tier")
        self.geometry("450x400")
        self.minsize(400, 300)  # Set minimum size for resizing
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

        if ticket_data:
            self.populate_fields()

    def create_form(self):
        """Create the form"""
        # Use scrollable frame
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tier Name
        ctk.CTkLabel(frame, text="Tier Name *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_name = ctk.CTkEntry(frame, placeholder_text="e.g., Early Bird, General Admission")
        self.entry_name.pack(fill="x", pady=(0, 15))

        # Price
        ctk.CTkLabel(frame, text="Price (AUD) *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_price = ctk.CTkEntry(frame, placeholder_text="e.g., 25.00")
        self.entry_price.pack(fill="x", pady=(0, 15))

        # Quantity Available
        ctk.CTkLabel(frame, text="Quantity Available *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_quantity = ctk.CTkEntry(frame, placeholder_text="e.g., 24")
        self.entry_quantity.pack(fill="x", pady=(0, 15))

        # Quantity Sold (only show if editing)
        if self.ticket_data:
            ctk.CTkLabel(frame, text="Quantity Sold", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
            self.entry_sold = ctk.CTkEntry(frame, placeholder_text="e.g., 12")
            self.entry_sold.pack(fill="x", pady=(0, 15))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def populate_fields(self):
        """Populate fields with existing data"""
        if not self.ticket_data:
            return

        self.entry_name.insert(0, self.ticket_data['tier_name'])
        self.entry_price.insert(0, str(self.ticket_data['price']))
        self.entry_quantity.insert(0, str(self.ticket_data['quantity_available']))

        if hasattr(self, 'entry_sold'):
            self.entry_sold.insert(0, str(self.ticket_data['quantity_sold']))

    def save(self):
        """Save the ticket tier"""
        # Validate
        if not self.entry_name.get():
            messagebox.showerror("Validation Error", "Tier name is required")
            return

        try:
            price = float(self.entry_price.get())
            if price < 0:
                messagebox.showerror("Validation Error", "Price must be positive")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Price must be a valid number")
            return

        try:
            quantity = int(self.entry_quantity.get())
            if quantity < 0:
                messagebox.showerror("Validation Error", "Quantity must be positive")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a whole number")
            return

        sold = 0
        if self.ticket_data and hasattr(self, 'entry_sold'):
            try:
                sold = int(self.entry_sold.get())
                if sold < 0:
                    messagebox.showerror("Validation Error", "Sold quantity must be positive")
                    return
                if sold > quantity:
                    messagebox.showerror("Validation Error", "Sold quantity cannot exceed available quantity")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Sold quantity must be a whole number")
                return

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        if self.ticket_data:
            # Update existing
            cursor.execute('''
                UPDATE ticket_tiers
                SET tier_name = ?, price = ?, quantity_available = ?, quantity_sold = ?
                WHERE id = ?
            ''', (self.entry_name.get(), price, quantity, sold, self.ticket_data['id']))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO ticket_tiers (event_id, tier_name, price, quantity_available, quantity_sold)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.event_id, self.entry_name.get(), price, quantity, 0))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Ticket tier saved successfully!")
        self.destroy()


class PrizeDialog(ctk.CTkToplevel):
    """Dialog for adding/editing materials and prizes"""

    def __init__(self, parent, db, event_id: int, prize_data: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.event_id = event_id
        self.prize_data = prize_data

        self.title("Edit Item" if prize_data else "Add Material/Prize")
        self.geometry("450x650")
        self.minsize(400, 500)  # Set minimum size for resizing
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

        if prize_data:
            self.populate_fields()

    def create_form(self):
        """Create the form"""
        # Use scrollable frame
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Item Type Selection
        ctk.CTkLabel(frame, text="Item Type *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(0, 5))

        type_frame = ctk.CTkFrame(frame, fg_color="white")
        type_frame.pack(fill="x", pady=(0, 15), padx=5, ipady=10)

        self.var_item_type = ctk.StringVar(value="prize")

        ctk.CTkRadioButton(
            type_frame,
            text="Prize Support",
            variable=self.var_item_type,
            value="prize",
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0"
        ).pack(side="left", padx=20)

        ctk.CTkRadioButton(
            type_frame,
            text="Event Material",
            variable=self.var_item_type,
            value="material",
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0"
        ).pack(side="left", padx=20)

        # Description
        ctk.CTkLabel(frame, text="Description *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(0, 5))
        self.entry_description = ctk.CTkEntry(frame, placeholder_text="e.g., 1st Place - Booster Box or Dice Set", font=ctk.CTkFont(size=15))
        self.entry_description.pack(fill="x", pady=(0, 15))

        # Quantity Needed Per Player
        ctk.CTkLabel(frame, text="Quantity Needed Per Player", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="How many items each player receives", text_color="#666666", font=ctk.CTkFont(size=15)).pack(anchor="w", pady=(0, 5))
        self.entry_quantity_per_player = ctk.CTkEntry(frame, placeholder_text="e.g., 1", font=ctk.CTkFont(size=15))
        self.entry_quantity_per_player.pack(fill="x", pady=(0, 15))

        # Recipients
        ctk.CTkLabel(frame, text="Number of Recipients *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="How many players receive this item?", text_color="#666666", font=ctk.CTkFont(size=15)).pack(anchor="w", pady=(0, 5))
        self.entry_recipients = ctk.CTkEntry(frame, placeholder_text="e.g., 1 for single prize, 24 for participation promos", font=ctk.CTkFont(size=15))
        self.entry_recipients.pack(fill="x", pady=(0, 15))

        # Total Quantity Needed (auto-calculated)
        ctk.CTkLabel(frame, text="Total Quantity Needed", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Auto-calculated: Quantity Per Player × Recipients", text_color="#666666", font=ctk.CTkFont(size=15)).pack(anchor="w", pady=(0, 5))
        self.entry_quantity = ctk.CTkEntry(frame, placeholder_text="Auto-calculated", font=ctk.CTkFont(size=15))
        self.entry_quantity.pack(fill="x", pady=(0, 15))

        # Cost Per Item
        ctk.CTkLabel(frame, text="Cost Per Item (AUD)", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Cost of one individual material or prize", text_color="#666666", font=ctk.CTkFont(size=15)).pack(anchor="w", pady=(0, 5))
        self.entry_cost_per = ctk.CTkEntry(frame, placeholder_text="e.g., 5.50", font=ctk.CTkFont(size=15))
        self.entry_cost_per.pack(fill="x", pady=(0, 15))

        # Total cost (calculated automatically)
        ctk.CTkLabel(frame, text="Total Cost (AUD)", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Auto-calculated: Total Quantity × Cost Per Item", text_color="#666666", font=ctk.CTkFont(size=15)).pack(anchor="w", pady=(0, 5))
        self.entry_total = ctk.CTkEntry(frame, placeholder_text="Auto-calculated", font=ctk.CTkFont(size=15))
        self.entry_total.pack(fill="x", pady=(0, 15))

        # Auto-calculate on field changes
        self.entry_quantity_per_player.bind('<KeyRelease>', self.calculate_totals)
        self.entry_recipients.bind('<KeyRelease>', self.calculate_totals)
        self.entry_cost_per.bind('<KeyRelease>', self.calculate_totals)

        # Set default value for new prizes
        if not self.prize_data:
            self.entry_recipients.insert(0, "1")

        # Received checkbox
        self.var_received = ctk.BooleanVar()
        ctk.CTkCheckBox(
            frame,
            text="Item Received (from supplier)",
            variable=self.var_received,
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        ).pack(anchor="w", pady=(10, 15))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            font=ctk.CTkFont(size=15),
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def calculate_totals(self, event=None):
        """Calculate quantity and total cost"""
        try:
            # Calculate total quantity
            qty_per_player = int(self.entry_quantity_per_player.get() or 0)
            recipients = int(self.entry_recipients.get() or 0)
            total_qty = qty_per_player * recipients

            self.entry_quantity.delete(0, 'end')
            self.entry_quantity.insert(0, str(total_qty))

            # Calculate total cost
            cost_per = float(self.entry_cost_per.get() or 0)
            total_cost = total_qty * cost_per

            self.entry_total.delete(0, 'end')
            self.entry_total.insert(0, f"{total_cost:.2f}")
        except:
            pass

    def populate_fields(self):
        """Populate fields with existing data"""
        if not self.prize_data:
            return

        # Set item type
        if self.prize_data.get('item_type'):
            self.var_item_type.set(self.prize_data['item_type'])

        self.entry_description.insert(0, self.prize_data['description'])

        # Populate quantity per player if available
        if self.prize_data.get('quantity_per_player'):
            self.entry_quantity_per_player.insert(0, str(self.prize_data['quantity_per_player']))

        # Populate recipients
        if self.prize_data.get('recipients'):
            self.entry_recipients.insert(0, str(self.prize_data['recipients']))
        else:
            self.entry_recipients.insert(0, "1")  # Default to 1

        # Populate total quantity (will be auto-calculated for new approach, but keep for legacy)
        if self.prize_data['quantity']:
            self.entry_quantity.insert(0, str(self.prize_data['quantity']))

        if self.prize_data['cost_per_item']:
            self.entry_cost_per.insert(0, str(self.prize_data['cost_per_item']))

        if self.prize_data['total_cost']:
            self.entry_total.insert(0, str(self.prize_data['total_cost']))

        self.var_received.set(bool(self.prize_data['is_received']))

    def save(self):
        """Save the prize"""
        # Validate
        if not self.entry_description.get():
            messagebox.showerror("Validation Error", "Description is required")
            return

        quantity = None
        if self.entry_quantity.get():
            try:
                quantity = int(self.entry_quantity.get())
                if quantity < 0:
                    messagebox.showerror("Validation Error", "Quantity must be positive")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Quantity must be a whole number")
                return

        cost_per = None
        if self.entry_cost_per.get():
            try:
                cost_per = float(self.entry_cost_per.get())
                if cost_per < 0:
                    messagebox.showerror("Validation Error", "Cost must be positive")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Cost must be a valid number")
                return

        total_cost = None
        if self.entry_total.get():
            try:
                total_cost = float(self.entry_total.get())
            except ValueError:
                total_cost = None

        # Validate recipients (required)
        if not self.entry_recipients.get():
            messagebox.showerror("Validation Error", "Number of recipients is required")
            return

        try:
            recipients = int(self.entry_recipients.get())
            if recipients < 1:
                messagebox.showerror("Validation Error", "Number of recipients must be at least 1")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Number of recipients must be a whole number")
            return

        # Get quantity per player
        quantity_per_player = None
        if self.entry_quantity_per_player.get():
            try:
                quantity_per_player = int(self.entry_quantity_per_player.get())
                if quantity_per_player < 0:
                    messagebox.showerror("Validation Error", "Quantity per player must be positive")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Quantity per player must be a whole number")
                return

        # Get item type
        item_type = self.var_item_type.get()

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        if self.prize_data:
            # Update existing
            cursor.execute('''
                UPDATE prize_items
                SET description = ?, quantity = ?, cost_per_item = ?, total_cost = ?, recipients = ?, is_received = ?, item_type = ?, quantity_per_player = ?
                WHERE id = ?
            ''', (self.entry_description.get(), quantity, cost_per, total_cost, recipients, self.var_received.get(), item_type, quantity_per_player, self.prize_data['id']))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO prize_items (event_id, description, quantity, cost_per_item, total_cost, recipients, is_received, item_type, quantity_per_player)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.event_id, self.entry_description.get(), quantity, cost_per, total_cost, recipients, self.var_received.get(), item_type, quantity_per_player))

        conn.commit()
        conn.close()

        item_type_name = "Material" if item_type == "material" else "Prize"
        messagebox.showinfo("Success", f"{item_type_name} saved successfully!")
        self.destroy()


class PostEventFeedbackDialog(ctk.CTkToplevel):
    """Dialog for adding post-event feedback with multiple save options"""

    def __init__(self, parent, db, event_id: int, template_id: Optional[int] = None):
        super().__init__(parent)

        self.db = db
        self.event_id = event_id
        self.template_id = template_id

        self.title("Add Post-Event Feedback/Note")
        self.geometry("600x500")
        self.minsize(500, 400)  # Set minimum size for resizing
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        """Create the form"""
        # Use scrollable frame
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Note text
        ctk.CTkLabel(frame, text="Note/Feedback *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Add any observations, feedback, or notes about this event.", text_color="#666666", font=ctk.CTkFont(size=15)).pack(anchor="w", pady=(0, 5))
        self.text_note = ctk.CTkTextbox(frame, height=150, font=ctk.CTkFont(size=15))
        self.text_note.pack(fill="both", expand=True, pady=(0, 15))

        # Save options
        ctk.CTkLabel(frame, text="Save To:", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(10, 5))

        save_options_frame = ctk.CTkFrame(frame, fg_color="white")
        save_options_frame.pack(fill="x", pady=(0, 15), padx=5, ipady=10)

        self.var_save_to_event = ctk.BooleanVar(value=True)
        self.var_save_to_template = ctk.BooleanVar(value=False)
        self.var_save_to_feedback = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            save_options_frame,
            text="Save to this event (visible in Notes tab)",
            variable=self.var_save_to_event,
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            border_color="black",
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            checkmark_color="white"
        ).pack(anchor="w", padx=15, pady=5)

        if self.template_id:
            ctk.CTkCheckBox(
                save_options_frame,
                text="Save to template (for future events of this type)",
                variable=self.var_save_to_template,
                text_color="#4A2D5E",
                font=ctk.CTkFont(size=15),
                border_color="black",
                fg_color="#8B5FBF",
                hover_color="#7A4FB0",
                checkmark_color="white"
            ).pack(anchor="w", padx=15, pady=5)

        ctk.CTkCheckBox(
            save_options_frame,
            text="Save to Feedback menu (visible across all events)",
            variable=self.var_save_to_feedback,
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            border_color="black",
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            checkmark_color="white"
        ).pack(anchor="w", padx=15, pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            font=ctk.CTkFont(size=15),
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def save(self):
        """Save the feedback/note"""
        note_text = self.text_note.get("1.0", "end-1c").strip()

        if not note_text:
            messagebox.showerror("Validation Error", "Note text is required")
            return

        # Check that at least one save option is selected
        if not (self.var_save_to_event.get() or self.var_save_to_template.get() or self.var_save_to_feedback.get()):
            messagebox.showerror("Validation Error", "Please select at least one save location")
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Save to event notes
            if self.var_save_to_event.get():
                cursor.execute('''
                    INSERT INTO event_notes (event_id, note_text, include_in_printout)
                    VALUES (?, ?, ?)
                ''', (self.event_id, note_text, 0))

            # Save to template feedback
            if self.var_save_to_template.get() and self.template_id:
                cursor.execute('''
                    INSERT INTO template_feedback (template_id, event_id, feedback_text)
                    VALUES (?, ?, ?)
                ''', (self.template_id, self.event_id, note_text))

            # Save to feedback menu
            if self.var_save_to_feedback.get():
                cursor.execute('''
                    INSERT INTO feedback_items (event_id, feedback_text)
                    VALUES (?, ?)
                ''', (self.event_id, note_text))

            conn.commit()
            messagebox.showinfo("Success", "Feedback saved successfully!")
            self.destroy()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to save feedback: {str(e)}")
        finally:
            conn.close()


class NoteDialog(ctk.CTkToplevel):
    """Dialog for adding/editing notes"""

    def __init__(self, parent, db, event_id: int, template_id: Optional[int] = None, note_data: Optional[dict] = None, from_notes_tab: bool = False):
        super().__init__(parent)

        self.db = db
        self.event_id = event_id
        self.template_id = template_id
        self.note_data = note_data
        self.from_notes_tab = from_notes_tab

        self.title("Edit Note" if note_data else "Add Note")
        self.geometry("500x420")
        self.minsize(400, 350)  # Set minimum size for resizing
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

        if note_data:
            self.populate_fields()

    def create_form(self):
        """Create the form"""
        # Use scrollable frame
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Note text
        ctk.CTkLabel(frame, text="Note *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.text_note = ctk.CTkTextbox(frame, height=150)
        self.text_note.pack(fill="both", expand=True, pady=(0, 15))

        # Show in Notes tab checkbox (only show if NOT creating from Notes tab)
        self.var_show_in_notes = ctk.BooleanVar()
        if self.from_notes_tab:
            # Automatically set to True if creating from Notes tab
            self.var_show_in_notes.set(True)
        else:
            # Show checkbox only when creating from Post-Event Analysis tab
            chk_notes = ctk.CTkCheckBox(
                frame,
                text="Show in Notes tab",
                variable=self.var_show_in_notes,
                text_color="#4A2D5E",
                border_color="black",
                fg_color="white",
                hover_color="#E6D9F2",
                checkmark_color="black"
            )
            chk_notes.pack(anchor="w", pady=(0, 10))

        # Include in printable PDF checkbox
        self.var_printout = ctk.BooleanVar()
        chk_printout = ctk.CTkCheckBox(
            frame,
            text="Include in printable PDF",
            variable=self.var_printout,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        )
        chk_printout.pack(anchor="w", pady=(0, 10))

        # Send to template checkbox (only show if event has a template)
        self.var_send_to_template = ctk.BooleanVar()
        if self.template_id:
            chk_template = ctk.CTkCheckBox(
                frame,
                text="Send feedback to template (for future events)",
                variable=self.var_send_to_template,
                text_color="#4A2D5E",
                border_color="black",
                fg_color="white",
                hover_color="#E6D9F2",
                checkmark_color="black"
            )
            chk_template.pack(anchor="w", pady=(0, 15))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x")

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def populate_fields(self):
        """Populate fields with existing data"""
        if not self.note_data:
            return

        self.text_note.insert("1.0", self.note_data['note_text'])
        self.var_show_in_notes.set(bool(self.note_data.get('show_in_notes_tab', 0)))
        self.var_printout.set(bool(self.note_data.get('include_in_printout', 0)))
        if self.template_id and self.note_data.get('send_to_template'):
            self.var_send_to_template.set(bool(self.note_data['send_to_template']))

    def save(self):
        """Save the note"""
        note_text = self.text_note.get("1.0", "end-1c").strip()

        if not note_text:
            messagebox.showerror("Validation Error", "Note text is required")
            return

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        send_to_template = self.var_send_to_template.get() if self.template_id else False

        if self.note_data:
            # Update existing
            cursor.execute('''
                UPDATE event_notes
                SET note_text = ?, show_in_notes_tab = ?, include_in_printout = ?, send_to_template = ?
                WHERE id = ?
            ''', (note_text, self.var_show_in_notes.get(), self.var_printout.get(), send_to_template, self.note_data['id']))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO event_notes (event_id, note_text, show_in_notes_tab, include_in_printout, send_to_template)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.event_id, note_text, self.var_show_in_notes.get(), self.var_printout.get(), send_to_template))

        # If sending to template, also add to template_feedback table
        if send_to_template and self.template_id:
            cursor.execute('''
                INSERT INTO template_feedback (template_id, event_id, feedback_text)
                VALUES (?, ?, ?)
            ''', (self.template_id, self.event_id, note_text))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Note saved successfully!")
        self.destroy()


class ChecklistItemDialog(ctk.CTkToplevel):
    """Dialog for adding/editing checklist items"""

    def __init__(self, parent, db, event_id: int, checklist_data: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.event_id = event_id
        self.checklist_data = checklist_data

        self.title("Edit Checklist Item" if checklist_data else "Add Checklist Item")
        self.geometry("500x450")
        self.minsize(400, 350)  # Set minimum size for resizing
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

        if checklist_data:
            self.populate_fields()

    def create_form(self):
        """Create the form"""
        # Use scrollable frame
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Description
        ctk.CTkLabel(frame, text="Description *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_description = ctk.CTkEntry(frame, placeholder_text="e.g., Order prize support")
        self.entry_description.pack(fill="x", pady=(0, 15))

        # Category - load from database
        ctk.CTkLabel(frame, text="Category *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))

        # Get categories from database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM checklist_categories ORDER BY sort_order')
        categories = [row['name'] for row in cursor.fetchall()]
        conn.close()

        self.combo_category = ctk.CTkComboBox(
            frame,
            values=categories
        )
        self.combo_category.set(categories[0] if categories else "Before the Event")
        self.combo_category.pack(fill="x", pady=(0, 15))

        # Due Date
        ctk.CTkLabel(frame, text="Due Date", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Optional - leave blank if no specific due date", text_color="#666666", font=ctk.CTkFont(size=10)).pack(anchor="w", pady=(0, 5))
        self.entry_due_date = DateEntry(
            frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            background='#8B5FBF',
            foreground='white',
            borderwidth=2
        )
        self.entry_due_date.pack(fill="x", pady=(0, 15))

        # Include in PDF checkbox
        self.var_include_pdf = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            frame,
            text="Include in PDF printout",
            variable=self.var_include_pdf,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        ).pack(anchor="w", pady=(0, 10))

        # Show on dashboard checkbox
        self.var_show_dashboard = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            frame,
            text="Show on dashboard",
            variable=self.var_show_dashboard,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        ).pack(anchor="w", pady=(0, 15))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def populate_fields(self):
        """Populate fields with existing data"""
        if not self.checklist_data:
            return

        self.entry_description.insert(0, self.checklist_data['description'])

        # Get category name from database if category_id exists
        if self.checklist_data.get('category_id'):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM checklist_categories WHERE id = ?', (self.checklist_data['category_id'],))
            result = cursor.fetchone()
            conn.close()
            if result:
                self.combo_category.set(result['name'])

        if self.checklist_data.get('due_date'):
            try:
                from datetime import datetime
                due_date = datetime.strptime(self.checklist_data['due_date'], '%Y-%m-%d')
                self.entry_due_date.set_date(due_date)
            except:
                pass

        self.var_include_pdf.set(bool(self.checklist_data.get('include_in_pdf', 1)))
        self.var_show_dashboard.set(bool(self.checklist_data.get('show_on_dashboard', 0)))

    def save(self):
        """Save the checklist item"""
        # Validate
        if not self.entry_description.get().strip():
            messagebox.showerror("Validation Error", "Description is required")
            return

        if not self.combo_category.get():
            messagebox.showerror("Validation Error", "Category is required")
            return

        # Get due date (can be None)
        due_date = None
        try:
            due_date_str = self.entry_due_date.get()
            if due_date_str:
                due_date = due_date_str
        except:
            pass

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Look up category_id from category name
        category_name = self.combo_category.get()
        cursor.execute('SELECT id FROM checklist_categories WHERE name = ?', (category_name,))
        category_result = cursor.fetchone()
        category_id = category_result[0] if category_result else None

        if self.checklist_data:
            # Update existing
            cursor.execute('''
                UPDATE event_checklist_items
                SET description = ?, category_id = ?, due_date = ?, include_in_pdf = ?, show_on_dashboard = ?
                WHERE id = ?
            ''', (self.entry_description.get().strip(),
                  category_id,
                  due_date,
                  1 if self.var_include_pdf.get() else 0,
                  1 if self.var_show_dashboard.get() else 0,
                  self.checklist_data['id']))
        else:
            # Insert new - get max sort_order for this event and category
            cursor.execute('''
                SELECT COALESCE(MAX(sort_order), -1) + 1 as next_order
                FROM event_checklist_items
                WHERE event_id = ? AND category_id IS ?
            ''', (self.event_id, category_id))
            next_order = cursor.fetchone()[0]

            cursor.execute('''
                INSERT INTO event_checklist_items
                (event_id, description, category_id, due_date, include_in_pdf, show_on_dashboard, is_completed, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            ''', (self.event_id,
                  self.entry_description.get().strip(),
                  category_id,
                  due_date,
                  1 if self.var_include_pdf.get() else 0,
                  1 if self.var_show_dashboard.get() else 0,
                  next_order))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Checklist item saved successfully!")
        self.destroy()


class LabourCostDialog(ctk.CTkToplevel):
    """Dialog for adding/editing labour cost entries"""

    def __init__(self, parent, db, event_id: int, labour_data: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.event_id = event_id
        self.labour_data = labour_data

        self.title("Edit Labour Cost Entry" if labour_data else "Add Labour Cost Entry")
        self.geometry("500x600")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

        if labour_data:
            self.populate_fields()

    def create_form(self):
        """Create the form"""
        # Use scrollable frame
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Staff Name
        ctk.CTkLabel(frame, text="Staff Name (Optional)", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frame, text="Leave blank if not tracking individual staff", text_color="#666666", font=ctk.CTkFont(size=10)).pack(anchor="w", pady=(0, 5))
        self.entry_staff_name = ctk.CTkEntry(frame, placeholder_text="e.g., John Smith")
        self.entry_staff_name.pack(fill="x", pady=(0, 15))

        # Hours Worked
        ctk.CTkLabel(frame, text="Hours Worked *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_hours = ctk.CTkEntry(frame, placeholder_text="e.g., 4.5")
        self.entry_hours.pack(fill="x", pady=(0, 15))

        # Rate Type
        ctk.CTkLabel(frame, text="Rate Type *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.combo_rate_type = ctk.CTkComboBox(
            frame,
            values=["Weekday", "Public Holiday"],
            command=self.update_rate
        )
        self.combo_rate_type.set("Weekday")
        self.combo_rate_type.pack(fill="x", pady=(0, 15))

        # Hourly Rate
        ctk.CTkLabel(frame, text="Hourly Rate (AUD) *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_rate = ctk.CTkEntry(frame, placeholder_text="Auto-filled from settings")
        self.entry_rate.pack(fill="x", pady=(0, 15))

        # Work Status
        ctk.CTkLabel(frame, text="Work Status *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.combo_work_status = ctk.CTkComboBox(
            frame,
            values=["Full", "Partial"]
        )
        self.combo_work_status.set("Full")
        self.combo_work_status.pack(fill="x", pady=(0, 15))

        # Total Cost (calculated)
        ctk.CTkLabel(frame, text="Total Cost (AUD)", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_total = ctk.CTkEntry(frame, placeholder_text="Auto-calculated", state="disabled")
        self.entry_total.pack(fill="x", pady=(0, 15))

        # Auto-calculate total when hours or rate changes
        self.entry_hours.bind('<KeyRelease>', self.calculate_total)
        self.entry_rate.bind('<KeyRelease>', self.calculate_total)

        # Set default rate based on rate type
        self.update_rate()

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def update_rate(self, event=None):
        """Update the hourly rate based on selected rate type"""
        rate_type = self.combo_rate_type.get()

        # Get rate from settings based on type
        if rate_type == "Public Holiday":
            rate = float(self.db.get_setting('public_holiday_rate') or 40.0)
        else:  # Weekday
            rate = float(self.db.get_setting('weekday_after_6pm_rate') or 25.5)

        self.entry_rate.delete(0, 'end')
        self.entry_rate.insert(0, f"{rate:.2f}")

        # Recalculate total
        self.calculate_total()

    def calculate_total(self, event=None):
        """Calculate total cost"""
        try:
            hours = float(self.entry_hours.get() or 0)
            rate = float(self.entry_rate.get() or 0)
            total = hours * rate

            self.entry_total.configure(state="normal")
            self.entry_total.delete(0, 'end')
            self.entry_total.insert(0, f"{total:.2f}")
            self.entry_total.configure(state="disabled")
        except:
            pass

    def populate_fields(self):
        """Populate fields with existing data"""
        if not self.labour_data:
            return

        if self.labour_data.get('staff_name'):
            self.entry_staff_name.insert(0, self.labour_data['staff_name'])

        if self.labour_data.get('hours_worked'):
            self.entry_hours.insert(0, str(self.labour_data['hours_worked']))

        if self.labour_data.get('rate_type'):
            # Capitalize first letter for display
            rate_type = self.labour_data['rate_type']
            if rate_type == 'weekday':
                self.combo_rate_type.set('Weekday')
            elif rate_type == 'public_holiday':
                self.combo_rate_type.set('Public Holiday')

        if self.labour_data.get('hourly_rate'):
            self.entry_rate.delete(0, 'end')
            self.entry_rate.insert(0, str(self.labour_data['hourly_rate']))

        if self.labour_data.get('work_status'):
            work_status = self.labour_data['work_status'].capitalize()
            self.combo_work_status.set(work_status)

        # Calculate and show total
        self.calculate_total()

    def save(self):
        """Save the labour cost entry"""
        # Validate
        try:
            hours = float(self.entry_hours.get())
            if hours <= 0:
                messagebox.showerror("Validation Error", "Hours worked must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Hours worked must be a valid number")
            return

        try:
            rate = float(self.entry_rate.get())
            if rate <= 0:
                messagebox.showerror("Validation Error", "Hourly rate must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Hourly rate must be a valid number")
            return

        # Calculate total
        total_cost = hours * rate

        # Get rate type (convert to lowercase for database)
        rate_type = 'public_holiday' if self.combo_rate_type.get() == 'Public Holiday' else 'weekday'

        # Get work status (convert to lowercase for database)
        work_status = self.combo_work_status.get().lower()

        # Get staff name (can be empty)
        staff_name = self.entry_staff_name.get().strip() or None

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        if self.labour_data:
            # Update existing
            cursor.execute('''
                UPDATE labour_costs
                SET staff_name = ?, hours_worked = ?, rate_type = ?, hourly_rate = ?,
                    work_status = ?, total_cost = ?
                WHERE id = ?
            ''', (staff_name, hours, rate_type, rate, work_status, total_cost, self.labour_data['id']))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO labour_costs
                (event_id, staff_name, hours_worked, rate_type, hourly_rate, work_status, total_cost, staff_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (self.event_id, staff_name, hours, rate_type, rate, work_status, total_cost))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Labour cost entry saved successfully!")
        self.destroy()


class PostEventNoteDialog(ctk.CTkToplevel):
    """Dialog for adding/editing post-event notes"""

    def __init__(self, parent, db, event_id: int, template_id: Optional[int] = None, note_data: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.event_id = event_id
        self.template_id = template_id
        self.note_data = note_data

        self.title("Edit Note" if note_data else "Add Note")
        self.geometry("500x350")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

        if note_data:
            self.populate_fields()

    def create_form(self):
        """Create the form"""
        # Use scrollable frame
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Note text
        ctk.CTkLabel(frame, text="Note *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.text_note = ctk.CTkTextbox(frame, height=150)
        self.text_note.pack(fill="both", expand=True, pady=(0, 15))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x")

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def populate_fields(self):
        """Populate fields with existing data"""
        if not self.note_data:
            return

        self.text_note.insert("1.0", self.note_data['note_text'])

    def save(self):
        """Save the note"""
        note_text = self.text_note.get("1.0", "end-1c").strip()

        if not note_text:
            messagebox.showerror("Validation Error", "Note text is required")
            return

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        if self.note_data:
            # Update existing
            cursor.execute('''
                UPDATE event_notes
                SET note_text = ?
                WHERE id = ?
            ''', (note_text, self.note_data['id']))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO event_notes (event_id, note_text, include_in_printout, send_to_template)
                VALUES (?, ?, 0, 0)
            ''', (self.event_id, note_text))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Note saved successfully!")
        self.destroy()


class TemplateSelectionDialog(ctk.CTkToplevel):
    """Dialog for selecting template(s) to save note to"""

    def __init__(self, parent, db, templates: list, note_data: dict, event_id: int):
        super().__init__(parent)

        self.db = db
        self.templates = templates
        self.note_data = note_data
        self.event_id = event_id
        self.selected_templates = []

        self.title("Select Templates")
        self.geometry("400x500")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        """Create the form"""
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Instructions
        ctk.CTkLabel(
            frame,
            text="Select which template(s) to save this note to:",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 15))

        # Template checkboxes
        self.template_vars = {}
        for template in self.templates:
            var = ctk.BooleanVar()
            chk = ctk.CTkCheckBox(
                frame,
                text=template['name'],
                variable=var,
                text_color="#4A2D5E",
                border_color="black",
                fg_color="white",
                hover_color="#E6D9F2",
                checkmark_color="black"
            )
            chk.pack(anchor="w", pady=5)
            self.template_vars[template['id']] = var

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save to Template(s)",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def save(self):
        """Save note to selected templates"""
        # Get selected templates
        selected = [tid for tid, var in self.template_vars.items() if var.get()]

        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one template")
            return

        # Save to template_feedback table
        conn = self.db.get_connection()
        cursor = conn.cursor()

        for template_id in selected:
            # Check if this note was already sent to this template
            cursor.execute('''
                SELECT id FROM template_feedback
                WHERE template_id = ? AND event_id = ? AND feedback_text = ?
            ''', (template_id, self.event_id, self.note_data['note_text']))

            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO template_feedback (template_id, event_id, feedback_text)
                    VALUES (?, ?, ?)
                ''', (template_id, self.event_id, self.note_data['note_text']))

        # Mark note as sent to template
        cursor.execute('''
            UPDATE event_notes
            SET send_to_template = 1
            WHERE id = ?
        ''', (self.note_data['id'],))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Note saved to {len(selected)} template(s)!")
        self.destroy()


class LaborProjectionDialog(ctk.CTkToplevel):
    """Dialog for adding/editing labor projection entries"""

    def __init__(self, parent, db, event_id: int, labor_data: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.event_id = event_id
        self.labor_data = labor_data

        self.title("Edit Worker Group" if labor_data else "Add Worker Group")
        self.geometry("500x450")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

        if labor_data:
            self.populate_fields()

    def create_form(self):
        """Create the form"""
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Number of workers
        ctk.CTkLabel(frame, text="Number of Workers *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_workers = ctk.CTkEntry(frame, placeholder_text="e.g., 2")
        self.entry_workers.pack(fill="x", pady=(0, 15))

        # Hours worked
        ctk.CTkLabel(frame, text="Hours per Worker *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_hours = ctk.CTkEntry(frame, placeholder_text="e.g., 4.5")
        self.entry_hours.pack(fill="x", pady=(0, 15))

        # Rate type selection
        ctk.CTkLabel(frame, text="Rate Type *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))

        # Get rates from settings
        weekday_before_6pm = float(self.db.get_setting('weekday_before_6pm_rate') or 22.00)
        weekday_after_6pm = float(self.db.get_setting('weekday_after_6pm_rate') or 25.50)
        saturday = float(self.db.get_setting('saturday_rate') or 30.00)
        sunday = float(self.db.get_setting('sunday_rate') or 35.00)
        public_holiday = float(self.db.get_setting('public_holiday_rate') or 40.00)

        self.rate_map = {
            "Weekday Before 6pm": weekday_before_6pm,
            "Weekday After 6pm": weekday_after_6pm,
            "Saturday": saturday,
            "Sunday": sunday,
            "Public Holiday": public_holiday
        }

        rate_options = [
            f"Weekday Before 6pm (${weekday_before_6pm:.2f}/hr)",
            f"Weekday After 6pm (${weekday_after_6pm:.2f}/hr)",
            f"Saturday (${saturday:.2f}/hr)",
            f"Sunday (${sunday:.2f}/hr)",
            f"Public Holiday (${public_holiday:.2f}/hr)"
        ]

        self.rate_type_var = ctk.StringVar(value=rate_options[0])
        self.rate_dropdown = ctk.CTkOptionMenu(
            frame,
            variable=self.rate_type_var,
            values=rate_options,
            fg_color="#8B5FBF",
            button_color="#7A4FB0",
            button_hover_color="#6A3F9F"
        )
        self.rate_dropdown.pack(fill="x", pady=(0, 15))

        # Calculated cost display
        ctk.CTkLabel(frame, text="Calculated Cost", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.label_cost = ctk.CTkLabel(frame, text="$0.00", text_color="#8B5FBF", font=ctk.CTkFont(size=18, weight="bold"))
        self.label_cost.pack(anchor="w", pady=(0, 15))

        # Calculate button
        ctk.CTkButton(
            frame,
            text="Calculate Cost",
            command=self.calculate_cost,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            height=35
        ).pack(fill="x", pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x")

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def populate_fields(self):
        """Populate fields with existing data"""
        if not self.labor_data:
            return

        self.entry_workers.insert(0, str(self.labor_data.get('staff_count', 1)))
        self.entry_hours.insert(0, str(self.labor_data.get('hours_worked', 0)))

        # Set rate type
        rate_type = self.labor_data.get('rate_type', '')
        rate = self.labor_data.get('hourly_rate', 0)

        # Find matching rate option
        for option in self.rate_dropdown.cget("values"):
            if rate_type in option:
                self.rate_type_var.set(option)
                break

        self.calculate_cost()

    def calculate_cost(self):
        """Calculate and display the labor cost"""
        try:
            workers = int(self.entry_workers.get())
            hours = float(self.entry_hours.get())

            if workers < 1:
                messagebox.showerror("Invalid Input", "Number of workers must be at least 1")
                return
            if hours <= 0:
                messagebox.showerror("Invalid Input", "Hours must be greater than 0")
                return

            # Extract rate from dropdown
            rate_text = self.rate_type_var.get()
            import re
            rate_match = re.search(r'\$([0-9.]+)', rate_text)
            rate = float(rate_match.group(1)) if rate_match else 0

            total_cost = workers * hours * rate
            self.label_cost.configure(text=f"${total_cost:.2f}")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for workers and hours")

    def save(self):
        """Save the labor entry"""
        # Validate
        try:
            workers = int(self.entry_workers.get())
            hours = float(self.entry_hours.get())

            if workers < 1:
                messagebox.showerror("Validation Error", "Number of workers must be at least 1")
                return
            if hours <= 0:
                messagebox.showerror("Validation Error", "Hours must be greater than 0")
                return

        except ValueError:
            messagebox.showerror("Validation Error", "Please enter valid numbers")
            return

        # Get rate type and rate
        rate_text = self.rate_type_var.get()
        import re
        rate_match = re.search(r'\$([0-9.]+)', rate_text)
        rate = float(rate_match.group(1)) if rate_match else 0

        # Extract rate type name (before the parenthesis)
        rate_type = rate_text.split('(')[0].strip()

        # Calculate total cost
        total_cost = workers * hours * rate

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        if self.labor_data:
            # Update existing
            cursor.execute('''
                UPDATE labour_costs
                SET staff_count = ?, hours_worked = ?, rate_type = ?, hourly_rate = ?, total_cost = ?
                WHERE id = ?
            ''', (workers, hours, rate_type, rate, total_cost, self.labor_data['id']))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO labour_costs (event_id, staff_count, hours_worked, rate_type, hourly_rate, total_cost)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.event_id, workers, hours, rate_type, rate, total_cost))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Worker group saved successfully!")
        self.destroy()


class EventDetailsEditDialog(ctk.CTkToplevel):
    """Dialog for editing basic event details including number of rounds"""

    def __init__(self, parent, db, event_id: int):
        super().__init__(parent)

        self.db = db
        self.event_id = event_id

        self.title("Edit Event Details")
        self.geometry("600x700")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        # Load event data
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.*,
                   et.name as event_type_name,
                   pf.name as format_name,
                   pm.name as pairing_method_name,
                   pa.name as pairing_app_name
            FROM events e
            LEFT JOIN event_types et ON e.event_type_id = et.id
            LEFT JOIN playing_formats pf ON e.playing_format_id = pf.id
            LEFT JOIN pairing_methods pm ON e.pairing_method_id = pm.id
            LEFT JOIN pairing_apps pa ON e.pairing_app_id = pa.id
            WHERE e.id = ?
        ''', (event_id,))
        self.event_data = dict(cursor.fetchone())
        conn.close()

        self.create_form()
        self.populate_fields()

    def create_form(self):
        """Create the edit form"""
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Event Name
        ctk.CTkLabel(frame, text="Event Name *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_name = ctk.CTkEntry(frame, placeholder_text="Enter event name", height=35)
        self.entry_name.pack(fill="x", pady=(0, 15))

        # Event Date
        ctk.CTkLabel(frame, text="Event Date *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_date = ctk.CTkEntry(frame, placeholder_text="YYYY-MM-DD", height=35)
        self.entry_date.pack(fill="x", pady=(0, 15))

        # Start Time
        ctk.CTkLabel(frame, text="Start Time", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_start_time = ctk.CTkEntry(frame, placeholder_text="HH:MM", height=35)
        self.entry_start_time.pack(fill="x", pady=(0, 15))

        # End Time
        ctk.CTkLabel(frame, text="End Time", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_end_time = ctk.CTkEntry(frame, placeholder_text="HH:MM", height=35)
        self.entry_end_time.pack(fill="x", pady=(0, 15))

        # Number of Rounds
        ctk.CTkLabel(frame, text="Number of Rounds", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_rounds = ctk.CTkEntry(frame, placeholder_text="Enter number of rounds", height=35)
        self.entry_rounds.pack(fill="x", pady=(0, 15))

        # Max Capacity
        ctk.CTkLabel(frame, text="Maximum Capacity", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_capacity = ctk.CTkEntry(frame, placeholder_text="Enter maximum capacity", height=35)
        self.entry_capacity.pack(fill="x", pady=(0, 15))

        # Description
        ctk.CTkLabel(frame, text="Description", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.text_description = ctk.CTkTextbox(frame, height=100)
        self.text_description.pack(fill="x", pady=(0, 15))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save Changes",
            command=self.save_changes,
            fg_color="#4CAF50",
            hover_color="#45A049",
            height=40
        )
        btn_save.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", fill="x", expand=True, padx=(5, 0))

    def populate_fields(self):
        """Populate form with existing data"""
        self.entry_name.insert(0, self.event_data.get('event_name', ''))
        self.entry_date.insert(0, self.event_data.get('event_date', ''))

        if self.event_data.get('start_time'):
            # Remove seconds from time if present
            start_time = self.event_data['start_time'].rsplit(':', 1)[0]
            self.entry_start_time.insert(0, start_time)

        if self.event_data.get('end_time'):
            end_time = self.event_data['end_time'].rsplit(':', 1)[0]
            self.entry_end_time.insert(0, end_time)

        if self.event_data.get('number_of_rounds'):
            self.entry_rounds.insert(0, str(self.event_data['number_of_rounds']))

        if self.event_data.get('max_capacity'):
            self.entry_capacity.insert(0, str(self.event_data['max_capacity']))

        if self.event_data.get('description'):
            self.text_description.insert("1.0", self.event_data['description'])

    def save_changes(self):
        """Save the edited event details"""
        # Get form data
        event_name = self.entry_name.get().strip()
        event_date = self.entry_date.get().strip()
        start_time = self.entry_start_time.get().strip() or None
        end_time = self.entry_end_time.get().strip() or None
        rounds = self.entry_rounds.get().strip()
        capacity = self.entry_capacity.get().strip()
        description = self.text_description.get("1.0", "end-1c").strip() or None

        # Validation
        if not event_name:
            messagebox.showerror("Validation Error", "Event name is required")
            return

        if not event_date:
            messagebox.showerror("Validation Error", "Event date is required")
            return

        # Update database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE events
            SET event_name = ?,
                event_date = ?,
                start_time = ?,
                end_time = ?,
                number_of_rounds = ?,
                max_capacity = ?,
                description = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            event_name,
            event_date,
            start_time,
            end_time,
            int(rounds) if rounds else None,
            int(capacity) if capacity else None,
            description,
            self.event_id
        ))

        conn.commit()
        conn.close()

        self.destroy()
