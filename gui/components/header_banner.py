"""
Header Banner v2.0

Extracted from customs_gui.py for GUI decomposition.
Creates the glossy black header with logo, company name, and buttons.
"""

import os
import tkinter as tk
from typing import Callable, Optional
from PIL import Image, ImageTk

from gui.branding import (
    APP_VERSION, COMPANY_NAME, COMPANY_SLOGAN, LOGO_FILE,
    DESIGNER_NAME_HEADER, BRAND_PRIMARY_COLOR, BRAND_SECONDARY_COLOR,
    BRAND_ACCENT_COLOR, BRAND_GOLD_COLOR, BRAND_TEXT_COLOR
)
from logging_system.logger import Logger


class HeaderBanner:
    """
    Header banner component.
    
    Displays:
    - Logo with motto
    - Company name and slogan
    - About and Update buttons
    - Version info
    """
    
    def __init__(
        self,
        parent: tk.Tk,
        logger: Logger,
        on_about_click: Callable,
        on_update_click: Callable
    ):
        """
        Create header banner.
        
        Args:
            parent: Parent window
            logger: Logger instance
            on_about_click: Callback for about button
            on_update_click: Callback for update button
        """
        self.parent = parent
        self.logger = logger
        self.on_about_click = on_about_click
        self.on_update_click = on_update_click
        self._logo_photo = None
        
        self._create_banner()
    
    def _create_banner(self) -> None:
        """Create the header banner."""
        # Header frame
        header_frame = tk.Frame(self.parent, bg=BRAND_PRIMARY_COLOR, height=105)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Inner container
        header_content = tk.Frame(header_frame, bg=BRAND_PRIMARY_COLOR)
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        
        # Left side: Logo + Motto
        self._create_left_section(header_content)
        
        # Center: Company name + Slogan
        self._create_center_section(header_content)
        
        # Right side: Buttons + Version
        self._create_right_section(header_content)
    
    def _create_left_section(self, parent: tk.Frame) -> None:
        """Create left section with logo and motto."""
        left_frame = tk.Frame(parent, bg=BRAND_PRIMARY_COLOR)
        left_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        # Logo
        logo_container = tk.Frame(left_frame, bg=BRAND_PRIMARY_COLOR)
        logo_container.pack(side=tk.LEFT)
        
        try:
            # Go up 3 levels: header_banner.py -> components -> gui -> project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            logo_path = os.path.join(base_dir, LOGO_FILE)
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img.thumbnail((65, 65), Image.Resampling.LANCZOS)
                self._logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(logo_container, image=self._logo_photo, bg=BRAND_PRIMARY_COLOR)
                logo_label.pack()
        except Exception as e:
            self.logger.warning(f"Could not load logo: {e}")
        
        # Motto
        motto_frame = tk.Frame(left_frame, bg=BRAND_PRIMARY_COLOR)
        motto_frame.pack(side=tk.LEFT, padx=(15, 0), fill=tk.Y)
        
        motto_lines = ["Thích thì thuê", "Không thích thì chê"]
        for line in motto_lines:
            tk.Label(
                motto_frame,
                text=line,
                font=("Segoe UI", 10, "italic"),
                fg=BRAND_GOLD_COLOR,
                bg=BRAND_PRIMARY_COLOR
            ).pack(anchor=tk.W, pady=(0, 1))
    
    def _create_center_section(self, parent: tk.Frame) -> None:
        """Create center section with company name and slogan."""
        center_frame = tk.Frame(parent, bg=BRAND_PRIMARY_COLOR)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            center_frame,
            text=COMPANY_NAME,
            font=("Segoe UI", 22, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(anchor=tk.CENTER, pady=(5, 0))
        
        tk.Label(
            center_frame,
            text=COMPANY_SLOGAN,
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(anchor=tk.CENTER, pady=(2, 0))
    
    def _create_right_section(self, parent: tk.Frame) -> None:
        """Create right section with buttons and version."""
        right_frame = tk.Frame(parent, bg=BRAND_PRIMARY_COLOR)
        right_frame.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Button row
        button_row = tk.Frame(right_frame, bg=BRAND_PRIMARY_COLOR)
        button_row.pack(anchor=tk.E)
        
        # About button
        about_btn = tk.Button(
            button_row,
            text="ℹ  Giới thiệu",
            font=("Segoe UI", 11, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_SECONDARY_COLOR,
            activebackground=BRAND_PRIMARY_COLOR,
            activeforeground=BRAND_ACCENT_COLOR,
            relief=tk.RIDGE,
            bd=2,
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.on_about_click
        )
        about_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Update button
        update_btn = tk.Button(
            button_row,
            text="🔄  Cập nhật",
            font=("Segoe UI", 11, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_SECONDARY_COLOR,
            activebackground=BRAND_PRIMARY_COLOR,
            activeforeground=BRAND_ACCENT_COLOR,
            relief=tk.RIDGE,
            bd=2,
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.on_update_click
        )
        update_btn.pack(side=tk.LEFT)
        
        # Version label
        tk.Label(
            right_frame,
            text=f"Version {APP_VERSION}",
            font=("Segoe UI", 9),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(anchor=tk.E, pady=(5, 0))
        
        # Designer info
        tk.Label(
            right_frame,
            text=DESIGNER_NAME_HEADER,
            font=("Segoe UI", 10),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(anchor=tk.E, pady=(2, 0))
