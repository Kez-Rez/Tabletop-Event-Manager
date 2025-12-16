"""Enhanced Help and FAQ view with Word-like rich text editing"""
import customtkinter as ctk
from tkinter import messagebox, font as tkfont
from datetime import datetime
import webbrowser
import tempfile
import os
import re
import html

class SaveDialog(ctk.CTkToplevel):
    """Custom dialog for saving with initials and change notes"""

    def __init__(self, parent, title="Save Changes"):
        super().__init__(parent)

        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")

        self.initials = None
        self.change_notes = None

        # Create UI
        self.create_ui()

    def create_ui(self):
        """Create dialog UI"""
        # Main frame
        main = ctk.CTkFrame(self, fg_color="white")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Initials field
        ctk.CTkLabel(
            main,
            text="Your Initials:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 5))

        self.initials_entry = ctk.CTkEntry(main, width=360, placeholder_text="e.g., JD")
        self.initials_entry.pack(pady=(0, 15))
        self.initials_entry.focus()

        # Change notes field
        ctk.CTkLabel(
            main,
            text="What changed? (optional):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 5))

        self.notes_entry = ctk.CTkEntry(main, width=360, placeholder_text="Brief description of changes")
        self.notes_entry.pack(pady=(0, 15))

        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(pady=(10, 0))

        ctk.CTkButton(
            btn_frame,
            text="Save",
            width=100,
            fg_color="#8B5FBF",
            hover_color="#7A4FAF",
            command=self.on_save
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            command=self.on_cancel
        ).pack(side="left", padx=5)

        # Bind Enter key
        self.bind("<Return>", lambda e: self.on_save())
        self.bind("<Escape>", lambda e: self.on_cancel())

    def on_save(self):
        """Handle save button"""
        initials = self.initials_entry.get().strip()
        if not initials:
            messagebox.showwarning("Required", "Please enter your initials", parent=self)
            return

        self.initials = initials
        self.change_notes = self.notes_entry.get().strip()
        self.destroy()

    def on_cancel(self):
        """Handle cancel button"""
        self.destroy()


class RichTextEditor(ctk.CTkFrame):
    """Rich text editor that works like Microsoft Word"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color="white")

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="#E6D9F2", height=40)
        toolbar.pack(fill="x", padx=2, pady=2)

        # Format buttons
        self.btn_bold = ctk.CTkButton(
            toolbar, text="B", width=40,
            command=self.toggle_bold,
            font=ctk.CTkFont(weight="bold"),
            fg_color="#C5A8D9"
        )
        self.btn_bold.pack(side="left", padx=2, pady=5)

        self.btn_italic = ctk.CTkButton(
            toolbar, text="I", width=40,
            command=self.toggle_italic,
            font=ctk.CTkFont(slant="italic"),
            fg_color="#C5A8D9"
        )
        self.btn_italic.pack(side="left", padx=2, pady=5)

        ctk.CTkButton(
            toolbar, text="H1", width=50,
            command=self.format_heading1,
            fg_color="#8B5FBF"
        ).pack(side="left", padx=2, pady=5)

        ctk.CTkButton(
            toolbar, text="H2", width=50,
            command=self.format_heading2,
            fg_color="#8B5FBF"
        ).pack(side="left", padx=2, pady=5)

        ctk.CTkButton(
            toolbar, text="H3", width=50,
            command=self.format_heading3,
            fg_color="#8B5FBF"
        ).pack(side="left", padx=2, pady=5)

        ctk.CTkButton(
            toolbar, text="Normal", width=60,
            command=self.format_normal,
            fg_color="#C5A8D9"
        ).pack(side="left", padx=2, pady=5)

        ctk.CTkButton(
            toolbar, text="• Bullet", width=70,
            command=self.insert_bullet,
            fg_color="#C5A8D9"
        ).pack(side="left", padx=2, pady=5)

        ctk.CTkButton(
            toolbar, text="☑ Checkbox", width=80,
            command=self.insert_checkbox,
            fg_color="#C5A8D9"
        ).pack(side="left", padx=2, pady=5)

        ctk.CTkButton(
            toolbar, text="1. Number", width=80,
            command=self.insert_numbered,
            fg_color="#C5A8D9"
        ).pack(side="left", padx=2, pady=5)

        # Text area with custom font
        self.text_area = ctk.CTkTextbox(self, font=ctk.CTkFont(size=15), wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=2, pady=2)

        # Configure text tags for formatting
        self.configure_tags()

        # Bind key events for auto-bullets and indentation
        text_widget = self.text_area._textbox
        text_widget.bind("<Return>", self.on_return_key)
        text_widget.bind("<Tab>", self.on_tab_key)
        text_widget.bind("<Shift-Tab>", self.on_shift_tab_key)

    def configure_tags(self):
        """Configure text tags for visual formatting"""
        # Get the underlying Text widget
        text_widget = self.text_area._textbox

        # Bold tag
        bold_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        text_widget.tag_configure("bold", font=bold_font)

        # Italic tag
        italic_font = tkfont.Font(family="Segoe UI", size=12, slant="italic")
        text_widget.tag_configure("italic", font=italic_font)

        # Bold + Italic tag
        bold_italic_font = tkfont.Font(family="Segoe UI", size=12, weight="bold", slant="italic")
        text_widget.tag_configure("bold_italic", font=bold_italic_font)

        # Heading 1
        h1_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        text_widget.tag_configure("h1", font=h1_font, foreground="#8B5FBF", spacing1=10, spacing3=10)

        # Heading 2
        h2_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        text_widget.tag_configure("h2", font=h2_font, foreground="#8B5FBF", spacing1=8, spacing3=8)

        # Heading 3
        h3_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        text_widget.tag_configure("h3", font=h3_font, foreground="#4A2D5E", spacing1=6, spacing3=6)

        # List items with different indentation levels
        text_widget.tag_configure("list_item_0", lmargin1=20, lmargin2=40)
        text_widget.tag_configure("list_item_1", lmargin1=60, lmargin2=80)
        text_widget.tag_configure("list_item_2", lmargin1=100, lmargin2=120)

    def on_return_key(self, event):
        """Handle Enter key - auto-continue bullets/checkboxes"""
        text_widget = self.text_area._textbox

        # Get current line
        current = text_widget.index("insert")
        line_start = text_widget.index(f"{current} linestart")
        line_end = text_widget.index(f"{current} lineend")
        line_text = text_widget.get(line_start, line_end)

        # Check if current line is a bullet or checkbox
        stripped = line_text.lstrip()
        indent = len(line_text) - len(stripped)

        # Check for empty bullet/checkbox - remove it and return to normal
        if stripped in ['• ', '☐ ', '☑ '] or (len(stripped) > 2 and stripped[:2] in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.'] and stripped[2:].strip() == ''):
            # Delete the bullet/checkbox and don't continue
            text_widget.delete(line_start, line_end)
            return None  # Allow normal newline

        # Continue bullet
        if stripped.startswith('• '):
            text_widget.insert("insert", '\n' + ' ' * indent + '• ')
            return "break"  # Prevent default newline

        # Continue checkbox
        if stripped.startswith('☐ ') or stripped.startswith('☑ '):
            text_widget.insert("insert", '\n' + ' ' * indent + '☐ ')
            return "break"

        # Continue numbered list
        match = re.match(r'(\d+)\.\s', stripped)
        if match:
            next_num = int(match.group(1)) + 1
            text_widget.insert("insert", f'\n{" " * indent}{next_num}. ')
            return "break"

        return None  # Allow normal newline

    def on_tab_key(self, event):
        """Handle Tab key - indent bullet/checkbox"""
        text_widget = self.text_area._textbox

        # Get current line
        current = text_widget.index("insert")
        line_start = text_widget.index(f"{current} linestart")
        line_end = text_widget.index(f"{current} lineend")
        line_text = text_widget.get(line_start, line_end)

        stripped = line_text.lstrip()

        # Only indent if it's a bullet, checkbox, or number
        if stripped.startswith('• ') or stripped.startswith('☐ ') or stripped.startswith('☑ ') or re.match(r'\d+\.\s', stripped):
            # Add 4 spaces at start of line
            text_widget.insert(line_start, '    ')
            return "break"  # Prevent default tab

        return None

    def on_shift_tab_key(self, event):
        """Handle Shift+Tab - unindent bullet/checkbox"""
        text_widget = self.text_area._textbox

        # Get current line
        current = text_widget.index("insert")
        line_start = text_widget.index(f"{current} linestart")
        line_end = text_widget.index(f"{current} lineend")
        line_text = text_widget.get(line_start, line_end)

        # Check if line starts with spaces
        if line_text.startswith('    '):
            # Remove 4 spaces
            text_widget.delete(line_start, f"{line_start} + 4c")
            return "break"
        elif line_text.startswith('  '):
            # Remove 2 spaces if only 2
            text_widget.delete(line_start, f"{line_start} + 2c")
            return "break"

        return None

    def toggle_bold(self):
        """Toggle bold formatting for selected text"""
        try:
            text_widget = self.text_area._textbox
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")

            # Check current tags
            current_tags = text_widget.tag_names(start)

            # Remove all paragraph-level tags first
            for tag in ["h1", "h2", "h3"]:
                if tag in current_tags:
                    return  # Don't allow bold on headings

            if "bold" in current_tags or "bold_italic" in current_tags:
                # Remove bold
                if "bold_italic" in current_tags:
                    text_widget.tag_remove("bold_italic", start, end)
                    text_widget.tag_add("italic", start, end)
                else:
                    text_widget.tag_remove("bold", start, end)
            else:
                # Add bold
                if "italic" in current_tags:
                    text_widget.tag_remove("italic", start, end)
                    text_widget.tag_add("bold_italic", start, end)
                else:
                    text_widget.tag_add("bold", start, end)
        except:
            pass

    def toggle_italic(self):
        """Toggle italic formatting for selected text"""
        try:
            text_widget = self.text_area._textbox
            start = text_widget.index("sel.first")
            end = text_widget.index("sel.last")

            # Check current tags
            current_tags = text_widget.tag_names(start)

            # Remove all paragraph-level tags first
            for tag in ["h1", "h2", "h3"]:
                if tag in current_tags:
                    return  # Don't allow italic on headings

            if "italic" in current_tags or "bold_italic" in current_tags:
                # Remove italic
                if "bold_italic" in current_tags:
                    text_widget.tag_remove("bold_italic", start, end)
                    text_widget.tag_add("bold", start, end)
                else:
                    text_widget.tag_remove("italic", start, end)
            else:
                # Add italic
                if "bold" in current_tags:
                    text_widget.tag_remove("bold", start, end)
                    text_widget.tag_add("bold_italic", start, end)
                else:
                    text_widget.tag_add("italic", start, end)
        except:
            pass

    def format_heading1(self):
        """Format current line as Heading 1"""
        self._format_line_as("h1")

    def format_heading2(self):
        """Format current line as Heading 2"""
        self._format_line_as("h2")

    def format_heading3(self):
        """Format current line as Heading 3"""
        self._format_line_as("h3")

    def format_normal(self):
        """Remove all formatting from current line"""
        self._format_line_as(None)

    def _format_line_as(self, tag_name):
        """Format the current line with a specific tag"""
        text_widget = self.text_area._textbox

        # Get current line start and end
        current = text_widget.index("insert")
        line_start = text_widget.index(f"{current} linestart")
        line_end = text_widget.index(f"{current} lineend")

        # Remove all formatting tags from the line
        for tag in ["bold", "italic", "bold_italic", "h1", "h2", "h3"]:
            text_widget.tag_remove(tag, line_start, line_end)

        # Apply new tag if specified
        if tag_name:
            text_widget.tag_add(tag_name, line_start, line_end)

    def insert_bullet(self):
        """Insert a bullet point"""
        text_widget = self.text_area._textbox

        # Check if we're at the start of a line
        current = text_widget.index("insert")
        line_start = text_widget.index(f"{current} linestart")

        if current == line_start or text_widget.get(line_start, current).strip() == '':
            # At start of line - just insert bullet
            text_widget.delete(line_start, current)
            text_widget.insert(line_start, "• ")
        else:
            # In middle of line - insert on new line
            text_widget.insert("insert", "\n• ")

    def insert_checkbox(self):
        """Insert a checkbox"""
        text_widget = self.text_area._textbox

        # Check if we're at the start of a line
        current = text_widget.index("insert")
        line_start = text_widget.index(f"{current} linestart")

        if current == line_start or text_widget.get(line_start, current).strip() == '':
            # At start of line - just insert checkbox
            text_widget.delete(line_start, current)
            text_widget.insert(line_start, "☐ ")
        else:
            # In middle of line - insert on new line
            text_widget.insert("insert", "\n☐ ")

    def insert_numbered(self):
        """Insert a numbered list item"""
        text_widget = self.text_area._textbox

        # Check if we're at the start of a line
        current = text_widget.index("insert")
        line_start = text_widget.index(f"{current} linestart")

        if current == line_start or text_widget.get(line_start, current).strip() == '':
            # At start of line - just insert number
            text_widget.delete(line_start, current)
            text_widget.insert(line_start, "1. ")
        else:
            # In middle of line - insert on new line
            text_widget.insert("insert", "\n1. ")

    def get_content(self):
        """Get content as HTML for storage"""
        text_widget = self.text_area._textbox
        content = text_widget.get("1.0", "end-1c")

        # Build HTML from text and tags
        html_parts = []
        lines = content.split('\n')

        in_ul = False
        in_ol = False
        in_checklist = False
        current_indent = 0

        for line in lines:
            if not line.strip():
                # Close any open lists
                if in_ul:
                    html_parts.append("</ul>")
                    in_ul = False
                if in_ol:
                    html_parts.append("</ol>")
                    in_ol = False
                if in_checklist:
                    html_parts.append("</ul>")
                    in_checklist = False
                html_parts.append("<p></p>")
                continue

            # Find line position in text widget
            line_index = content.find(line)
            if line_index == -1:
                continue

            # Get character position
            char_count = content[:line_index].count('\n')
            line_start = f"{char_count + 1}.0"
            line_end = f"{char_count + 1}.end"

            # Check tags at line start
            tags = text_widget.tag_names(line_start)

            # Calculate indentation
            stripped = line.lstrip()
            indent_level = (len(line) - len(stripped)) // 4  # 4 spaces per indent

            # Check list type
            is_bullet = stripped.startswith('• ')
            is_checkbox = stripped.startswith('☐ ') or stripped.startswith('☑ ')
            is_checked = stripped.startswith('☑ ')
            is_numbered = len(stripped) > 2 and stripped[0].isdigit() and stripped[1:3] in ['. ', ') ']

            if is_checkbox:
                if not in_checklist:
                    if in_ul:
                        html_parts.append("</ul>")
                        in_ul = False
                    if in_ol:
                        html_parts.append("</ol>")
                        in_ol = False
                    html_parts.append('<ul class="checklist">')
                    in_checklist = True
                    current_indent = indent_level

                # Handle indent changes
                if indent_level > current_indent:
                    html_parts.append('<ul class="checklist">')
                elif indent_level < current_indent:
                    for _ in range(current_indent - indent_level):
                        html_parts.append("</ul>")
                current_indent = indent_level

                item_text = stripped[2:].strip()  # Remove checkbox and space
                checkbox_style = 'checked' if is_checked else 'unchecked'
                html_parts.append(f'<li class="{checkbox_style}">{html.escape(item_text)}</li>')

            elif is_bullet:
                if not in_ul:
                    if in_checklist:
                        html_parts.append("</ul>")
                        in_checklist = False
                    if in_ol:
                        html_parts.append("</ol>")
                        in_ol = False
                    html_parts.append("<ul>")
                    in_ul = True
                    current_indent = indent_level

                # Handle indent changes
                if indent_level > current_indent:
                    html_parts.append("<ul>")
                elif indent_level < current_indent:
                    for _ in range(current_indent - indent_level):
                        html_parts.append("</ul>")
                current_indent = indent_level

                item_text = stripped[2:]  # Remove bullet and space
                html_parts.append(f"<li>{html.escape(item_text)}</li>")

            elif is_numbered:
                if not in_ol:
                    if in_ul:
                        html_parts.append("</ul>")
                        in_ul = False
                    if in_checklist:
                        html_parts.append("</ul>")
                        in_checklist = False
                    html_parts.append("<ol>")
                    in_ol = True
                    current_indent = indent_level

                # Handle indent changes
                if indent_level > current_indent:
                    html_parts.append("<ol>")
                elif indent_level < current_indent:
                    for _ in range(current_indent - indent_level):
                        html_parts.append("</ol>")
                current_indent = indent_level

                # Find where the actual text starts after number
                match = re.match(r'\d+[\.\)]\s*', stripped)
                if match:
                    item_text = stripped[match.end():]
                    html_parts.append(f"<li>{html.escape(item_text)}</li>")
            else:
                # Close any open lists
                if in_ul:
                    html_parts.append("</ul>")
                    in_ul = False
                if in_ol:
                    html_parts.append("</ol>")
                    in_ol = False
                if in_checklist:
                    html_parts.append("</ul>")
                    in_checklist = False
                current_indent = 0

                # Regular paragraph or heading
                if "h1" in tags:
                    html_parts.append(f"<h1>{html.escape(line)}</h1>")
                elif "h2" in tags:
                    html_parts.append(f"<h2>{html.escape(line)}</h2>")
                elif "h3" in tags:
                    html_parts.append(f"<h3>{html.escape(line)}</h3>")
                else:
                    html_parts.append(f"<p>{html.escape(line)}</p>")

        # Close any remaining open lists
        if in_ul:
            html_parts.append("</ul>")
        if in_ol:
            html_parts.append("</ol>")
        if in_checklist:
            html_parts.append("</ul>")

        return '\n'.join(html_parts)

    def set_content(self, html_content):
        """Set content from HTML"""
        text_widget = self.text_area._textbox
        text_widget.delete("1.0", "end")

        if not html_content:
            return

        # Parse HTML and insert with formatting
        self._parse_and_insert_html(html_content)

    def _parse_and_insert_html(self, html_content):
        """Parse HTML and insert with appropriate formatting tags"""
        text_widget = self.text_area._textbox

        # Simple HTML parser
        lines = html_content.split('\n')
        indent_level = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Heading 1
            if line.startswith('<h1>') and line.endswith('</h1>'):
                content = line[4:-5]
                content = html.unescape(content)
                start = text_widget.index("insert")
                text_widget.insert("insert", content + '\n')
                end = text_widget.index("insert - 1c")
                text_widget.tag_add("h1", start, end)

            # Heading 2
            elif line.startswith('<h2>') and line.endswith('</h2>'):
                content = line[4:-5]
                content = html.unescape(content)
                start = text_widget.index("insert")
                text_widget.insert("insert", content + '\n')
                end = text_widget.index("insert - 1c")
                text_widget.tag_add("h2", start, end)

            # Heading 3
            elif line.startswith('<h3>') and line.endswith('</h3>'):
                content = line[4:-5]
                content = html.unescape(content)
                start = text_widget.index("insert")
                text_widget.insert("insert", content + '\n')
                end = text_widget.index("insert - 1c")
                text_widget.tag_add("h3", start, end)

            # Unordered list start
            elif line.startswith('<ul'):
                if 'checklist' not in line:
                    indent_level += 1
                continue
            elif line.startswith('</ul>'):
                indent_level = max(0, indent_level - 1)
                continue

            # List item
            elif line.startswith('<li'):
                indent = '    ' * (indent_level - 1) if indent_level > 0 else ''

                # Check if it's a checklist item
                if 'class="checked"' in line or 'class="unchecked"' in line:
                    checkbox = '☑' if 'checked' in line else '☐'
                    # Extract content
                    match = re.search(r'>(.*?)</li>', line)
                    if match:
                        content = html.unescape(match.group(1))
                        text_widget.insert("insert", f"{indent}{checkbox} {content}\n")
                else:
                    # Regular bullet
                    content = re.search(r'<li.*?>(.*?)</li>', line)
                    if content:
                        text = html.unescape(content.group(1))
                        text_widget.insert("insert", f"{indent}• {text}\n")

            # Ordered list
            elif line.startswith('<ol>'):
                indent_level += 1
                self._ol_counter = 1
                continue
            elif line.startswith('</ol>'):
                indent_level = max(0, indent_level - 1)
                continue

            # Paragraph
            elif line.startswith('<p>') and line.endswith('</p>'):
                content = line[3:-4]
                if not content or content == '':
                    text_widget.insert("insert", '\n')
                else:
                    content = html.unescape(content)
                    content = re.sub(r'<[^>]+>', '', content)
                    text_widget.insert("insert", content + '\n')


class HelpView(ctk.CTkFrame):
    """Enhanced Help view with editable content and event type guides"""

    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.configure(fg_color="#F5F0F6")

        # Create header
        self.create_header()

        # Create tabbed content
        self.create_content()

    def create_header(self):
        """Create the header section"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text="Help & Documentation",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(side="left")

    def create_content(self):
        """Create tabbed content area"""
        # Tab view
        self.tabview = ctk.CTkTabview(self, fg_color="white", segmented_button_fg_color="#E6D9F2",
                                      segmented_button_selected_color="#C5A8D9",
                                      segmented_button_unselected_color="#F5F0F6")
        self.tabview.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Add tabs
        self.tab_help = self.tabview.add("Help & FAQ")
        self.tab_guides = self.tabview.add("Event Type Guides")

        # Populate tabs
        self.create_help_tab()
        self.create_guides_tab()

    def create_help_tab(self):
        """Create the help/FAQ tab with editable sections"""
        # Get help sections from database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM help_content ORDER BY sort_order')
        sections = cursor.fetchall()
        conn.close()

        if not sections:
            ctk.CTkLabel(
                self.tab_help,
                text="No help content available",
                font=ctk.CTkFont(size=15),
                text_color="#999999"
            ).pack(pady=40)
            return

        # Scrollable frame for all help sections
        scroll = ctk.CTkScrollableFrame(self.tab_help, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        for section in sections:
            self.create_help_section(scroll, dict(section))

    def create_help_section(self, parent, section):
        """Create a single editable help section"""
        section_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=1, border_color="#E6D9F2")
        section_frame.pack(fill="x", pady=10, padx=5)

        # Header with title and edit button
        header = ctk.CTkFrame(section_frame, fg_color="#F5F0F6", corner_radius=8)
        header.pack(fill="x", padx=10, pady=10)

        title = ctk.CTkLabel(
            header,
            text=section['title'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(side="left", padx=10, pady=10)

        # Edit/View mode toggle
        edit_btn = ctk.CTkButton(
            header,
            text="Edit",
            width=80,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            command=lambda: self.toggle_edit_mode(section_frame, section)
        )
        edit_btn.pack(side="right", padx=10, pady=5)

        # Content area (view mode by default)
        content_frame = ctk.CTkFrame(section_frame, fg_color="white")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Display content (parsed HTML)
        self.display_html_content(content_frame, section['content'])

        # Store references
        section_frame._edit_btn = edit_btn
        section_frame._content_frame = content_frame
        section_frame._section_data = section
        section_frame._is_editing = False

    def toggle_edit_mode(self, section_frame, section):
        """Toggle between edit and view mode"""
        if section_frame._is_editing:
            # Save and switch to view mode
            self.save_help_section(section_frame, section)
        else:
            # Switch to edit mode
            self.enter_edit_mode(section_frame, section)

    def enter_edit_mode(self, section_frame, section):
        """Enter edit mode for a help section"""
        # Clear content frame
        for widget in section_frame._content_frame.winfo_children():
            widget.destroy()

        # Create rich text editor
        editor = RichTextEditor(section_frame._content_frame, fg_color="white")
        editor.pack(fill="both", expand=True, pady=10)
        editor.set_content(section['content'])

        # Update button text
        section_frame._edit_btn.configure(text="Save")
        section_frame._is_editing = True
        section_frame._editor = editor

    def save_help_section(self, section_frame, section):
        """Save help section and return to view mode"""
        # Get content from editor
        new_content = section_frame._editor.get_content()

        # Show save dialog
        dialog = SaveDialog(self)
        self.wait_window(dialog)

        if not dialog.initials:
            return  # User cancelled

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Update help content
        new_version = section['current_version'] + 1
        cursor.execute('''
            UPDATE help_content
            SET content = ?, current_version = ?, last_modified = ?, modified_by = ?
            WHERE id = ?
        ''', (new_content, new_version, datetime.now(), dialog.initials, section['id']))

        # Save revision
        cursor.execute('''
            INSERT INTO help_revisions (help_content_id, version_number, content, change_notes, modified_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (section['id'], new_version, new_content, dialog.change_notes or '', dialog.initials))

        conn.commit()
        conn.close()

        # Update section data
        section['content'] = new_content
        section['current_version'] = new_version

        # Clear and show in view mode
        for widget in section_frame._content_frame.winfo_children():
            widget.destroy()

        self.display_html_content(section_frame._content_frame, new_content)

        # Update button
        section_frame._edit_btn.configure(text="Edit")
        section_frame._is_editing = False

        messagebox.showinfo("Success", f"Help section saved!\nVersion: {new_version}")

    def display_html_content(self, parent, html_content):
        """Display HTML content in a formatted way"""
        # Simple HTML renderer using CTkTextbox with tags
        text_display = ctk.CTkTextbox(parent, font=ctk.CTkFont(size=15), wrap="word")
        text_display.pack(fill="both", expand=True, pady=5)

        # Configure tags
        text_widget = text_display._textbox
        text_widget.tag_configure("h1", font=tkfont.Font(family="Segoe UI", size=20, weight="bold"),
                                 foreground="#8B5FBF", spacing1=10, spacing3=10)
        text_widget.tag_configure("h2", font=tkfont.Font(family="Segoe UI", size=16, weight="bold"),
                                 foreground="#8B5FBF", spacing1=8, spacing3=8)
        text_widget.tag_configure("h3", font=tkfont.Font(family="Segoe UI", size=14, weight="bold"),
                                 foreground="#4A2D5E", spacing1=6, spacing3=6)
        text_widget.tag_configure("bold", font=tkfont.Font(family="Segoe UI", size=12, weight="bold"))
        text_widget.tag_configure("italic", font=tkfont.Font(family="Segoe UI", size=12, slant="italic"))

        # Parse and display HTML
        self._render_html_simple(text_widget, html_content)

        # Make read-only
        text_display.configure(state="disabled")

    def _render_html_simple(self, text_widget, html_content):
        """Simple HTML renderer"""
        lines = html_content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('<h1>') and line.endswith('</h1>'):
                content = html.unescape(line[4:-5])
                start = text_widget.index("insert")
                text_widget.insert("insert", content + '\n')
                end = text_widget.index("insert - 1c")
                text_widget.tag_add("h1", start, end)

            elif line.startswith('<h2>') and line.endswith('</h2>'):
                content = html.unescape(line[4:-5])
                start = text_widget.index("insert")
                text_widget.insert("insert", content + '\n')
                end = text_widget.index("insert - 1c")
                text_widget.tag_add("h2", start, end)

            elif line.startswith('<h3>') and line.endswith('</h3>'):
                content = html.unescape(line[4:-5])
                start = text_widget.index("insert")
                text_widget.insert("insert", content + '\n')
                end = text_widget.index("insert - 1c")
                text_widget.tag_add("h3", start, end)

            elif line.startswith('<p>') and line.endswith('</p>'):
                content = line[3:-4]
                if content:
                    content = html.unescape(content)
                    content = re.sub(r'<[^>]+>', '', content)
                    text_widget.insert("insert", content + '\n')
                else:
                    text_widget.insert("insert", '\n')

            elif line.startswith('<li'):
                # Check if it's a checkbox
                if 'class="checked"' in line:
                    match = re.search(r'>(.*?)</li>', line)
                    if match:
                        content = html.unescape(match.group(1))
                        text_widget.insert("insert", f"  ☑ {content}\n")
                elif 'class="unchecked"' in line:
                    match = re.search(r'>(.*?)</li>', line)
                    if match:
                        content = html.unescape(match.group(1))
                        text_widget.insert("insert", f"  ☐ {content}\n")
                else:
                    # Regular bullet
                    content = re.search(r'<li.*?>(.*?)</li>', line)
                    if content:
                        text = html.unescape(content.group(1))
                        text_widget.insert("insert", f"  • {text}\n")

            elif line in ['<ul>', '</ul>', '<ol>', '</ol>', '<ul class="checklist">']:
                continue

    def create_guides_tab(self):
        """Create the event type guides tab"""
        # Top section with event type selector
        top_frame = ctk.CTkFrame(self.tab_guides, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            top_frame,
            text="Select Event Type:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left", padx=10)

        # Get event types
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM event_types ORDER BY name')
        event_types = cursor.fetchall()
        conn.close()

        if not event_types:
            ctk.CTkLabel(
                self.tab_guides,
                text="No event types available",
                font=ctk.CTkFont(size=15),
                text_color="#999999"
            ).pack(pady=40)
            return

        # Event type dropdown
        event_type_names = [et['name'] for et in event_types]
        self.event_type_var = ctk.StringVar(value=event_type_names[0])

        dropdown = ctk.CTkOptionMenu(
            top_frame,
            variable=self.event_type_var,
            values=event_type_names,
            command=self.load_event_guide,
            fg_color="#C5A8D9",
            button_color="#8B5FBF",
            button_hover_color="#7A4FAF"
        )
        dropdown.pack(side="left", padx=10)

        # Guide content area
        self.guide_content_frame = ctk.CTkFrame(self.tab_guides, fg_color="white", corner_radius=8)
        self.guide_content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Store event types
        self.event_types = {et['name']: et['id'] for et in event_types}

        # Load first guide
        self.load_event_guide(event_type_names[0])

    def load_event_guide(self, event_type_name):
        """Load guide for selected event type"""
        # Clear current content
        for widget in self.guide_content_frame.winfo_children():
            widget.destroy()

        event_type_id = self.event_types[event_type_name]

        # Get guide from database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM event_type_guides WHERE event_type_id = ?', (event_type_id,))
        guide = cursor.fetchone()
        conn.close()

        if not guide:
            # No guide exists - show create option
            self.show_create_guide_option(event_type_name, event_type_id)
        else:
            # Show existing guide
            self.show_guide(dict(guide))

    def show_create_guide_option(self, event_type_name, event_type_id):
        """Show option to create a new guide"""
        ctk.CTkLabel(
            self.guide_content_frame,
            text=f"No guide exists for {event_type_name}",
            font=ctk.CTkFont(size=15),
            text_color="#999999"
        ).pack(pady=20)

        ctk.CTkButton(
            self.guide_content_frame,
            text="Create Guide",
            fg_color="#8B5FBF",
            hover_color="#7A4FAF",
            command=lambda: self.create_new_guide(event_type_name, event_type_id)
        ).pack(pady=10)

    def create_new_guide(self, event_type_name, event_type_id):
        """Create a new event type guide"""
        # Insert empty guide
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO event_type_guides (event_type_id, title, content, modified_by)
            VALUES (?, ?, ?, ?)
        ''', (event_type_id, f"How to Run {event_type_name}", "<h1>Event Checklist</h1>\n<p>Add your checklist items here...</p>", "System"))
        conn.commit()

        # Get the newly created guide
        cursor.execute('SELECT * FROM event_type_guides WHERE event_type_id = ?', (event_type_id,))
        guide = cursor.fetchone()
        conn.close()

        # Clear and show guide in edit mode
        for widget in self.guide_content_frame.winfo_children():
            widget.destroy()

        self.show_guide(dict(guide), start_in_edit=True)

    def show_guide(self, guide, start_in_edit=False):
        """Show an existing guide"""
        # Header with title and buttons
        header = ctk.CTkFrame(self.guide_content_frame, fg_color="#F5F0F6", corner_radius=8)
        header.pack(fill="x", padx=10, pady=10)

        title = ctk.CTkLabel(
            header,
            text=guide['title'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(side="left", padx=10, pady=10)

        # Buttons frame
        buttons = ctk.CTkFrame(header, fg_color="transparent")
        buttons.pack(side="right", padx=10)

        print_btn = ctk.CTkButton(
            buttons,
            text="Print",
            width=80,
            fg_color="#D4A5D4",
            hover_color="#C494C4",
            command=lambda: self.print_guide(guide)
        )
        print_btn.pack(side="left", padx=5)

        edit_btn = ctk.CTkButton(
            buttons,
            text="Edit",
            width=80,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            command=lambda: self.toggle_guide_edit(guide)
        )
        edit_btn.pack(side="left", padx=5)

        # Content area
        content_frame = ctk.CTkFrame(self.guide_content_frame, fg_color="white")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Store references
        self.guide_content_frame._edit_btn = edit_btn
        self.guide_content_frame._content_frame = content_frame
        self.guide_content_frame._guide_data = guide
        self.guide_content_frame._is_editing = False

        if start_in_edit:
            self.enter_guide_edit_mode()
        else:
            self.display_html_content(content_frame, guide['content'])

    def toggle_guide_edit(self, guide):
        """Toggle edit mode for guide"""
        if self.guide_content_frame._is_editing:
            self.save_event_guide()
        else:
            self.enter_guide_edit_mode()

    def enter_guide_edit_mode(self):
        """Enter edit mode for guide"""
        # Clear content frame
        for widget in self.guide_content_frame._content_frame.winfo_children():
            widget.destroy()

        # Create editor
        editor = RichTextEditor(self.guide_content_frame._content_frame, fg_color="white")
        editor.pack(fill="both", expand=True, pady=10)
        editor.set_content(self.guide_content_frame._guide_data['content'])

        # Update button
        self.guide_content_frame._edit_btn.configure(text="Save")
        self.guide_content_frame._is_editing = True
        self.guide_content_frame._editor = editor

    def save_event_guide(self):
        """Save event guide changes"""
        # Get content
        new_content = self.guide_content_frame._editor.get_content()
        guide = self.guide_content_frame._guide_data

        # Show save dialog
        dialog = SaveDialog(self)
        self.wait_window(dialog)

        if not dialog.initials:
            return  # User cancelled

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        new_version = guide['current_version'] + 1
        cursor.execute('''
            UPDATE event_type_guides
            SET content = ?, current_version = ?, last_modified = ?, modified_by = ?
            WHERE id = ?
        ''', (new_content, new_version, datetime.now(), dialog.initials, guide['id']))

        # Save revision
        cursor.execute('''
            INSERT INTO guide_revisions (guide_id, version_number, content, change_notes, modified_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (guide['id'], new_version, new_content, dialog.change_notes or '', dialog.initials))

        conn.commit()
        conn.close()

        # Update guide data
        guide['content'] = new_content
        guide['current_version'] = new_version

        # Return to view mode
        for widget in self.guide_content_frame._content_frame.winfo_children():
            widget.destroy()

        self.display_html_content(self.guide_content_frame._content_frame, new_content)

        self.guide_content_frame._edit_btn.configure(text="Edit")
        self.guide_content_frame._is_editing = False

        messagebox.showinfo("Success", f"Guide saved!\nVersion: {new_version}")

    def print_guide(self, guide):
        """Print guide to HTML and open in browser"""
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{guide['title']}</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #8B5FBF; font-size: 24px; }}
                h2 {{ color: #8B5FBF; font-size: 20px; }}
                h3 {{ color: #4A2D5E; font-size: 16px; }}
                p {{ margin: 10px 0; }}
                ul, ol {{ margin: 10px 0; padding-left: 30px; }}
                li {{ margin: 5px 0; }}
                ul.checklist {{ list-style: none; }}
                ul.checklist li.checked::before {{ content: "☑ "; }}
                ul.checklist li.unchecked::before {{ content: "☐ "; }}
            </style>
        </head>
        <body>
            <h1>{guide['title']}</h1>
            {guide['content']}
            <hr>
            <p style="font-size: 12px; color: #999;">
                Version {guide['current_version']} |
                Last modified: {guide['last_modified']} by {guide['modified_by'] or 'Unknown'}
            </p>
        </body>
        </html>
        '''

        # Save to temp file and open
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name

        webbrowser.open('file://' + temp_path)
