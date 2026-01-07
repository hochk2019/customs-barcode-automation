"""
Simple tests for performance optimization features in declaration printing.
"""

import importlib.util
import sys

if "pytest" in sys.modules and importlib.util.find_spec("declaration_printing") is None:
    import pytest
    pytest.skip("declaration_printing package not installed", allow_module_level=True)

import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime
from decimal import Decimal

import pytest
from openpyxl import Workbook

from declaration_printing.declaration_printer import DeclarationPrinter
from config.configuration_manager import ConfigurationManager
from logging_system.logger import Logger


class TestPerformanceOptimization:
    """Tests for performance optimization features."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir()
        
        # Create mock logger and config manager
        self.mock_logger = Mock(spec=Logger)
        self.mock_config_manager = Mock(spec=ConfigurationManager)
        
        # Mock the config attribute
        mock_config = Mock()
        mock_config.has_section.return_value = False
        mock_config.add_section.return_value = None
        self.mock_config_manager.config = mock_config
        
        # Create declaration printer
        self.printer = DeclarationPrinter(
            config_manager=self.mock_config_manager,
            logger=self.mock_logger,
            output_directory=str(self.output_dir)
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_performance_metrics_initialization(self):
        """Test that performance metrics are properly initialized."""
        assert hasattr(self.printer, 'performance_metrics')
        assert 'cache_hits' in self.printer.performance_metrics
        assert 'cache_misses' in self.printer.performance_metrics
        assert 'total_processing_time' in self.printer.performance_metrics
        
        # Initial values should be zero
        assert self.printer.performance_metrics['cache_hits'] == 0
        assert self.printer.performance_metrics['cache_misses'] == 0
        assert self.printer.performance_metrics['total_processing_time'] == 0.0
    
    def test_template_cache_initialization(self):
        """Test that template cache is properly initialized."""
        assert hasattr(self.printer, '_template_cache')
        assert hasattr(self.printer, '_cache_lock')
        assert isinstance(self.printer._template_cache, dict)
        assert len(self.printer._template_cache) == 0
    
    def test_batch_processing_with_realistic_volume(self):
        """Test batch processing with realistic data volumes."""
        # Generate test declaration numbers
        declaration_numbers = []
        for i in range(20):  # Reduced for CI performance
            if i % 2 == 0:
                declaration_numbers.append(f"30525440{i:04d}")  # Export
            else:
                declaration_numbers.append(f"10777283{i:04d}")  # Import
        
        # Mock data extraction to return test data
        def mock_extract_with_fallback(decl_num):
            from declaration_printing.models import DeclarationData, DeclarationType, GoodsItem
            from declaration_printing.type_detector import DeclarationTypeDetector
            
            declaration_type = DeclarationTypeDetector().detect_type(decl_num)
            
            return DeclarationData(
                declaration_number=decl_num,
                declaration_type=declaration_type,
                customs_office="1801",
                declaration_date=datetime(2024, 1, 15),
                company_tax_code="0123456789",
                company_name="Test Company Ltd",
                company_address="123 Test Street",
                partner_name="Partner Company",
                partner_address="456 Partner Street",
                country_of_origin="VN" if declaration_type.name == "EXPORT_CLEARANCE" else "US",
                country_of_destination="US" if declaration_type.name == "EXPORT_CLEARANCE" else "VN",
                total_value=Decimal('50000.00'),
                currency="USD",
                exchange_rate=Decimal('24000'),
                goods_list=[
                    GoodsItem(
                        item_number=1,
                        hs_code="1234567890",
                        description="Test Product",
                        quantity=Decimal('100'),
                        unit="PCS",
                        unit_price=Decimal('500.00'),
                        total_value=Decimal('50000.00'),
                        origin_country="VN"
                    )
                ],
                total_weight=Decimal('1000.5'),
                total_packages=10,
                transport_method="SEA",
                bill_of_lading="BL123456",
                container_numbers=["CONT123456"],
                additional_data={'status': 'T', 'channel': 'GREEN'}
            )
        
        with patch.object(self.printer.data_extractor, 'extract_with_fallback', side_effect=mock_extract_with_fallback):
            # Measure processing time
            start_time = datetime.now()
            
            # Execute batch processing
            result = self.printer.print_declarations(declaration_numbers)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Verify results
            assert result.total_processed == len(declaration_numbers)
            assert result.successful > 0  # At least some should succeed
            assert processing_time < 30.0  # Should complete within 30 seconds
            
            # Verify performance metrics were updated
            assert self.printer.performance_metrics['total_processing_time'] > 0
    
    def test_memory_optimization_with_large_data(self):
        """Test memory optimization with larger data sets."""
        # Create a declaration with many goods items to test memory handling
        declaration_number = "305254403660"
        
        def mock_extract_with_fallback(decl_num):
            from declaration_printing.models import DeclarationData, DeclarationType, GoodsItem
            
            # Create many goods items to test memory optimization
            goods_list = []
            for i in range(100):  # 100 goods items
                goods_list.append(GoodsItem(
                    item_number=i + 1,
                    hs_code=f"123456789{i}",
                    description=f"Test Product {i}",
                    quantity=Decimal('100'),
                    unit="PCS",
                    unit_price=Decimal('500.00'),
                    total_value=Decimal('50000.00'),
                    origin_country="VN"
                ))
            
            return DeclarationData(
                declaration_number=decl_num,
                declaration_type=DeclarationType.EXPORT_CLEARANCE,
                customs_office="1801",
                declaration_date=datetime(2024, 1, 15),
                company_tax_code="0123456789",
                company_name="Test Company Ltd",
                company_address="123 Test Street",
                partner_name="Partner Company",
                partner_address="456 Partner Street",
                country_of_origin="VN",
                country_of_destination="US",
                total_value=Decimal('5000000.00'),  # Large value
                currency="USD",
                exchange_rate=Decimal('24000'),
                goods_list=goods_list,
                total_weight=Decimal('100000.5'),  # Large weight
                total_packages=1000,  # Many packages
                transport_method="SEA",
                bill_of_lading="BL123456",
                container_numbers=[f"CONT{i:06d}" for i in range(10)],  # Multiple containers
                additional_data={'status': 'T', 'channel': 'GREEN'}
            )
        
        with patch.object(self.printer.data_extractor, 'extract_with_fallback', side_effect=mock_extract_with_fallback):
            # Process the large declaration
            result = self.printer.print_single_declaration(declaration_number)
            
            # Verify successful processing
            assert result.success is True
            assert result.declaration_number == declaration_number
            assert result.output_file_path is not None
            
            # Verify output file was created
            output_file = Path(result.output_file_path)
            assert output_file.exists()
            assert output_file.stat().st_size > 0  # File should have content
    
    def test_error_handling_performance(self):
        """Test that error handling doesn't significantly impact performance."""
        # Create a mix of valid and invalid declaration numbers
        declaration_numbers = [
            "305254403660",  # Valid export
            "invalid_number",  # Invalid format
            "107772836360",  # Valid import
            "another_invalid",  # Invalid format
            "305254416960"   # Valid export
        ]
        
        def mock_extract_with_fallback(decl_num):
            if "invalid" in decl_num:
                return None  # Simulate extraction failure
            
            from declaration_printing.models import DeclarationData, DeclarationType, GoodsItem
            from declaration_printing.type_detector import DeclarationTypeDetector
            
            declaration_type = DeclarationTypeDetector().detect_type(decl_num)
            
            return DeclarationData(
                declaration_number=decl_num,
                declaration_type=declaration_type,
                customs_office="1801",
                declaration_date=datetime(2024, 1, 15),
                company_tax_code="0123456789",
                company_name="Test Company Ltd",
                company_address="123 Test Street",
                partner_name="Partner Company",
                partner_address="456 Partner Street",
                country_of_origin="VN",
                country_of_destination="US",
                total_value=Decimal('50000.00'),
                currency="USD",
                exchange_rate=Decimal('24000'),
                goods_list=[],
                total_weight=Decimal('1000.5'),
                total_packages=10,
                transport_method="SEA",
                bill_of_lading="BL123456",
                container_numbers=["CONT123456"],
                additional_data={'status': 'T', 'channel': 'GREEN'}
            )
        
        with patch.object(self.printer.data_extractor, 'extract_with_fallback', side_effect=mock_extract_with_fallback):
            # Measure processing time
            start_time = datetime.now()
            
            # Execute batch processing with mixed results
            result = self.printer.print_declarations(declaration_numbers)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Verify results
            assert result.total_processed == len(declaration_numbers)
            assert result.successful == 3  # 3 valid declarations
            assert result.failed == 2      # 2 invalid declarations
            
            # Error handling shouldn't significantly slow down processing
            assert processing_time < 10.0  # Should complete within 10 seconds
            
            # Verify performance metrics
            assert self.printer.performance_metrics['total_processing_time'] > 0