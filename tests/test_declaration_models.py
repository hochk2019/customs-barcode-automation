"""
Unit tests for declaration data models

Tests Declaration id generation, ProcessedDeclaration display_name,
and WorkflowResult duration calculation.
"""

import pytest
from datetime import datetime, timedelta
from models.declaration_models import (
    Declaration,
    ProcessedDeclaration,
    WorkflowResult,
    OperationMode
)
import tempfile
import os


class TestDeclaration:
    """Unit tests for Declaration dataclass"""
    
    def test_declaration_id_generation(self):
        """Test that Declaration id is generated correctly"""
        # Arrange
        declaration_date = datetime(2023, 12, 6, 14, 30, 25)
        declaration = Declaration(
            declaration_number="308010891440",
            tax_code="2300782217",
            declaration_date=declaration_date,
            customs_office_code="18A3",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description="Test goods"
        )
        
        # Act
        declaration_id = declaration.id
        
        # Assert
        expected_id = "2300782217_308010891440_20231206"
        assert declaration_id == expected_id
    
    def test_declaration_id_format(self):
        """Test that Declaration id follows the correct format"""
        # Arrange
        declaration_date = datetime(2024, 1, 15, 10, 0, 0)
        declaration = Declaration(
            declaration_number="123456789012",
            tax_code="0123456789",
            declaration_date=declaration_date,
            customs_office_code="18A3",
            transport_method="2",
            channel="Vang",
            status="T",
            goods_description=None
        )
        
        # Act
        declaration_id = declaration.id
        
        # Assert
        assert declaration_id == "0123456789_123456789012_20240115"
        assert declaration_id.count("_") == 2
    
    def test_declaration_to_dict(self):
        """Test that Declaration can be serialized to dict"""
        # Arrange
        declaration_date = datetime(2023, 12, 6, 14, 30, 25)
        declaration = Declaration(
            declaration_number="308010891440",
            tax_code="2300782217",
            declaration_date=declaration_date,
            customs_office_code="18A3",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description="Test goods"
        )
        
        # Act
        result = declaration.to_dict()
        
        # Assert
        assert isinstance(result, dict)
        assert result['declaration_number'] == "308010891440"
        assert result['tax_code'] == "2300782217"
        assert result['declaration_date'] == declaration_date
        assert result['customs_office_code'] == "18A3"
        assert result['transport_method'] == "1"
        assert result['channel'] == "Xanh"
        assert result['status'] == "T"
        assert result['goods_description'] == "Test goods"


class TestProcessedDeclaration:
    """Unit tests for ProcessedDeclaration dataclass"""
    
    def test_display_name_generation(self):
        """Test that ProcessedDeclaration display_name is generated correctly"""
        # Arrange
        processed = ProcessedDeclaration(
            id=1,
            declaration_number="308010891440",
            tax_code="2300782217",
            declaration_date="20231206",
            file_path="/output/2300782217_308010891440.pdf",
            processed_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        display_name = processed.display_name
        
        # Assert
        assert display_name == "2300782217_308010891440"
    
    def test_display_name_format(self):
        """Test that display_name follows TaxCode_DeclarationNumber format"""
        # Arrange
        processed = ProcessedDeclaration(
            id=2,
            declaration_number="123456789012",
            tax_code="0123456789",
            declaration_date="20240115",
            file_path="/output/0123456789_123456789012.pdf",
            processed_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        display_name = processed.display_name
        
        # Assert
        assert display_name == "0123456789_123456789012"
        assert display_name.count("_") == 1
    
    def test_file_exists_when_file_present(self):
        """Test that file_exists returns True when file exists"""
        # Arrange - create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as f:
            temp_path = f.name
            f.write("test content")
        
        try:
            processed = ProcessedDeclaration(
                id=1,
                declaration_number="308010891440",
                tax_code="2300782217",
                declaration_date="20231206",
                file_path=temp_path,
                processed_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Act
            exists = processed.file_exists()
            
            # Assert
            assert exists is True
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_file_exists_when_file_missing(self):
        """Test that file_exists returns False when file doesn't exist"""
        # Arrange
        processed = ProcessedDeclaration(
            id=1,
            declaration_number="308010891440",
            tax_code="2300782217",
            declaration_date="20231206",
            file_path="/nonexistent/path/file.pdf",
            processed_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        exists = processed.file_exists()
        
        # Assert
        assert exists is False


class TestWorkflowResult:
    """Unit tests for WorkflowResult dataclass"""
    
    def test_duration_calculation_with_end_time(self):
        """Test that WorkflowResult duration is calculated correctly"""
        # Arrange
        start = datetime(2023, 12, 6, 14, 30, 0)
        end = datetime(2023, 12, 6, 14, 35, 30)
        result = WorkflowResult(
            total_fetched=10,
            total_eligible=8,
            success_count=7,
            error_count=1,
            start_time=start,
            end_time=end
        )
        
        # Act
        duration = result.duration
        
        # Assert
        expected_duration = timedelta(minutes=5, seconds=30)
        assert duration == expected_duration
        assert duration.total_seconds() == 330
    
    def test_duration_calculation_without_end_time(self):
        """Test that duration returns zero when end_time is None"""
        # Arrange
        result = WorkflowResult(
            total_fetched=10,
            total_eligible=8,
            success_count=7,
            error_count=1,
            start_time=datetime.now(),
            end_time=None
        )
        
        # Act
        duration = result.duration
        
        # Assert
        assert duration == timedelta(0)
        assert duration.total_seconds() == 0
    
    def test_workflow_result_default_values(self):
        """Test that WorkflowResult has correct default values"""
        # Arrange & Act
        result = WorkflowResult()
        
        # Assert
        assert result.total_fetched == 0
        assert result.total_eligible == 0
        assert result.success_count == 0
        assert result.error_count == 0
        assert result.end_time is None
        assert isinstance(result.start_time, datetime)
    
    def test_duration_calculation_same_time(self):
        """Test duration when start and end are the same"""
        # Arrange
        same_time = datetime(2023, 12, 6, 14, 30, 0)
        result = WorkflowResult(
            start_time=same_time,
            end_time=same_time
        )
        
        # Act
        duration = result.duration
        
        # Assert
        assert duration == timedelta(0)


class TestOperationMode:
    """Unit tests for OperationMode enum"""
    
    def test_operation_mode_values(self):
        """Test that OperationMode has correct values"""
        # Assert
        assert OperationMode.AUTOMATIC.value == "automatic"
        assert OperationMode.MANUAL.value == "manual"
    
    def test_operation_mode_members(self):
        """Test that OperationMode has exactly two members"""
        # Assert
        assert len(OperationMode) == 2
        assert OperationMode.AUTOMATIC in OperationMode
        assert OperationMode.MANUAL in OperationMode
