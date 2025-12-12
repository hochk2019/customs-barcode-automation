"""
Cache Manager

This module provides caching for preview data.

Requirements: 9.2, 9.3, 9.4
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class CacheEntry:
    """Cache entry with data and metadata"""
    data: List[Any]
    timestamp: datetime
    company_filter: str
    date_range: Tuple[datetime, datetime]


class CacheManager:
    """
    Manager for preview data caching.
    
    Requirements: 9.2, 9.3, 9.4
    """
    
    CACHE_TTL_MINUTES = 5
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cached entry if valid"""
        if key in self._cache and self.is_valid(key):
            return self._cache[key]
        return None
    
    def set(self, key: str, data: List[Any], filters: dict) -> None:
        """Store data in cache"""
        self._cache[key] = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            company_filter=filters.get('company', ''),
            date_range=filters.get('date_range', (None, None))
        )
    
    def is_valid(self, key: str) -> bool:
        """Check if cache entry is still valid (not expired)"""
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        age = datetime.now() - entry.timestamp
        return age.total_seconds() < self.CACHE_TTL_MINUTES * 60
    
    def invalidate(self, key: str = None) -> None:
        """Invalidate cache entry or all entries"""
        if key is None:
            self._cache.clear()
        elif key in self._cache:
            del self._cache[key]
    
    def generate_key(self, company: str, from_date: datetime, to_date: datetime) -> str:
        """Generate cache key from filters"""
        key_str = f"{company}_{from_date.isoformat()}_{to_date.isoformat()}"
        return hashlib.md5(key_str.encode()).hexdigest()
