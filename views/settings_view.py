"""Settings view UI"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from database import Database
from typing import Optional
import shutil
from datetime import datetime
import os

class SettingsView(ctk.CTkFrame):
    """Settings and configuration view"""

    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db

        self.configure(fg_color="#F5F0F6")

        # Create header
        self.create_header()

        # Create tabbed interface for different settings sections
        self.create_tabs()

    def create_header(self):
        """Create the header"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        title = ctk.CTkLabel(
            header_frame,
            text="Settings",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(side="left")

    def create_tabs(self):
        """Create tabbed settings interface"""
        # Tab view
        self.tabview = ctk.CTkTabview(self, fg_color="#F5F0F6")
        self.tabview.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Create tabs
        self.tabview.add("Event Types")
        self.tabview.add("Playing Formats")
        self.tabview.add("Pairing Methods")
        self.tabview.add("Pairing Apps")
        self.tabview.add("Award Rates")
        self.tabview.add("Backup")

        # Populate tabs
        self.create_event_types_tab()
        self.create_formats_tab()
        self.create_methods_tab()
        self.create_apps_tab()
        self.create_rates_tab()
        self.create_backup_tab()

    def create_event_types_tab(self):
        """Create event types management tab"""
        tab = self.tabview.tab("Event Types")
        self.create_manage_list_tab(tab, "event_types", "Event Type", "Event Types")

    def create_formats_tab(self):
        """Create playing formats management tab"""
        tab = self.tabview.tab("Playing Formats")
        self.create_manage_list_tab(tab, "playing_formats", "Playing Format", "Playing Formats")

    def create_methods_tab(self):
        """Create pairing methods management tab"""
        tab = self.tabview.tab("Pairing Methods")
        self.create_manage_list_tab(tab, "pairing_methods", "Pairing Method", "Pairing Methods")

    def create_apps_tab(self):
        """Create pairing apps management tab"""
        tab = self.tabview.tab("Pairing Apps")
        self.create_manage_list_tab(tab, "pairing_apps", "Pairing App", "Pairing Apps")

    def create_manage_list_tab(self, parent, table_name: str, singular: str, plural: str):
        """Create a generic list management tab"""
        # Header with add button
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header,
            text=f"Manage {plural}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4A2D5E"
        ).pack(side="left")

        btn_add = ctk.CTkButton(
            header,
            text=f"+ Add {singular}",
            command=lambda: self.add_item(table_name, singular),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=120
        )
        btn_add.pack(side="right")

        # Scrollable list
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="white")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Load and display items
        self.load_items(scroll_frame, table_name, singular)

    def load_items(self, parent, table_name: str, singular: str):
        """Load and display items from a table"""
        # Clear existing
        for widget in parent.winfo_children():
            widget.destroy()

        # Get items
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name} ORDER BY name')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not items:
            ctk.CTkLabel(
                parent,
                text=f"No {singular.lower()}s yet. Add your first one!",
                text_color="#999999"
            ).pack(pady=20)
            return

        # Display items
        for item in items:
            self.create_item_card(parent, table_name, singular, item)

    def create_item_card(self, parent, table_name: str, singular: str, item: dict):
        """Create a card for a single item"""
        card = ctk.CTkFrame(parent, fg_color="#F9F5FA")
        card.pack(fill="x", padx=10, pady=2)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)

        # Name
        name_label = ctk.CTkLabel(
            content,
            text=item['name'],
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)

        # Edit button
        btn_edit = ctk.CTkButton(
            content,
            text="Edit",
            command=lambda: self.edit_item(table_name, singular, item),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=60,
            height=25
        )
        btn_edit.pack(side="right", padx=(5, 0))

        # Delete button
        btn_delete = ctk.CTkButton(
            content,
            text="Delete",
            command=lambda: self.delete_item(table_name, singular, item),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=60,
            height=25
        )
        btn_delete.pack(side="right")

    def add_item(self, table_name: str, singular: str):
        """Show dialog to add a new item"""
        dialog = EditItemDialog(self, self.db, table_name, singular, None)
        self.wait_window(dialog)
        # Reload the appropriate tab
        self.reload_current_tab(table_name)

    def edit_item(self, table_name: str, singular: str, item: dict):
        """Show dialog to edit an item"""
        dialog = EditItemDialog(self, self.db, table_name, singular, item)
        self.wait_window(dialog)
        # Reload the appropriate tab
        self.reload_current_tab(table_name)

    def delete_item(self, table_name: str, singular: str, item: dict):
        """Delete an item after confirmation"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{item['name']}'?\n\nThis cannot be undone."
        )
        if result:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table_name} WHERE id = ?', (item['id'],))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", f"'{item['name']}' has been deleted.")
            self.reload_current_tab(table_name)

    def reload_current_tab(self, table_name: str):
        """Reload the current tab"""
        # Determine which tab to reload based on table name
        tab_map = {
            'event_types': ('Event Types', 'Event Type', 'Event Types'),
            'playing_formats': ('Playing Formats', 'Playing Format', 'Playing Formats'),
            'pairing_methods': ('Pairing Methods', 'Pairing Method', 'Pairing Methods'),
            'pairing_apps': ('Pairing Apps', 'Pairing App', 'Pairing Apps')
        }

        if table_name in tab_map:
            tab_name, singular, plural = tab_map[table_name]
            tab = self.tabview.tab(tab_name)

            # Clear and recreate
            for widget in tab.winfo_children():
                widget.destroy()

            self.create_manage_list_tab(tab, table_name, singular, plural)

    def create_rates_tab(self):
        """Create award rates configuration tab"""
        tab = self.tabview.tab("Award Rates")

        ctk.CTkLabel(
            tab,
            text="Configure Australian Award Rates",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=10, pady=(10, 20))

        # Form frame
        form = ctk.CTkFrame(tab, fg_color="white")
        form.pack(fill="x", padx=10, pady=10)

        form_content = ctk.CTkFrame(form, fg_color="transparent")
        form_content.pack(fill="x", padx=20, pady=20)

        # Weekday before 6pm rate
        ctk.CTkLabel(
            form_content,
            text="Weekday Before 6pm Rate ($/hour):",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=10)

        self.entry_weekday_before_rate = ctk.CTkEntry(form_content, width=150)
        self.entry_weekday_before_rate.grid(row=0, column=1, padx=10, pady=10)
        weekday_before_rate = self.db.get_setting('weekday_before_6pm_rate')
        if weekday_before_rate:
            self.entry_weekday_before_rate.insert(0, weekday_before_rate)

        # Weekday after 6pm rate
        ctk.CTkLabel(
            form_content,
            text="Weekday After 6pm Rate ($/hour):",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=1, column=0, sticky="w", pady=10)

        self.entry_weekday_after_rate = ctk.CTkEntry(form_content, width=150)
        self.entry_weekday_after_rate.grid(row=1, column=1, padx=10, pady=10)
        weekday_after_rate = self.db.get_setting('weekday_after_6pm_rate')
        if weekday_after_rate:
            self.entry_weekday_after_rate.insert(0, weekday_after_rate)

        # Saturday rate
        ctk.CTkLabel(
            form_content,
            text="Saturday Rate ($/hour):",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=2, column=0, sticky="w", pady=10)

        self.entry_saturday_rate = ctk.CTkEntry(form_content, width=150)
        self.entry_saturday_rate.grid(row=2, column=1, padx=10, pady=10)
        saturday_rate = self.db.get_setting('saturday_rate')
        if saturday_rate:
            self.entry_saturday_rate.insert(0, saturday_rate)

        # Sunday rate
        ctk.CTkLabel(
            form_content,
            text="Sunday Rate ($/hour):",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=3, column=0, sticky="w", pady=10)

        self.entry_sunday_rate = ctk.CTkEntry(form_content, width=150)
        self.entry_sunday_rate.grid(row=3, column=1, padx=10, pady=10)
        sunday_rate = self.db.get_setting('sunday_rate')
        if sunday_rate:
            self.entry_sunday_rate.insert(0, sunday_rate)

        # Public holiday rate
        ctk.CTkLabel(
            form_content,
            text="Public Holiday Rate ($/hour):",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=4, column=0, sticky="w", pady=10)

        self.entry_public_holiday_rate = ctk.CTkEntry(form_content, width=150)
        self.entry_public_holiday_rate.grid(row=4, column=1, padx=10, pady=10)
        public_holiday_rate = self.db.get_setting('public_holiday_rate')
        if public_holiday_rate:
            self.entry_public_holiday_rate.insert(0, public_holiday_rate)

        # Save button
        btn_save_rates = ctk.CTkButton(
            form_content,
            text="Save Rates",
            command=self.save_rates,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=150,
            height=35
        )
        btn_save_rates.grid(row=5, column=0, columnspan=2, pady=20)

    def save_rates(self):
        """Save award rates"""
        try:
            # Validate rates
            weekday_before = float(self.entry_weekday_before_rate.get())
            weekday_after = float(self.entry_weekday_after_rate.get())
            saturday = float(self.entry_saturday_rate.get())
            sunday = float(self.entry_sunday_rate.get())
            public_holiday = float(self.entry_public_holiday_rate.get())

            if any(rate < 0 for rate in [weekday_before, weekday_after, saturday, sunday, public_holiday]):
                messagebox.showerror("Validation Error", "Rates must be positive numbers")
                return

            # Save to database
            self.db.update_setting('weekday_before_6pm_rate', str(weekday_before))
            self.db.update_setting('weekday_after_6pm_rate', str(weekday_after))
            self.db.update_setting('saturday_rate', str(saturday))
            self.db.update_setting('sunday_rate', str(sunday))
            self.db.update_setting('public_holiday_rate', str(public_holiday))

            messagebox.showinfo("Success", "Award rates updated successfully!")

        except ValueError:
            messagebox.showerror("Validation Error", "Please enter valid numbers for rates")

    def create_backup_tab(self):
        """Create database backup tab"""
        tab = self.tabview.tab("Backup")

        ctk.CTkLabel(
            tab,
            text="Database Backup & Restore",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=10, pady=(10, 20))

        # Backup section
        backup_frame = ctk.CTkFrame(tab, fg_color="white")
        backup_frame.pack(fill="x", padx=10, pady=10)

        backup_content = ctk.CTkFrame(backup_frame, fg_color="transparent")
        backup_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            backup_content,
            text="Create a backup of your database:",
            text_color="#4A2D5E"
        ).pack(anchor="w", pady=(0, 10))

        btn_backup = ctk.CTkButton(
            backup_content,
            text="Backup Database Now",
            command=self.backup_database,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_backup.pack(fill="x", pady=10)

        # Info
        ctk.CTkLabel(
            backup_content,
            text="Your database file: events.db\nBackups will include the date and time.",
            text_color="#666666",
            font=ctk.CTkFont(size=15)
        ).pack(anchor="w", pady=(10, 0))

    def backup_database(self):
        """Backup the database file"""
        try:
            # Ask user where to save
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                initialfile=f"events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                title="Save Database Backup"
            )

            if backup_path:
                # Copy the database file
                shutil.copy2("events.db", backup_path)
                messagebox.showinfo("Success", f"Database backed up successfully!\n\nSaved to:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to backup database:\n{str(e)}")


class EditItemDialog(ctk.CTkToplevel):
    """Dialog for adding/editing a dropdown item"""

    def __init__(self, parent, db, table_name: str, singular: str, item: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.table_name = table_name
        self.singular = singular
        self.item = item

        # Configure window
        if item:
            self.title(f"Edit {singular}")
        else:
            self.title(f"Add {singular}")

        self.geometry("400x200")
        self.configure(fg_color="#F5F0F6")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Create form
        self.create_form()

    def create_form(self):
        """Create the form"""
        frame = ctk.CTkFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Name
        ctk.CTkLabel(
            frame,
            text=f"{self.singular} Name *",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.entry_name = ctk.CTkEntry(frame, placeholder_text=f"e.g., {self.get_example()}")
        self.entry_name.pack(fill="x", pady=(0, 20))

        # Pre-fill if editing
        if self.item:
            self.entry_name.insert(0, self.item['name'])

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x")

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def get_example(self) -> str:
        """Get example text based on type"""
        examples = {
            'event_types': 'Pokemon TCG',
            'playing_formats': 'Limited',
            'pairing_methods': 'Double Elimination',
            'pairing_apps': 'BattleScribe'
        }
        return examples.get(self.table_name, 'New Item')

    def save(self):
        """Save the item"""
        name = self.entry_name.get().strip()

        if not name:
            messagebox.showerror("Validation Error", f"{self.singular} name is required")
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            if self.item:
                # Update existing
                cursor.execute(f'UPDATE {self.table_name} SET name = ? WHERE id = ?', (name, self.item['id']))
                messagebox.showinfo("Success", f"{self.singular} updated successfully!")
            else:
                # Check for duplicates
                cursor.execute(f'SELECT COUNT(*) as count FROM {self.table_name} WHERE name = ?', (name,))
                if cursor.fetchone()['count'] > 0:
                    messagebox.showerror("Error", f"'{name}' already exists!")
                    conn.close()
                    return

                # Insert new
                cursor.execute(f'INSERT INTO {self.table_name} (name) VALUES (?)', (name,))
                messagebox.showinfo("Success", f"{self.singular} added successfully!")

            conn.commit()
            conn.close()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
