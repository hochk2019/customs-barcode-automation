"""
Unit tests for DeclarationProcessor

These tests verify specific examples and edge cases for declaration processing.
"""

import pytest
from datetime import datetime

from models.declaration_models import Declaration
from processors.declaration_processor import DeclarationProcessor


class TestDeclarationProcessor:
    """Unit tests for DeclarationProcessor class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = DeclarationProcessor()
    
    def test_green_channel_eligibility(self):
        """Test that green channel declarations with cleared status are eligible"""
        declaration = Declaration(
            declaration_number='308010891440',
            tax_code='2300782217',
            declaration_date=datetime(2023, 1, 5),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description='Normal goods'
        )
        
        assert self.processor.is_eligible(declaration) == True
    
    def test_yellow_channel_eligibility(self):
        """Test that yellow channel declarations with cleared status are eligible"""
        declaration = Declaration(
            declaration_number='305254416960',
            tax_code='0700798384',
            declaration_date=datetime(2022, 12, 30),
            customs_office_code='18A3',
            transport_method='2',
            channel='Vang',
            status='T',
            goods_description='Normal goods'
        )
        
        assert self.processor.is_eligible(declaration) == True
    
    def test_red_channel_exclusion(self):
        """Test that red channel declarations are excluded"""
        declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 12, 6),
            customs_office_code='18A3',
            transport_method='1',
            channel='Do',  # Red channel
            status='T',
            goods_description='Normal goods'
        )
        
        assert self.processor.is_eligible(declaration) == False
    
    def test_transport_method_9999_exclusion(self):
        """Test that transport method 9999 is excluded"""
        declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 12, 6),
            customs_office_code='18A3',
            transport_method='9999',  # Other transport method
            channel='Xanh',
            status='T',
            goods_description='Normal goods'
        )
        
        assert self.processor.is_eligible(declaration) == False
    
    def test_internal_code_nktc_exclusion(self):
        """Test that internal code #&NKTC is excluded"""
        declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 12, 6),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description='#&NKTC Some description'
        )
        
        assert self.processor.is_eligible(declaration) == False
    
    def test_internal_code_xktc_exclusion(self):
        """Test that internal code #&XKTC is excluded"""
        declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 12, 6),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description='#&XKTC Some description'
        )
        
        assert self.processor.is_eligible(declaration) == False
    
    def test_non_cleared_status_exclusion(self):
        """Test that non-cleared status declarations are excluded"""
        declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 12, 6),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='P',  # Pending status
            goods_description='Normal goods'
        )
        
        assert self.processor.is_eligible(declaration) == False
    
    def test_none_goods_description(self):
        """Test that None goods description is handled correctly"""
        declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 12, 6),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description=None
        )
        
        assert self.processor.is_eligible(declaration) == True
    
    def test_date_formatting(self):
        """Test date formatting to ddmmyyyy"""
        test_date = datetime(2023, 1, 5)
        formatted = self.processor.format_date(test_date)
        
        assert formatted == '05012023'
    
    def test_date_formatting_double_digit_day_month(self):
        """Test date formatting with double digit day and month"""
        test_date = datetime(2022, 12, 30)
        formatted = self.processor.format_date(test_date)
        
        assert formatted == '30122022'
    
    def test_filter_declarations(self):
        """Test filtering a list of declarations"""
        declarations = [
            Declaration(
                declaration_number='308010891440',
                tax_code='2300782217',
                declaration_date=datetime(2023, 1, 5),
                customs_office_code='18A3',
                transport_method='1',
                channel='Xanh',
                status='T',
                goods_description='Normal goods'
            ),
            Declaration(
                declaration_number='123456789012',
                tax_code='1234567890',
                declaration_date=datetime(2023, 12, 6),
                customs_office_code='18A3',
                transport_method='9999',
                channel='Xanh',
                status='T',
                goods_description='Normal goods'
            ),
            Declaration(
                declaration_number='305254416960',
                tax_code='0700798384',
                declaration_date=datetime(2022, 12, 30),
                customs_office_code='18A3',
                transport_method='2',
                channel='Vang',
                status='T',
                goods_description='Normal goods'
            ),
        ]
        
        eligible = self.processor.filter_declarations(declarations)
        
        # Should have 2 eligible declarations (first and third)
        assert len(eligible) == 2
        assert eligible[0].declaration_number == '308010891440'
        assert eligible[1].declaration_number == '305254416960'
    
    def test_filter_declarations_empty_list(self):
        """Test filtering an empty list"""
        declarations = []
        eligible = self.processor.filter_declarations(declarations)
        
        assert len(eligible) == 0
        assert eligible == []
    
    def test_filter_declarations_all_ineligible(self):
        """Test filtering when all declarations are ineligible"""
        declarations = [
            Declaration(
                declaration_number='123456789012',
                tax_code='1234567890',
                declaration_date=datetime(2023, 12, 6),
                customs_office_code='18A3',
                transport_method='9999',
                channel='Xanh',
                status='T',
                goods_description='Normal goods'
            ),
            Declaration(
                declaration_number='123456789013',
                tax_code='1234567891',
                declaration_date=datetime(2023, 12, 6),
                customs_office_code='18A3',
                transport_method='1',
                channel='Do',
                status='T',
                goods_description='Normal goods'
            ),
        ]
        
        eligible = self.processor.filter_declarations(declarations)
        
        assert len(eligible) == 0
        assert eligible == []
