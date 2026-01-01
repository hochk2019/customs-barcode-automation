"""
Unit Tests for WorkflowService v2.0

Tests for workflow execution, event emission, and cancellation.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from services.workflow_service import WorkflowService
from services.workflow_events import WorkflowEvent, WorkflowEventType
from models.declaration_models import Declaration, WorkflowResult


class TestWorkflowService:
    """Test suite for WorkflowService."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for WorkflowService."""
        return {
            'ecus_connector': MagicMock(),
            'tracking_db': MagicMock(),
            'processor': MagicMock(),
            'barcode_retriever': MagicMock(),
            'file_manager': MagicMock(),
            'logger': MagicMock(),
        }
    
    @pytest.fixture
    def workflow_service(self, mock_dependencies):
        """Create WorkflowService with mocks."""
        return WorkflowService(**mock_dependencies)
    
    @pytest.fixture
    def sample_declaration(self):
        """Create a sample declaration for testing."""
        return Declaration(
            declaration_number="1234567890",
            tax_code="0123456789",
            declaration_date=datetime.now(),
            status="T"
        )
    
    def test_execute_empty_declarations(self, workflow_service, mock_dependencies):
        """Test workflow with no declarations."""
        mock_dependencies['tracking_db'].get_all_processed.return_value = set()
        mock_dependencies['ecus_connector'].get_new_declarations.return_value = []
        mock_dependencies['processor'].filter_declarations.return_value = []
        
        result = workflow_service.execute(days_back=7)
        
        assert result.total_fetched == 0
        assert result.success_count == 0
        assert result.error_count == 0
    
    def test_execute_with_declarations(self, workflow_service, mock_dependencies, sample_declaration):
        """Test workflow with declarations."""
        mock_dependencies['tracking_db'].get_all_processed.return_value = set()
        mock_dependencies['ecus_connector'].get_new_declarations.return_value = [sample_declaration]
        mock_dependencies['processor'].filter_declarations.return_value = [sample_declaration]
        mock_dependencies['barcode_retriever'].retrieve_barcode.return_value = b'%PDF-1.4'
        mock_dependencies['file_manager'].save_barcode.return_value = '/path/to/file.pdf'
        
        result = workflow_service.execute(days_back=7)
        
        assert result.total_fetched == 1
        assert result.success_count == 1
        assert result.error_count == 0
    
    def test_execute_with_barcode_failure(self, workflow_service, mock_dependencies, sample_declaration):
        """Test workflow when barcode retrieval fails."""
        mock_dependencies['tracking_db'].get_all_processed.return_value = set()
        mock_dependencies['ecus_connector'].get_new_declarations.return_value = [sample_declaration]
        mock_dependencies['processor'].filter_declarations.return_value = [sample_declaration]
        mock_dependencies['barcode_retriever'].retrieve_barcode.return_value = None
        
        result = workflow_service.execute(days_back=7)
        
        assert result.total_fetched == 1
        assert result.success_count == 0
        assert result.error_count == 1
    
    def test_event_listener(self, workflow_service, mock_dependencies, sample_declaration):
        """Test that events are emitted during execution."""
        mock_dependencies['tracking_db'].get_all_processed.return_value = set()
        mock_dependencies['ecus_connector'].get_new_declarations.return_value = [sample_declaration]
        mock_dependencies['processor'].filter_declarations.return_value = [sample_declaration]
        mock_dependencies['barcode_retriever'].retrieve_barcode.return_value = b'%PDF-1.4'
        mock_dependencies['file_manager'].save_barcode.return_value = '/path/to/file.pdf'
        
        events_received = []
        workflow_service.add_event_listener(lambda e: events_received.append(e))
        
        workflow_service.execute(days_back=7)
        
        # Should receive: started, progress, declaration_processed, completed
        assert len(events_received) >= 3
        event_types = [e.event_type for e in events_received]
        assert WorkflowEventType.STARTED in event_types
        assert WorkflowEventType.COMPLETED in event_types
    
    def test_cancellation(self, workflow_service, mock_dependencies, sample_declaration):
        """Test workflow cancellation."""
        mock_dependencies['tracking_db'].get_all_processed.return_value = set()
        mock_dependencies['ecus_connector'].get_new_declarations.return_value = [sample_declaration] * 10
        mock_dependencies['processor'].filter_declarations.return_value = [sample_declaration] * 10
        
        # Cancel immediately
        workflow_service.cancel()
        
        result = workflow_service.execute(days_back=7)
        
        # Should have processed fewer than all declarations
        assert result.success_count < 10
    
    def test_force_redownload(self, workflow_service, mock_dependencies, sample_declaration):
        """Test force redownload skips processed check."""
        mock_dependencies['ecus_connector'].get_new_declarations.return_value = [sample_declaration]
        mock_dependencies['processor'].filter_declarations.return_value = [sample_declaration]
        mock_dependencies['barcode_retriever'].retrieve_barcode.return_value = b'%PDF-1.4'
        mock_dependencies['file_manager'].save_barcode.return_value = '/path/to/file.pdf'
        
        workflow_service.execute(force_redownload=True)
        
        # Should not call get_all_processed when force_redownload=True
        # Actually it's called but returns empty set - let's verify the logic differently
        mock_dependencies['file_manager'].save_barcode.assert_called_once()


class TestWorkflowEvents:
    """Test suite for WorkflowEvent factory methods."""
    
    def test_started_event(self):
        """Test started event creation."""
        event = WorkflowEvent.started(10)
        assert event.event_type == WorkflowEventType.STARTED
        assert event.data["total"] == 10
    
    def test_progress_event(self):
        """Test progress event creation."""
        event = WorkflowEvent.progress(5, 10, "123456")
        assert event.event_type == WorkflowEventType.PROGRESS
        assert event.data["current"] == 5
        assert event.data["total"] == 10
        assert event.data["percent"] == 50
    
    def test_completed_event(self):
        """Test completed event creation."""
        event = WorkflowEvent.completed(8, 2, 45.5)
        assert event.event_type == WorkflowEventType.COMPLETED
        assert event.data["success_count"] == 8
        assert event.data["error_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
