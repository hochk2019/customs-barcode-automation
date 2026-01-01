"""
WebDriver Manager v2.0

Manages Selenium WebDriver lifecycle for web scraping fallback.
Extracted from BarcodeRetriever for single responsibility.

Responsibilities:
1. Create and configure Chrome WebDriver
2. Session management
3. Cleanup on exit
"""

import os
import threading
from typing import Optional
from contextlib import contextmanager

# Optional selenium imports (may not be installed)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    webdriver = None
    Options = None
    Service = None

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    ChromeDriverManager = None

from logging_system.logger import Logger


class WebDriverManager:
    """
    Manages Selenium WebDriver instances.
    
    Thread-safe singleton pattern ensures only one driver per thread.
    """
    
    def __init__(self, logger: Logger, headless: bool = True):
        """
        Initialize WebDriver manager.
        
        Args:
            logger: Logger instance
            headless: If True, run browser in headless mode
        """
        self.logger = logger
        self.headless = headless
        self._local = threading.local()
        self._lock = threading.Lock()
    
    def _create_driver(self) -> webdriver.Chrome:
        """
        Create a new Chrome WebDriver instance.
        
        Returns:
            Configured Chrome WebDriver
        """
        options = Options()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        # Common options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        
        # Disable logging noise
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Use webdriver-manager to auto-download driver
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            self.logger.warning(f"ChromeDriverManager failed: {e}, trying system chromedriver")
            # Fallback to system chromedriver
            driver = webdriver.Chrome(options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        self.logger.info("Created new Chrome WebDriver instance")
        return driver
    
    def get_driver(self) -> webdriver.Chrome:
        """
        Get WebDriver for current thread.
        
        Creates new driver if one doesn't exist for this thread.
        
        Returns:
            Chrome WebDriver instance
        """
        driver = getattr(self._local, 'driver', None)
        
        if driver is None:
            driver = self._create_driver()
            self._local.driver = driver
        
        return driver
    
    @contextmanager
    def driver_session(self):
        """
        Context manager for using WebDriver.
        
        Usage:
            with manager.driver_session() as driver:
                driver.get(url)
        """
        driver = self.get_driver()
        try:
            yield driver
        except Exception as e:
            self.logger.error(f"WebDriver error: {e}")
            # Try to recover by recreating driver
            self.close_driver()
            raise
    
    def close_driver(self) -> None:
        """Close WebDriver for current thread."""
        driver = getattr(self._local, 'driver', None)
        if driver:
            try:
                driver.quit()
                self.logger.info("Closed Chrome WebDriver")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self._local.driver = None
    
    def navigate_to(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: Target URL
            
        Returns:
            True if navigation succeeded
        """
        try:
            driver = self.get_driver()
            driver.get(url)
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            return False
    
    def get_page_source(self) -> Optional[str]:
        """
        Get current page source.
        
        Returns:
            Page HTML source or None
        """
        try:
            driver = self.get_driver()
            return driver.page_source
        except Exception as e:
            self.logger.error(f"Failed to get page source: {e}")
            return None


# Global instance
_manager: Optional[WebDriverManager] = None


def get_webdriver_manager(logger: Logger = None) -> WebDriverManager:
    """Get global WebDriver manager instance."""
    global _manager
    if _manager is None and logger is not None:
        _manager = WebDriverManager(logger)
    return _manager
