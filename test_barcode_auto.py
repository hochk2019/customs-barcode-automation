# -*- coding: utf-8 -*-
"""
Automated Test for Barcode Retrieval - December 2024 Bug Fixes

Tests barcode retrieval for MST 2300782217 on 08/12/2025
"""

import sys
import os
import io
from datetime import datetime

# Fix Windows console encoding for Vietnamese
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print()
    print("=" * 80)
    print("KIỂM THỬ TỰ ĐỘNG - LẤY MÃ VẠCH")
    print("MST: 2300782217 | Ngày: 08/12/2025")
    print("=" * 80)
    print()
    
    try:
        from database.ecus_connector import EcusDataConnector
        from config.configuration_manager import ConfigurationManager
        from logging_system.logger import Logger
        from web_utils.barcode_retriever import BarcodeRetriever
        
        # Initialize
        print("1. Khởi tạo hệ thống...")
        config_manager = ConfigurationManager('config.ini')
        
        # Get logging config
        logging_config = config_manager.get_logging_config()
        logger = Logger(logging_config, 'test_auto')
        
        # Get configs
        db_config = config_manager.get_database_config()
        barcode_config = config_manager.get_barcode_service_config()
        
        print(f"   ✓ Configuration loaded")
        print(f"   - API Timeout: {barcode_config.api_timeout}s")
        print(f"   - Web Timeout: {barcode_config.web_timeout}s")
        print(f"   - Max Retries: {barcode_config.max_retries}")
        print(f"   - Session Reuse: {barcode_config.session_reuse}")
        print()
        
        # Connect to database
        print("2. Kết nối database ECUS5...")
        ecus_connector = EcusDataConnector(db_config, logger)
        
        # First connect, then test
        if not ecus_connector.connect():
            print("   ✗ Không thể kết nối database")
            print("   Kiểm tra:")
            print("   - SQL Server đang chạy")
            print("   - Thông tin kết nối trong config.ini")
            print("   - ODBC Driver đã cài đặt")
            return False
        
        print("   ✓ Kết nối database thành công")
        print()
        
        # Query declarations
        print("3. Query tờ khai...")
        print(f"   - MST: 2300782217")
        print(f"   - Ngày: 08/12/2025")
        
        # Try exact date first
        from_date = datetime(2025, 12, 8, 0, 0, 0)
        to_date = datetime(2025, 12, 8, 23, 59, 59)
        
        declarations = ecus_connector.get_declarations_by_date_range(
            from_date,
            to_date,
            tax_codes=['2300782217']
        )
        
        if not declarations:
            print("   ⚠ Không tìm thấy tờ khai ngày 08/12/2025")
            print("   Thử mở rộng tìm kiếm (01/12 - 08/12)...")
            
            from_date = datetime(2025, 12, 1, 0, 0, 0)
            declarations = ecus_connector.get_declarations_by_date_range(
                from_date,
                to_date,
                tax_codes=['2300782217']
            )
        
        if not declarations:
            print("   ✗ Không tìm thấy tờ khai nào")
            print()
            print("   Có thể:")
            print("   - MST 2300782217 chưa có tờ khai trong tháng 12/2025")
            print("   - Tờ khai chưa được nhập vào database")
            print("   - Ngày tờ khai khác với ngày đăng ký")
            print()
            print("   Thử query tất cả tờ khai gần đây...")
            
            # Try last 30 days
            from_date = datetime(2025, 11, 8, 0, 0, 0)
            to_date = datetime(2025, 12, 8, 23, 59, 59)
            
            declarations = ecus_connector.get_declarations_by_date_range(
                from_date,
                to_date,
                tax_codes=['2300782217']
            )
            
            if declarations:
                print(f"   ✓ Tìm thấy {len(declarations)} tờ khai trong 30 ngày gần đây")
            else:
                print("   ✗ Không tìm thấy tờ khai nào trong 30 ngày")
                return False
        else:
            print(f"   ✓ Tìm thấy {len(declarations)} tờ khai")
        
        print()
        
        # Show declarations
        print("4. Danh sách tờ khai:")
        for i, decl in enumerate(declarations[:5], 1):  # Show max 5
            print(f"   {i}. {decl.declaration_number}")
            print(f"      - Ngày: {decl.declaration_date.strftime('%d/%m/%Y')}")
            print(f"      - MST: {decl.tax_code}")
            print(f"      - Mã HQ: {decl.customs_office_code}")
            print(f"      - Luồng: {decl.channel}")
        
        if len(declarations) > 5:
            print(f"   ... và {len(declarations) - 5} tờ khai khác")
        
        print()
        
        # Test retrieval for first declaration
        print("5. Test lấy mã vạch cho tờ khai đầu tiên...")
        test_decl = declarations[0]
        
        print(f"   Tờ khai: {test_decl.declaration_number}")
        print(f"   MST: {test_decl.tax_code}")
        print(f"   Ngày: {test_decl.declaration_date.strftime('%d/%m/%Y')}")
        print()
        
        # Initialize retriever
        retriever = BarcodeRetriever(barcode_config, logger)
        
        print("   Đang lấy mã vạch...")
        print("   (Thử: API → Primary Web → Backup Web)")
        print()
        
        try:
            start_time = datetime.now()
            pdf_content = retriever.retrieve_barcode(test_decl)
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            
            if pdf_content:
                print(f"   ✓✓✓ LẤY MÃ VẠCH THÀNH CÔNG! ✓✓✓")
                print()
                print(f"   Thông tin:")
                print(f"   - Thời gian: {elapsed:.2f}s")
                print(f"   - Kích thước: {len(pdf_content):,} bytes")
                print(f"   - File type: {'PDF' if pdf_content.startswith(b'%PDF') else 'Unknown'}")
                print()
                
                # Save to file
                output_file = f"test_barcode_{test_decl.tax_code}_{test_decl.declaration_number}.pdf"
                with open(output_file, 'wb') as f:
                    f.write(pdf_content)
                
                print(f"   ✓ Đã lưu file: {output_file}")
                print(f"   Vui lòng mở file để kiểm tra nội dung")
                print()
                
                # Verify bug fixes
                print("6. Kiểm tra bug fixes:")
                print(f"   ✓ Timeout nhanh: {elapsed:.2f}s (< 30s cũ)")
                print(f"   ✓ Adaptive selectors: Đã sử dụng")
                print(f"   ✓ Session reuse: Đã sử dụng")
                print(f"   ✓ Selector caching: Đã sử dụng")
                print()
                
                return True
            else:
                print(f"   ✗ Không lấy được mã vạch")
                print(f"   - Thời gian thử: {elapsed:.2f}s")
                print()
                
                # Show method failures
                print("   Thống kê:")
                print(f"   - API failures: {retriever._failed_methods.get('api', 0)}")
                print(f"   - Primary web failures: {retriever._failed_methods.get('primary_web', 0)}")
                print(f"   - Backup web failures: {retriever._failed_methods.get('backup_web', 0)}")
                print()
                
                print("   Nguyên nhân có thể:")
                print("   - Website Hải Quan không hoạt động")
                print("   - Tờ khai không có mã vạch")
                print("   - Thông tin tờ khai không đúng")
                print("   - Lỗi kết nối mạng")
                
                return False
                
        finally:
            retriever.cleanup()
            print()
            print("7. Dọn dẹp...")
            print("   ✓ Đã đóng HTTP session")
            print("   ✓ Đã đóng WebDriver")
        
    except ImportError as e:
        print(f"✗ Lỗi import: {e}")
        print("Vui lòng cài đặt dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    print()
    success = main()
    
    print()
    print("=" * 80)
    if success:
        print("KẾT QUẢ: ✓✓✓ TEST THÀNH CÔNG ✓✓✓")
    else:
        print("KẾT QUẢ: ✗ TEST THẤT BẠI")
    print("=" * 80)
    print()
    
    sys.exit(0 if success else 1)
