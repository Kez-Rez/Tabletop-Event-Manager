"""Navigation manager for in-window view transitions"""
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any


class NavigationManager:
    """Manages navigation between views in the main window"""

    def __init__(self, main_frame: ctk.CTkFrame):
        """
        Initialize navigation manager

        Args:
            main_frame: The main content frame where views will be displayed
        """
        self.main_frame = main_frame
        self.view_stack = []  # Stack of (view_widget, view_name, context) tuples
        self.current_view = None

    def navigate_to(self, view_class, view_name: str = None, context: Dict[str, Any] = None,
                   replace: bool = False):
        """
        Navigate to a new view

        Args:
            view_class: The view class to instantiate (should accept parent, navigation_manager, context)
            view_name: Optional name for the view
            context: Optional context data to pass to the view
            replace: If True, replace current view instead of pushing to stack
        """
        # Hide current view if exists
        if self.current_view:
            self.current_view.pack_forget()

            # Only destroy if replacing
            if replace and self.view_stack:
                old_view = self.view_stack.pop()[0]
                old_view.destroy()

        # Create new view
        context = context or {}
        new_view = view_class(
            parent=self.main_frame,
            navigation_manager=self,
            context=context
        )

        # Store in stack
        self.view_stack.append((new_view, view_name or view_class.__name__, context))

        # Display new view
        new_view.pack(fill="both", expand=True)
        self.current_view = new_view

    def go_back(self, levels: int = 1):
        """
        Go back to previous view(s)

        Args:
            levels: Number of levels to go back (default 1)
        """
        if len(self.view_stack) <= 1:
            # Can't go back further
            return

        # Remove current view
        if self.current_view:
            self.current_view.pack_forget()
            self.current_view.destroy()
            self.view_stack.pop()
            self.current_view = None

        # Remove additional levels if specified
        for _ in range(levels - 1):
            if len(self.view_stack) > 1:
                view, _, _ = self.view_stack.pop()
                view.pack_forget()
                view.destroy()

        # Restore previous view (don't recreate, just show it)
        if self.view_stack:
            prev_view = self.view_stack[-1][0]  # Get the view from tuple

            # If the view has a refresh method, call it
            if hasattr(prev_view, 'refresh'):
                prev_view.refresh()

            # Show the previous view
            prev_view.pack(fill="both", expand=True)
            self.current_view = prev_view

    def can_go_back(self) -> bool:
        """Check if we can navigate back"""
        return len(self.view_stack) > 1

    def clear_stack(self):
        """Clear the entire navigation stack"""
        while len(self.view_stack) > 1:
            view, _, _ = self.view_stack.pop()
            if view != self.current_view:
                view.pack_forget()
                view.destroy()


class NavigableView(ctk.CTkFrame):
    """Base class for views that support navigation"""

    def __init__(self, parent, navigation_manager: NavigationManager, context: Dict[str, Any] = None):
        """
        Initialize navigable view

        Args:
            parent: Parent widget
            navigation_manager: NavigationManager instance
            context: Optional context data passed from previous view
        """
        super().__init__(parent, fg_color="#F5F0F6")
        self.navigation_manager = navigation_manager
        self.context = context or {}

    def create_header_with_back(self, title: str, show_back: bool = True) -> ctk.CTkFrame:
        """
        Create a standard header with back button

        Args:
            title: Title text to display
            show_back: Whether to show the back button

        Returns:
            The header frame for additional customization
        """
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Back button
        if show_back and self.navigation_manager.can_go_back():
            btn_back = ctk.CTkButton(
                header_frame,
                text="← Back",
                command=self.navigation_manager.go_back,
                fg_color="#C5A8D9",
                hover_color="#B491CC",
                text_color="#4A2D5E",
                width=100,
                height=35
            )
            btn_back.pack(side="left", padx=(0, 20))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title_label.pack(side="left")

        return header_frame
