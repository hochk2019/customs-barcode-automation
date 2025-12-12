"""Test to check container seal data from API"""
from datetime import date

# Simple mock logger
class MockLogger:
    def debug(self, msg, **kwargs): pass
    def info(self, msg, **kwargs): print(f'INFO: {msg}')
    def warning(self, msg, **kwargs): print(f'WARNING: {msg}')
    def error(self, msg, **kwargs): print(f'ERROR: {msg}')

from web_utils.qrcode_api_client import QRCodeContainerApiClient

# Test data for container declaration (MaPTVC = 2)
ma_so_thue = '2301298337'
so_to_khai = '308044805740'
ma_hai_quan = '18A3'
ngay_to_khai = date(2025, 12, 10)

print('Testing API with container declaration...')
print('='*60)
client = QRCodeContainerApiClient(logger=MockLogger())
try:
    result = client.query_bang_ke(ma_so_thue, so_to_khai, ma_hai_quan, ngay_to_khai)
    
    if result:
        print(f'ma_ptvc: {result.ma_ptvc}')
        print(f'is_container_declaration: {result.is_container_declaration}')
        print(f'Number of containers: {len(result.containers)}')
        print('='*60)
        
        for i, cont in enumerate(result.containers):
            print(f'\nContainer {i+1}:')
            print(f'  STT: {cont.stt}')
            print(f'  SoContainer: "{cont.so_container}"')
            print(f'  SoSeal: "{cont.so_seal}"')
            print(f'  SoSealHQ: "{cont.so_seal_hq}"')
            print(f'  Has BarcodeImage: {bool(cont.barcode_image)}')
            print(f'  GhiChu: "{cont.ghi_chu}"')
    else:
        print('No result from API')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    client.close()
