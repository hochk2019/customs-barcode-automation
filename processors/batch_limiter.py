"""
Batch Limiter

This module provides batch download limiting functionality.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

from typing import Tuple
from config.configuration_manager import ConfigurationManager


class BatchLimiter:
    """
    Limiter for batch download operations.
    
    Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
    """
    
    MIN_LIMIT = 1
    MAX_LIMIT = 50
    DEFAULT_LIMIT = 20
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
    
    def get_limit(self) -> int:
        """
        Get the current batch limit.
        
        Returns:
            Batch limit value (clamped to valid range)
        """
        limit = self.config_manager.get_batch_limit()
        return self._clamp_limit(limit)
    
    def set_limit(self, limit: int) -> bool:
        """
        Set the batch limit.
        
        Args:
            limit: New limit value
            
        Returns:
            True if valid and set, False if invalid
        """
        if not self._is_valid_limit(limit):
            return False
        
        self.config_manager.set_batch_limit(limit)
        return True
    
    def validate_selection(self, count: int) -> Tuple[bool, str]:
        """
        Validate selection count against batch limit.
        
        Args:
            count: Number of selected items
            
        Returns:
            Tuple of (is_valid, message)
            
        Requirements: 10.1, 10.2
        """
        limit = self.get_limit()
        
        if count <= 0:
            return False, "Vui lòng chọn ít nhất một tờ khai"
        
        if count > limit:
            return False, f"Bạn đã chọn {count} tờ khai, vượt quá giới hạn {limit}. Vui lòng bỏ chọn bớt."
        
        return True, ""
    
    def _is_valid_limit(self, limit: int) -> bool:
        """Check if limit value is valid"""
        return self.MIN_LIMIT <= limit <= self.MAX_LIMIT
    
    def _clamp_limit(self, limit: int) -> int:
        """Clamp limit to valid range, use default for invalid"""
        if limit is None or limit < self.MIN_LIMIT or limit > self.MAX_LIMIT:
            return self.DEFAULT_LIMIT
        return limit
