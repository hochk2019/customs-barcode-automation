"""
Declaration Processor

This module contains the DeclarationProcessor class that applies business rules
to filter customs declarations based on channel, status, transport method, and
internal management codes.
"""

from typing import List
from datetime import datetime
from models.declaration_models import Declaration


class DeclarationProcessor:
    """
    Applies business rules to filter declarations.
    
    Responsibilities:
    - Filter by channel (Green/Yellow)
    - Filter by cleared status
    - Exclude by transport method
    - Exclude by internal management codes
    - Transform date formats
    """
    
    def __init__(self):
        """Initialize the DeclarationProcessor"""
        pass
    
    def filter_declarations(self, declarations: List[Declaration]) -> List[Declaration]:
        """
        Filter a list of declarations based on eligibility rules.
        
        Args:
            declarations: List of Declaration objects to filter
            
        Returns:
            List of eligible Declaration objects
        """
        return [decl for decl in declarations if self.is_eligible(decl)]
    
    def is_eligible(self, declaration: Declaration) -> bool:
        """
        Check if a declaration is eligible for barcode retrieval.
        
        Business rules:
        - Channel must be 'Xanh' (Green) or 'Vang' (Yellow)
        - Status must be 'T' (Cleared)
        - Transport method must not be '9999' (Other)
        - Goods description must not start with '#&NKTC' or '#&XKTC'
        
        Args:
            declaration: Declaration object to check
            
        Returns:
            True if eligible, False otherwise
        """
        # Check channel - must be Green or Yellow
        if declaration.channel not in ['Xanh', 'Vang']:
            return False
        
        # Check status - must be cleared
        if declaration.status != 'T':
            return False
        
        # Check transport method - exclude code 9999
        if declaration.transport_method == '9999':
            return False
        
        # Check internal management codes in goods description
        if declaration.goods_description:
            if declaration.goods_description.startswith('#&NKTC'):
                return False
            if declaration.goods_description.startswith('#&XKTC'):
                return False
        
        return True
    
    def format_date(self, date: datetime) -> str:
        """
        Format a datetime object to ddmmyyyy string format.
        
        Args:
            date: datetime object to format
            
        Returns:
            Date string in ddmmyyyy format
        """
        return date.strftime('%d%m%Y')
