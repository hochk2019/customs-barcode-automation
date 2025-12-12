"""
Test lấy mã vạch cho nhiều tờ khai
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.configuration_manager import ConfigurationManager
from logging_system.logger import Logger
from database.ecus_connector import EcusDataConnector
from web_utils.barcode_retriever import BarcodeRetriever


def test_multiple_declarations():
    """Test lấy mã vạch cho nhiều tờ khai"""
    
    print("=" * 80)
    print("TEST LẤY MÃ VẠCH CHO NHIỀU TỜ KHAI")
    print("=" * 80)
    print()
    
    # Initialize
    config_manager = ConfigurationManager('config.ini')
    logging_config = config_manager.get_logging_config()
    logger = Logger(logging_config, 'test_multiple')
    
    db_config = config_manager.get_database_config()
    barcode_config = config_manager.get_barcode_service_config()
    
    # Connect to database
    connector = EcusDataConnector(db_config, logger)
    connector.connect()
    
    # Get declarations
    tax_code = "2300782217"
    date = datetime(2025, 12, 8)
    
    declarations = connector.get_declarations_by_date_range(date, date, [tax_code])
    print(f"Tìm thấy {len(declarations)} tờ khai")
    print()
    
    # Initialize barcode retriever
    retriever = BarcodeRetriever(barcode_config, logger)
    
    # Test first 5 declarations for thorough testing
    results = []
    test_count = min(5, len(declarations))
    
    for i, decl in enumerate(declarations[:test_count]):
        print(f"[{i+1}/{test_count}] Tờ khai: {decl.declaration_number}")
        print(f"    MST: {decl.tax_code}")
        print(f"    Ngày: {decl.declaration_date.strftime('%d/%m/%Y')}")
        print(f"    Mã HQ: {decl.customs_office_code}")
        
        start_time = datetime.now()
        pdf_content = retriever.retrieve_barcode(decl)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if pdf_content:
            filename = f"barcode_{decl.tax_code}_{decl.declaration_number}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_content)
            print(f"    ✓ THÀNH CÔNG - {len(pdf_content):,} bytes - {elapsed:.1f}s")
            print(f"    ✓ Đã lưu: {filename}")
            results.append(('SUCCESS', decl.declaration_number, len(pdf_content), elapsed))
        else:
            print(f"    ✗ THẤT BẠI - {elapsed:.1f}s")
            results.append(('FAILED', decl.declaration_number, 0, elapsed))
        
        print()
    
    # Summary
    print("=" * 80)
    print("KẾT QUẢ TỔNG HỢP")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r[0] == 'SUCCESS')
    total_count = len(results)
    
    print(f"Thành công: {success_count}/{total_count}")
    print()
    
    for status, decl_num, size, elapsed in results:
        icon = "✓" if status == 'SUCCESS' else "✗"
        print(f"  {icon} {decl_num}: {size:,} bytes ({elapsed:.1f}s)")
    
    print()
    print("=" * 80)
    
    # Cleanup
    retriever.cleanup()
    connector.disconnect()
    
    return success_count == total_count


if __name__ == "__main__":
    success = test_multiple_declarations()
    sys.exit(0 if success else 1)
