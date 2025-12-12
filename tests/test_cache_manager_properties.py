"""
Property-based tests for Cache Manager

**Feature: v1.3-enhancements**
"""

from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
import pytest

from processors.cache_manager import CacheManager, CacheEntry


# **Feature: v1.3-enhancements, Property 10: Cache Validity**
# **Validates: Requirements 9.2, 9.3**
def test_property_cache_validity_fresh():
    """
    Fresh cache entries should be valid.
    
    **Feature: v1.3-enhancements, Property 10: Cache Validity**
    **Validates: Requirements 9.2, 9.3**
    """
    manager = CacheManager()
    
    key = manager.generate_key("company", datetime.now(), datetime.now())
    manager.set(key, [1, 2, 3], {'company': 'company'})
    
    assert manager.is_valid(key) == True


def test_property_cache_get_returns_data():
    """
    Getting a valid cache entry should return the stored data.
    
    **Feature: v1.3-enhancements, Property 10: Cache Validity**
    **Validates: Requirements 9.2, 9.3**
    """
    manager = CacheManager()
    
    test_data = [{'id': 1}, {'id': 2}]
    key = manager.generate_key("test", datetime.now(), datetime.now())
    manager.set(key, test_data, {'company': 'test'})
    
    entry = manager.get(key)
    assert entry is not None
    assert entry.data == test_data


def test_property_cache_invalidate_single():
    """
    Invalidating a single key should only remove that entry.
    
    **Feature: v1.3-enhancements, Property 10: Cache Validity**
    **Validates: Requirements 9.2, 9.3**
    """
    manager = CacheManager()
    
    key1 = manager.generate_key("company1", datetime.now(), datetime.now())
    key2 = manager.generate_key("company2", datetime.now(), datetime.now())
    
    manager.set(key1, [1], {'company': 'company1'})
    manager.set(key2, [2], {'company': 'company2'})
    
    manager.invalidate(key1)
    
    assert manager.get(key1) is None
    assert manager.get(key2) is not None


def test_property_cache_invalidate_all():
    """
    Invalidating all should clear the cache.
    
    **Feature: v1.3-enhancements, Property 10: Cache Validity**
    **Validates: Requirements 9.2, 9.3**
    """
    manager = CacheManager()
    
    key1 = manager.generate_key("company1", datetime.now(), datetime.now())
    key2 = manager.generate_key("company2", datetime.now(), datetime.now())
    
    manager.set(key1, [1], {'company': 'company1'})
    manager.set(key2, [2], {'company': 'company2'})
    
    manager.invalidate()
    
    assert manager.get(key1) is None
    assert manager.get(key2) is None


@given(company=st.text(min_size=1, max_size=20))
@settings(max_examples=50)
def test_property_cache_key_generation(company):
    """
    Cache keys should be deterministic for same inputs.
    
    **Feature: v1.3-enhancements, Property 10: Cache Validity**
    **Validates: Requirements 9.2, 9.3**
    """
    manager = CacheManager()
    
    from_date = datetime(2024, 1, 1)
    to_date = datetime(2024, 1, 31)
    
    key1 = manager.generate_key(company, from_date, to_date)
    key2 = manager.generate_key(company, from_date, to_date)
    
    assert key1 == key2, "Same inputs should generate same key"
