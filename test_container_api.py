"""Test API and PDF generation for container declaration (MaPTVC = 2)"""
from datetime import date

# Simple mock logger
class MockLogger:
    def debug(self, msg, **kwargs): pass
    def info(self, msg, **kwargs): print(f'INFO: {msg}')
    def warning(self, msg, **kwargs): print(f'WARNING: {msg}')
    def error(self, msg, **kwargs): print(f'ERROR: {msg}')

from web_utils.qrcode_api_client import QRCodeContainerApiClient
from web_utils.barcode_pdf_generator import BarcodePdfGenerator

# Test data for container declaration (MaPTVC = 2)
ma_so_thue = '2301298337'
so_to_khai = '308044805740'
ma_hai_quan = '18A3'
ngay_to_khai = date(2025, 12, 10)

print('Testing API with container declaration...')
client = QRCodeContainerApiClient(logger=MockLogger())
try:
    result = client.query_bang_ke(ma_so_thue, so_to_khai, ma_hai_quan, ngay_to_khai)
    
    if result:
        print(f'ma_ptvc: {result.ma_ptvc}')
        print(f'is_container_declaration: {result.is_container_declaration}')
        print(f'Number of containers: {len(result.containers)}')
        
        for i, cont in enumerate(result.containers):
            print(f'  Container {i+1}: {cont.so_container}')
        
        # Generate PDF
        print('\nGenerating container PDF...')
        generator = BarcodePdfGenerator(logger=MockLogger())
        pdf_bytes = generator.generate_pdf(result)
        
        if pdf_bytes:
            output_file = 'test_container_pdf_v2.pdf'
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            print(f'PDF saved: {output_file} ({len(pdf_bytes)} bytes)')
        else:
            print('Failed to generate PDF')
    else:
        print('No result from API')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    client.close()
