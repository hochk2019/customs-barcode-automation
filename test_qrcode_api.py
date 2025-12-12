"""
Test script for QRCode API Client

This script tests the new QRCode API client with real data.
"""

from datetime import date, datetime
from web_utils.qrcode_api_client import QRCodeContainerApiClient, QRCodeApiError
from logging_system.logger import Logger
from models.config_models import LoggingConfig


def get_logger():
    """Create a logger instance for testing"""
    config = LoggingConfig(
        log_level='DEBUG',
        log_file='logs/test_api.log',
        max_log_size=10485760,
        backup_count=3
    )
    return Logger(config)


def test_api_connection():
    """Test basic API connection"""
    print("=" * 60)
    print("Testing QRCode API Connection")
    print("=" * 60)
    
    logger = get_logger()
    client = QRCodeContainerApiClient(logger=logger, timeout=30)
    
    print(f"Service URL: {client.service_url}")
    
    # Test connection
    print("\n1. Testing connection...")
    if client.test_connection():
        print("   ✓ Connection successful!")
    else:
        print("   ✗ Connection failed!")
        return False
    
    return True


def test_query_declaration():
    """Test querying a declaration"""
    print("\n" + "=" * 60)
    print("Testing QueryBangKeDanhSachContainer")
    print("=" * 60)
    
    logger = get_logger()
    client = QRCodeContainerApiClient(logger=logger, timeout=30)
    
    # Test data from Fiddler capture
    test_cases = [
        {
            'ma_so_thue': '0109742786',
            'so_to_khai': '107781064420',
            'ma_hai_quan': '01B1',  # Mã hải quan từ response
            'ngay_dang_ky': date(2025, 12, 9)
        },
        # Add more test cases as needed
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing with:")
        print(f"   - Mã số thuế: {test['ma_so_thue']}")
        print(f"   - Số tờ khai: {test['so_to_khai']}")
        print(f"   - Mã hải quan: {test['ma_hai_quan']}")
        print(f"   - Ngày đăng ký: {test['ngay_dang_ky']}")
        
        try:
            result = client.query_bang_ke(
                ma_so_thue=test['ma_so_thue'],
                so_to_khai=test['so_to_khai'],
                ma_hai_quan=test['ma_hai_quan'],
                ngay_dang_ky=test['ngay_dang_ky']
            )
            
            if result:
                print("\n   ✓ Query successful!")
                print(f"\n   Response data:")
                print(f"   - Mã số thuế: {result.ma_so_thue}")
                print(f"   - Số tờ khai: {result.so_to_khai}")
                print(f"   - Ngày tờ khai: {result.ngay_to_khai}")
                print(f"   - Tên đơn vị XNK: {result.ten_don_vi_xnk}")
                print(f"   - Loại hình: {result.loai_hinh} - {result.ten_loai_hinh}")
                print(f"   - Trạng thái: {result.trang_thai_to_khai}")
                print(f"   - Luồng: {result.luong_to_khai}")
                print(f"   - Số định danh: {result.so_dinh_danh}")
                print(f"   - Ghi chú: {result.ghi_chu}")
                print(f"   - Số lượng hàng: {result.so_luong_hang} {result.dvt_so_luong_hang}")
                print(f"   - Trọng lượng: {result.tong_trong_luong_hang} {result.dvt_tong_trong_luong_hang}")
                print(f"   - Thời gian lấy dữ liệu: {result.thoi_gian_lay_du_lieu}")
                
                if result.thong_bao_loi:
                    print(f"   - Thông báo lỗi: {result.thong_bao_loi}")
                
                if result.containers:
                    print(f"\n   Containers ({len(result.containers)}):")
                    for c in result.containers:
                        print(f"     - {c.so_container} (Seal: {c.so_seal}, Weight: {c.trong_luong})")
            else:
                print("\n   ✗ No data returned")
                
        except QRCodeApiError as e:
            print(f"\n   ✗ API Error: {e}")
        except Exception as e:
            print(f"\n   ✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    client.close()


def test_soap_request_format():
    """Test SOAP request format"""
    print("\n" + "=" * 60)
    print("Testing SOAP Request Format")
    print("=" * 60)
    
    logger = get_logger()
    client = QRCodeContainerApiClient(logger=logger)
    
    # Build a sample request
    request = client._build_soap_request(
        ma_so_thue='2300944637',
        so_to_khai='308038881420',
        ma_hai_quan='18A3',
        ngay_dang_ky=date(2025, 12, 9)
    )
    
    print("\nGenerated SOAP Request:")
    print("-" * 40)
    print(request)
    print("-" * 40)
    
    client.close()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("QRCode API Client Test Suite")
    print("=" * 60)
    
    # Test 1: Connection
    if not test_api_connection():
        print("\nConnection test failed. Exiting.")
        exit(1)
    
    # Test 2: SOAP format
    test_soap_request_format()
    
    # Test 3: Query declaration
    test_query_declaration()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
