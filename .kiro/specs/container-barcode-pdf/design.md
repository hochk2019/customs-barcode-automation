# Design Document - Container Barcode PDF

## Overview

Tính năng này mở rộng module `BarcodePdfGenerator` để hỗ trợ tạo PDF cho tờ khai hàng container (MaPTVC = 2). Khi phát hiện tờ khai container, hệ thống sẽ sử dụng layout khác với bảng 6 cột chứa thông tin container và mã QR cho từng container.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    QRCodeContainerApiClient                      │
│  - query_bang_ke() returns ContainerDeclarationInfo              │
│  - _parse_bang_ke() extracts container list with QR images       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ContainerDeclarationInfo                        │
│  - ma_ptvc: str (determines PDF layout)                          │
│  - containers: List[ContainerInfo] (with barcode_image)          │
│  - is_container_declaration property                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BarcodePdfGenerator                           │
│  - generate_pdf() checks ma_ptvc                                 │
│  - _build_content() or _build_container_content()                │
│  - _build_container_table() creates 6-column table               │
│  - _decode_qr_image() converts base64 to ReportLab Image         │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. ContainerInfo (Updated Data Model)

```python
@dataclass
class ContainerInfo:
    """Information about a container in the declaration"""
    stt: int = 0
    so_container: str = ""
    so_seal: str = ""
    so_seal_hq: str = ""
    barcode_image: str = ""  # Base64 encoded PNG
    ghi_chu: str = ""
```

### 2. ContainerDeclarationInfo (Updated)

```python
@dataclass
class ContainerDeclarationInfo:
    # ... existing fields ...
    
    @property
    def is_container_declaration(self) -> bool:
        """Check if this is a container declaration (MaPTVC = 2)"""
        return str(self.ma_ptvc) == "2"
```

### 3. BarcodePdfGenerator (Updated)

```python
class BarcodePdfGenerator:
    def generate_pdf(self, info: ContainerDeclarationInfo) -> Optional[bytes]:
        """Generate PDF - routes to appropriate layout based on ma_ptvc"""
        if info.is_container_declaration:
            elements = self._build_container_content(info)
        else:
            elements = self._build_content(info)
        # ... rest of generation
    
    def _build_container_content(self, info: ContainerDeclarationInfo) -> list:
        """Build PDF content for container declarations"""
        # Header section (similar but no barcode, shows "- 2")
        # Title: "DANH SÁCH CONTAINER"
        # Items 1-9 (same as regular)
        # Container table (6 columns)
        # Notes section
    
    def _build_container_table(self, containers: List[ContainerInfo]) -> Table:
        """Build 6-column table for containers"""
        # Columns: STT, SỐ HIỆU CONTAINER, SỐ SEAL CONTAINER, 
        #          SỐ SEAL HẢI QUAN, XÁC NHẬN, MÃ VẠCH
    
    def _decode_qr_image(self, base64_data: str) -> Optional[Image]:
        """Decode base64 PNG to ReportLab Image"""
        # Decode base64 -> bytes -> BytesIO -> Image
```

## Data Models

### Container Table Structure

| Column | Header | Data Source | Width |
|--------|--------|-------------|-------|
| 1 | STT | Stt field | 1cm |
| 2 | SỐ HIỆU CONTAINER (1) | SoContainer | 3cm |
| 3 | SỐ SEAL CONTAINER (Nếu có) (2) | SoSeal | 2.5cm |
| 4 | SỐ SEAL HẢI QUAN (Nếu có) (3) | SoSealHQ | 2.5cm |
| 5 | XÁC NHẬN CỦA CÔNG CHỨC HẢI QUAN (4) | Empty | 3cm |
| 6 | MÃ VẠCH (5) | BarcodeImage (QR) | 2.5cm |

### API Response Structure (BangKe)

```xml
<BangKe>
  <diffgr:diffgram>
    <DocumentElement>
      <Table_BangKe>
        <Stt>1</Stt>
        <SoContainer>BEAU6168370 </SoContainer>
        <SoSeal>NA </SoSeal>
        <SoSealHQ>#####</SoSealHQ>
        <BarcodeImage>iVBORw0KGgo...</BarcodeImage>
        <GhiChu />
      </Table_BangKe>
      <!-- More containers... -->
    </DocumentElement>
  </diffgr:diffgram>
</BangKe>
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Container Declaration Detection
*For any* declaration data, if MaPTVC equals "2" then is_container_declaration should return True, otherwise it should return False.
**Validates: Requirements 1.1, 1.2**

### Property 2: PDF Layout Selection
*For any* declaration data, if is_container_declaration is True then the generated PDF should contain "DANH SÁCH CONTAINER", otherwise it should contain "DANH SÁCH HÀNG HÓA".
**Validates: Requirements 1.3, 3.1**

### Property 3: Container Row Count
*For any* container declaration with N containers in the BangKe list, the generated PDF table should have exactly N data rows with STT values from 1 to N.
**Validates: Requirements 5.2**

### Property 4: Seal Value Display
*For any* container with SoSealHQ value of "#####", the displayed value in column 3 should be empty. For any other non-empty SoSealHQ value, it should be displayed as-is.
**Validates: Requirements 5.4, 5.5**

### Property 5: Base64 Image Decoding Round-Trip
*For any* valid base64 encoded PNG image, decoding and re-encoding should produce equivalent image data.
**Validates: Requirements 6.1**

### Property 6: BangKe Parsing Completeness
*For any* valid BangKe XML with N Table_BangKe elements, parsing should produce exactly N ContainerInfo objects with all fields correctly extracted.
**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

### Property 7: Whitespace Trimming
*For any* SoContainer or SoSeal string with leading or trailing whitespace, the displayed value should have no leading or trailing whitespace.
**Validates: Requirements 7.5**

## Error Handling

1. **Invalid Base64 Data**: If BarcodeImage contains invalid base64 data, log error and display empty cell
2. **Missing Container Data**: If BangKe section is empty for MaPTVC=2, generate PDF with empty table
3. **Missing Fields**: If SoContainer is empty, skip that container row
4. **Large Container Lists**: Handle declarations with many containers (pagination if needed)

## Testing Strategy

### Property-Based Testing

Using `hypothesis` library for Python:

1. **Container Detection Property**: Generate random MaPTVC values and verify is_container_declaration
2. **Layout Selection Property**: Generate declarations with various MaPTVC values and check PDF title
3. **Row Count Property**: Generate container lists of various sizes and verify table row count
4. **Seal Display Property**: Generate containers with various SoSealHQ values and verify display
5. **Base64 Decoding Property**: Generate valid PNG images, encode to base64, decode and compare
6. **Parsing Property**: Generate valid BangKe XML and verify parsed container count and fields
7. **Whitespace Trimming Property**: Generate strings with whitespace and verify trimming

### Unit Tests

1. Test `is_container_declaration` property with edge cases
2. Test `_decode_qr_image()` with valid and invalid base64 data
3. Test `_parse_bang_ke()` with sample XML data
4. Test `_build_container_table()` with various container lists
5. Test `_build_container_content()` generates correct structure

### Integration Tests

1. Test full PDF generation for container declaration (MaPTVC=2)
2. Test full PDF generation for regular declaration (MaPTVC=1)
3. Test with real API response data from test file
