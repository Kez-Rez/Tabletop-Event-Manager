"""Selectable text widgets for displaying copyable text"""
import customtkinter as ctk
import tkinter as tk


class SelectableLabel(ctk.CTkTextbox):
    """A label-like widget that allows text selection and copying"""

    def __init__(self, master, text="", **kwargs):
        # Extract label-specific kwargs that don't apply to textbox
        wraplength = kwargs.pop('wraplength', None)
        justify = kwargs.pop('justify', 'left')
        anchor = kwargs.pop('anchor', None)

        # Set default textbox styling to look like a label
        kwargs.setdefault('fg_color', 'transparent')
        kwargs.setdefault('border_width', 0)
        kwargs.setdefault('activate_scrollbars', False)

        super().__init__(master, **kwargs)

        # Insert text
        self.insert("1.0", text)

        # Make it look read-only by preventing modifications
        # but still allow selection and copying
        self._readonly = True
        self.bind("<Key>", lambda e: "break" if self._readonly and e.keysym not in ['c', 'C', 'a', 'A'] or (e.state & 0x4) == 0 else None)
        self.bind("<Button-3>", self._show_context_menu)  # Right-click menu

    def _show_context_menu(self, event):
        """Show context menu for copy operation"""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Copy", command=self._copy_text)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _copy_text(self):
        """Copy selected text to clipboard"""
        try:
            selected_text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            # No selection, copy all
            text = self.get("1.0", "end-1c")
            self.clipboard_clear()
            self.clipboard_append(text)


class SelectableEntry(ctk.CTkEntry):
    """A single-line entry widget that's readonly but allows copying"""

    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)

        if text:
            self.insert(0, text)

        # Make readonly
        self.configure(state="readonly")
