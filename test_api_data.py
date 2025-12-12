"""Test API to check is_container data"""
from datetime import date
import sys

# Simple mock logger
class MockLogger:
    def debug(self, msg, **kwargs): print(f"DEBUG: {msg}")
    def info(self, msg, **kwargs): print(f"INFO: {msg}")
    def warning(self, msg, **kwargs): print(f"WARNING: {msg}")
    def error(self, msg, **kwargs): print(f"ERROR: {msg}")

from web_utils.qrcode_api_client import QRCodeContainerApiClient

# Test data
ma_so_thue = "2300944637"
so_to_khai = "107785877140"
ma_hai_quan = "18A3"
ngay_to_khai = date(2025, 12, 10)

print(f"Testing API with:")
print(f"  MST: {ma_so_thue}")
print(f"  TK: {so_to_khai}")
print(f"  HQ: {ma_hai_quan}")
print(f"  Date: {ngay_to_khai}")
print()

client = QRCodeContainerApiClient(logger=MockLogger())
try:
    result = client.query_bang_ke(ma_so_thue, so_to_khai, ma_hai_quan, ngay_to_khai)
    
    if result:
        print("=== API Response ===")
        print(f"so_to_khai: {result.so_to_khai}")
        print(f"ten_chi_cuc_hai_quan_gs: {result.ten_chi_cuc_hai_quan_gs}")
        print(f"ma_ddgs: {result.ma_ddgs}")
        print(f"ten_ddgs: {result.ten_ddgs}")
        print(f"is_container: {result.is_container}")
        print(f"so_dinh_danh: {result.so_dinh_danh}")
        print()
        
        # Build full string like in PDF generator (FIXED: use MaPTVC instead of IsContainer)
        chi_cuc_gs = result.ten_chi_cuc_hai_quan_gs or 'CC HQ CK Sân bay QT Nội Bài'
        if result.ma_ddgs and result.ten_ddgs:
            ma_ptvc_str = f" - {result.ma_ptvc}" if result.ma_ptvc else ""
            chi_cuc_gs_full = f"{chi_cuc_gs} - {result.ma_ddgs}: {result.ten_ddgs}{ma_ptvc_str}"
        elif result.ten_ddgs:
            ma_ptvc_str = f" - {result.ma_ptvc}" if result.ma_ptvc else ""
            chi_cuc_gs_full = f"{chi_cuc_gs} - {result.ten_ddgs}{ma_ptvc_str}"
        else:
            chi_cuc_gs_full = chi_cuc_gs
        
        print(f"ma_ptvc: {result.ma_ptvc}")
        
        print(f"=== Full Chi cuc GS string ===")
        print(f"1. Chi cục hải quan giám sát: {chi_cuc_gs_full}")
    else:
        print("No result returned from API")
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
