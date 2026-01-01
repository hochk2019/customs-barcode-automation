"""
Property-based tests for DeclarationDataExtractor.

Tests the data source priority and fallback logic to ensure correct behavior
across various scenarios and data availability conditions.
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from hypothesis import given, strategies as st, assume, settings

from declaration_printing.data_extractor import DeclarationDataExtractor
from declaration_printing.models import DeclarationData, DeclarationType, GoodsItem
from models.config_models import DatabaseConfig
from logging_system.logger import Logger


# Test data generators
@st.composite
def declaration_number_strategy(draw):
    """Generate valid declaration numbers"""
    prefix = draw(st.sampled_from(['10', '30']))  # Import or Export
    suffix = draw(st.text(alphabet='0123456789', min_size=10, max_size=10))
    return prefix + suffix


@st.composite
def declaration_data_strategy(draw):
    """Generate DeclarationData objects for testing"""
    declaration_number = draw(declaration_number_strategy())
    
    # Determine type based on number
    if declaration_number.startswith('30'):
        declaration_type = DeclarationType.EXPORT_CLEARANCE
    else:
        declaration_type = DeclarationType.IMPORT_CLEARANCE
    
    return DeclarationData(
        declaration_number=declaration_number,
        declaration_type=declaration_type,
        customs_office=draw(st.text(min_size=1, max_size=10)),
        declaration_date=draw(st.datetimes(min_value=datetime(2020, 1, 1))),
        company_tax_code=draw(st.text(alphabet='0123456789', min_size=10, max_size=13)),
        company_name=draw(st.text(min_size=1, max_size=100)),
        company_address=draw(st.text(min_size=1, max_size=200)),
        partner_name=draw(st.text(min_size=1, max_size=100)),
        partner_address=draw(st.text(min_size=1, max_size=200)),
        country_of_origin=draw(st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=2, max_size=2)),
        country_of_destination=draw(st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=2, max_size=2)),
        total_value=draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999.99'))),
        currency=draw(st.sampled_from(['USD', 'EUR', 'VND'])),
        exchange_rate=draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('50000'))),
        goods_list=[],
        total_weight=draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('99999.99'))),
        total_packages=draw(st.integers(min_value=1, max_value=1000)),
        transport_method=draw(st.text(min_size=1, max_size=20)),
        bill_of_lading=draw(st.text(min_size=1, max_size=50)),
        container_numbers=[],
        additional_data={}
    )


@st.composite
def xml_content_strategy(draw):
    """Generate XML content for testing"""
    declaration_number = draw(declaration_number_strategy())
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Root>
  <App>ECUS5VNACCS2018</App>
  <DToKhaiMDIDs>
    <DToKhaiMD>
      <Data>
        <SOTK>{declaration_number}</SOTK>
        <MA_DV>0123456789</MA_DV>
        <_Ten_DV_L1>Test Company</_Ten_DV_L1>
        <DIA_CHI_DV>Test Address</DIA_CHI_DV>
        <NGAY_DK>2023-01-01</NGAY_DK>
        <MA_HQ>TEST</MA_HQ>
        <DV_DT>Partner Company</DV_DT>
        <DIA_CHI_DT>Partner Address</DIA_CHI_DT>
        <NUOC_XK>VN</NUOC_XK>
        <NUOC_NK>US</NUOC_NK>
        <TONGTGTT>1000.00</TONGTGTT>
        <MA_NT_TGTT>USD</MA_NT_TGTT>
        <TYGIA_VND>23000</TYGIA_VND>
        <TR_LUONG>100.50</TR_LUONG>
        <SO_KIEN>5</SO_KIEN>
        <MA_PTVT>SEA</MA_PTVT>
        <VAN_DON>TEST123</VAN_DON>
        <TTTK>T</TTTK>
        <PLUONG>Xanh</PLUONG>
        <MA_LH>E52</MA_LH>
      </Data>
    </DToKhaiMD>
  </DToKhaiMDIDs>
</Root>"""
    
    return declaration_number, xml_content


