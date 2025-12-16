"""
Branding and Version Information

This module contains all branding, version, and company information
for the Customs Barcode Automation application.
"""

# Version Information - Import from main.py to keep single source of truth
# Note: This is imported at runtime to avoid circular imports
def get_app_version():
    """Get app version from main module."""
    try:
        from main import APP_VERSION as MAIN_VERSION
        return MAIN_VERSION
    except ImportError:
        return "1.3.1"  # Fallback version

APP_VERSION = "1.3.3"  # Keep in sync with main.py
APP_NAME = "Customs Barcode Automation"
APP_FULL_NAME = f"{APP_NAME} v{APP_VERSION}"

# Company Information
COMPANY_NAME = "GOLDEN LOGISTICS"
COMPANY_NAME_FULL = "Golden Logistics Co.,Ltd"
COMPANY_SLOGAN = "Chuyên làm thủ tục HQ - Vận chuyển hàng toàn quốc"
COMPANY_MOTTO = '"Thích thì thuê - Không thích thì chê - Nhưng đừng bỏ!"'

# Designer Information
DESIGNER_NAME_HEADER = "Designer: Học HK"  # For header banner only
DESIGNER_NAME = "Liên hệ để được tư vấn thủ tục hải quan miễn phí - đúng quy định - có lợi nhất cho DN về lâu dài!"  # For footer and about dialog
DESIGNER_EMAIL = "Hochk2019@gmail.com"
DESIGNER_PHONE = "0868.333.606"

# Logo
LOGO_FILE = "Logo.png"

# Colors for branding - High contrast dark theme
BRAND_PRIMARY_COLOR = "#0d0d0d"      # Glossy black background
BRAND_SECONDARY_COLOR = "#1a1a1a"    # Slightly lighter black
BRAND_ACCENT_COLOR = "#d4a853"       # Gold accent (lighter)
BRAND_GOLD_COLOR = "#FFD700"         # Bright gold for main text
BRAND_TEXT_COLOR = "#ffffff"         # White text
BRAND_GRAY_COLOR = "#888888"         # Gray for subtle text

# Window settings
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION} - {COMPANY_NAME}"
