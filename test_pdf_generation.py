"""
Test PDF generation from API data
"""
from datetime import date
from web_utils.qrcode_api_client import QRCodeContainerApiClient
from web_utils.barcode_pdf_generator import BarcodePdfGenerator
from logging_system.logger import Logger
from models.config_models import LoggingConfig


def main():
    # Setup logger
    config = LoggingConfig(
        log_level='DEBUG',
        log_file='logs/test_pdf.log',
        max_log_size=10485760,
        backup_count=3
    )
    logger = Logger(config)
    
    # Test data
    mst = "2300944637"
    hq = "18A3"
    tk = "107785050920"
    ngay = date(2025, 12, 9)
    
    print(f"Testing PDF generation for:")
    print(f"  - MST: {mst}")
    print(f"  - Mã HQ: {hq}")
    print(f"  - Số TK: {tk}")
    print(f"  - Ngày: {ngay}")
    print()
    
    # Step 1: Get data from API
    print("1. Fetching data from API...")
    api_client = QRCodeContainerApiClient(logger=logger, timeout=30)
    
    try:
        info = api_client.query_bang_ke(
            ma_so_thue=mst,
            so_to_khai=tk,
            ma_hai_quan=hq,
            ngay_dang_ky=ngay
        )
        
        if not info:
            print("   ERROR: No data returned from API")
            return
        
        if info.has_error:
            print(f"   ERROR: {info.thong_bao_loi}")
            return
        
        print("   SUCCESS! Data received:")
        print(f"   - Tên DN: {info.ten_don_vi_xnk}")
        print(f"   - Số định danh: {info.so_dinh_danh}")
        print(f"   - Trạng thái: {info.trang_thai_to_khai}")
        print(f"   - Luồng: {info.luong_to_khai}")
        print(f"   - Ghi chú: {info.ghi_chu}")
        print()
        
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    finally:
        api_client.close()
    
    # Step 2: Generate PDF
    print("2. Generating PDF...")
    pdf_generator = BarcodePdfGenerator(logger=logger)
    
    try:
        pdf_bytes = pdf_generator.generate_pdf(info)
        
        if not pdf_bytes:
            print("   ERROR: Failed to generate PDF")
            return
        
        # Save PDF to file
        import time
        output_file = f"test_barcode_{tk}_{int(time.time())}.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"   SUCCESS! PDF saved to: {output_file}")
        print(f"   Size: {len(pdf_bytes)} bytes")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("Test completed successfully!")


if __name__ == '__main__':
    main()
