"""
Unit tests for database connectivity

This module contains unit tests for the EcusDataConnector class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
import pyodbc

from database.ecus_connector import EcusDataConnector, DatabaseConnectionError
from models.config_models import DatabaseConfig
from models.declaration_models import Declaration


@pytest.fixture
def db_config():
    """Fixture for database configuration"""
    return DatabaseConfig(
        server="test_server",
        database="test_db",
        username="test_user",
        password="test_pass",
        timeout=30
    )


@pytest.fixture
def mock_logger():
    """Fixture for mock logger"""
    return Mock()


@pytest.fixture
def connector(db_config, mock_logger):
    """Fixture for EcusDataConnector"""
    return EcusDataConnector(db_config, logger=mock_logger)


def test_connection_string_generation(db_config):
    """Test that connection string is generated correctly"""
    expected = (
        "DRIVER={SQL Server};"
        "SERVER=test_server;"
        "DATABASE=test_db;"
        "UID=test_user;"
        "PWD=test_pass;"
        "Connection Timeout=30;"
    )
    assert db_config.connection_string == expected


def test_successful_connection(connector):
    """Test successful database connection"""
    with patch('pyodbc.connect') as mock_connect:
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        result = connector.connect()
        
        assert result is True
        assert connector._connection == mock_connection
        mock_connect.assert_called_once()


def test_connection_failure_handling(connector):
    """Test handling of connection failures"""
    with patch('pyodbc.connect') as mock_connect:
        mock_connect.side_effect = pyodbc.Error("Connection failed")
        
        result = connector.connect()
        
        assert result is False
        assert connector._connection is None


def test_disconnect(connector):
    """Test database disconnection"""
    mock_connection = Mock()
    connector._connection = mock_connection
    
    connector.disconnect()
    
    mock_connection.close.assert_called_once()
    assert connector._connection is None


def test_disconnect_with_error(connector):
    """Test disconnect handles errors gracefully"""
    mock_connection = Mock()
    mock_connection.close.side_effect = Exception("Close failed")
    connector._connection = mock_connection
    
    # Should not raise exception
    connector.disconnect()
    
    assert connector._connection is None


def test_test_connection_active(connector):
    """Test connection test when connection is active"""
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_connection.cursor.return_value = mock_cursor
    connector._connection = mock_connection
    
    result = connector.test_connection()
    
    assert result is True
    mock_cursor.execute.assert_called_once_with("SELECT 1")
    mock_cursor.close.assert_called_once()


def test_test_connection_inactive(connector):
    """Test connection test when connection is inactive"""
    connector._connection = None
    
    result = connector.test_connection()
    
    assert result is False


def test_test_connection_error(connector):
    """Test connection test when query fails"""
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_cursor.execute.side_effect = pyodbc.Error("Query failed")
    mock_connection.cursor.return_value = mock_cursor
    connector._connection = mock_connection
    
    result = connector.test_connection()
    
    assert result is False


def test_reconnect_success(connector):
    """Test successful reconnection"""
    with patch.object(connector, 'disconnect') as mock_disconnect:
        with patch.object(connector, 'connect', return_value=True) as mock_connect:
            result = connector.reconnect()
            
            assert result is True
            mock_disconnect.assert_called_once()
            mock_connect.assert_called_once()


def test_reconnect_failure(connector):
    """Test failed reconnection"""
    with patch.object(connector, 'disconnect') as mock_disconnect:
        with patch.object(connector, 'connect', return_value=False) as mock_connect:
            result = connector.reconnect()
            
            assert result is False
            mock_disconnect.assert_called_once()
            mock_connect.assert_called_once()


def test_query_execution_with_mock_data(connector):
    """Test query execution with mock data"""
    # Create mock connection and cursor
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_connection.cursor.return_value = mock_cursor
    connector._connection = mock_connection
    
    # Create mock row data
    mock_row = Mock()
    mock_row.declaration_number = "308010891440"
    mock_row.tax_code = "2300782217"
    mock_row.declaration_date = datetime(2023, 1, 5, 14, 25, 30)
    mock_row.customs_office_code = "18A3"
    mock_row.transport_method = "1"
    mock_row.channel = "Xanh"
    mock_row.status = "T"
    mock_row.goods_description = "Test goods"
    
    mock_cursor.__iter__ = Mock(return_value=iter([mock_row]))
    
    # Mock test_connection to return True
    with patch.object(connector, 'test_connection', return_value=True):
        declarations = connector.get_new_declarations(set())
    
    assert len(declarations) == 1
    declaration = declarations[0]
    assert declaration.declaration_number == "308010891440"
    assert declaration.tax_code == "2300782217"
    assert declaration.channel == "Xanh"
    assert declaration.status == "T"


def test_query_filters_processed_declarations(connector):
    """Test that already processed declarations are filtered out"""
    # Create mock connection and cursor
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_connection.cursor.return_value = mock_cursor
    connector._connection = mock_connection
    
    # Create mock row data
    mock_row = Mock()
    mock_row.declaration_number = "308010891440"
    mock_row.tax_code = "2300782217"
    mock_row.declaration_date = datetime(2023, 1, 5)
    mock_row.customs_office_code = "18A3"
    mock_row.transport_method = "1"
    mock_row.channel = "Xanh"
    mock_row.status = "T"
    mock_row.goods_description = None
    
    mock_cursor.__iter__ = Mock(return_value=iter([mock_row]))
    
    # Create processed_ids set with the declaration ID
    processed_ids = {"2300782217_308010891440_20230105"}
    
    # Mock test_connection to return True
    with patch.object(connector, 'test_connection', return_value=True):
        declarations = connector.get_new_declarations(processed_ids)
    
    # Should return empty list since declaration is already processed
    assert len(declarations) == 0


def test_query_handles_database_error(connector):
    """Test that database errors are handled properly"""
    # Create mock connection and cursor
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_cursor.execute.side_effect = pyodbc.Error("Query failed")
    mock_connection.cursor.return_value = mock_cursor
    connector._connection = mock_connection
    
    # Mock test_connection to return True
    with patch.object(connector, 'test_connection', return_value=True):
        with pytest.raises(DatabaseConnectionError):
            connector.get_new_declarations(set())


def test_context_manager(connector):
    """Test context manager functionality"""
    with patch.object(connector, 'connect') as mock_connect:
        with patch.object(connector, 'disconnect') as mock_disconnect:
            with connector:
                pass
            
            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()


def test_map_row_to_declaration(connector):
    """Test mapping database row to Declaration object"""
    mock_row = Mock()
    mock_row.declaration_number = "  308010891440  "
    mock_row.tax_code = "  2300782217  "
    mock_row.declaration_date = datetime(2023, 1, 5)
    mock_row.customs_office_code = "  18A3  "
    mock_row.transport_method = "  1  "
    mock_row.channel = "  Xanh  "
    mock_row.status = "  T  "
    mock_row.goods_description = "  Test goods  "
    
    declaration = connector._map_row_to_declaration(mock_row)
    
    # Verify values are stripped
    assert declaration.declaration_number == "308010891440"
    assert declaration.tax_code == "2300782217"
    assert declaration.customs_office_code == "18A3"
    assert declaration.transport_method == "1"
    assert declaration.channel == "Xanh"
    assert declaration.status == "T"
    assert declaration.goods_description == "Test goods"


def test_map_row_with_none_values(connector):
    """Test mapping row with None values"""
    mock_row = Mock()
    mock_row.declaration_number = None
    mock_row.tax_code = None
    mock_row.declaration_date = datetime(2023, 1, 5)
    mock_row.customs_office_code = None
    mock_row.transport_method = None
    mock_row.channel = None
    mock_row.status = None
    mock_row.goods_description = None
    
    declaration = connector._map_row_to_declaration(mock_row)
    
    # Verify empty strings for None values
    assert declaration.declaration_number == ""
    assert declaration.tax_code == ""
    assert declaration.customs_office_code == ""
    assert declaration.transport_method == ""
    assert declaration.channel == ""
    assert declaration.status == ""
    assert declaration.goods_description is None


def test_map_row_with_so_hstk_field(connector):
    """Test mapping database row with so_hstk field correctly mapped
    
    Requirements: 2.1 - System SHALL identify declarations by SoHSTK field
    """
    mock_row = Mock()
    mock_row.declaration_number = "308010891440"
    mock_row.tax_code = "2300782217"
    mock_row.declaration_date = datetime(2023, 1, 5)
    mock_row.customs_office_code = "18A3"
    mock_row.transport_method = "1"
    mock_row.channel = "Xanh"
    mock_row.status = "T"
    mock_row.goods_description = "Test goods"
    mock_row.so_hstk = "  ABC123#&NKTC456  "
    
    declaration = connector._map_row_to_declaration(mock_row)
    
    # Verify so_hstk is correctly mapped and stripped
    assert declaration.so_hstk == "ABC123#&NKTC456"
    # Verify is_xnktc property works with the mapped value
    assert declaration.is_xnktc is True


def test_map_row_with_so_hstk_xktc_pattern(connector):
    """Test mapping row with XKTC pattern in so_hstk
    
    Requirements: 2.2 - System SHALL identify XKTC declarations
    """
    mock_row = Mock()
    mock_row.declaration_number = "308010891440"
    mock_row.tax_code = "2300782217"
    mock_row.declaration_date = datetime(2023, 1, 5)
    mock_row.customs_office_code = "18A3"
    mock_row.transport_method = "1"
    mock_row.channel = "Xanh"
    mock_row.status = "T"
    mock_row.goods_description = "Test goods"
    mock_row.so_hstk = "XYZ#&XKTC789"
    
    declaration = connector._map_row_to_declaration(mock_row)
    
    assert declaration.so_hstk == "XYZ#&XKTC789"
    assert declaration.is_xnktc is True


def test_map_row_with_so_hstk_gcptq_pattern(connector):
    """Test mapping row with GCPTQ pattern in so_hstk
    
    Requirements: 2.3 - System SHALL identify GCPTQ declarations
    """
    mock_row = Mock()
    mock_row.declaration_number = "308010891440"
    mock_row.tax_code = "2300782217"
    mock_row.declaration_date = datetime(2023, 1, 5)
    mock_row.customs_office_code = "18A3"
    mock_row.transport_method = "1"
    mock_row.channel = "Xanh"
    mock_row.status = "T"
    mock_row.goods_description = "Test goods"
    mock_row.so_hstk = "DEF#&GCPTQ000"
    
    declaration = connector._map_row_to_declaration(mock_row)
    
    assert declaration.so_hstk == "DEF#&GCPTQ000"
    assert declaration.is_xnktc is True


def test_map_row_with_so_hstk_none(connector):
    """Test mapping row with None so_hstk field
    
    Requirements: 2.4 - Null SoHSTK SHALL be treated as normal declaration
    """
    mock_row = Mock()
    mock_row.declaration_number = "308010891440"
    mock_row.tax_code = "2300782217"
    mock_row.declaration_date = datetime(2023, 1, 5)
    mock_row.customs_office_code = "18A3"
    mock_row.transport_method = "1"
    mock_row.channel = "Xanh"
    mock_row.status = "T"
    mock_row.goods_description = "Test goods"
    mock_row.so_hstk = None
    
    declaration = connector._map_row_to_declaration(mock_row)
    
    assert declaration.so_hstk is None
    assert declaration.is_xnktc is False


def test_map_row_with_so_hstk_normal_declaration(connector):
    """Test mapping row with normal (non-XNK TC) so_hstk value
    
    Requirements: 2.1 - Normal declarations should not be identified as XNK TC
    """
    mock_row = Mock()
    mock_row.declaration_number = "308010891440"
    mock_row.tax_code = "2300782217"
    mock_row.declaration_date = datetime(2023, 1, 5)
    mock_row.customs_office_code = "18A3"
    mock_row.transport_method = "1"
    mock_row.channel = "Xanh"
    mock_row.status = "T"
    mock_row.goods_description = "Test goods"
    mock_row.so_hstk = "NORMAL_HSTK_12345"
    
    declaration = connector._map_row_to_declaration(mock_row)
    
    assert declaration.so_hstk == "NORMAL_HSTK_12345"
    assert declaration.is_xnktc is False


def test_map_row_without_so_hstk_attribute(connector):
    """Test mapping row when so_hstk attribute doesn't exist (backward compatibility)"""
    mock_row = Mock(spec=['declaration_number', 'tax_code', 'declaration_date', 
                          'customs_office_code', 'transport_method', 'channel', 
                          'status', 'goods_description'])
    mock_row.declaration_number = "308010891440"
    mock_row.tax_code = "2300782217"
    mock_row.declaration_date = datetime(2023, 1, 5)
    mock_row.customs_office_code = "18A3"
    mock_row.transport_method = "1"
    mock_row.channel = "Xanh"
    mock_row.status = "T"
    mock_row.goods_description = "Test goods"
    
    declaration = connector._map_row_to_declaration(mock_row)
    
    # Should handle missing attribute gracefully
    assert declaration.so_hstk is None
    assert declaration.is_xnktc is False
