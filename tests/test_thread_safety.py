"""
Thread Safety Tests v2.0

Tests for thread-safe access to preferences, connection pool, and workflow service.
"""

import pytest
import threading
import time
import tempfile
import os

from config.preferences_service import PreferencesService
from models.config_models import DatabaseConfig


class TestThreadSafety:
    """Test suite for thread safety across components."""
    
    def test_preferences_concurrent_writes(self):
        """Test concurrent writes to preferences."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{}')
            temp_path = f.name
        
        try:
            service = PreferencesService(temp_path)
            errors = []
            write_count = [0]
            
            def writer(value):
                try:
                    for _ in range(50):
                        service.set("max_companies", value)
                        write_count[0] += 1
                except Exception as e:
                    errors.append(e)
            
            threads = [
                threading.Thread(target=writer, args=(i,))
                for i in range(1, 6)
            ]
            
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            assert len(errors) == 0, f"Thread errors: {errors}"
            assert write_count[0] == 250  # 5 threads * 50 writes
        finally:
            os.unlink(temp_path)
    
    def test_preferences_concurrent_read_write(self):
        """Test concurrent reads and writes to preferences."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{}')
            temp_path = f.name
        
        try:
            service = PreferencesService(temp_path)
            errors = []
            
            def writer():
                try:
                    for i in range(100):
                        service.set("max_companies", (i % 10) + 1)
                except Exception as e:
                    errors.append(("writer", e))
            
            def reader():
                try:
                    for _ in range(100):
                        _ = service.get("max_companies")
                except Exception as e:
                    errors.append(("reader", e))
            
            threads = [
                threading.Thread(target=writer),
                threading.Thread(target=reader),
                threading.Thread(target=reader),
                threading.Thread(target=writer),
            ]
            
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            assert len(errors) == 0, f"Thread errors: {errors}"
        finally:
            os.unlink(temp_path)
    
    def test_event_bus_concurrent_publish(self):
        """Test concurrent event publishing."""
        from services.event_bus import EventBus, EventType
        
        bus = EventBus()
        received = []
        lock = threading.Lock()
        
        def handler(event):
            with lock:
                received.append(event)
        
        bus.subscribe(EventType.WORKFLOW_PROGRESS, handler)
        
        errors = []
        
        def publisher(thread_id):
            try:
                for i in range(50):
                    bus.publish(
                        EventType.WORKFLOW_PROGRESS, 
                        {"thread": thread_id, "index": i}
                    )
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=publisher, args=(i,))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Thread errors: {errors}"
        assert len(received) == 250  # 5 threads * 50 publishes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
