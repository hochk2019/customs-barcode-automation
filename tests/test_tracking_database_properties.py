"""
Property-based tests for TrackingDatabase

These tests verify correctness properties using Hypothesis.
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from hypothesis import given, strategies as st, settings
from database.tracking_database import TrackingDatabase
from models.declaration_models import Declaration


# Strategy for generating valid declarations
@st.composite
def declaration_strategy(draw):
    """Generate random valid declarations"""
    declaration_number = draw(st.text(
        min_size=12, 
        max_size=12, 
        alphabet=st.characters(whitelist_categories=('Nd',))
    ))
    tax_code = draw(st.text(
        min_size=10, 
        max_size=10, 
        alphabet=st.characters(whitelist_categories=('Nd',))
    ))
    
    # Generate a date within a reasonable range
    year = draw(st.integers(min_value=2020, max_value=2025))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # Safe for all months
    
    declaration_date = datetime(year, month, day)
    
    customs_office_code = draw(st.text(min_size=4, max_size=4, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    transport_method = draw(st.sampled_from(['1', '2', '3', '4', '5', '6', '7', '8', '9999']))
    channel = draw(st.sampled_from(['Xanh', 'Vang', 'Do']))
    status = draw(st.sampled_from(['T', 'P', 'H', 'K']))
    goods_description = draw(st.one_of(st.none(), st.text(max_size=100)))
    
    return Declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        declaration_date=declaration_date,
        customs_office_code=customs_office_code,
        transport_method=transport_method,
        channel=channel,
        status=status,
        goods_description=goods_description
    )


# Feature: customs-barcode-automation, Property 15: Tracking database uniqueness
@given(declaration=declaration_strategy())
@settings(max_examples=100, deadline=None)
def test_property_tracking_uniqueness(declaration):
    """
    For any CustomsDeclaration, the unique identifier in the tracking database 
    should be the combination of DeclarationNumber, TaxCode, and declaration date.
    
    Validates: Requirements 8.3
    """
    # Create a temporary database for this test
    temp_dir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(temp_dir, 'test_tracking.db')
        temp_db = TrackingDatabase(db_path)
        
        # Add the declaration
        file_path = f"/test/{declaration.tax_code}_{declaration.declaration_number}.pdf"
        temp_db.add_processed(declaration, file_path)
        
        # Verify it's marked as processed
        assert temp_db.is_processed(declaration)
        
        # Create a declaration with same unique key but different other fields
        declaration_same_key = Declaration(
            declaration_number=declaration.declaration_number,
            tax_code=declaration.tax_code,
            declaration_date=declaration.declaration_date,
            customs_office_code="DIFF",  # Different field
            transport_method="1",  # Different field
            channel="Xanh",  # Different field
            status="T",  # Different field
            goods_description="Different"  # Different field
        )
        
        # Should still be marked as processed (same unique key)
        assert temp_db.is_processed(declaration_same_key)
        
        # Create a declaration with different unique key
        from datetime import timedelta
        declaration_diff_key = Declaration(
            declaration_number=declaration.declaration_number,
            tax_code=declaration.tax_code,
            declaration_date=declaration.declaration_date + timedelta(days=1),  # Different date
            customs_office_code=declaration.customs_office_code,
            transport_method=declaration.transport_method,
            channel=declaration.channel,
            status=declaration.status,
            goods_description=declaration.goods_description
        )
        
        # Should NOT be marked as processed (different unique key)
        assert not temp_db.is_processed(declaration_diff_key)
        
        # Verify the ID format matches the expected pattern
        processed_ids = temp_db.get_all_processed()
        assert declaration.id in processed_ids
        assert declaration_diff_key.id not in processed_ids
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


# Feature: customs-barcode-automation, Property 16: Duplicate processing prevention
@given(declarations=st.lists(declaration_strategy(), min_size=1, max_size=10))
@settings(max_examples=100, deadline=None)
def test_property_duplicate_prevention(declarations):
    """
    For any CustomsDeclaration already in the tracking database, it should be 
    excluded from the processing queue unless force_redownload is True.
    
    Validates: Requirements 8.2
    """
    # Create a temporary database for this test
    temp_dir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(temp_dir, 'test_tracking.db')
        temp_db = TrackingDatabase(db_path)
        
        # Add all declarations to the tracking database
        for declaration in declarations:
            file_path = f"/test/{declaration.tax_code}_{declaration.declaration_number}.pdf"
            temp_db.add_processed(declaration, file_path)
        
        # Get all processed IDs
        processed_ids = temp_db.get_all_processed()
        
        # Verify that all declarations are in the processed set
        for declaration in declarations:
            assert declaration.id in processed_ids
            assert temp_db.is_processed(declaration)
        
        # Simulate filtering logic: declarations in processed_ids should be excluded
        # This mimics the workflow where we check against processed_ids
        declarations_to_process = [
            decl for decl in declarations 
            if decl.id not in processed_ids
        ]
        
        # Since all declarations are already processed, none should be in the queue
        assert len(declarations_to_process) == 0
        
        # Now test with a new declaration (not in database)
        new_declaration = Declaration(
            declaration_number="999999999999",
            tax_code="9999999999",
            declaration_date=datetime(2025, 1, 1),
            customs_office_code="TEST",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description=None
        )
        
        # New declaration should NOT be in processed set
        assert new_declaration.id not in processed_ids
        assert not temp_db.is_processed(new_declaration)
        
        # New declaration should be eligible for processing
        all_declarations = declarations + [new_declaration]
        declarations_to_process = [
            decl for decl in all_declarations 
            if decl.id not in processed_ids
        ]
        
        # Only the new declaration should be in the queue
        assert len(declarations_to_process) == 1
        assert declarations_to_process[0].id == new_declaration.id
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
