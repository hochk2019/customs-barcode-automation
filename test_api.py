"""
Debug test for declaration 107851575050
"""
import sys
sys.path.insert(0, '.')

from web_utils.qrcode_api_client import QRCodeContainerApiClient
from datetime import datetime

class SimpleLogger:
    def info(self, msg): print(f"[INFO] {msg}")
    def debug(self, msg): print(f"[DEBUG] {msg}")
    def warning(self, msg): print(f"[WARN] {msg}")
    def error(self, msg, *args, **kwargs): print(f"[ERROR] {msg}")

logger = SimpleLogger()

print("=" * 70)
print("Testing declaration 107851575050 (reported as cleared but shows pending)")
print("MST: 0109742786, TK: 107851575050, HQ: 01M1, Date: 30/12/2025")
print("-" * 70)

client = QRCodeContainerApiClient(logger=logger, timeout=15)
result = client.query_bang_ke(
    ma_so_thue='0109742786',
    so_to_khai='107851575050',
    ma_hai_quan='01M1',
    ngay_dang_ky=datetime(2025, 12, 30)
)

print("\n=== FULL API RESPONSE ===")
print(f"is_valid: {result.is_valid}")
print(f"has_error: {result.has_error}")
print(f"ThongBaoLoi: '{result.thong_bao_loi}'")
print(f"MaTrangThaiToKhai: '{result.ma_trang_thai_to_khai}'")
print(f"TrangThaiToKhai: '{result.trang_thai_to_khai}'")
print(f"LuongToKhai: '{result.luong_to_khai}'")
print(f"TenDonViXNK: '{result.ten_don_vi_xnk}'")
print(f"Containers: {len(result.containers) if result.containers else 0}")

# Check for barcodes
if result.containers:
    for i, c in enumerate(result.containers[:3]):
        has_barcode = bool(c.barcode_image)
        print(f"  Container {i+1}: {c.so_container}, has_barcode: {has_barcode}")

# Current detection logic
print("\n=== DETECTION LOGIC ===")
trang_thai = (result.trang_thai_to_khai or "").lower()
error_msg = (result.thong_bao_loi or "").lower()

cleared_keywords = ["thông quan", "thong quan", "chấp nhận thông quan"]
transfer_keywords = ["chuyển địa điểm", "chuyen dia diem"]

is_cleared = any(kw in trang_thai for kw in cleared_keywords)
is_transfer = any(kw in trang_thai for kw in transfer_keywords)
is_pending_error = "chưa được cấp phép" in error_msg

print(f"trang_thai check for 'thông quan': {is_cleared}")
print(f"trang_thai check for 'chuyển địa điểm': {is_transfer}")
print(f"error_msg check for 'chưa được cấp phép': {is_pending_error}")

# Check barcodes
has_barcodes = False
if result.containers:
    has_barcodes = any(c.barcode_image for c in result.containers)
print(f"has_barcodes: {has_barcodes}")

print("\n=== FINAL STATUS ===")
if is_cleared:
    print(">>> CLEARED (Đã thông quan)")
elif is_transfer:
    print(">>> TRANSFER (Chuyển địa điểm)")
elif is_pending_error:
    print(">>> PENDING (Chưa được cấp phép)")
elif has_barcodes:
    print(">>> CLEARED by barcode check")
else:
    print(">>> UNKNOWN")