class TestDeclarationDataExtractorProperties:
    """Property-based tests for DeclarationDataExtractor"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.logger = Mock(spec=Logger)
        self.db_config = DatabaseConfig(
            server="test_server",
            database="test_db",
            username="test_user",
            password="test_pass"
        )
    
    @given(declaration_number_strategy())
    @settings(max_examples=100)
    def test_property_data_source_priority_database_first(self, declaration_number):
        """
        **Feature: customs-declaration-printing, Property 3: Data source priority and fallback**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        For any declaration number, when database data is available, 
        the system should return database data without attempting XML fallback.
        """
        # Create extractor with both database and XML configured
        with tempfile.TemporaryDirectory() as temp_dir:
            extractor = DeclarationDataExtractor(
                db_config=self.db_config,
                xml_directory=temp_dir,
                logger=self.logger
            )
            
            # Mock database extraction to return data
            mock_db_data = Mock(spec=DeclarationData)
            mock_db_data.declaration_number = declaration_number
            
            with patch.object(extractor, 'extract_from_database', return_value=mock_db_data) as mock_db:
                with patch.object(extractor, 'extract_from_xml') as mock_xml:
                    
                    result = extractor.extract_with_fallback(declaration_number)
                    
                    # Database should be tried first
                    mock_db.assert_called_once_with(declaration_number)
                    
                    # XML should not be attempted when database succeeds
                    mock_xml.assert_not_called()
                    
                    # Result should be database data
                    assert result == mock_db_data
    
    @given(declaration_number_strategy())
    @settings(max_examples=100)
    def test_property_data_source_fallback_to_xml(self, declaration_number):
        """
        **Feature: customs-declaration-printing, Property 3: Data source priority and fallback**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        For any declaration number, when database extraction fails,
        the system should attempt XML extraction as fallback.
        """
        # Create extractor with both database and XML configured
        with tempfile.TemporaryDirectory() as temp_dir:
            extractor = DeclarationDataExtractor(
                db_config=self.db_config,
                xml_directory=temp_dir,
                logger=self.logger
            )
            
            # Mock XML data
            mock_xml_data = Mock(spec=DeclarationData)
            mock_xml_data.declaration_number = declaration_number
            
            with patch.object(extractor, 'extract_from_database', return_value=None) as mock_db:
                with patch.object(extractor, 'find_xml_file', return_value=f"{temp_dir}/test.xml"):
                    with patch.object(extractor, 'extract_from_xml', return_value=mock_xml_data) as mock_xml:
                        
                        result = extractor.extract_with_fallback(declaration_number)
                        
                        # Database should be tried first
                        mock_db.assert_called_once_with(declaration_number)
                        
                        # XML should be attempted when database fails
                        mock_xml.assert_called_once()
                        
                        # Result should be XML data
                        assert result == mock_xml_data
    
    @given(declaration_number_strategy())
    @settings(max_examples=100)
    def test_property_basic_template_creation(self, declaration_number):
        """
        **Feature: customs-declaration-printing, Property 3: Data source priority and fallback**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        For any declaration number, when both database and XML extraction fail,
        the system should create a basic template with the declaration number.
        """
        # Create extractor with both database and XML configured
        with tempfile.TemporaryDirectory() as temp_dir:
            extractor = DeclarationDataExtractor(
                db_config=self.db_config,
                xml_directory=temp_dir,
                logger=self.logger
            )
            
            with patch.object(extractor, 'extract_from_database', return_value=None):
                with patch.object(extractor, 'find_xml_file', return_value=None):
                    
                    result = extractor.extract_with_fallback(declaration_number)
                    
                    # Should return a basic template
                    assert result is not None
                    assert result.declaration_number == declaration_number
                    
                    # Should have correct declaration type based on number
                    if declaration_number.startswith('30'):
                        assert result.declaration_type == DeclarationType.EXPORT_CLEARANCE
                    else:
                        assert result.declaration_type == DeclarationType.IMPORT_CLEARANCE
                    
                    # Should have basic template marker
                    assert result.additional_data.get('source') == 'basic_template'
    
    @given(declaration_data_strategy(), declaration_data_strategy())
    @settings(max_examples=50)
    def test_property_data_merging_database_priority(self, db_data, xml_data):
        """
        **Feature: customs-declaration-printing, Property 3: Data source priority and fallback**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        For any database and XML data with the same declaration number,
        merging should prioritize database values over XML values.
        """
        # Ensure both data have same declaration number
        xml_data.declaration_number = db_data.declaration_number
        
        extractor = DeclarationDataExtractor(logger=self.logger)
        
        result = extractor.merge_data_sources(db_data, xml_data)
        
        assert result is not None
        
        # Database values should take priority
        assert result.declaration_number == db_data.declaration_number
        assert result.company_tax_code == db_data.company_tax_code
        assert result.company_name == db_data.company_name
        assert result.total_value == db_data.total_value
        assert result.currency == db_data.currency
    
    @given(xml_content_strategy())
    @settings(max_examples=50)
    def test_property_xml_extraction_completeness(self, xml_data):
        """
        **Feature: customs-declaration-printing, Property 3: Data source priority and fallback**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        For any valid XML content, extraction should produce a DeclarationData
        with the correct declaration number and type.
        """
        declaration_number, xml_content = xml_data
        
        with tempfile.TemporaryDirectory() as temp_dir:
            xml_file = Path(temp_dir) / f"test_{declaration_number}.xml"
            xml_file.write_text(xml_content, encoding='utf-8')
            
            extractor = DeclarationDataExtractor(
                xml_directory=temp_dir,
                logger=self.logger
            )
            
            result = extractor.extract_from_xml(str(xml_file))
            
            assert result is not None
            assert result.declaration_number == declaration_number
            
            # Should have correct type based on number
            if declaration_number.startswith('30'):
                assert result.declaration_type == DeclarationType.EXPORT_CLEARANCE
            else:
                assert result.declaration_type == DeclarationType.IMPORT_CLEARANCE
    
    @given(declaration_number_strategy())
    @settings(max_examples=100)
    def test_property_no_database_config_fallback(self, declaration_number):
        """
        **Feature: customs-declaration-printing, Property 3: Data source priority and fallback**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        For any declaration number, when no database configuration is provided,
        the system should skip database extraction and go directly to XML fallback.
        """
        # Create extractor without database config
        with tempfile.TemporaryDirectory() as temp_dir:
            extractor = DeclarationDataExtractor(
                db_config=None,  # No database config
                xml_directory=temp_dir,
                logger=self.logger
            )
            
            mock_xml_data = Mock(spec=DeclarationData)
            mock_xml_data.declaration_number = declaration_number
            
            with patch.object(extractor, 'find_xml_file', return_value=f"{temp_dir}/test.xml"):
                with patch.object(extractor, 'extract_from_xml', return_value=mock_xml_data) as mock_xml:
                    
                    result = extractor.extract_with_fallback(declaration_number)
                    
                    # Should attempt XML extraction
                    mock_xml.assert_called_once()
                    
                    # Result should be XML data
                    assert result == mock_xml_data
    
    @given(st.lists(declaration_number_strategy(), min_size=1, max_size=5))
    @settings(max_examples=20)
    def test_property_multiple_declarations_independence(self, declaration_numbers):
        """
        **Feature: customs-declaration-printing, Property 3: Data source priority and fallback**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        For any list of declaration numbers, extraction results should be
        independent - failure of one should not affect others.
        """
        extractor = DeclarationDataExtractor(logger=self.logger)
        
        results = []
        for declaration_number in declaration_numbers:
            with patch.object(extractor, 'extract_from_database', return_value=None):
                with patch.object(extractor, 'find_xml_file', return_value=None):
                    result = extractor.extract_with_fallback(declaration_number)
                    results.append(result)
        
        # All should return basic templates
        assert len(results) == len(declaration_numbers)
        
        for i, result in enumerate(results):
            assert result is not None
            assert result.declaration_number == declaration_numbers[i]
            assert result.additional_data.get('source') == 'basic_template'