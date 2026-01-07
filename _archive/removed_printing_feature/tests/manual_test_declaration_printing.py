"""
Manual test script for declaration printing functionality.

This script tests the complete declaration printing workflow with real sample data
to verify that the feature works correctly for both import and export declarations.

Usage: python tests/manual_test_declaration_printing.py
"""

import importlib.util
import sys

if "pytest" in sys.modules and importlib.util.find_spec("declaration_printing") is None:
    import pytest
    pytest.skip("declaration_printing package not installed", allow_module_level=True)

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from declaration_printing.declaration_printer import DeclarationPrinter
from declaration_printing.models import DeclarationData, DeclarationType, GoodsItem
from config.configuration_manager import ConfigurationManager
from logging_system.logger import Logger
from datetime import datetime
from decimal import Decimal


class ManualDeclarationPrintingTest:
    """Manual test for declaration printing functionality."""
    
    def __init__(self):
        """Initialize the test environment."""
        print("🔧 Khởi tạo môi trường test...")
        
        # Setup output directory
        self.output_dir = "test_output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize logger
        from models.config_models import LoggingConfig
        logging_config = LoggingConfig(
            log_level="INFO",
            log_file="logs/test.log",
            max_log_size=10485760,  # 10MB
            backup_count=5
        )
        self.logger = Logger(logging_config)
        
        # Initialize configuration manager (optional for this test)
        try:
            self.config_manager = ConfigurationManager()
        except Exception as e:
            print(f"⚠️  Không thể tải config manager: {e}")
            self.config_manager = None
        
        # Initialize declaration printer
        self.printer = DeclarationPrinter(
            config_manager=self.config_manager,
            logger=self.logger,
            output_directory=self.output_dir
        )
        
        print(f"✅ Đã khởi tạo xong. Thư mục output: {self.output_dir}")
    
    def create_sample_import_declaration(self) -> DeclarationData:
        """Create sample import declaration data (NK - 10...)."""
        return DeclarationData(
            # Basic Information
            declaration_number="107772836360",
            declaration_type=DeclarationType.IMPORT_CLEARANCE,
            customs_office="Cục Hải quan TP.HCM",
            declaration_date=datetime(2024, 1, 15),
            
            # Company Information
            company_tax_code="0123456789",
            company_name="CÔNG TY TNHH ABC VIỆT NAM",
            company_address="123 Đường Nguyễn Văn Cừ, Quận 5, TP.HCM",
            
            # Trade Information
            partner_name="ABC TRADING CO., LTD",
            partner_address="123 Main Street, New York, USA",
            country_of_origin="US",
            country_of_destination="VN",
            
            # Financial Information
            total_value=Decimal("50000.00"),
            currency="USD",
            exchange_rate=Decimal("24500.00"),
            
            # Goods Information
            goods_list=[
                GoodsItem(
                    item_number=1,
                    hs_code="8471300000",
                    description="Máy tính xách tay",
                    quantity=Decimal("10"),
                    unit="Cái",
                    unit_price=Decimal("1000.00"),
                    total_value=Decimal("10000.00"),
                    origin_country="US"
                ),
                GoodsItem(
                    item_number=2,
                    hs_code="8528721000",
                    description="Màn hình LCD",
                    quantity=Decimal("20"),
                    unit="Cái",
                    unit_price=Decimal("500.00"),
                    total_value=Decimal("10000.00"),
                    origin_country="US"
                )
            ],
            total_weight=Decimal("150.5"),
            total_packages=3,
            
            # Transport Information
            transport_method="Đường biển",
            bill_of_lading="MSKU1234567",
            container_numbers=["MSKU1234567"],
            
            # Additional Fields
            additional_data={
                "status": "T",  # Thông quan
                "customs_procedure": "40",
                "warehouse": "ICD Tân Cảng",
                "inspector": "Nguyễn Văn A",
                "inspection_date": "2024-01-16"
            }
        )
    
    def create_sample_export_declaration(self) -> DeclarationData:
        """Create sample export declaration data (XK - 30...)."""
        return DeclarationData(
            # Basic Information
            declaration_number="305254403660",
            declaration_type=DeclarationType.EXPORT_CLEARANCE,
            customs_office="Cục Hải quan TP.HCM",
            declaration_date=datetime(2024, 1, 20),
            
            # Company Information
            company_tax_code="0987654321",
            company_name="CÔNG TY CỔ PHẦN XYZ",
            company_address="456 Đường Lê Văn Việt, Quận 9, TP.HCM",
            
            # Trade Information
            partner_name="XYZ IMPORT EXPORT LLC",
            partner_address="789 Business Ave, Los Angeles, USA",
            country_of_origin="VN",
            country_of_destination="US",
            
            # Financial Information
            total_value=Decimal("75000.00"),
            currency="USD",
            exchange_rate=Decimal("24500.00"),
            
            # Goods Information
            goods_list=[
                GoodsItem(
                    item_number=1,
                    hs_code="6403999000",
                    description="Giày da xuất khẩu",
                    quantity=Decimal("500"),
                    unit="Đôi",
                    unit_price=Decimal("25.00"),
                    total_value=Decimal("12500.00"),
                    origin_country="VN"
                ),
                GoodsItem(
                    item_number=2,
                    hs_code="6204620000",
                    description="Quần áo nữ",
                    quantity=Decimal("1000"),
                    unit="Cái",
                    unit_price=Decimal("15.00"),
                    total_value=Decimal("15000.00"),
                    origin_country="VN"
                )
            ],
            total_weight=Decimal("250.8"),
            total_packages=50,
            
            # Transport Information
            transport_method="Đường biển",
            bill_of_lading="COSCO9876543",
            container_numbers=["COSCO9876543", "COSCO9876544"],
            
            # Additional Fields
            additional_data={
                "status": "T",  # Thông quan
                "customs_procedure": "10",
                "warehouse": "Cảng Cát Lái",
                "inspector": "Trần Thị B",
                "inspection_date": "2024-01-21"
            }
        )
    
    def test_import_declaration_printing(self) -> bool:
        """Test printing import declaration (NK)."""
        print("\n📋 Test 1: In tờ khai nhập khẩu (NK)")
        print("=" * 50)
        
        try:
            # Create sample data
            declaration_data = self.create_sample_import_declaration()
            print(f"✅ Đã tạo dữ liệu mẫu cho tờ khai: {declaration_data.declaration_number}")
            
            # Print declaration
            print("🖨️  Đang in tờ khai...")
            result = self.printer.print_single_declaration(declaration_data.declaration_number)
            
            if result.success:
                print(f"✅ In thành công!")
                print(f"📁 File đã tạo: {result.output_file_path}")
                print(f"⏱️  Thời gian xử lý: {result.processing_time:.2f} giây")
                
                # Check if file exists
                if result.output_file_path and os.path.exists(result.output_file_path):
                    file_size = os.path.getsize(result.output_file_path)
                    print(f"📊 Kích thước file: {file_size:,} bytes")
                    return True
                else:
                    print("❌ File không tồn tại sau khi in")
                    return False
            else:
                print(f"❌ In thất bại: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi trong quá trình test: {e}")
            return False
    
    def test_export_declaration_printing(self) -> bool:
        """Test printing export declaration (XK)."""
        print("\n📋 Test 2: In tờ khai xuất khẩu (XK)")
        print("=" * 50)
        
        try:
            # Create sample data
            declaration_data = self.create_sample_export_declaration()
            print(f"✅ Đã tạo dữ liệu mẫu cho tờ khai: {declaration_data.declaration_number}")
            
            # Print declaration
            print("🖨️  Đang in tờ khai...")
            result = self.printer.print_single_declaration(declaration_data.declaration_number)
            
            if result.success:
                print(f"✅ In thành công!")
                print(f"📁 File đã tạo: {result.output_file_path}")
                print(f"⏱️  Thời gian xử lý: {result.processing_time:.2f} giây")
                
                # Check if file exists
                if result.output_file_path and os.path.exists(result.output_file_path):
                    file_size = os.path.getsize(result.output_file_path)
                    print(f"📊 Kích thước file: {file_size:,} bytes")
                    return True
                else:
                    print("❌ File không tồn tại sau khi in")
                    return False
            else:
                print(f"❌ In thất bại: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi trong quá trình test: {e}")
            return False
    
    def test_batch_printing(self) -> bool:
        """Test batch printing with both import and export declarations."""
        print("\n📋 Test 3: In hàng loạt (Batch)")
        print("=" * 50)
        
        try:
            declaration_numbers = ["107772836360", "305254403660"]
            print(f"🔄 Đang in {len(declaration_numbers)} tờ khai...")
            
            # Print batch
            result = self.printer.print_declarations(declaration_numbers)
            
            print(f"📊 Kết quả batch:")
            print(f"   - Tổng số: {result.total_processed}")
            print(f"   - Thành công: {result.successful}")
            print(f"   - Thất bại: {result.failed}")
            print(f"   - Thời gian: {result.total_time:.2f} giây")
            print(f"   - Bị hủy: {'Có' if result.cancelled else 'Không'}")
            
            if result.successful > 0:
                print("✅ Batch printing thành công!")
                return True
            else:
                print("❌ Batch printing thất bại!")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi trong quá trình test batch: {e}")
            return False
    
    def test_template_validation(self) -> bool:
        """Test template validation."""
        print("\n📋 Test 4: Kiểm tra template")
        print("=" * 50)
        
        try:
            # Check import template
            import_template = self.printer.template_manager.get_template_path(DeclarationType.IMPORT_CLEARANCE)
            print(f"📄 Template NK: {import_template}")
            
            if os.path.exists(import_template):
                print("✅ Template NK tồn tại")
                import_valid = self.printer.template_manager.validate_template(import_template)
                print(f"✅ Template NK hợp lệ: {'Có' if import_valid else 'Không'}")
            else:
                print("❌ Template NK không tồn tại")
                return False
            
            # Check export template
            export_template = self.printer.template_manager.get_template_path(DeclarationType.EXPORT_CLEARANCE)
            print(f"📄 Template XK: {export_template}")
            
            if os.path.exists(export_template):
                print("✅ Template XK tồn tại")
                export_valid = self.printer.template_manager.validate_template(export_template)
                print(f"✅ Template XK hợp lệ: {'Có' if export_valid else 'Không'}")
            else:
                print("❌ Template XK không tồn tại")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi kiểm tra template: {e}")
            return False
    
    def run_all_tests(self) -> None:
        """Run all manual tests."""
        print("🚀 BẮT ĐẦU KIỂM THỬ TÍNH NĂNG IN TỜ KHAI")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run tests
        tests = [
            ("Kiểm tra template", self.test_template_validation),
            ("In tờ khai nhập khẩu", self.test_import_declaration_printing),
            ("In tờ khai xuất khẩu", self.test_export_declaration_printing),
            ("In hàng loạt", self.test_batch_printing)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Lỗi trong test '{test_name}': {e}")
                results.append((test_name, False))
        
        # Summary
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("📊 KẾT QUẢ KIỂM THỬ")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Tổng kết: {passed}/{total} tests passed")
        print(f"⏱️  Tổng thời gian: {total_time:.2f} giây")
        
        if passed == total:
            print("🎉 TẤT CẢ TESTS ĐỀU THÀNH CÔNG!")
            print("✅ Tính năng in tờ khai hoạt động bình thường")
        else:
            print("⚠️  CÓ TESTS THẤT BẠI!")
            print("❌ Cần kiểm tra và sửa lỗi")
        
        # Show output files
        print(f"\n📁 Các file đã tạo trong thư mục '{self.output_dir}':")
        if os.path.exists(self.output_dir):
            files = list(Path(self.output_dir).glob("*.xlsx"))
            if files:
                for file in files:
                    size = file.stat().st_size
                    print(f"   - {file.name} ({size:,} bytes)")
            else:
                print("   (Không có file nào)")
        
        print("\n🔍 Hướng dẫn kiểm tra thủ công:")
        print("1. Mở các file Excel trong thư mục test_output")
        print("2. Kiểm tra dữ liệu đã được điền đúng vào template")
        print("3. Xác nhận format và layout của file")
        print("4. Kiểm tra tên file theo convention: ToKhaiHQ7[X/N]_QDTQ_[SoToKhai].xlsx")


def main():
    """Main function to run the manual test."""
    try:
        # Create and run test
        test = ManualDeclarationPrintingTest()
        test.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n⏹️  Test bị dừng bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()