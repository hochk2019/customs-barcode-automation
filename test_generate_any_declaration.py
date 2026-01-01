#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test tạo tờ khai từ database với bất kỳ số tờ khai nào
"""

from generate_declaration_from_db import DeclarationGenerator, DeclarationComparator
from pathlib import Path
import sys

def test_generate(declaration_number: str):
    """Test tạo tờ khai"""
    
    print(f"\n{'='*70}")
    print(f"🧪 TEST TẠO TỜ KHAI: {declaration_number}")
    print(f"{'='*70}")
    
    generator = DeclarationGenerator("test_output")
    
    output_file = generator.generate(declaration_number)
    
    if output_file:
        print(f"\n✅ Thành công: {output_file}")
        
        # Kiểm tra file
        file_size = Path(output_file).stat().st_size
        print(f"   📊 Kích thước: {file_size:,} bytes")
        
        return output_file
    else:
        print(f"\n❌ Thất bại!")
        return None

def list_recent_declarations():
    """Liệt kê các tờ khai gần đây trong database"""
    
    from database.ecus_connector import EcusDataConnector
    from config.configuration_manager import ConfigurationManager
    
    print(f"\n{'='*70}")
    print(f"📋 CÁC TỜ KHAI GẦN ĐÂY TRONG DATABASE")
    print(f"{'='*70}")
    
    config = ConfigurationManager("config.ini")
    db_config = config.get_database_config()
    
    connector = EcusDataConnector(db_config)
    
    if not connector.connect():
        print("❌ Không thể kết nối database!")
        return []
    
    try:
        cursor = connector._connection.cursor()
        
        # Lấy 20 tờ khai gần nhất
        query = """
            SELECT TOP 20 SOTK, _XorN, MA_LH, MA_HQ, NGAY_DK, MA_DV, _Ten_DV_L1, SOHANG
            FROM DTOKHAIMD 
            ORDER BY NGAY_DK DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"\n{'Số TK':<15} {'Loại':<5} {'Mã LH':<6} {'HQ':<6} {'Ngày ĐK':<12} {'MST':<12} {'Tên DN':<30} {'Hàng':<5}")
        print("-" * 100)
        
        declarations = []
        for row in rows:
            sotk, xorn, ma_lh, ma_hq, ngay_dk, ma_dv, ten_dv, sohang = row
            ngay_str = ngay_dk.strftime('%d/%m/%Y') if ngay_dk else ''
            ten_dv_short = (ten_dv or '')[:28]
            
            print(f"{sotk:<15} {xorn or 'N':<5} {ma_lh or '':<6} {ma_hq or '':<6} {ngay_str:<12} {ma_dv or '':<12} {ten_dv_short:<30} {sohang or 0:<5}")
            
            declarations.append({
                'sotk': sotk,
                'xorn': xorn,
                'ma_lh': ma_lh,
                'ten_dv': ten_dv
            })
        
        cursor.close()
        connector.disconnect()
        
        return declarations
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return []

if __name__ == "__main__":
    # Liệt kê các tờ khai gần đây
    declarations = list_recent_declarations()
    
    if len(sys.argv) > 1:
        # Nếu có tham số, tạo tờ khai đó
        declaration_number = sys.argv[1]
        test_generate(declaration_number)
    else:
        # Mặc định test với tờ khai đầu tiên trong danh sách
        if declarations:
            print(f"\n💡 Để tạo tờ khai, chạy: python test_generate_any_declaration.py <số_tờ_khai>")
            print(f"   Ví dụ: python test_generate_any_declaration.py {declarations[0]['sotk']}")
            
            # Test với tờ khai đầu tiên
            print(f"\n🧪 Auto-test với tờ khai: {declarations[0]['sotk']}")
            test_generate(declarations[0]['sotk'])
