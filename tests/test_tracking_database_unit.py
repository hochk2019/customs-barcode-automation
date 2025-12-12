"""
Unit tests for TrackingDatabase

These tests verify specific functionality of the tracking database.
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from database.tracking_database import TrackingDatabase
from models.declaration_models import Declaration


class TestTrackingDatabase:
    """Unit tests for TrackingDatabase"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def tracking_db(self, temp_dir):
        """Create a tracking database for testing"""
        db_path = os.path.join(temp_dir, 'test_tracking.db')
        return TrackingDatabase(db_path)
    
    @pytest.fixture
    def sample_declaration(self):
        """Create a sample declaration for testing"""
        return Declaration(
            declaration_number="308010891440",
            tax_code="2300782217",
            declaration_date=datetime(2023, 1, 5),
            customs_office_code="18A3",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description="Test goods"
        )
    
    def test_database_creation(self, temp_dir):
        """Test that database is created successfully"""
        db_path = os.path.join(temp_dir, 'test_tracking.db')
        db = TrackingDatabase(db_path)
        
        # Verify database file exists
        assert os.path.exists(db_path)
    
    def test_add_processed_declaration(self, tracking_db, sample_declaration):
        """Test adding a processed declaration"""
        file_path = "/test/2300782217_308010891440.pdf"
        
        # Add declaration
        tracking_db.add_processed(sample_declaration, file_path)
        
        # Verify it's marked as processed
        assert tracking_db.is_processed(sample_declaration)
    
    def test_check_if_processed(self, tracking_db, sample_declaration):
        """Test checking if a declaration is processed"""
        file_path = "/test/2300782217_308010891440.pdf"
        
        # Initially not processed
        assert not tracking_db.is_processed(sample_declaration)
        
        # Add declaration
        tracking_db.add_processed(sample_declaration, file_path)
        
        # Now it should be processed
        assert tracking_db.is_processed(sample_declaration)
    
    def test_get_all_processed(self, tracking_db):
        """Test getting all processed declaration IDs"""
        # Create multiple declarations
        declarations = [
            Declaration(
                declaration_number="308010891440",
                tax_code="2300782217",
                declaration_date=datetime(2023, 1, 5),
                customs_office_code="18A3",
                transport_method="1",
                channel="Xanh",
                status="T",
                goods_description=None
            ),
            Declaration(
                declaration_number="305254416960",
                tax_code="0700798384",
                declaration_date=datetime(2022, 12, 30),
                customs_office_code="18A3",
                transport_method="2",
                channel="Vang",
                status="T",
                goods_description=None
            ),
            Declaration(
                declaration_number="105205185850",
                tax_code="2300646077",
                declaration_date=datetime(2023, 1, 5),
                customs_office_code="18A3",
                transport_method="1",
                channel="Xanh",
                status="T",
                goods_description=None
            )
        ]
        
        # Add all declarations
        for decl in declarations:
            file_path = f"/test/{decl.tax_code}_{decl.declaration_number}.pdf"
            tracking_db.add_processed(decl, file_path)
        
        # Get all processed IDs
        processed_ids = tracking_db.get_all_processed()
        
        # Verify all declarations are in the set
        assert len(processed_ids) == 3
        for decl in declarations:
            assert decl.id in processed_ids
    
    def test_get_all_processed_details(self, tracking_db, sample_declaration):
        """Test getting detailed information about processed declarations"""
        file_path = "/test/2300782217_308010891440.pdf"
        
        # Add declaration
        tracking_db.add_processed(sample_declaration, file_path)
        
        # Get details
        details = tracking_db.get_all_processed_details()
        
        # Verify details
        assert len(details) == 1
        assert details[0].declaration_number == sample_declaration.declaration_number
        assert details[0].tax_code == sample_declaration.tax_code
        assert details[0].file_path == file_path
        assert details[0].processed_at is not None
        assert details[0].updated_at is not None
    
    def test_search_declarations_by_number(self, tracking_db):
        """Test searching declarations by declaration number"""
        # Create multiple declarations
        declarations = [
            Declaration(
                declaration_number="308010891440",
                tax_code="2300782217",
                declaration_date=datetime(2023, 1, 5),
                customs_office_code="18A3",
                transport_method="1",
                channel="Xanh",
                status="T",
                goods_description=None
            ),
            Declaration(
                declaration_number="305254416960",
                tax_code="0700798384",
                declaration_date=datetime(2022, 12, 30),
                customs_office_code="18A3",
                transport_method="2",
                channel="Vang",
                status="T",
                goods_description=None
            )
        ]
        
        # Add all declarations
        for decl in declarations:
            file_path = f"/test/{decl.tax_code}_{decl.declaration_number}.pdf"
            tracking_db.add_processed(decl, file_path)
        
        # Search by partial declaration number
        results = tracking_db.search_declarations("308010")
        
        # Verify results
        assert len(results) == 1
        assert results[0].declaration_number == "308010891440"
    
    def test_search_declarations_by_tax_code(self, tracking_db):
        """Test searching declarations by tax code"""
        # Create multiple declarations
        declarations = [
            Declaration(
                declaration_number="308010891440",
                tax_code="2300782217",
                declaration_date=datetime(2023, 1, 5),
                customs_office_code="18A3",
                transport_method="1",
                channel="Xanh",
                status="T",
                goods_description=None
            ),
            Declaration(
                declaration_number="305254416960",
                tax_code="0700798384",
                declaration_date=datetime(2022, 12, 30),
                customs_office_code="18A3",
                transport_method="2",
                channel="Vang",
                status="T",
                goods_description=None
            )
        ]
        
        # Add all declarations
        for decl in declarations:
            file_path = f"/test/{decl.tax_code}_{decl.declaration_number}.pdf"
            tracking_db.add_processed(decl, file_path)
        
        # Search by partial tax code
        results = tracking_db.search_declarations("0700")
        
        # Verify results
        assert len(results) == 1
        assert results[0].tax_code == "0700798384"
    
    def test_update_processed_timestamp(self, tracking_db, sample_declaration):
        """Test updating the processed timestamp"""
        file_path = "/test/2300782217_308010891440.pdf"
        
        # Add declaration
        tracking_db.add_processed(sample_declaration, file_path)
        
        # Get initial details
        details_before = tracking_db.get_all_processed_details()
        initial_updated_at = details_before[0].updated_at
        
        # Wait a moment to ensure timestamp difference
        import time
        time.sleep(1)
        
        # Update timestamp
        tracking_db.update_processed_timestamp(sample_declaration)
        
        # Get updated details
        details_after = tracking_db.get_all_processed_details()
        updated_updated_at = details_after[0].updated_at
        
        # Verify timestamp was updated
        assert updated_updated_at > initial_updated_at
    
    def test_rebuild_from_directory(self, tracking_db, temp_dir):
        """Test rebuilding database from directory"""
        # Create a directory with PDF files
        pdf_dir = os.path.join(temp_dir, 'pdfs')
        os.makedirs(pdf_dir)
        
        # Create some PDF files
        pdf_files = [
            "2300782217_308010891440.pdf",
            "0700798384_305254416960.pdf",
            "2300646077_105205185850.pdf"
        ]
        
        for filename in pdf_files:
            file_path = os.path.join(pdf_dir, filename)
            with open(file_path, 'w') as f:
                f.write("dummy pdf content")
        
        # Rebuild database
        tracking_db.rebuild_from_directory(pdf_dir)
        
        # Verify all files were added
        details = tracking_db.get_all_processed_details()
        assert len(details) == 3
        
        # Verify filenames were parsed correctly
        tax_codes = {d.tax_code for d in details}
        declaration_numbers = {d.declaration_number for d in details}
        
        assert "2300782217" in tax_codes
        assert "0700798384" in tax_codes
        assert "2300646077" in tax_codes
        
        assert "308010891440" in declaration_numbers
        assert "305254416960" in declaration_numbers
        assert "105205185850" in declaration_numbers
    
    def test_rebuild_from_nonexistent_directory(self, tracking_db):
        """Test rebuilding from a directory that doesn't exist"""
        with pytest.raises(ValueError, match="Directory does not exist"):
            tracking_db.rebuild_from_directory("/nonexistent/directory")
    
    def test_duplicate_declaration_handling(self, tracking_db, sample_declaration):
        """Test that adding the same declaration twice updates the record"""
        file_path1 = "/test/path1.pdf"
        file_path2 = "/test/path2.pdf"
        
        # Add declaration first time
        tracking_db.add_processed(sample_declaration, file_path1)
        
        # Add same declaration again with different file path
        tracking_db.add_processed(sample_declaration, file_path2)
        
        # Should still have only one record
        details = tracking_db.get_all_processed_details()
        assert len(details) == 1
        
        # File path should be updated to the latest
        assert details[0].file_path == file_path2
    
    def test_empty_database(self, tracking_db):
        """Test operations on empty database"""
        # Get all processed should return empty set
        processed_ids = tracking_db.get_all_processed()
        assert len(processed_ids) == 0
        
        # Get all details should return empty list
        details = tracking_db.get_all_processed_details()
        assert len(details) == 0
        
        # Search should return empty list
        results = tracking_db.search_declarations("anything")
        assert len(results) == 0
