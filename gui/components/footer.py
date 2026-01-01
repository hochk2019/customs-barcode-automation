"""
Footer Component v2.0

Extracted from customs_gui.py for GUI decomposition.
Creates the footer with designer info and contact.
"""

import tkinter as tk

from gui.branding import (
    DESIGNER_NAME, DESIGNER_EMAIL, DESIGNER_PHONE,
    BRAND_PRIMARY_COLOR, BRAND_ACCENT_COLOR
)


class Footer:
    """
    Footer component with designer credits.
    
    Displays:
    - Designer name (left)
    - Contact info (right)
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Create footer.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self._create_footer()
    
    def _create_footer(self) -> None:
        """Create the footer."""
        footer_frame = tk.Frame(self.parent, bg=BRAND_PRIMARY_COLOR, height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        # Footer content
        footer_content = tk.Frame(footer_frame, bg=BRAND_PRIMARY_COLOR)
        footer_content.pack(fill=tk.BOTH, expand=True, padx=15)
        
        # Left: Designer info
        tk.Label(
            footer_content,
            text=DESIGNER_NAME,
            font=("Segoe UI", 9),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(side=tk.LEFT, pady=5)
        
        # Right: Contact info
        tk.Label(
            footer_content,
            text=f"📧 {DESIGNER_EMAIL}  |  📞 {DESIGNER_PHONE}",
            font=("Segoe UI", 9),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(side=tk.RIGHT, pady=5)
