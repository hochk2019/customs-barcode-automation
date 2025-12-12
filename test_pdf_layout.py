"""Test PDF layout - check header centering and bold labels"""
from datetime import date
from web_utils.qrcode_api_client import QRCodeContainerApiClient
from web_utils.barcode_pdf_generator import BarcodePdfGenerator

# Simple mock logger
class MockLogger:
    def debug(self, msg, **kwargs): print(f"DEBUG: {msg}")
    def info(self, msg, **kwargs): print(f"INFO: {msg}")
    def warning(self, msg, **kwargs): print(f"WARNING: {msg}")
    def error(self, msg, **kwargs): print(f"ERROR: {msg}")

# Test data
ma_so_thue = "2300944637"
so_to_khai = "107785877140"
ma_hai_quan = "18A3"
ngay_to_khai = date(2025, 12, 10)

print("=== Testing PDF Layout ===")
print(f"MST: {ma_so_thue}, TK: {so_to_khai}")
print()

# Get API data
client = QRCodeContainerApiClient(logger=MockLogger())
try:
    result = client.query_bang_ke(ma_so_thue, so_to_khai, ma_hai_quan, ngay_to_khai)
    
    if result:
        print("API data retrieved successfully")
        print(f"  is_container: {result.is_container}")
        print()
        
        # Generate PDF
        generator = BarcodePdfGenerator(logger=MockLogger())
        pdf_bytes = generator.generate_pdf(result)
        
        if pdf_bytes:
            output_file = f"test_layout_{so_to_khai}.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            print(f"PDF generated: {output_file} ({len(pdf_bytes)} bytes)")
            print()
            print("Please check the PDF for:")
            print("  1. 'Hải quan Bắc Ninh' centered under 'Chi cục Hải quan khu vực V'")
            print("  2. Items 1-9 labels are bold (e.g., '1. Chi cục hải quan giám sát:')")
            print("  3. Item 1 shows full content including ' - 0' at end")
        else:
            print("ERROR: Failed to generate PDF")
    else:
        print("ERROR: No result from API")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    client.close()
