"""
Unit Tests for Preferences Service v2.0

Tests for config persistence, file locking, and schema validation.
"""

import pytest
import os
import tempfile
import json
import threading
from pathlib import Path

from config.preferences_service import PreferencesService


class TestPreferencesService:
    """Test suite for PreferencesService."""
    
    @pytest.fixture
    def temp_prefs_file(self):
        """Create a temporary preferences file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{}')
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def prefs_service(self, temp_prefs_file):
        """Create a PreferencesService instance with temp file."""
        return PreferencesService(temp_prefs_file)
    
    def test_init_creates_defaults(self, prefs_service):
        """Test that initialization applies default values."""
        assert prefs_service.include_pending == True
        assert prefs_service.exclude_xnktc == False
        assert prefs_service.max_companies == 5
    
    def test_set_and_get_boolean(self, prefs_service):
        """Test setting and getting boolean preferences."""
        prefs_service.include_pending = False
        assert prefs_service.include_pending == False
        
        prefs_service.include_pending = True
        assert prefs_service.include_pending == True
    
    def test_set_and_get_integer(self, prefs_service):
        """Test setting and getting integer preferences."""
        prefs_service.max_companies = 7
        assert prefs_service.max_companies == 7
    
    def test_integer_clamping(self, prefs_service):
        """Test that integers are clamped to schema bounds."""
        # max_companies has max=10
        prefs_service.set("max_companies", 20)
        assert prefs_service.max_companies == 10
        
        # min=1
        prefs_service.set("max_companies", 0)
        assert prefs_service.max_companies == 1
    
    def test_set_and_get_list(self, prefs_service):
        """Test setting and getting list preferences."""
        companies = ["1234567890", "0987654321"]
        prefs_service.selected_companies = companies
        assert prefs_service.selected_companies == companies
    
    def test_persistence(self, temp_prefs_file):
        """Test that preferences persist across instances."""
        # Set value in first instance
        service1 = PreferencesService(temp_prefs_file)
        service1.include_pending = False
        service1.max_companies = 8
        
        # Create new instance and verify persistence
        service2 = PreferencesService(temp_prefs_file)
        assert service2.include_pending == False
        assert service2.max_companies == 8
    
    def test_reset_to_defaults(self, prefs_service):
        """Test resetting all preferences to defaults."""
        prefs_service.include_pending = False
        prefs_service.max_companies = 10
        
        prefs_service.reset_to_defaults()
        
        assert prefs_service.include_pending == True
        assert prefs_service.max_companies == 5
    
    def test_get_all(self, prefs_service):
        """Test getting all preferences as dict."""
        all_prefs = prefs_service.get_all()
        assert isinstance(all_prefs, dict)
        assert "include_pending" in all_prefs
        assert "max_companies" in all_prefs
    
    def test_unknown_key_raises(self, prefs_service):
        """Test that setting unknown key raises ValueError."""
        with pytest.raises(ValueError):
            prefs_service.set("unknown_key", "value")
    
    def test_thread_safety(self, prefs_service):
        """Test thread-safe access to preferences."""
        errors = []
        
        def writer_thread(value):
            try:
                for _ in range(100):
                    prefs_service.max_companies = value
            except Exception as e:
                errors.append(e)
        
        def reader_thread():
            try:
                for _ in range(100):
                    _ = prefs_service.max_companies
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=writer_thread, args=(3,)),
            threading.Thread(target=writer_thread, args=(7,)),
            threading.Thread(target=reader_thread),
            threading.Thread(target=reader_thread),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Thread errors: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
