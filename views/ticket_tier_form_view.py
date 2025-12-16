"""Ticket tier creation/editing form as an in-window view"""
import customtkinter as ctk
from tkinter import messagebox
from utils.navigation import NavigableView


class TicketTierFormView(NavigableView):
    """Form view for creating or editing ticket tiers"""

    def __init__(self, parent, navigation_manager, context=None):
        super().__init__(parent, navigation_manager, context)

        self.db = context.get('db')
        self.event_manager = context.get('event_manager')
        self.event_id = context.get('event_id')
        self.tier_data = context.get('tier_data')  # None for new tier

        self.create_ui()

    def create_ui(self):
        """Create the form UI"""
        # Header with back button
        title = "Edit Ticket Tier" if self.tier_data else "New Ticket Tier"
        self.create_header_with_back(title)

        # Main content
        content_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        form_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Tier Name
        ctk.CTkLabel(
            form_container,
            text="Tier Name *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="e.g., Standard, VIP, Early Bird",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.name_entry.pack(fill="x", pady=(0, 20))

        # Price
        ctk.CTkLabel(
            form_container,
            text="Price *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.price_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="e.g., 25.00",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.price_entry.pack(fill="x", pady=(0, 20))

        # Quantity Available
        ctk.CTkLabel(
            form_container,
            text="Quantity Available *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.quantity_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="e.g., 50",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.quantity_entry.pack(fill="x", pady=(0, 30))

        # Populate if editing
        if self.tier_data:
            self.populate_form()

        # Action Buttons
        button_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # Save Button
        btn_save = ctk.CTkButton(
            button_frame,
            text="Save Tier",
            command=self.save_tier,
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        btn_save.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Cancel Button
        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.navigation_manager.go_back,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        btn_cancel.pack(side="left", fill="x", expand=True, padx=(10, 0))

    def populate_form(self):
        """Populate form with existing tier data"""
        if not self.tier_data:
            return

        self.name_entry.insert(0, self.tier_data.get('tier_name', ''))
        self.price_entry.insert(0, str(self.tier_data.get('price', '')))
        self.quantity_entry.insert(0, str(self.tier_data.get('quantity_available', '')))

    def save_tier(self):
        """Validate and save the ticket tier"""
        # Get form data
        tier_name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        # Validation
        if not tier_name:
            messagebox.showerror("Validation Error", "Tier name is required", parent=self)
            return

        if not price:
            messagebox.showerror("Validation Error", "Price is required", parent=self)
            return

        if not quantity:
            messagebox.showerror("Validation Error", "Quantity available is required", parent=self)
            return

        try:
            price_float = float(price)
            quantity_int = int(quantity)

            if price_float < 0:
                messagebox.showerror("Validation Error", "Price must be positive", parent=self)
                return

            if quantity_int < 0:
                messagebox.showerror("Validation Error", "Quantity must be positive", parent=self)
                return

        except ValueError:
            messagebox.showerror("Validation Error", "Invalid price or quantity format", parent=self)
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            if self.tier_data:
                # Update existing
                cursor.execute('''
                    UPDATE ticket_tiers
                    SET tier_name = ?, price = ?, quantity_available = ?
                    WHERE id = ?
                ''', (tier_name, price_float, quantity_int, self.tier_data['id']))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO ticket_tiers (event_id, tier_name, price, quantity_available)
                    VALUES (?, ?, ?, ?)
                ''', (self.event_id, tier_name, price_float, quantity_int))

            conn.commit()
            conn.close()

            # Go back
            self.navigation_manager.go_back()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tier: {str(e)}", parent=self)
